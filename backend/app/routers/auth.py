from datetime import datetime, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies.auth import TokenClaims, get_current_user, user_to_response, verify_firebase_token
from app.dependencies.database import get_db
from app.models.user import UserResponse, UserRole, UserStats

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/sync", response_model=UserResponse)
async def sync_user(
    claims: Annotated[TokenClaims, Depends(verify_firebase_token)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
):
    now = datetime.now(timezone.utc)
    update = {
        "$set": {
            "email": claims.email,
            "displayName": claims.name or claims.email.split("@")[0],
            "photoUrl": claims.picture,
            "updatedAt": now,
            "isActive": True,
        },
        "$setOnInsert": {
            "role": UserRole.both.value,
            "stats": UserStats().model_dump(),
            "createdAt": now,
        },
    }
    await db.users.update_one(
        {"firebaseUid": claims.uid},
        update,
        upsert=True,
    )
    user = await db.users.find_one({"firebaseUid": claims.uid})
    return user_to_response(user)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
):
    return user_to_response(current_user)
