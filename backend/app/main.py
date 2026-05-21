"""LiftLink FastAPI application entry point."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.dependencies.database import close_motor_client, get_motor_client
from app.exceptions import register_exception_handlers
from app.routers import api_router

settings = get_settings()


def _init_firebase() -> None:
    """Initialize Firebase Admin if service account file exists."""
    cred_path = settings.firebase_credentials_path
    if not cred_path.is_file():
        return
    import firebase_admin
    from firebase_admin import credentials

    if not firebase_admin._apps:
        firebase_admin.initialize_app(credentials.Certificate(str(cred_path)))


@asynccontextmanager
async def lifespan(app: FastAPI):
    _init_firebase()
    if settings.mongodb_uri:
        get_motor_client()
    yield
    await close_motor_client()


app = FastAPI(
    title="LiftLink API",
    description="AI-Powered Hyper-Local Campus Ride-Pooling — Parul University",
    version="1.0.0",
    lifespan=lifespan,
)

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health_check():
    """Liveness check for load balancers and frontend connectivity test."""
    mongo_status = "not_configured"
    if settings.mongodb_uri:
        try:
            await get_motor_client().admin.command("ping")
            mongo_status = "ok"
        except Exception as exc:
            mongo_status = f"error: {exc}"

    firebase_status = (
        "configured"
        if settings.firebase_credentials_path.is_file()
        else "not_configured"
    )

    return {
        "status": "ok",
        "service": "liftlink-api",
        "mongodb": mongo_status,
        "firebase": firebase_status,
    }
