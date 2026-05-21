"""Campus POI models (Phase 6 fuzzy search)."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.models.geo import GeoPoint


class PoiCategory(str, Enum):
    gate = "gate"
    hostel = "hostel"
    academic = "academic"
    landmark = "landmark"
    bus_stop = "bus_stop"
    other = "other"


class PoiCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    aliases: list[str] = Field(default_factory=list)
    location: GeoPoint
    category: PoiCategory = PoiCategory.landmark


class PoiResponse(BaseModel):
    id: str
    name: str
    aliases: list[str]
    location: GeoPoint
    category: PoiCategory
    isActive: bool = True


class PoiSearchResult(BaseModel):
    poiId: str
    name: str
    matchedAlias: str
    score: int
    location: GeoPoint
    category: PoiCategory


class PoiSearchResponse(BaseModel):
    results: list[PoiSearchResult]
