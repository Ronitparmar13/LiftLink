"""Driver inbox: requests for a specific offer."""

from typing import Annotated, Any

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.request import RequestResponse
from app.routers.requests import _request_to_response

router = APIRouter(tags=["requests"])


@router.get("/offers/{offer_id}/requests", response_model=list[RequestResponse])
async def list_offer_requests(
    offer_id: str,
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
):
    try:
        oid = ObjectId(offer_id)
    except InvalidId as exc:
        raise HTTPException(status_code=404, detail="Offer not found") from exc

    offer = await db.ride_offers.find_one({"_id": oid})
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    if offer["driverId"] != current_user["_id"]:
        raise HTTPException(status_code=403, detail="Not your offer")

    cursor = db.ride_requests.find({"offerId": oid}).sort("createdAt", -1)
    return [_request_to_response(doc) async for doc in cursor]
