"""Distance and fuel-split cost calculations."""

import math

from app.config import get_settings
from app.models.geo import GeoLineString, GeoPoint


def _haversine_km(lng1: float, lat1: float, lng2: float, lat2: float) -> float:
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def distance_km(point_a: GeoPoint, point_b: GeoPoint) -> float:
    lng1, lat1 = point_a.coordinates
    lng2, lat2 = point_b.coordinates
    return round(_haversine_km(lng1, lat1, lng2, lat2), 2)


def linestring_distance_km(route: GeoLineString) -> float:
    coords = route.coordinates
    total = 0.0
    for i in range(len(coords) - 1):
        lng1, lat1 = coords[i]
        lng2, lat2 = coords[i + 1]
        total += _haversine_km(lng1, lat1, lng2, lat2)
    return round(total, 2)


def fuel_split_cost(distance_km: float, rate_per_km: float | None = None) -> float:
    settings = get_settings()
    rate = rate_per_km if rate_per_km is not None else settings.fuel_split_rate_per_km
    return round(distance_km * rate, 2)
