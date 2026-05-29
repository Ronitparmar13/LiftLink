"""Ride offer models."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.geo import GeoLineString, GeoPoint
from app.services.sanitize import sanitize_text


class OfferStatus(str, Enum):
    open = "open"
    full = "full"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class OfferCreate(BaseModel):
    startPoint: GeoPoint
    endPoint: GeoPoint
    route: GeoLineString
    startLabel: str = Field(..., min_length=1, max_length=200)
    endLabel: str = Field(..., min_length=1, max_length=200)
    departureTime: datetime
    availableSeats: int = Field(default=1, ge=1, le=6)
    notes: str = Field(default="", max_length=200)

    @field_validator("startLabel", "endLabel", "notes")
    @classmethod
    def sanitize_html(cls, v: str) -> str:
        return sanitize_text(v)


class OfferUpdate(BaseModel):
    departureTime: Optional[datetime] = None
    availableSeats: Optional[int] = Field(default=None, ge=1, le=6)
    notes: Optional[str] = Field(default=None, max_length=200)

    @field_validator("notes")
    @classmethod
    def sanitize_html(cls, v: Optional[str]) -> Optional[str]:
        return sanitize_text(v) if v is not None else v


class OfferResponse(BaseModel):
    id: str
    driverId: str
    route: GeoLineString
    startLabel: str
    endLabel: str
    startPoint: GeoPoint
    endPoint: GeoPoint
    departureTime: datetime
    availableSeats: int
    status: OfferStatus
    estimatedDistanceKm: float
    fuelSplitRatePerKm: float
    estimatedFuelSplitTotal: float
    notes: str = ""
    createdAt: datetime
    updatedAt: datetime
