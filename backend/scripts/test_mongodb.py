#!/usr/bin/env python3
"""Test MongoDB Atlas connection. Run from backend/ with venv activated."""

import sys
from pathlib import Path

# Allow importing app config when run as script
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from app.config import get_settings


def main() -> int:
    settings = get_settings()
    if not settings.mongodb_uri:
        print("ERROR: MONGODB_URI is empty. Set it in backend/.env")
        return 1

    import certifi
    from pymongo import MongoClient

    client = MongoClient(
        settings.mongodb_uri,
        serverSelectionTimeoutMS=5000,
        tlsCAFile=certifi.where(),
    )
    try:
        client.admin.command("ping")
        print("MongoDB ping: OK")
        db = client["liftlink"]
        print(f"Database: {db.name}")
        return 0
    except Exception as exc:
        print(f"MongoDB ping: FAILED — {exc}")
        return 1
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
