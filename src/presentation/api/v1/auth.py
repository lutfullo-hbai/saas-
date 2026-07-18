"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.auth.jwt_service import create_access_token
from src.infrastructure.db.models.user import UserModel
from src.presentation.api.dependencies import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])


class TelegramAuthRequest(BaseModel):
    """Telegram orqali autentifikatsiya so'rovi."""

    telegram_id: str
    name: str


class TokenResponse(BaseModel):
    """JWT token javobi."""

    access_token: str
    token_type: str = "bearer"


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

    token = create_access_token(user.id, user.telegram_id)
    return TokenResponse(access_token=token)
