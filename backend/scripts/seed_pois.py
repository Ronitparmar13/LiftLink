#!/usr/bin/env python3
"""Seed campus POIs for fuzzy search. Run from backend/: python scripts/seed_pois.py"""

import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from app.config import get_settings
from app.dependencies.database import close_motor_client, get_database


POIS = [
    ("Parul University Main Entrance", ["Uni Gate", "Main Gate", "PU Gate"], [73.2105, 22.3120], "gate"),
    ("PIET Hostel Block", ["Hostel PIET", "PIET BH", "Boys Hostel"], [73.2120, 22.3140], "hostel"),
    ("Vadodara Bus Station", ["CBS", "Bus Stand", "Central Bus Station"], [73.1950, 22.3070], "bus_stop"),
    ("PIET Academic Block", ["PIET", "Engineering Block"], [73.2130, 22.3150], "academic"),
    ("Parul Sevashram Hospital", ["Hospital", "PU Hospital"], [73.2145, 22.3180], "landmark"),
    ("Parul Institute of Pharmacy", ["Pharmacy Block", "PIP"], [73.2118, 22.3165], "academic"),
    ("Central Library", ["Library", "PU Library"], [73.2128, 22.3138], "academic"),
    ("Food Court", ["Canteen", "PU Food Court"], [73.2112, 22.3132], "landmark"),
    ("Admin Block", ["Administration", "Main Office"], [73.2109, 22.3127], "academic"),
    ("Sports Ground", ["Ground", "Cricket Ground"], [73.2155, 22.3160], "landmark"),
    ("Hostel Gate", ["Hostel Entrance", "Hostel Circle"], [73.2126, 22.3148], "gate"),
    ("Waghodia Road Junction", ["Waghodia Chokdi", "Junction"], [73.2050, 22.3100], "landmark"),
    ("Sayajigunj Circle", ["Sayajigunj", "Railway Side"], [73.2180, 22.3220], "landmark"),
    ("Alkapuri", ["Alkapuri Circle", "Alkapuri Stop"], [73.2200, 22.3250], "landmark"),
    ("PU Bus Stop", ["Campus Bus Stop", "University Bus Stop"], [73.2098, 22.3115], "bus_stop"),
]


async def main() -> int:
    settings = get_settings()
    if not settings.mongodb_uri:
        print("ERROR: MONGODB_URI not set")
        return 1

    now = datetime.now(timezone.utc)
    db = get_database()
    for name, aliases, coordinates, category in POIS:
        await db.campus_pois.update_one(
            {"name": name},
            {
                "$set": {
                    "aliases": aliases,
                    "location": {"type": "Point", "coordinates": coordinates},
                    "category": category,
                    "isActive": True,
                    "updatedAt": now,
                },
                "$setOnInsert": {"createdAt": now},
            },
            upsert=True,
        )
    print(f"Seeded {len(POIS)} campus POIs.")
    await close_motor_client()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
