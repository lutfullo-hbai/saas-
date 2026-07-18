"""Authentication API endpoints with refresh token support."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.auth.jwt_service import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from src.infrastructure.db.models.user import UserModel
from src.presentation.api.dependencies import CurrentUser, get_current_user, get_db
from src.presentation.schemas.user import UserUpdate

router = APIRouter(prefix="/auth", tags=["Authentication"])


class TelegramAuthRequest(BaseModel):
    """Telegram orqali autentifikatsiya so'rovi."""

    telegram_id: str
    name: str


class TokenResponse(BaseModel):
    """JWT token javobi."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Refresh token so'rovi."""

    refresh_token: str


@router.post("/telegram", response_model=TokenResponse)
async def telegram_auth(
    request: TelegramAuthRequest,
    session: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Telegram orqali ro'yxatdan o'tish va token olish."""
    result = await session.execute(
        select(UserModel).where(UserModel.telegram_id == request.telegram_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        user = UserModel(
            telegram_id=request.telegram_id,
            name=request.name,
        )
        session.add(user)
        await session.flush()

    access_token = create_access_token(user.id, user.telegram_id)
    refresh_token = create_refresh_token(user.id, user.telegram_id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    session: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Refresh token orqali yangi access token olish."""
    payload = decode_refresh_token(request.refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yaroqsiz refresh token",
        )

    # Foydalanuvchi mavjudligini tekshirish
    result = await session.execute(
        select(UserModel).where(UserModel.id == payload["user_id"])
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Foydalanuvchi topilmadi",
        )

    # Yangi tokenlar yaratish (rotate pattern)
    access_token = create_access_token(user.id, user.telegram_id)
    refresh_token = create_refresh_token(user.id, user.telegram_id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.patch("/{user_id}")
async def update_user(
    user_id: UUID,
    request: UserUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Foydalanuvchi ma'lumotlarini yangilash."""
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ruxsat yo'q",
        )

    result = await session.execute(
        select(UserModel).where(UserModel.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi topilmadi",
        )

    if request.name is not None:
        user.name = request.name
    if request.timezone is not None:
        user.timezone = request.timezone
    if request.notification_prefs is not None:
        user.notification_prefs = request.notification_prefs

    await session.commit()

    return {
        "id": str(user.id),
        "telegram_id": user.telegram_id,
        "name": user.name,
        "timezone": user.timezone,
    }
