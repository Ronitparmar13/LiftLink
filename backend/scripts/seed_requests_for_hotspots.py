#!/usr/bin/env python3
"""Seed accepted/completed requests so K-Means hotspots can be demoed."""

import asyncio
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from bson import ObjectId

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from app.dependencies.database import close_motor_client, get_database
from app.config import get_settings


CENTERS = [
    ([73.2105, 22.3120], "Parul University Main Entrance"),
    ([73.2120, 22.3140], "PIET Hostel Block"),
    ([73.2180, 22.3220], "Sayajigunj Circle"),
    ([73.2200, 22.3250], "Alkapuri"),
]


def jitter(center: list[float]) -> list[float]:
    return [
        round(center[0] + random.uniform(-0.0008, 0.0008), 6),
        round(center[1] + random.uniform(-0.0008, 0.0008), 6),
    ]


async def main() -> int:
    if not get_settings().mongodb_uri:
        print("ERROR: MONGODB_URI not set")
        return 1

    db = get_database()
    users = await db.users.find({}, projection={"_id": 1}).to_list(length=2)
    offer = await db.ride_offers.find_one({})
    if len(users) < 1 or not offer:
        print("ERROR: Need at least one user and one ride offer before seeding hotspot requests.")
        await close_motor_client()
        return 1

    now = datetime.now(timezone.utc)
    docs = []
    for i in range(32):
        center, label = CENTERS[i % len(CENTERS)]
        pickup = jitter(center)
        dropoff = jitter(CENTERS[(i + 1) % len(CENTERS)][0])
        docs.append(
            {
                "riderId": users[0]["_id"],
                "offerId": offer["_id"],
                "pickup": {"type": "Point", "coordinates": pickup},
                "dropoff": {"type": "Point", "coordinates": dropoff},
                "pickupLabel": label,
                "dropoffLabel": "Demo dropoff",
                "riderDistanceKm": 2.0,
                "estimatedFuelSplitCost": 7.0,
                "status": "completed" if i % 3 else "accepted",
                "driverResponseAt": now - timedelta(days=i % 7),
                "paymentMethodNote": "unspecified",
                "createdAt": now - timedelta(days=i % 12),
                "updatedAt": now - timedelta(days=i % 12),
            }
        )

    await db.ride_requests.delete_many({"pickupLabel": {"$in": [c[1] for c in CENTERS]}})
    result = await db.ride_requests.insert_many(docs)
    print(f"Inserted {len(result.inserted_ids)} demo hotspot requests.")
    await close_motor_client()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
