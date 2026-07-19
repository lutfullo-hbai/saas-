"""PostgreSQL implementation of IUserRepository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces import IUserRepository
from src.infrastructure.db.models.user import UserModel


class PostgresUserRepository(IUserRepository):
    """PostgreSQL foydalanuvchi repository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, user_id: UUID) -> dict | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user:
            return {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "name": user.name,
                "timezone": user.timezone,
                "notification_prefs": user.notification_prefs,
                "created_at": user.created_at,
            }
        return None

    async def get_by_telegram_id(self, telegram_id: str) -> dict | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if user:
            return {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "name": user.name,
                "timezone": user.timezone,
                "notification_prefs": user.notification_prefs,
                "created_at": user.created_at,
            }
        return None

    async def create(self, user_data: dict) -> dict:
        user = UserModel(**user_data)
        self._session.add(user)
        await self._session.flush()
        return {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "name": user.name,
            "timezone": user.timezone,
            "notification_prefs": user.notification_prefs,
            "created_at": user.created_at,
        }

    async def update(self, user_id: UUID, user_data: dict) -> dict | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user:
            for key, value in user_data.items():
                setattr(user, key, value)
            await self._session.flush()
            return {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "name": user.name,
                "timezone": user.timezone,
                "notification_prefs": user.notification_prefs,
                "created_at": user.created_at,
            }
        return None
