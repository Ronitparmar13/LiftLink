"""Ride request models."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.models.geo import GeoPoint


class RequestStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    cancelled = "cancelled"
    completed = "completed"


class PaymentMethodNote(str, Enum):
    cash = "cash"
    upi = "upi"
    unspecified = "unspecified"


class RequestCreate(BaseModel):
    offerId: str
    pickup: GeoPoint
    dropoff: GeoPoint
    pickupLabel: str = Field(..., min_length=1, max_length=200)
    dropoffLabel: str = Field(..., min_length=1, max_length=200)


class RequestResponse(BaseModel):
    id: str
    riderId: str
    offerId: str
    pickup: GeoPoint
    dropoff: GeoPoint
    pickupLabel: str
    dropoffLabel: str
    riderDistanceKm: float
    estimatedFuelSplitCost: float
    status: RequestStatus
    driverResponseAt: Optional[datetime] = None
    paymentMethodNote: PaymentMethodNote = PaymentMethodNote.unspecified
    createdAt: datetime
    updatedAt: datetime


class ContactSummary(BaseModel):
    id: str
    displayName: str
    photoUrl: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class OfferSummary(BaseModel):
    id: str
    startLabel: str
    endLabel: str
    departureTime: datetime
    status: str
    fuelSplitRatePerKm: float


class RequestDetailResponse(BaseModel):
    request: RequestResponse
    offer: OfferSummary
    rider: ContactSummary
    driver: ContactSummary
