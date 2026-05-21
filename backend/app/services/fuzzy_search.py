"""Fuzzy POI search for colloquial campus location names."""

from __future__ import annotations

from difflib import SequenceMatcher
from typing import Any

from app.models.common import serialize_doc
from app.models.poi import PoiSearchResult

try:
    from rapidfuzz import fuzz, process
except ImportError:  # pragma: no cover - dev fallback until deps are installed
    fuzz = None
    process = None


def _normalize(value: str) -> str:
    return " ".join(value.lower().strip().split())


def _fallback_score(query: str, choice: str) -> int:
    return round(SequenceMatcher(None, _normalize(query), _normalize(choice)).ratio() * 100)


def _choice_strings(poi: dict[str, Any]) -> list[str]:
    values = [poi["name"], *poi.get("aliases", [])]
    return [v for v in values if v and v.strip()]


def search_pois(
    query: str,
    pois: list[dict[str, Any]],
    *,
    limit: int = 10,
    min_score: int = 70,
) -> list[PoiSearchResult]:
    cleaned = query.strip()
    if not cleaned:
        return []

    candidates: list[tuple[int, str, dict[str, Any]]] = []
    for poi in pois:
        for choice in _choice_strings(poi):
            if fuzz is not None:
                score = int(fuzz.WRatio(cleaned, choice))
            else:
                score = _fallback_score(cleaned, choice)
            candidates.append((score, choice, poi))

    candidates.sort(key=lambda item: item[0], reverse=True)
    seen: set[str] = set()
    results: list[PoiSearchResult] = []

    for score, matched_alias, poi in candidates:
        serialized = serialize_doc(poi)
        assert serialized is not None
        poi_id = serialized["id"]
        if score < min_score or poi_id in seen:
            continue
        seen.add(poi_id)
        results.append(
            PoiSearchResult(
                poiId=poi_id,
                name=serialized["name"],
                matchedAlias=matched_alias,
                score=score,
                location=serialized["location"],
                category=serialized["category"],
            )
        )
        if len(results) >= limit:
            break

    return results
