"""CreateGoalUseCase."""

from uuid import UUID

from src.application.interfaces import IGoalRepository
from src.domain.entities.goal import Goal


class CreateGoalUseCase:
    """Maqsad yaratish use case."""

    def __init__(self, goal_repo: IGoalRepository):
        self._goal_repo = goal_repo

    async def execute(
        self,
        user_id: UUID,
        title: str,
        description: str = "",
        target_date=None,
    ) -> Goal:
        """Yangi maqsad yaratish."""
        goal = Goal(
            user_id=user_id,
            title=title,
            description=description,
            target_date=target_date,
        )
        return await self._goal_repo.create(goal)
