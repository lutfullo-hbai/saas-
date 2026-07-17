"""ProcessCheckInUseCase."""

from datetime import datetime
from uuid import UUID

from src.application.interfaces import IScheduledTaskRepository, IScoreRepository
from src.domain.entities.checkin import CheckIn
from src.domain.entities.score_event import ScoreEvent
from src.domain.exceptions import AlreadyCheckedInError
from src.domain.value_objects.score_formula import calculate_score


class ProcessCheckInUseCase:
    """Check-in qayta ishlash use case — Precision Engine bilan."""

    def __init__(
        self,
        task_repo: IScheduledTaskRepository,
        score_repo: IScoreRepository,
    ):
        self._task_repo = task_repo
        self._score_repo = score_repo

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

        score = calculate_score(
            scheduled_time_minutes=0,
            checkin_time_minutes=delta_minutes,
            tolerance_minutes=10,
            task_weight=1.0,
        )

        score_event = ScoreEvent(
            checkin_id=UUID(int=0),
            raw_delta_minutes=delta_minutes,
            computed_score=score,
        )

        await self._task_repo.update_status(scheduled_task_id, "completed")

        return (
            CheckIn(
                scheduled_task_id=scheduled_task_id,
                checkin_time=checkin_time,
                method=method,
                user_note=user_note,
            ),
            score_event,
        )
