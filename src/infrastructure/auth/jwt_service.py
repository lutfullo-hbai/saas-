"""JWT authentication service with refresh token support."""

import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from jose import JWTError, jwt

from src.config.settings import settings


def create_access_token(
    user_id: UUID, email: str, telegram_id: int | None = None
) -> str:
    """Access token yaratish — qisqa muddatli (15 daqiqa)."""
    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_expiration_minutes)
    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "access",
        "exp": expire,
        "iat": datetime.now(UTC),
    }
    if telegram_id is not None:
        payload["telegram_id"] = telegram_id
    return jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )


def create_refresh_token(
    user_id: UUID, email: str, telegram_id: int | None = None
) -> str:
    """Refresh token yaratish — uzoq muddatli (30 kun).

    Refresh token database'da sessiya sifatida saqlanadi.
    Har bir token unique JTI (JWT ID) ga ega.
    """
    jti = secrets.token_hex(16)
    expire = datetime.now(UTC) + timedelta(days=settings.jwt_refresh_expiration_days)
    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "refresh",
        "jti": jti,
        "exp": expire,
        "iat": datetime.now(UTC),
    }
    if telegram_id is not None:
        payload["telegram_id"] = telegram_id
    return jwt.encode(
        payload, settings.jwt_refresh_secret_key, algorithm=settings.jwt_algorithm
    )


def decode_access_token(token: str) -> dict | None:
    """Access tokenni decode qilish."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        if payload.get("type") != "access":
            return None
        user_id = payload.get("sub")
        email = payload.get("email")
        if user_id is None or email is None:
            return None
        result = {"user_id": UUID(user_id), "email": email}
        if "telegram_id" in payload:
            result["telegram_id"] = payload["telegram_id"]
        return result
    except JWTError:
        return None


def decode_refresh_token(token: str) -> dict | None:
    """Refresh tokenni decode qilish."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_refresh_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        if payload.get("type") != "refresh":
            return None
        user_id = payload.get("sub")
        email = payload.get("email")
        jti = payload.get("jti")
        if user_id is None or email is None or jti is None:
            return None
        result = {
            "user_id": UUID(user_id),
            "email": email,
            "jti": jti,
        }
        if "telegram_id" in payload:
            result["telegram_id"] = payload["telegram_id"]
        return result
    except JWTError:
        return None
