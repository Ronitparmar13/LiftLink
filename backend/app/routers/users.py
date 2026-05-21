from datetime import datetime, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies.auth import get_current_user, user_to_response
from app.dependencies.database import get_db
from app.models.user import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_profile(
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
):
    return user_to_response(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_profile(
    body: UserUpdate,
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
):
    updates = body.model_dump(exclude_unset=True)
    if not updates:
        return user_to_response(current_user)
    if "vehicle" in updates and updates["vehicle"] is not None:
        updates["vehicle"] = body.vehicle.model_dump(exclude_none=True)
    updates["updatedAt"] = datetime.now(timezone.utc)
    await db.users.update_one({"_id": current_user["_id"]}, {"$set": updates})
    updated = await db.users.find_one({"_id": current_user["_id"]})
    return user_to_response(updated)


@router.get("/{user_id}", response_model=UserResponse)
async def get_public_user(
    user_id: str,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    _: Annotated[dict[str, Any], Depends(get_current_user)],
):
    from bson import ObjectId
    from bson.errors import InvalidId

    try:
        oid = ObjectId(user_id)
    except InvalidId as exc:
        raise HTTPException(status_code=404, detail="User not found") from exc

    user = await db.users.find_one({"_id": oid})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_to_response(user)
