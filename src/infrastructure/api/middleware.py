"""Rate limiting and request tracking middleware using Redis."""

import uuid
from collections.abc import Callable

import redis.asyncio as redis
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Har bir request'ga unique ID qo'shish."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        from src.config.logging import request_id_var

        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        request_id_var.set(request_id)

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Redis-based rate limiting middleware."""

    def __init__(
        self,
        app,
        redis_url: str = "redis://localhost:6379/0",
        requests_per_minute: int = 60,
        burst_size: int = 10,
    ):
        super().__init__(app)
        self.redis_url = redis_url
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.redis: redis.Redis | None = None

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Request rate limitni tekshirish."""
        if self.redis is None:
            self.redis = redis.from_url(self.redis_url)

        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path

        # Health check, docs va static uchun rate limit yo'q
        if path in [
            "/health",
            "/health/ready",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/metrics",
        ]:
            return await call_next(request)

        # Auth endpoint'lari uchun qattiqroq rate limit (30 urinish / 15 daqiqa)
        is_auth_endpoint = "/auth/" in path and any(
            p in path for p in ["/login", "/register", "/refresh"]
        )
        if is_auth_endpoint:
            auth_key = f"auth_rate:{client_ip}"
            try:
                auth_count = await self.redis.incr(auth_key)
                if auth_count == 1:
                    await self.redis.expire(auth_key, 900)  # 15 daqiqa
                if auth_count > 30:
                    return JSONResponse(
                        status_code=429,
                        content={
                            "detail": "Auth endpoint'larga juda ko'p so'rov. 15 daqiqadan keyin qayta urinib ko'ring.",
                            "retry_after": 900,
                        },
                        headers={"Retry-After": "900"},
                    )
            except Exception:
                pass

        # Rate limit key
        key = f"rate_limit:{client_ip}:{path}"

        try:
            current = await self.redis.incr(key)
            if current == 1:
                await self.redis.expire(key, 60)

            if current > self.requests_per_minute:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Too many requests",
                        "retry_after": 60,
                    },
                    headers={"Retry-After": "60"},
                )

            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
            response.headers["X-RateLimit-Remaining"] = str(
                max(0, self.requests_per_minute - current)
            )
            return response

        except Exception:
            # Redis xato bo'lsa, rate limitni o'tkazib yuborish
            return await call_next(request)


class UserRateLimitMiddleware(BaseHTTPMiddleware):
    """Foydalanuvchi darajasida rate limiting."""

    def __init__(
        self,
        app,
        redis_url: str = "redis://localhost:6379/0",
        free_limit: int = 100,
        pro_limit: int = 1000,
    ):
        super().__init__(app)
        self.redis_url = redis_url
        self.free_limit = free_limit
        self.pro_limit = pro_limit
        self.redis: redis.Redis | None = None

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Foydalanuvchi rate limitini tekshirish."""
        if self.redis is None:
            self.redis = redis.from_url(self.redis_url)

        # User ID olish (auth dan)
        user_id = getattr(request.state, "user_id", None)
        if not user_id:
            return await call_next(request)

        # User tier olish (free/pro)
        tier = getattr(request.state, "tier", "free")
        limit = self.pro_limit if tier == "pro" else self.free_limit

        key = f"user_rate:{user_id}"

        try:
            current = await self.redis.incr(key)
            if current == 1:
                await self.redis.expire(key, 86400)  # Kunlik limit

            if current > limit:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Daily limit exceeded",
                        "limit": limit,
                        "current": current,
                        "tier": tier,
                    },
                )

            response = await call_next(request)
            response.headers["X-DailyLimit-Limit"] = str(limit)
            response.headers["X-DailyLimit-Remaining"] = str(max(0, limit - current))
            return response

        except Exception:
            return await call_next(request)
