"""Hotspot clustering response models."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.geo import GeoPoint


class HotspotCluster(BaseModel):
    clusterId: int
    centroid: GeoPoint
    label: str
    requestCount: int
    radiusMeters: float


class HotspotSnapshotResponse(BaseModel):
    id: str | None = None
    generatedAt: datetime | None = None
    clusters: list[HotspotCluster] = Field(default_factory=list)
    sampleSize: int = 0
    algorithm: str = "kmeans"
    k: int = 0


class TrendingZone(BaseModel):
    label: str
    centroid: list[float]
    requestCount: int


class TrendingHotspotsResponse(BaseModel):
    generatedAt: datetime | None = None
    zones: list[TrendingZone] = Field(default_factory=list)
    sampleSize: int = 0
