"""Tests for campus POI fuzzy matching."""

from app.services.fuzzy_search import search_pois


POIS = [
    {
        "_id": "main",
        "name": "Parul University Main Entrance",
        "aliases": ["Uni Gate", "Main Gate", "PU Gate"],
        "location": {"type": "Point", "coordinates": [73.2105, 22.3120]},
        "category": "gate",
        "isActive": True,
    },
    {
        "_id": "hostel",
        "name": "PIET Hostel Block",
        "aliases": ["Hostel PIET", "PIET BH"],
        "location": {"type": "Point", "coordinates": [73.2120, 22.3140]},
        "category": "hostel",
        "isActive": True,
    },
]


def test_uni_gate_matches_main_entrance():
    results = search_pois("uni gate", POIS)
    assert results
    assert results[0].name == "Parul University Main Entrance"
    assert results[0].score >= 70


def test_low_quality_query_returns_empty():
    assert search_pois("zzzzzz", POIS) == []
