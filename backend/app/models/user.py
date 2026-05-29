"""User profile models."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.services.sanitize import sanitize_text


class UserRole(str, Enum):
    rider = "rider"
    driver = "driver"
    both = "both"


class VehicleType(str, Enum):
    two_wheeler = "two_wheeler"
    car = "car"
    other = "other"


class VehicleInfo(BaseModel):
    type: Optional[VehicleType] = None
    description: Optional[str] = None

    @field_validator("description")
    @classmethod
    def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
        return sanitize_text(v) if v is not None else v


class UserStats(BaseModel):
    ridesAsDriver: int = 0
    ridesAsRider: int = 0


class UserUpdate(BaseModel):
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    vehicle: Optional[VehicleInfo] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            sanitized = sanitize_text(v)
            if sanitized and not sanitized.startswith("+91"):
                raise ValueError("phone must start with +91")
            if sanitized and len(sanitized) != 13:
                raise ValueError("phone must be +91 followed by 10 digits")
            return sanitized
        return v


class UserResponse(BaseModel):
    id: str
    firebaseUid: str
    email: EmailStr
    displayName: str
    photoUrl: Optional[str] = None
    phone: Optional[str] = None
    role: UserRole = UserRole.both
    vehicle: Optional[VehicleInfo] = None
    stats: UserStats = Field(default_factory=UserStats)
    isActive: bool = True
    createdAt: datetime
    updatedAt: datetime
