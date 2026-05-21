"""Geospatial matching unit tests."""

from datetime import datetime, timedelta, timezone

import pytest

from app.models.geo import GeoLineString, GeoPoint
from app.services.geo_match import (
    compute_match_score,
    offer_passes_coarse_filters,
    point_to_linestring_min_distance_m,
    route_matches_points,
)

# Campus corridor: Main Gate → PIET → Alkapuri [lng, lat]
ROUTE = GeoLineString(
    coordinates=[
        [73.2105, 22.3120],
        [73.2120, 22.3140],
        [73.2200, 22.3250],
    ]
)

ON_ROUTE_PICKUP = GeoPoint(coordinates=[73.2110, 22.3130])
ON_ROUTE_DROPOFF = GeoPoint(coordinates=[73.2180, 22.3220])
OFF_ROUTE = GeoPoint(coordinates=[73.1950, 22.3070])  # ~2 km west


def test_point_on_route_within_500m():
    d = point_to_linestring_min_distance_m(ON_ROUTE_PICKUP, ROUTE)
    assert d < 500


def test_point_far_from_route_fails():
    d = point_to_linestring_min_distance_m(OFF_ROUTE, ROUTE)
    assert d > 500


def test_route_matches_both_pickup_and_dropoff():
    ok, pu, do = route_matches_points(
        ROUTE.model_dump(), ON_ROUTE_PICKUP, ON_ROUTE_DROPOFF, radius_meters=500
    )
    assert ok is True
    assert pu < 500
    assert do < 500


def test_only_pickup_near_not_enough():
    ok, _, _ = route_matches_points(
        ROUTE.model_dump(), ON_ROUTE_PICKUP, OFF_ROUTE, radius_meters=500
    )
    assert ok is False


def test_coarse_filter_expired_departure():
    now = datetime.now(timezone.utc)
    offer = {
        "status": "open",
        "availableSeats": 2,
        "departureTime": now - timedelta(hours=2),
    }
    assert offer_passes_coarse_filters(offer, now, now + timedelta(hours=4)) is False


def test_coarse_filter_full_seats():
    now = datetime.now(timezone.utc)
    offer = {
        "status": "open",
        "availableSeats": 0,
        "departureTime": now + timedelta(hours=1),
    }
    assert offer_passes_coarse_filters(offer, now, now + timedelta(hours=4)) is False


def test_match_score_perfect_near_zero_distance():
    score = compute_match_score(10.0, 20.0, 500)
    assert 0.9 < score <= 1.0
