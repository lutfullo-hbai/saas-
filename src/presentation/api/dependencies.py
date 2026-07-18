"""Dependency injection for API endpoints."""

from collections.abc import AsyncGenerator
from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.auth.jwt_service import decode_access_token
from src.infrastructure.db.models.user import UserModel
from src.infrastructure.db.session import get_db_session

security = HTTPBearer()


@dataclass
class CurrentUser:
    """Hozirgi foydalanuvchi ma'lumotlari."""

    user_id: UUID
    telegram_id: str


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """DB session dependency — endpoint'larda ishlatiladi."""
    async for session in get_db_session():
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    """Hozirgi foydalanuvchini token orqali aniqlash."""
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Noto'g'ri yoki muddati o'tgan token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return CurrentUser(
        user_id=payload["user_id"],
        telegram_id=payload["telegram_id"],
    )


async def get_current_admin_user(
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> CurrentUser:
    """Hozirgi foydalanuvchi admin ekanligini tekshirish."""
    result = await session.execute(
        select(UserModel).where(UserModel.id == current_user.user_id)
    )
    user = result.scalar_one_or_none()
    if not user or not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin huquqi talab qilinadi",
        )
    return current_user
