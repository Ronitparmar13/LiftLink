"""Firebase authentication dependencies."""

from dataclasses import dataclass
from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import get_settings
from app.dependencies.database import get_db
from app.models.common import serialize_doc
from app.models.user import UserResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

security = HTTPBearer(auto_error=False)


@dataclass
class TokenClaims:
    uid: str
    email: str
    name: str | None
    picture: str | None


async def verify_firebase_token(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(security)
    ],
) -> TokenClaims:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    settings = get_settings()
    if not settings.firebase_credentials_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firebase is not configured on the server",
        )

    from firebase_admin import auth

    try:
        decoded: dict[str, Any] = auth.verify_id_token(credentials.credentials)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Firebase token: {exc}",
        ) from exc

    email = (decoded.get("email") or "").lower()
    domain = settings.allowed_email_domain.lower()
    if not email.endswith(f"@{domain}"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Only @{domain} email addresses are allowed",
        )

    return TokenClaims(
        uid=decoded["uid"],
        email=email,
        name=decoded.get("name"),
        picture=decoded.get("picture"),
    )


async def get_current_user(
    claims: Annotated[TokenClaims, Depends(verify_firebase_token)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
) -> dict[str, Any]:
    user = await db.users.find_one({"firebaseUid": claims.uid})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found. Call POST /auth/sync after login.",
        )
    if not user.get("isActive", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )
    return user


def user_to_response(doc: dict[str, Any]) -> UserResponse:
    serialized = serialize_doc(doc)
    assert serialized is not None
    return UserResponse(**serialized)
