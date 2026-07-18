"""ProcessCheckInUseCase."""

from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces import IScheduledTaskRepository, IScoreRepository
from src.domain.entities.checkin import CheckIn
from src.domain.entities.score_event import ScoreEvent
from src.domain.exceptions import AlreadyCheckedInError
from src.domain.value_objects.score_formula import calculate_score
from src.infrastructure.db.models.checkin import CheckInModel
from src.infrastructure.db.models.score_event import ScoreEventModel


class ProcessCheckInUseCase:
    """Check-in qayta ishlash use case — Precision Engine bilan."""

    def __init__(
        self,
        task_repo: IScheduledTaskRepository,
        score_repo: IScoreRepository,
        session: AsyncSession,
    ):
        self._task_repo = task_repo
        self._score_repo = score_repo
        self._session = session

    async def execute(
        self,
        scheduled_task_id: UUID,
        checkin_time: datetime,
        method: str = "telegram",
        user_note: str = "",
    ) -> tuple[CheckIn, ScoreEvent]:
        """Check-in ni qayta ishlash va ball hisoblash."""
        task = await self._task_repo.get_by_id(scheduled_task_id)
        if task is None:
            raise ValueError("Vazifa topilmadi")
        if task.status != "pending":
            raise AlreadyCheckedInError()

        delta_minutes = (checkin_time - task.scheduled_datetime).total_seconds() / 60

        from src.infrastructure.db.models.task_template import TaskTemplateModel
        from sqlalchemy import select

        result = await self._session.execute(
            select(TaskTemplateModel).where(
                TaskTemplateModel.id == task.task_template_id
            )
        )
        template = result.scalar_one_or_none()
        tolerance_minutes = template.tolerance_minutes if template else 10
        task_weight = template.task_weight if template else 1.0

        score = calculate_score(
            scheduled_time_minutes=0,
            checkin_time_minutes=delta_minutes,
            tolerance_minutes=tolerance_minutes,
            task_weight=task_weight,
        )

        await self._task_repo.update_status(scheduled_task_id, "completed")

        checkin_model = CheckInModel(
            scheduled_task_id=scheduled_task_id,
            checkin_time=checkin_time,
            method=method,
            user_note=user_note,
        )
        self._session.add(checkin_model)
        await self._session.flush()

        score_model = ScoreEventModel(
            checkin_id=checkin_model.id,
            raw_delta_minutes=delta_minutes,
            computed_score=score,
            formula_version="v1",
            calculation_meta={
                "tolerance_minutes": tolerance_minutes,
                "task_weight": task_weight,
            },
        )
        self._session.add(score_model)
        await self._session.flush()

        return (
            CheckIn(
                id=checkin_model.id,
                scheduled_task_id=scheduled_task_id,
                checkin_time=checkin_time,
                method=method,
                user_note=user_note,
            ),
            ScoreEvent(
                id=score_model.id,
                checkin_id=checkin_model.id,
                raw_delta_minutes=delta_minutes,
                computed_score=score,
            ),
        )
