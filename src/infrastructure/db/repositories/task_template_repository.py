"""PostgreSQL implementation of ITaskTemplateRepository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces import ITaskTemplateRepository
from src.domain.entities.task_template import TaskTemplate
from src.infrastructure.db.models.task_template import TaskTemplateModel


class PostgresTaskTemplateRepository(ITaskTemplateRepository):
    """PostgreSQL vazifa shabloni repository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: TaskTemplateModel) -> TaskTemplate:
        return TaskTemplate(
            id=model.id,
            plan_id=model.plan_id,
            title=model.title,
            recurrence_rule=model.recurrence_rule,
            scheduled_time=model.scheduled_time,
            tolerance_minutes=model.tolerance_minutes,
            task_weight=model.task_weight,
            is_active=model.is_active,
        )

    async def get_by_id(self, template_id: UUID) -> TaskTemplate | None:
        result = await self._session.execute(
            select(TaskTemplateModel).where(TaskTemplateModel.id == template_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_plan_id(self, plan_id: UUID) -> list[TaskTemplate]:
        result = await self._session.execute(
            select(TaskTemplateModel).where(TaskTemplateModel.plan_id == plan_id)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def create(self, template: TaskTemplate) -> TaskTemplate:
        model = TaskTemplateModel(
            id=template.id,
            plan_id=template.plan_id,
            title=template.title,
            recurrence_rule=template.recurrence_rule,
            scheduled_time=template.scheduled_time,
            tolerance_minutes=template.tolerance_minutes,
            task_weight=template.task_weight,
            is_active=template.is_active,
        )
        self._session.add(model)
        await self._session.flush()
        return template

    async def update(self, template_id: UUID, template_data: dict) -> TaskTemplate | None:
        result = await self._session.execute(
            select(TaskTemplateModel).where(TaskTemplateModel.id == template_id)
        )
        model = result.scalar_one_or_none()
        if model:
            for key, value in template_data.items():
                setattr(model, key, value)
            await self._session.flush()
            return self._to_entity(model)
        return None
