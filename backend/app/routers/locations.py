"""Campus POI and fuzzy location search endpoints."""

from datetime import datetime, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.common import serialize_doc
from app.models.poi import PoiCreate, PoiResponse, PoiSearchResponse
from app.services.fuzzy_search import search_pois

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/locations", tags=["locations"])


def _poi_to_response(doc: dict[str, Any]) -> PoiResponse:
    serialized = serialize_doc(doc)
    assert serialized is not None
    return PoiResponse(**serialized)


@router.get("/pois", response_model=list[PoiResponse])
async def list_pois(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    _: Annotated[dict[str, Any], Depends(get_current_user)],
):
    cursor = db.campus_pois.find({"isActive": True}).sort("name", 1)
    return [_poi_to_response(doc) async for doc in cursor]


@router.post("/pois", response_model=PoiResponse, status_code=status.HTTP_201_CREATED)
async def create_poi(
    body: PoiCreate,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    _: Annotated[dict[str, Any], Depends(get_current_user)],
):
    now = datetime.now(timezone.utc)
    doc = {
        **body.model_dump(),
        "isActive": True,
        "createdAt": now,
        "updatedAt": now,
    }
    result = await db.campus_pois.insert_one(doc)
    created = await db.campus_pois.find_one({"_id": result.inserted_id})
    return _poi_to_response(created)


@limiter.limit("30/minute")
@router.get("/search", response_model=PoiSearchResponse)
async def search_locations(
    request: Request,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
    _: Annotated[dict[str, Any], Depends(get_current_user)],
    q: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(default=10, ge=1, le=20),
):
    pois = await db.campus_pois.find({"isActive": True}).to_list(length=500)
    return PoiSearchResponse(results=search_pois(q, pois, limit=limit))
