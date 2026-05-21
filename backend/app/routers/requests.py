from datetime import datetime, timezone
from typing import Annotated, Any

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.common import serialize_doc
from app.models.offer import OfferStatus
from app.models.request import RequestCreate, RequestResponse, RequestStatus
from app.services.cost_calc import distance_km, fuel_split_cost

router = APIRouter(prefix="/requests", tags=["requests"])


def _request_to_response(doc: dict[str, Any]) -> RequestResponse:
    serialized = serialize_doc(doc)
    assert serialized is not None
    return RequestResponse(**serialized)


def _parse_object_id(value: str, label: str = "Resource") -> ObjectId:
    try:
        return ObjectId(value)
    except InvalidId as exc:
        raise HTTPException(status_code=404, detail=f"{label} not found") from exc


async def _get_offer_or_404(db: AsyncIOMotorDatabase, offer_id: str) -> dict[str, Any]:
    offer = await db.ride_offers.find_one({"_id": _parse_object_id(offer_id, "Offer")})
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    return offer


def _can_view_request(
    request_doc: dict[str, Any], offer: dict[str, Any], user: dict[str, Any]
) -> bool:
    return (
        request_doc["riderId"] == user["_id"]
        or offer["driverId"] == user["_id"]
    )


@router.post("", response_model=RequestResponse, status_code=status.HTTP_201_CREATED)
async def create_request(
    body: RequestCreate,
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
):
    offer = await _get_offer_or_404(db, body.offerId)

    if offer.get("status") != OfferStatus.open.value:
        raise HTTPException(status_code=409, detail="Offer is not open for requests")
    if offer["driverId"] == current_user["_id"]:
        raise HTTPException(status_code=400, detail="Cannot request your own offer")
    if offer.get("departureTime") and offer["departureTime"] < datetime.now(
        timezone.utc
    ):
        raise HTTPException(status_code=400, detail="Offer departure time has passed")

    offer_oid = offer["_id"]
    duplicate = await db.ride_requests.find_one(
        {
            "riderId": current_user["_id"],
            "offerId": offer_oid,
            "status": {"$in": [RequestStatus.pending.value, RequestStatus.accepted.value]},
        }
    )
    if duplicate:
        raise HTTPException(
            status_code=409,
            detail="You already have a pending or accepted request for this offer",
        )

    rider_km = distance_km(body.pickup, body.dropoff)
    cost = fuel_split_cost(rider_km, offer.get("fuelSplitRatePerKm"))
    now = datetime.now(timezone.utc)

    doc = {
        "riderId": current_user["_id"],
        "offerId": offer_oid,
        "pickup": body.pickup.model_dump(),
        "dropoff": body.dropoff.model_dump(),
        "pickupLabel": body.pickupLabel,
        "dropoffLabel": body.dropoffLabel,
        "riderDistanceKm": rider_km,
        "estimatedFuelSplitCost": cost,
        "status": RequestStatus.pending.value,
        "driverResponseAt": None,
        "paymentMethodNote": "unspecified",
        "createdAt": now,
        "updatedAt": now,
    }
    result = await db.ride_requests.insert_one(doc)
    created = await db.ride_requests.find_one({"_id": result.inserted_id})
    return _request_to_response(created)


@router.get("/inbox/driver", response_model=list[RequestResponse])
async def driver_pending_inbox(
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
):
    """All pending requests across the driver's offers."""
    offer_ids = [
        doc["_id"]
        async for doc in db.ride_offers.find(
            {"driverId": current_user["_id"]},
            projection={"_id": 1},
        )
    ]
    if not offer_ids:
        return []
    cursor = db.ride_requests.find(
        {"offerId": {"$in": offer_ids}, "status": RequestStatus.pending.value}
    ).sort("createdAt", -1)
    return [_request_to_response(doc) async for doc in cursor]


@router.get("/mine", response_model=list[RequestResponse])
async def list_my_requests(
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
):
    cursor = db.ride_requests.find({"riderId": current_user["_id"]}).sort(
        "createdAt", -1
    )
    return [_request_to_response(doc) async for doc in cursor]


@router.get("/{request_id}", response_model=RequestResponse)
async def get_request(
    request_id: str,
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
):
    req = await db.ride_requests.find_one(
        {"_id": _parse_object_id(request_id, "Request")}
    )
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    offer = await db.ride_offers.find_one({"_id": req["offerId"]})
    if not offer or not _can_view_request(req, offer, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to view this request")
    return _request_to_response(req)
