"""Geospatial offer matching for riders."""

from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import get_settings
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.common import serialize_doc
from app.models.match import (
    DriverSummary,
    MatchResult,
    OfferMatchRequest,
    OfferMatchResponse,
)
from app.routers.offers import _offer_to_response
from app.services.cost_calc import distance_km, fuel_split_cost
from app.services.geo_match import (
    compute_match_score,
    offer_passes_coarse_filters,
    route_matches_points,
)

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/offers", tags=["offers"])


@limiter.limit("10/minute")
@router.post("/match", response_model=OfferMatchResponse)
async def match_offers(
    request: Request,
    body: OfferMatchRequest,
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
):
    settings = get_settings()
    now = datetime.now(timezone.utc)
    departure_after = body.departureAfter or now
    departure_before = body.departureBefore or (now + timedelta(hours=4))

    rider_km = distance_km(body.pickup, body.dropoff)

    query = {
        "status": "open",
        "availableSeats": {"$gt": 0},
        "departureTime": {"$gte": departure_after, "$lte": departure_before},
        "driverId": {"$ne": current_user["_id"]},
    }

    candidates = await db.ride_offers.find(query).to_list(length=200)
    results: list[MatchResult] = []

    for offer in candidates:
        if not offer_passes_coarse_filters(offer, departure_after, departure_before):
            continue

        matches, pickup_m, dropoff_m = route_matches_points(
            offer["route"], body.pickup, body.dropoff
        )
        if not matches:
            continue

        driver_doc = await db.users.find_one({"_id": offer["driverId"]})
        if not driver_doc:
            continue

        driver_serialized = serialize_doc(driver_doc)
        assert driver_serialized is not None

        rate = offer.get("fuelSplitRatePerKm", settings.fuel_split_rate_per_km)
        cost = fuel_split_cost(rider_km, rate)
        score = compute_match_score(pickup_m, dropoff_m, settings.geo_match_radius_meters)

        results.append(
            MatchResult(
                offer=_offer_to_response(offer),
                driver=DriverSummary(
                    id=driver_serialized["id"],
                    displayName=driver_serialized["displayName"],
                    photoUrl=driver_serialized.get("photoUrl"),
                    vehicle=driver_serialized.get("vehicle"),
                ),
                riderDistanceKm=rider_km,
                estimatedFuelSplitCost=cost,
                matchScore=score,
                pickupDistanceM=round(pickup_m, 1),
                dropoffDistanceM=round(dropoff_m, 1),
            )
        )

    results.sort(key=lambda m: m.matchScore, reverse=True)

    return OfferMatchResponse(
        matches=results,
        matchRadiusMeters=settings.geo_match_radius_meters,
    )
