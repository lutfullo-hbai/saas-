"""AddTaskTemplateUseCase."""

from uuid import UUID

from src.application.interfaces import ITaskTemplateRepository
from src.domain.entities.task_template import TaskTemplate


class AddTaskTemplateUseCase:
    """Vazifa shabloni qo'shish use case."""

    def __init__(self, template_repo: ITaskTemplateRepository):
        self._template_repo = template_repo

    async def execute(
        self,
        plan_id: UUID,
        title: str,
        recurrence_rule: str = "FREQ=DAILY",
        scheduled_time: str = "09:00",
        tolerance_minutes: int = 10,
        task_weight: float = 1.0,
    ) -> TaskTemplate:
        """Rejaga yangi vazifa shabloni qo'shish."""
        template = TaskTemplate(
            plan_id=plan_id,
            title=title,
            recurrence_rule=recurrence_rule,
            scheduled_time=scheduled_time,
            tolerance_minutes=tolerance_minutes,
            task_weight=task_weight,
        )
        return await self._template_repo.create(template)
