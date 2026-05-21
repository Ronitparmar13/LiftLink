"""Unit tests for distance and fuel-split calculations."""

import pytest

from app.models.geo import GeoLineString, GeoPoint
from app.services.cost_calc import distance_km, fuel_split_cost, linestring_distance_km

# Campus coordinates from PRD [lng, lat]
MAIN = GeoPoint(coordinates=[73.2105, 22.3120])
PIET = GeoPoint(coordinates=[73.2120, 22.3140])


def test_distance_km_campus_points():
    d = distance_km(MAIN, PIET)
    assert 0 < d < 5


def test_linestring_distance():
    route = GeoLineString(
        coordinates=[
            [73.2105, 22.3120],
            [73.2120, 22.3140],
            [73.2200, 22.3250],
        ]
    )
    d = linestring_distance_km(route)
    assert d > distance_km(MAIN, PIET)


def test_fuel_split_cost():
    assert fuel_split_cost(10.0, 3.5) == 35.0
    assert fuel_split_cost(6.2, 4.0) == 24.8
