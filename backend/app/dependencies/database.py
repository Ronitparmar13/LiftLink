"""MongoDB Motor async client and FastAPI dependency."""

from typing import AsyncGenerator

import certifi
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import get_settings

_client: AsyncIOMotorClient | None = None


def get_motor_client() -> AsyncIOMotorClient:
    global _client
    settings = get_settings()
    if not settings.mongodb_uri:
        raise RuntimeError(
            "MONGODB_URI is not set. Copy backend/.env.example to backend/.env"
        )
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongodb_uri, tlsCAFile=certifi.where())
    return _client


def get_database() -> AsyncIOMotorDatabase:
    return get_motor_client()["liftlink"]


async def close_motor_client() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None


async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    yield get_database()
