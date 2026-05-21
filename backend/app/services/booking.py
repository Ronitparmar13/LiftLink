"""Ride request state transitions with atomic seat updates."""

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.offer import OfferStatus
from app.models.request import RequestStatus


async def _get_request_and_offer(
    db: AsyncIOMotorDatabase, request_id: ObjectId
) -> tuple[dict[str, Any], dict[str, Any]]:
    req = await db.ride_requests.find_one({"_id": request_id})
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    offer = await db.ride_offers.find_one({"_id": req["offerId"]})
    if not offer:
        raise HTTPException(status_code=404, detail="Linked offer not found")
    return req, offer


async def accept_request(
    db: AsyncIOMotorDatabase, request_id: ObjectId, driver_user_id: ObjectId
) -> dict[str, Any]:
    req, offer = await _get_request_and_offer(db, request_id)

    if offer["driverId"] != driver_user_id:
        raise HTTPException(status_code=403, detail="Only the offer driver can accept")
    if req["status"] != RequestStatus.pending.value:
        raise HTTPException(status_code=409, detail="Request is not pending")
    if offer.get("status") not in (OfferStatus.open.value, OfferStatus.full.value):
        raise HTTPException(status_code=409, detail="Offer is no longer accepting riders")

    now = datetime.now(timezone.utc)

    # Atomic seat decrement — prevents double-accept race
    updated_offer = await db.ride_offers.find_one_and_update(
        {
            "_id": offer["_id"],
            "status": OfferStatus.open.value,
            "availableSeats": {"$gt": 0},
        },
        {
            "$inc": {"availableSeats": -1},
            "$set": {"updatedAt": now},
        },
        return_document=True,
    )

    if not updated_offer:
        raise HTTPException(
            status_code=409,
            detail="No seats available or offer is not open",
        )

    new_seats = updated_offer["availableSeats"]
    offer_updates: dict[str, Any] = {"updatedAt": now}
    if new_seats <= 0:
        offer_updates["status"] = OfferStatus.full.value
        offer_updates["availableSeats"] = 0

    if offer_updates.get("status"):
        await db.ride_offers.update_one(
            {"_id": offer["_id"]},
            {"$set": offer_updates},
        )

    await db.ride_requests.update_one(
        {"_id": request_id, "status": RequestStatus.pending.value},
        {
            "$set": {
                "status": RequestStatus.accepted.value,
                "driverResponseAt": now,
                "updatedAt": now,
            }
        },
    )

    updated_req = await db.ride_requests.find_one({"_id": request_id})
    if updated_req["status"] != RequestStatus.accepted.value:
        # Roll back seat if request update failed (rare)
        await db.ride_offers.update_one(
            {"_id": offer["_id"]},
            {"$inc": {"availableSeats": 1}, "$set": {"status": OfferStatus.open.value}},
        )
        raise HTTPException(status_code=409, detail="Request could not be accepted")

    return updated_req


async def reject_request(
    db: AsyncIOMotorDatabase, request_id: ObjectId, driver_user_id: ObjectId
) -> dict[str, Any]:
    req, offer = await _get_request_and_offer(db, request_id)

    if offer["driverId"] != driver_user_id:
        raise HTTPException(status_code=403, detail="Only the offer driver can reject")
    if req["status"] != RequestStatus.pending.value:
        raise HTTPException(status_code=409, detail="Request is not pending")

    now = datetime.now(timezone.utc)
    await db.ride_requests.update_one(
        {"_id": request_id},
        {
            "$set": {
                "status": RequestStatus.rejected.value,
                "driverResponseAt": now,
                "updatedAt": now,
            }
        },
    )
    return await db.ride_requests.find_one({"_id": request_id})


async def cancel_request(
    db: AsyncIOMotorDatabase, request_id: ObjectId, rider_user_id: ObjectId
) -> dict[str, Any]:
    req, _offer = await _get_request_and_offer(db, request_id)

    if req["riderId"] != rider_user_id:
        raise HTTPException(status_code=403, detail="Only the rider can cancel")
    if req["status"] != RequestStatus.pending.value:
        raise HTTPException(status_code=409, detail="Only pending requests can be cancelled")

    now = datetime.now(timezone.utc)
    await db.ride_requests.update_one(
        {"_id": request_id},
        {"$set": {"status": RequestStatus.cancelled.value, "updatedAt": now}},
    )
    return await db.ride_requests.find_one({"_id": request_id})


async def complete_request(
    db: AsyncIOMotorDatabase, request_id: ObjectId, user_id: ObjectId
) -> dict[str, Any]:
    req, offer = await _get_request_and_offer(db, request_id)

    if user_id not in (req["riderId"], offer["driverId"]):
        raise HTTPException(status_code=403, detail="Not authorized")
    if req["status"] != RequestStatus.accepted.value:
        raise HTTPException(status_code=409, detail="Only accepted rides can be completed")

    now = datetime.now(timezone.utc)
    await db.ride_requests.update_one(
        {"_id": request_id},
        {"$set": {"status": RequestStatus.completed.value, "updatedAt": now}},
    )

    await db.users.update_one(
        {"_id": req["riderId"]},
        {"$inc": {"stats.ridesAsRider": 1}, "$set": {"updatedAt": now}},
    )
    await db.users.update_one(
        {"_id": offer["driverId"]},
        {"$inc": {"stats.ridesAsDriver": 1}, "$set": {"updatedAt": now}},
    )

    return await db.ride_requests.find_one({"_id": request_id})
