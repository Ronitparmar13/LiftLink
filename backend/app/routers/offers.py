from datetime import datetime, timezone
from typing import Annotated, Any, Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import get_settings
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.common import serialize_doc
from app.models.offer import OfferCreate, OfferResponse, OfferStatus, OfferUpdate
from app.services.cost_calc import fuel_split_cost, linestring_distance_km

router = APIRouter(prefix="/offers", tags=["offers"])


def _offer_to_response(doc: dict[str, Any]) -> OfferResponse:
    serialized = serialize_doc(doc)
    assert serialized is not None
    return OfferResponse(**serialized)


def _parse_object_id(value: str) -> ObjectId:
    try:
        return ObjectId(value)
    except InvalidId as exc:
        raise HTTPException(status_code=404, detail="Offer not found") from exc


@router.post("", response_model=OfferResponse, status_code=status.HTTP_201_CREATED)
async def create_offer(
    body: OfferCreate,
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
):
    if body.departureTime < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="departureTime must be in the future")

    settings = get_settings()
    distance = linestring_distance_km(body.route)
    rate = settings.fuel_split_rate_per_km
    now = datetime.now(timezone.utc)

    doc = {
        "driverId": current_user["_id"],
        "route": body.route.model_dump(),
        "startLabel": body.startLabel,
        "endLabel": body.endLabel,
        "startPoint": body.startPoint.model_dump(),
        "endPoint": body.endPoint.model_dump(),
        "departureTime": body.departureTime,
        "availableSeats": body.availableSeats,
        "status": OfferStatus.open.value,
        "estimatedDistanceKm": distance,
        "fuelSplitRatePerKm": rate,
        "estimatedFuelSplitTotal": fuel_split_cost(distance, rate),
        "notes": body.notes,
        "createdAt": now,
        "updatedAt": now,
    }
    result = await db.ride_offers.insert_one(doc)
    created = await db.ride_offers.find_one({"_id": result.inserted_id})
    return _offer_to_response(created)


@router.get("/mine", response_model=list[OfferResponse])
async def list_my_offers(
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
):
    cursor = db.ride_offers.find({"driverId": current_user["_id"]}).sort(
        "departureTime", -1
    )
    return [_offer_to_response(doc) async for doc in cursor]


@router.get("", response_model=list[OfferResponse])
async def list_offers(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    _: Annotated[dict[str, Any], Depends(get_current_user)],
    status_filter: Optional[OfferStatus] = Query(None, alias="status"),
    departure_after: Optional[datetime] = Query(None),
    departure_before: Optional[datetime] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    query: dict[str, Any] = {}
    if status_filter:
        query["status"] = status_filter.value
    if departure_after:
        query.setdefault("departureTime", {})["$gte"] = departure_after
    if departure_before:
        query.setdefault("departureTime", {})["$lte"] = departure_before
    cursor = (
        db.ride_offers.find(query).sort("departureTime", 1).skip(offset).limit(limit)
    )
    return [_offer_to_response(doc) async for doc in cursor]


@router.get("/{offer_id}", response_model=OfferResponse)
async def get_offer(
    offer_id: str,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    _: Annotated[dict[str, Any], Depends(get_current_user)],
):
    offer = await db.ride_offers.find_one({"_id": _parse_object_id(offer_id)})
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    return _offer_to_response(offer)


@router.patch("/{offer_id}", response_model=OfferResponse)
async def update_offer(
    offer_id: str,
    body: OfferUpdate,
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
):
    oid = _parse_object_id(offer_id)
    offer = await db.ride_offers.find_one({"_id": oid})
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    if offer["driverId"] != current_user["_id"]:
        raise HTTPException(status_code=403, detail="Not your offer")
    if offer.get("status") != OfferStatus.open.value:
        raise HTTPException(status_code=409, detail="Only open offers can be updated")

    updates = body.model_dump(exclude_unset=True)
    if not updates:
        return _offer_to_response(offer)
    updates["updatedAt"] = datetime.now(timezone.utc)
    await db.ride_offers.update_one({"_id": oid}, {"$set": updates})
    updated = await db.ride_offers.find_one({"_id": oid})
    return _offer_to_response(updated)


@router.delete("/{offer_id}", response_model=OfferResponse)
async def cancel_offer(
    offer_id: str,
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
):
    oid = _parse_object_id(offer_id)
    offer = await db.ride_offers.find_one({"_id": oid})
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    if offer["driverId"] != current_user["_id"]:
        raise HTTPException(status_code=403, detail="Not your offer")

    await db.ride_offers.update_one(
        {"_id": oid},
        {
            "$set": {
                "status": OfferStatus.cancelled.value,
                "updatedAt": datetime.now(timezone.utc),
            }
        },
    )
    updated = await db.ride_offers.find_one({"_id": oid})
    return _offer_to_response(updated)
