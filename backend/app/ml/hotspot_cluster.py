"""K-Means hotspot clustering for recent rider pickup demand."""

from __future__ import annotations

import math
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any

import numpy as np
from motor.motor_asyncio import AsyncIOMotorDatabase
from sklearn.cluster import KMeans

from app.models.request import RequestStatus
from app.services.geo_match import point_to_linestring_min_distance_m


def _k_for_sample_size(n_samples: int) -> int:
    if n_samples < 3:
        return 0
    return min(5, max(3, n_samples // 10))


def _point_radius_m(points: list[list[float]], centroid: list[float]) -> float:
    if not points:
        return 0.0
    line = {"type": "LineString", "coordinates": [centroid, centroid]}
    distances = [point_to_linestring_min_distance_m(tuple(p), line) for p in points]
    return round(max(distances), 1)


async def _nearest_poi_label(
    db: AsyncIOMotorDatabase, centroid: list[float]
) -> str:
    pois = await db.campus_pois.find({"isActive": True}).to_list(length=200)
    if not pois:
        return "Trending pickup zone"

    best_name = "Trending pickup zone"
    best_distance = float("inf")
    line = {"type": "LineString", "coordinates": [centroid, centroid]}
    for poi in pois:
        distance = point_to_linestring_min_distance_m(
            tuple(poi["location"]["coordinates"]),
            line,
        )
        if distance < best_distance:
            best_distance = distance
            best_name = poi["name"]
    return f"Trending: {best_name}"


async def build_hotspot_snapshot(
    db: AsyncIOMotorDatabase,
    *,
    days: int = 30,
) -> dict[str, Any]:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    cursor = db.ride_requests.find(
        {
            "status": {"$in": [RequestStatus.accepted.value, RequestStatus.completed.value]},
            "createdAt": {"$gte": since},
            "pickup.coordinates": {"$exists": True},
        },
        projection={"pickup": 1},
    )
    points = [
        doc["pickup"]["coordinates"]
        async for doc in cursor
        if doc.get("pickup", {}).get("coordinates")
    ]
    sample_size = len(points)
    k = _k_for_sample_size(sample_size)

    now = datetime.now(timezone.utc)
    if k == 0:
        return {
            "generatedAt": now,
            "clusters": [],
            "sampleSize": sample_size,
            "algorithm": "kmeans",
            "k": 0,
        }

    array = np.array(points, dtype=float)
    model = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = model.fit_predict(array)
    counts = Counter(int(label) for label in labels)

    clusters: list[dict[str, Any]] = []
    for cluster_id, centroid_arr in enumerate(model.cluster_centers_):
        centroid = [round(float(centroid_arr[0]), 6), round(float(centroid_arr[1]), 6)]
        cluster_points = [
            points[i] for i, label in enumerate(labels) if int(label) == cluster_id
        ]
        clusters.append(
            {
                "clusterId": cluster_id,
                "centroid": {"type": "Point", "coordinates": centroid},
                "label": await _nearest_poi_label(db, centroid),
                "requestCount": counts[cluster_id],
                "radiusMeters": _point_radius_m(cluster_points, centroid),
            }
        )

    clusters.sort(key=lambda c: c["requestCount"], reverse=True)
    return {
        "generatedAt": now,
        "clusters": clusters,
        "sampleSize": sample_size,
        "algorithm": "kmeans",
        "k": k,
    }
