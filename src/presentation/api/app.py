"""FastAPI application with graceful shutdown support."""

import asyncio
import time
from contextlib import asynccontextmanager
from datetime import UTC, datetime

import redis.asyncio as aioredis
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text

from src.config.logging import get_logger
from src.config.settings import settings
from src.infrastructure.api.middleware import (
    RateLimitMiddleware,
    RequestIDMiddleware,
    UserRateLimitMiddleware,
)
from src.infrastructure.db.session import async_session_factory, engine
from src.presentation.api.v1.admin import router as admin_router
from src.presentation.api.v1.auth import router as auth_router
from src.presentation.api.v1.checkins import router as checkins_router
from src.presentation.api.v1.goals import router as goals_router
from src.presentation.api.v1.insights import router as insights_router
from src.presentation.api.v1.plans import router as plans_router
from src.presentation.api.v1.task_templates import router as task_templates_router

logger = get_logger(__name__)

# Graceful shutdown state
_active_requests: int = 0
_shutdown_event = asyncio.Event()
GRACEFUL_TIMEOUT_SECONDS = 30


@asynccontextmanager
async def lifespan(app: FastAPI):
    """App lifecycle — startup va graceful shutdown."""
    logger.info("app_started", env=settings.app_env)
    yield
    # Shutdown
    logger.info("graceful_shutdown_started", active_requests=_active_requests)
    _shutdown_event.set()

    # Active request'larni tugallash uchun kutish
    deadline = time.monotonic() + GRACEFUL_TIMEOUT_SECONDS
    while _active_requests > 0 and time.monotonic() < deadline:
        logger.info("waiting_for_active_requests", remaining=_active_requests)
        await asyncio.sleep(0.5)

    if _active_requests > 0:
        logger.warning("shutdown_timeout_forced", remaining=_active_requests)

    # Resurslarni tozalash
    await engine.dispose()
    logger.info("db_engine_disposed")
    logger.info("graceful_shutdown_completed")


app = FastAPI(
    title="Disipl API",
    description="AI-Powered Personal Discipline & Goal Execution System",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.app_env != "testing":
    app.add_middleware(
        RateLimitMiddleware,
        redis_url=settings.redis_url,
        requests_per_minute=60,
    )
    app.add_middleware(
        UserRateLimitMiddleware,
        redis_url=settings.redis_url,
    )
    app.add_middleware(RequestIDMiddleware)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Barcha kutilmagan xatolarni ushlab, structured log yozish."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        "unhandled_exception",
        exc_type=type(exc).__name__,
        exc_msg=str(exc),
        path=request.url.path,
        method=request.method,
        request_id=request_id,
    )
    return Response(
        content='{"detail":"Internal server error"}',
        status_code=500,
        media_type="application/json",
        headers={"X-Request-ID": request_id},
    )


@app.middleware("http")
async def track_active_requests(request: Request, call_next):
    """Request sonini kuzatish va shutdown paytida yangilarini rad etish."""
    global _active_requests
    if _shutdown_event.is_set():
        return Response(
            content='{"detail":"Server is shutting down"}',
            status_code=503,
            media_type="application/json",
        )
    _active_requests += 1
    try:
        response = await call_next(request)
        return response
    finally:
        _active_requests -= 1


Instrumentator().instrument(app).expose(app)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(goals_router, prefix="/api/v1")
app.include_router(plans_router, prefix="/api/v1")
app.include_router(task_templates_router, prefix="/api/v1")
app.include_router(checkins_router, prefix="/api/v1")
app.include_router(insights_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")


async def _check_db() -> dict:
    """PostgreSQL ulanishini tekshirish."""
    start = time.monotonic()
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
        latency_ms = round((time.monotonic() - start) * 1000, 2)
        return {"status": "ok", "latency_ms": latency_ms}
    except Exception as e:
        latency_ms = round((time.monotonic() - start) * 1000, 2)
        return {"status": "error", "error": str(e), "latency_ms": latency_ms}


async def _check_redis() -> dict:
    """Redis ulanishini tekshirish."""
    start = time.monotonic()
    try:
        client = aioredis.from_url(settings.redis_url)
        await client.ping()
        await client.aclose()
        latency_ms = round((time.monotonic() - start) * 1000, 2)
        return {"status": "ok", "latency_ms": latency_ms}
    except Exception as e:
        latency_ms = round((time.monotonic() - start) * 1000, 2)
        return {"status": "error", "error": str(e), "latency_ms": latency_ms}


@app.get("/health")
async def health_check():
    """Liveness probe — server ishlayaptimi."""
    return {
        "status": "ok",
        "service": "disipl",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/health/ready")
async def readiness_check():
    """Readiness probe — barcha bog'liqliklar ishlayaptimi."""
    db_health = await _check_db()
    redis_health = await _check_redis()

    all_healthy = db_health["status"] == "ok" and redis_health["status"] == "ok"

    return {
        "status": "ok" if all_healthy else "degraded",
        "timestamp": datetime.now(UTC).isoformat(),
        "checks": {
            "database": db_health,
            "redis": redis_health,
        },
    }
