"""JWT authentication service."""

from datetime import datetime, timedelta
from uuid import UUID

from jose import JWTError, jwt

from src.config.settings import settings


def create_access_token(user_id: UUID, telegram_id: str) -> str:
    """JWT token yaratish."""
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)
    payload = {
        "sub": str(user_id),
        "telegram_id": telegram_id,
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict | None:
    """JWT tokenni decode qilish."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        user_id = payload.get("sub")
        telegram_id = payload.get("telegram_id")
        if user_id is None or telegram_id is None:
            return None
        return {"user_id": UUID(user_id), "telegram_id": telegram_id}
    except JWTError:
        return None
