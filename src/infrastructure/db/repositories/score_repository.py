"""PostgreSQL implementation of IScoreRepository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces import IScoreRepository
from src.domain.entities.score_event import ScoreEvent
from src.infrastructure.db.models.score_event import ScoreEventModel


class PostgresScoreRepository(IScoreRepository):
    """PostgreSQL ball repository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: ScoreEventModel) -> ScoreEvent:
        return ScoreEvent(
            id=model.id,
            checkin_id=model.checkin_id,
            raw_delta_minutes=model.raw_delta_minutes,
            computed_score=model.computed_score,
            formula_version=model.formula_version,
            calculation_meta=model.calculation_meta or {},
            created_at=model.created_at,
        )

    async def get_by_checkin_id(self, checkin_id: UUID) -> ScoreEvent | None:
        result = await self._session.execute(
            select(ScoreEventModel).where(ScoreEventModel.checkin_id == checkin_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_user_id(self, user_id: UUID) -> list[ScoreEvent]:
        from src.infrastructure.db.models.checkin import CheckInModel
        from src.infrastructure.db.models.scheduled_task import ScheduledTaskModel
        from src.infrastructure.db.models.task_template import TaskTemplateModel
        from src.infrastructure.db.models.plan import PlanModel
        from src.infrastructure.db.models.goal import GoalModel

        result = await self._session.execute(
            select(ScoreEventModel)
            .join(CheckInModel, ScoreEventModel.checkin_id == CheckInModel.id)
            .join(
                ScheduledTaskModel,
                CheckInModel.scheduled_task_id == ScheduledTaskModel.id,
            )
            .join(
                TaskTemplateModel,
                TaskTemplateModel.id == ScheduledTaskModel.task_template_id,
            )
            .join(PlanModel, PlanModel.id == TaskTemplateModel.plan_id)
            .join(GoalModel, GoalModel.id == PlanModel.goal_id)
            .where(GoalModel.user_id == user_id)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def create(self, event: ScoreEvent) -> ScoreEvent:
        model = ScoreEventModel(
            id=event.id,
            checkin_id=event.checkin_id,
            raw_delta_minutes=event.raw_delta_minutes,
            computed_score=event.computed_score,
            formula_version=event.formula_version,
            calculation_meta=event.calculation_meta,
            created_at=event.created_at,
        )
        self._session.add(model)
        await self._session.flush()
        return event
