"""PATCH actions for ride request lifecycle."""

from typing import Annotated, Any

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.common import serialize_doc
from app.models.request import (
    ContactSummary,
    OfferSummary,
    RequestDetailResponse,
    RequestResponse,
    RequestStatus,
)
from app.routers.requests import _request_to_response
from app.services.booking import (
    accept_request,
    cancel_request,
    complete_request,
    reject_request,
)

router = APIRouter(prefix="/requests", tags=["requests"])


def _parse_oid(value: str) -> ObjectId:
    try:
        return ObjectId(value)
    except InvalidId as exc:
        raise HTTPException(status_code=404, detail="Request not found") from exc


@router.get("/{request_id}/detail", response_model=RequestDetailResponse)
async def get_request_detail(
    request_id: str,
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
):
    oid = _parse_oid(request_id)
    req = await db.ride_requests.find_one({"_id": oid})
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    offer = await db.ride_offers.find_one({"_id": req["offerId"]})
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    is_rider = req["riderId"] == current_user["_id"]
    is_driver = offer["driverId"] == current_user["_id"]
    if not is_rider and not is_driver:
        raise HTTPException(status_code=403, detail="Not authorized")

    rider_doc = await db.users.find_one({"_id": req["riderId"]})
    driver_doc = await db.users.find_one({"_id": offer["driverId"]})
    if not rider_doc or not driver_doc:
        raise HTTPException(status_code=404, detail="User not found")

    show_contact = req["status"] == RequestStatus.accepted.value

    def _contact(doc: dict[str, Any], show: bool) -> ContactSummary:
        s = serialize_doc(doc)
        assert s is not None
        return ContactSummary(
            id=s["id"],
            displayName=s["displayName"],
            photoUrl=s.get("photoUrl"),
            phone=s.get("phone") if show else None,
            email=s.get("email") if show else None,
        )

    return RequestDetailResponse(
        request=_request_to_response(req),
        offer=OfferSummary(
            id=str(offer["_id"]),
            startLabel=offer["startLabel"],
            endLabel=offer["endLabel"],
            departureTime=offer["departureTime"],
            status=offer.get("status", "open"),
            fuelSplitRatePerKm=offer.get("fuelSplitRatePerKm", 3.5),
        ),
        rider=_contact(rider_doc, show_contact),
        driver=_contact(driver_doc, show_contact),
    )


@router.patch("/{request_id}/accept", response_model=RequestResponse)
async def accept_ride_request(
    request_id: str,
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
):
    updated = await accept_request(db, _parse_oid(request_id), current_user["_id"])
    return _request_to_response(updated)


@router.patch("/{request_id}/reject", response_model=RequestResponse)
async def reject_ride_request(
    request_id: str,
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
):
    updated = await reject_request(db, _parse_oid(request_id), current_user["_id"])
    return _request_to_response(updated)


@router.patch("/{request_id}/cancel", response_model=RequestResponse)
async def cancel_ride_request(
    request_id: str,
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
):
    updated = await cancel_request(db, _parse_oid(request_id), current_user["_id"])
    return _request_to_response(updated)


@router.patch("/{request_id}/complete", response_model=RequestResponse)
async def complete_ride_request(
    request_id: str,
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
):
    updated = await complete_request(db, _parse_oid(request_id), current_user["_id"])
    return _request_to_response(updated)
