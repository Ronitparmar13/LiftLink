#!/usr/bin/env python3
"""Seed sample ride offers (requires a user document in `users`)."""

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from app.config import get_settings
from app.dependencies.database import close_motor_client, get_database

# PRD Appendix 7.2 — [lng, lat]
CAMPUS_MAIN = [73.2105, 22.3120]
PIET_HOSTEL = [73.2120, 22.3140]
ALKAPURI = [73.2200, 22.3250]
SAYAJIGUNJ = [73.2180, 22.3220]


async def main() -> int:
    settings = get_settings()
    if not settings.mongodb_uri:
        print("ERROR: MONGODB_URI not set")
        return 1

    db = get_database()
    driver = await db.users.find_one({})
    if not driver:
        print("ERROR: No users in database. Run POST /auth/sync after Firebase login first.")
        await close_motor_client()
        return 1

    now = datetime.now(timezone.utc)
    samples = [
        {
            "driverId": driver["_id"],
            "route": {
                "type": "LineString",
                "coordinates": [CAMPUS_MAIN, PIET_HOSTEL, ALKAPURI],
            },
            "startLabel": "Parul University Main Entrance",
            "endLabel": "Alkapuri, Vadodara",
            "startPoint": {"type": "Point", "coordinates": CAMPUS_MAIN},
            "endPoint": {"type": "Point", "coordinates": ALKAPURI},
            "departureTime": now + timedelta(hours=2),
            "availableSeats": 2,
            "status": "open",
            "estimatedDistanceKm": 8.4,
            "fuelSplitRatePerKm": settings.fuel_split_rate_per_km,
            "estimatedFuelSplitTotal": round(8.4 * settings.fuel_split_rate_per_km, 2),
            "notes": "Leaving sharp — seed data",
            "createdAt": now,
            "updatedAt": now,
        },
        {
            "driverId": driver["_id"],
            "route": {
                "type": "LineString",
                "coordinates": [CAMPUS_MAIN, SAYAJIGUNJ],
            },
            "startLabel": "Uni Gate",
            "endLabel": "Sayajigunj Circle",
            "startPoint": {"type": "Point", "coordinates": CAMPUS_MAIN},
            "endPoint": {"type": "Point", "coordinates": SAYAJIGUNJ},
            "departureTime": now + timedelta(hours=4),
            "availableSeats": 1,
            "status": "open",
            "estimatedDistanceKm": 6.2,
            "fuelSplitRatePerKm": settings.fuel_split_rate_per_km,
            "estimatedFuelSplitTotal": round(6.2 * settings.fuel_split_rate_per_km, 2),
            "notes": "Seed offer 2",
            "createdAt": now,
            "updatedAt": now,
        },
    ]

    await db.ride_offers.delete_many({"notes": {"$regex": "^Seed"}})
    result = await db.ride_offers.insert_many(samples)
    print(f"Inserted {len(result.inserted_ids)} sample offers for driver {driver.get('email')}")

    await close_motor_client()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
