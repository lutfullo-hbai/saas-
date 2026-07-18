"""JWT authentication service with refresh token support."""

import secrets
from datetime import datetime, timedelta
from uuid import UUID

from jose import JWTError, jwt

from src.config.settings import settings


def create_access_token(user_id: UUID, telegram_id: str) -> str:
    """Access token yaratish — qisqa muddatli."""
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)
    payload = {
        "sub": str(user_id),
        "telegram_id": telegram_id,
        "type": "access",
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: UUID, telegram_id: str) -> str:
    """Refresh token yaratish — uzoq muddatli.

    Refresh token database'da saqlanishi kerak.
    """
    expire = datetime.utcnow() + timedelta(days=settings.jwt_refresh_expiration_days)
    payload = {
        "sub": str(user_id),
        "telegram_id": telegram_id,
        "type": "refresh",
        "jti": secrets.token_hex(16),  # Unique token ID
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_refresh_secret_key, algorithm=settings.jwt_algorithm)


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
        telegram_id = payload.get("telegram_id")
        if user_id is None or telegram_id is None:
            return None
        return {"user_id": UUID(user_id), "telegram_id": telegram_id}
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
        telegram_id = payload.get("telegram_id")
        jti = payload.get("jti")
        if user_id is None or telegram_id is None or jti is None:
            return None
        return {
            "user_id": UUID(user_id),
            "telegram_id": telegram_id,
            "jti": jti,
        }
    except JWTError:
        return None
