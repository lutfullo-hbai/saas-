"""CreatePlanManuallyUseCase."""

from uuid import UUID

from src.application.interfaces import IPlanRepository
from src.domain.entities.plan import Plan


class CreatePlanManuallyUseCase:
    """Reja yaratish use case (foydalanuvchi tomonidan)."""

    def __init__(self, plan_repo: IPlanRepository):
        self._plan_repo = plan_repo

    async def execute(self, goal_id: UUID, source: str = "manual") -> Plan:
        """Maqsad uchun yangi reja yaratish."""
        plan = Plan(goal_id=goal_id, source=source)
        return await self._plan_repo.create(plan)
