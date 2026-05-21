"""Trending pickup hotspot endpoints."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.ml.hotspot_cluster import build_hotspot_snapshot
from app.models.common import serialize_doc
from app.models.hotspot import (
    HotspotSnapshotResponse,
    TrendingHotspotsResponse,
    TrendingZone,
)

router = APIRouter(prefix="/hotspots", tags=["hotspots"])


def _snapshot_to_response(doc: dict[str, Any] | None) -> HotspotSnapshotResponse:
    if not doc:
        return HotspotSnapshotResponse()
    serialized = serialize_doc(doc)
    assert serialized is not None
    return HotspotSnapshotResponse(**serialized)


@router.post("/refresh", response_model=HotspotSnapshotResponse)
async def refresh_hotspots(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    _: Annotated[dict[str, Any], Depends(get_current_user)],
):
    snapshot = await build_hotspot_snapshot(db)
    result = await db.hotspot_snapshots.insert_one(snapshot)
    created = await db.hotspot_snapshots.find_one({"_id": result.inserted_id})
    return _snapshot_to_response(created)


@router.get("/trending", response_model=TrendingHotspotsResponse)
async def get_trending_hotspots(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    _: Annotated[dict[str, Any], Depends(get_current_user)],
):
    snapshot = await db.hotspot_snapshots.find_one(sort=[("generatedAt", -1)])
    if not snapshot:
        return TrendingHotspotsResponse()

    zones = [
        TrendingZone(
            label=cluster["label"],
            centroid=cluster["centroid"]["coordinates"],
            requestCount=cluster["requestCount"],
        )
        for cluster in snapshot.get("clusters", [])
    ]
    return TrendingHotspotsResponse(
        generatedAt=snapshot.get("generatedAt"),
        zones=zones,
        sampleSize=snapshot.get("sampleSize", 0),
    )
