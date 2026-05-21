"""User profile models."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


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


class UserStats(BaseModel):
    ridesAsDriver: int = 0
    ridesAsRider: int = 0


class UserUpdate(BaseModel):
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    vehicle: Optional[VehicleInfo] = None


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
