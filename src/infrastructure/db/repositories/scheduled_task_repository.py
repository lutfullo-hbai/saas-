"""PostgreSQL implementation of IScheduledTaskRepository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces import IScheduledTaskRepository
from src.domain.entities.scheduled_task import ScheduledTask
from src.infrastructure.db.models.scheduled_task import ScheduledTaskModel


class PostgresScheduledTaskRepository(IScheduledTaskRepository):
    """PostgreSQL rejalashtirilgan vazifa repository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: ScheduledTaskModel) -> ScheduledTask:
        return ScheduledTask(
            id=model.id,
            task_template_id=model.task_template_id,
            scheduled_date=model.scheduled_date,
            scheduled_datetime=model.scheduled_datetime,
            status=model.status,
            notification_sent_at=model.notification_sent_at,
        )

    async def get_by_id(self, task_id: UUID) -> ScheduledTask | None:
        result = await self._session.execute(
            select(ScheduledTaskModel).where(ScheduledTaskModel.id == task_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_date(self, scheduled_date) -> list[ScheduledTask]:
        result = await self._session.execute(
            select(ScheduledTaskModel).where(
                ScheduledTaskModel.scheduled_date == scheduled_date
            )
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_pending_by_date(self, scheduled_date) -> list[ScheduledTask]:
        result = await self._session.execute(
            select(ScheduledTaskModel).where(
                ScheduledTaskModel.scheduled_date == scheduled_date,
                ScheduledTaskModel.status == "pending",
            )
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def create(self, task: ScheduledTask) -> ScheduledTask:
        model = ScheduledTaskModel(
            id=task.id,
            task_template_id=task.task_template_id,
            scheduled_date=task.scheduled_date,
            scheduled_datetime=task.scheduled_datetime,
            status=task.status,
            notification_sent_at=task.notification_sent_at,
        )
        self._session.add(model)
        await self._session.flush()
        return task

    async def update_status(self, task_id: UUID, status: str) -> ScheduledTask | None:
        result = await self._session.execute(
            select(ScheduledTaskModel).where(ScheduledTaskModel.id == task_id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.status = status
            await self._session.flush()
            return self._to_entity(model)
        return None
