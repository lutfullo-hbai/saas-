"""PostgreSQL implementation of IPlanRepository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces import IPlanRepository
from src.domain.entities.plan import Plan
from src.infrastructure.db.models.plan import PlanModel


class PostgresPlanRepository(IPlanRepository):
    """PostgreSQL reja repository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: PlanModel) -> Plan:
        return Plan(
            id=model.id,
            goal_id=model.goal_id,
            version=model.version,
            source=model.source,
            is_active=model.is_active,
            created_at=model.created_at,
        )

    async def get_by_id(self, plan_id: UUID) -> Plan | None:
        result = await self._session.execute(
            select(PlanModel).where(PlanModel.id == plan_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_goal_id(self, goal_id: UUID) -> list[Plan]:
        result = await self._session.execute(
            select(PlanModel).where(PlanModel.goal_id == goal_id)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_active_plan(self, goal_id: UUID) -> Plan | None:
        result = await self._session.execute(
            select(PlanModel).where(
                PlanModel.goal_id == goal_id, PlanModel.is_active == True
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, plan: Plan) -> Plan:
        model = PlanModel(
            id=plan.id,
            goal_id=plan.goal_id,
            version=plan.version,
            source=plan.source,
            is_active=plan.is_active,
            created_at=plan.created_at,
        )
        self._session.add(model)
        await self._session.flush()
        return plan
