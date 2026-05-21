"""
Geospatial route matching for LiftLink (Semester 6).

Strategy: MongoDB coarse filter + Python post-filter (recommended for reliability).

Rules:
- Match radius: GEO_MATCH_RADIUS_METERS (default 500 m).
- Rider pickup AND dropoff must both be within radius of the driver's route LineString.
- Only offers with status=open, availableSeats>0, departureTime in window.
- Coordinates are always GeoJSON [longitude, latitude].

We do NOT rely on startPoint/endPoint alone — riders may board mid-route.
"""

from __future__ import annotations

import math
from datetime import datetime
from typing import Any

from app.config import get_settings
from app.models.geo import GeoLineString, GeoPoint


def _lat_lng_to_local_meters(
    lat: float, lng: float, ref_lat: float, ref_lng: float
) -> tuple[float, float]:
    """Approximate local East-North meters (accurate enough for campus scale)."""
    x = (lng - ref_lng) * math.cos(math.radians(ref_lat)) * 111_320.0
    y = (lat - ref_lat) * 110_540.0
    return x, y


def _point_to_segment_distance_m(
    px: float, py: float, x1: float, y1: float, x2: float, y2: float
) -> float:
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    return math.hypot(px - proj_x, py - proj_y)


def point_to_linestring_min_distance_m(
    point: GeoPoint | tuple[float, float],
    linestring: GeoLineString | dict[str, Any],
) -> float:
    """
    Minimum distance in meters from a point to a LineString route.

    Uses local tangent-plane projection (valid for sub-10 km campus distances).
    """
    if isinstance(point, GeoPoint):
        lng, lat = point.coordinates
    else:
        lng, lat = point

    if isinstance(linestring, GeoLineString):
        coords = linestring.coordinates
    else:
        coords = linestring["coordinates"]

    if len(coords) < 2:
        return float("inf")

    ref_lat, ref_lng = lat, lng
    px, py = _lat_lng_to_local_meters(lat, lng, ref_lat, ref_lng)
    min_dist = float("inf")

    for i in range(len(coords) - 1):
        lng1, lat1 = coords[i]
        lng2, lat2 = coords[i + 1]
        x1, y1 = _lat_lng_to_local_meters(lat1, lng1, ref_lat, ref_lng)
        x2, y2 = _lat_lng_to_local_meters(lat2, lng2, ref_lat, ref_lng)
        d = _point_to_segment_distance_m(px, py, x1, y1, x2, y2)
        min_dist = min(min_dist, d)

    return min_dist


def route_matches_points(
    route: dict[str, Any],
    pickup: GeoPoint,
    dropoff: GeoPoint,
    radius_meters: float | None = None,
) -> tuple[bool, float, float]:
    """
    Return (matches, pickup_distance_m, dropoff_distance_m).
    """
    settings = get_settings()
    radius = radius_meters if radius_meters is not None else settings.geo_match_radius_meters

    pickup_m = point_to_linestring_min_distance_m(pickup, route)
    dropoff_m = point_to_linestring_min_distance_m(dropoff, route)
    matches = pickup_m <= radius and dropoff_m <= radius
    return matches, pickup_m, dropoff_m


def compute_match_score(pickup_m: float, dropoff_m: float, radius_meters: float) -> float:
    """Higher is better; 1.0 = perfect overlap with route."""
    avg = (pickup_m + dropoff_m) / 2.0
    score = 1.0 - (avg / radius_meters)
    return round(max(0.0, min(1.0, score)), 3)


def offer_passes_coarse_filters(
    offer: dict[str, Any],
    departure_after: datetime,
    departure_before: datetime,
) -> bool:
    if offer.get("status") != "open":
        return False
    if offer.get("availableSeats", 0) <= 0:
        return False
    dep = offer.get("departureTime")
    if dep is None:
        return False
    return departure_after <= dep <= departure_before
