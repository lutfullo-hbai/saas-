"""Dependency injection for API endpoints."""

from collections.abc import AsyncGenerator
from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.auth.auth_service import AuthService
from src.infrastructure.db.session import get_db_session

security = HTTPBearer(auto_error=False)


@dataclass
class CurrentUser:
    """Hozirgi foydalanuvchi ma'lumotlari."""

    user_id: UUID
    email: str
    telegram_id: int | None = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """DB session dependency — endpoint'larda ishlatiladi."""
    async for session in get_db_session():
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> CurrentUser:
    """Hozirgi foydalanuvchini token orqali aniqlash."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autentifikatsiya talab qilinadi",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    payload = AuthService.validate_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Noto'g'ri yoki muddati o'tgan token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return CurrentUser(
        user_id=payload["user_id"],
        email=payload["email"],
        telegram_id=payload.get("telegram_id"),
    )


async def get_current_admin_user(
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> CurrentUser:
    """Hozirgi foydalanuvchi admin ekanligini tekshirish."""
    auth_service = AuthService(session)
    if not await auth_service.is_admin(current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin huquqi talab qilinadi",
        )
    return current_user


def get_client_ip(request: Request) -> str | None:
    """Client IP manzilini olish."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None
