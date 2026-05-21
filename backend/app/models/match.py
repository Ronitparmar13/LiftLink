"""Offer matching request/response models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.geo import GeoPoint
from app.models.offer import OfferResponse
from app.models.user import UserResponse


class OfferMatchRequest(BaseModel):
    pickup: GeoPoint
    dropoff: GeoPoint
    pickupLabel: str = Field(default="", max_length=200)
    dropoffLabel: str = Field(default="", max_length=200)
    departureAfter: Optional[datetime] = None
    departureBefore: Optional[datetime] = None


class DriverSummary(BaseModel):
    id: str
    displayName: str
    photoUrl: Optional[str] = None
    vehicle: Optional[dict] = None


class MatchResult(BaseModel):
    offer: OfferResponse
    driver: DriverSummary
    riderDistanceKm: float
    estimatedFuelSplitCost: float
    matchScore: float
    pickupDistanceM: float
    dropoffDistanceM: float


class OfferMatchResponse(BaseModel):
    matches: list[MatchResult]
    matchRadiusMeters: int
