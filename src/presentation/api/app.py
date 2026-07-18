"""FastAPI application."""

import time
from datetime import datetime

import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text

from src.config.settings import settings
from src.infrastructure.api.middleware import RateLimitMiddleware
from src.infrastructure.db.session import async_session_factory
from src.presentation.api.v1.admin import router as admin_router
from src.presentation.api.v1.auth import router as auth_router
from src.presentation.api.v1.checkins import router as checkins_router
from src.presentation.api.v1.goals import router as goals_router
from src.presentation.api.v1.insights import router as insights_router
from src.presentation.api.v1.plans import router as plans_router
from src.presentation.api.v1.task_templates import router as task_templates_router

app = FastAPI(
    title="Disipl API",
    description="AI-Powered Personal Discipline & Goal Execution System",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://disipl.uz",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    RateLimitMiddleware,
    redis_url=settings.redis_url,
    requests_per_minute=60,
)

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
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/health/ready")
async def readiness_check():
    """Readiness probe — barcha bog'liqliklar ishlayaptimi."""
    db_health = await _check_db()
    redis_health = await _check_redis()

    all_healthy = db_health["status"] == "ok" and redis_health["status"] == "ok"

    return {
        "status": "ok" if all_healthy else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "database": db_health,
            "redis": redis_health,
        },
    }
