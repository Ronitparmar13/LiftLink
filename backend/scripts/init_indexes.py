#!/usr/bin/env python3
"""Create MongoDB indexes idempotently. Run from backend/: python scripts/init_indexes.py"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from app.config import get_settings
from app.dependencies.database import get_database, get_motor_client, close_motor_client


INDEX_SPECS = [
    ("users", [("firebaseUid", 1)], {"unique": True, "name": "firebaseUid_unique"}),
    ("users", [("email", 1)], {"unique": True, "name": "email_unique"}),
    ("ride_offers", [("route", "2dsphere")], {"name": "route_2dsphere"}),
    ("ride_offers", [("startPoint", "2dsphere")], {"name": "startPoint_2dsphere"}),
    ("ride_offers", [("endPoint", "2dsphere")], {"name": "endPoint_2dsphere"}),
    (
        "ride_offers",
        [("status", 1), ("departureTime", 1)],
        {"name": "status_departureTime"},
    ),
    ("ride_offers", [("driverId", 1)], {"name": "driverId"}),
    ("ride_requests", [("pickup", "2dsphere")], {"name": "pickup_2dsphere"}),
    ("ride_requests", [("dropoff", "2dsphere")], {"name": "dropoff_2dsphere"}),
    (
        "ride_requests",
        [("riderId", 1), ("status", 1)],
        {"name": "riderId_status"},
    ),
    (
        "ride_requests",
        [("offerId", 1), ("status", 1)],
        {"name": "offerId_status"},
    ),
    ("campus_pois", [("location", "2dsphere")], {"name": "location_2dsphere"}),
    ("campus_pois", [("name", 1)], {"name": "name"}),
    ("hotspot_snapshots", [("generatedAt", -1)], {"name": "generatedAt_desc"}),
]


async def main() -> int:
    settings = get_settings()
    if not settings.mongodb_uri:
        print("ERROR: MONGODB_URI not set in backend/.env")
        return 1

    db = get_database()
    for collection, keys, kwargs in INDEX_SPECS:
        name = kwargs.get("name", str(keys))
        result = await db[collection].create_index(keys, **kwargs)
        print(f"  [{collection}] {name} -> {result}")

    print("\nIndexes on ride_offers:")
    async for idx in db.ride_offers.list_indexes():
        print(f"  - {idx['name']}: {idx.get('key')}")

    await close_motor_client()
    print("\nAll indexes created successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
