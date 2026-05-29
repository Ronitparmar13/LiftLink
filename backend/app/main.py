"""LiftLink FastAPI application entry point."""

import logging
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.dependencies.database import close_motor_client, get_motor_client
from app.exceptions import register_exception_handlers
from app.routers import api_router

logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","request_id":"%(request_id)s","message":"%(message)s"}',
)
logger = logging.getLogger("liftlink")

settings = get_settings()

limiter = Limiter(key_func=get_remote_address)

APP_VERSION = "1.0.0"


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
    state=limiter,
)

register_exception_handlers(app)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
    request.state.request_id = request_id
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
    logger.info(
        "%s %s %s %sms",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
        extra={"request_id": request_id},
    )
    response.headers["X-Request-ID"] = request_id
    return response

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
        "version": APP_VERSION,
        "mongodb": mongo_status,
        "firebase": firebase_status,
    }
