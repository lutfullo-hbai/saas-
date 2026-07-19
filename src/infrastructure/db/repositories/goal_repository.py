"""PostgreSQL implementation of IGoalRepository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces import IGoalRepository
from src.domain.entities.goal import Goal
from src.infrastructure.db.models.goal import GoalModel


class PostgresGoalRepository(IGoalRepository):
    """PostgreSQL maqsad repository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, goal_id: UUID) -> Goal | None:
        result = await self._session.execute(
            select(GoalModel).where(GoalModel.id == goal_id)
        )
        model = result.scalar_one_or_none()
        if model:
            return Goal(
                id=model.id,
                user_id=model.user_id,
                title=model.title,
                description=model.description or "",
                target_date=model.target_date,
                status=model.status,
                created_at=model.created_at,
            )
        return None

    async def get_by_user_id(self, user_id: UUID) -> list[Goal]:
        result = await self._session.execute(
            select(GoalModel).where(GoalModel.user_id == user_id)
        )
        models = result.scalars().all()
        return [
            Goal(
                id=m.id,
                user_id=m.user_id,
                title=m.title,
                description=m.description or "",
                target_date=m.target_date,
                status=m.status,
                created_at=m.created_at,
            )
            for m in models
        ]

    async def create(self, goal: Goal) -> Goal:
        model = GoalModel(
            id=goal.id,
            user_id=goal.user_id,
            title=goal.title,
            description=goal.description,
            target_date=goal.target_date,
            status=goal.status,
            created_at=goal.created_at,
        )
        self._session.add(model)
        await self._session.flush()
        return goal

    async def update(self, goal_id: UUID, goal_data: dict) -> Goal | None:
        result = await self._session.execute(
            select(GoalModel).where(GoalModel.id == goal_id)
        )
        model = result.scalar_one_or_none()
        if model:
            for key, value in goal_data.items():
                setattr(model, key, value)
            await self._session.flush()
            return Goal(
                id=model.id,
                user_id=model.user_id,
                title=model.title,
                description=model.description or "",
                target_date=model.target_date,
                status=model.status,
                created_at=model.created_at,
            )
        return None
