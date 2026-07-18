"""PostgreSQL implementation of ICheckInRepository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces import ICheckInRepository
from src.domain.entities.checkin import CheckIn
from src.infrastructure.db.models.checkin import CheckInModel


class PostgresCheckInRepository(ICheckInRepository):
    """PostgreSQL check-in repository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: CheckInModel) -> CheckIn:
        return CheckIn(
            id=model.id,
            scheduled_task_id=model.scheduled_task_id,
            checkin_time=model.checkin_time,
            method=model.method,
            user_note=model.user_note or "",
            created_at=model.created_at,
        )

    async def get_by_scheduled_task_id(self, scheduled_task_id: UUID) -> CheckIn | None:
        result = await self._session.execute(
            select(CheckInModel).where(
                CheckInModel.scheduled_task_id == scheduled_task_id
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, checkin: CheckIn) -> CheckIn:
        model = CheckInModel(
            id=checkin.id,
            scheduled_task_id=checkin.scheduled_task_id,
            checkin_time=checkin.checkin_time,
            method=checkin.method,
            user_note=checkin.user_note,
        )
        self._session.add(model)
        await self._session.flush()
        return checkin
