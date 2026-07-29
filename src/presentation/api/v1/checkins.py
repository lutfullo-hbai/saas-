"""Check-ins API endpoints."""

from datetime import UTC, date, datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.process_checkin import ProcessCheckInUseCase
from src.infrastructure.db.models.scheduled_task import ScheduledTaskModel
from src.infrastructure.db.models.goal import GoalModel
from src.infrastructure.db.models.plan import PlanModel
from src.infrastructure.db.models.task_template import TaskTemplateModel
from src.infrastructure.db.repositories.checkin_repository import (
    PostgresCheckInRepository,
)
from src.infrastructure.db.repositories.scheduled_task_repository import (
    PostgresScheduledTaskRepository,
)
from src.infrastructure.db.repositories.score_repository import PostgresScoreRepository
from src.infrastructure.db.repositories.task_template_repository import (
    PostgresTaskTemplateRepository,
)
from src.presentation.api.dependencies import CurrentUser, get_current_user, get_db
from src.presentation.schemas.checkin import CheckInCreate, CheckInResponse
from src.presentation.schemas.score import ScoreEventResponse
from src.utils.datetime_utils import utc_now

router = APIRouter(prefix="/checkins", tags=["Check-ins"])


@router.get("/today")
async def get_today_checkins(
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[dict]:
    """Bugungi check-in larni olish."""
    result = await session.execute(
        select(ScheduledTaskModel)
        .join(
            TaskTemplateModel,
            TaskTemplateModel.id == ScheduledTaskModel.task_template_id,
        )
        .join(PlanModel, PlanModel.id == TaskTemplateModel.plan_id)
        .join(GoalModel, GoalModel.id == PlanModel.goal_id)
        .where(ScheduledTaskModel.scheduled_date == date.today())
        .where(GoalModel.user_id == current_user.id)
    )
    tasks = result.scalars().all()

    checkins = []
    for task in tasks:
        template_result = await session.execute(
            select(TaskTemplateModel).where(
                TaskTemplateModel.id == task.task_template_id
            )
        )
        template = template_result.scalar_one_or_none()
        checkins.append(
            {
                "id": str(task.id),
                "title": template.title if template else "Noma'lum",
                "status": task.status,
                "time": (
                    task.scheduled_datetime.strftime("%H:%M")
                    if task.scheduled_datetime
                    else "??:??"
                ),
            }
        )

    return checkins


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_checkin(
    request: CheckInCreate,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Check-in yaratish va ball olish."""
    task_repo = PostgresScheduledTaskRepository(session)
    score_repo = PostgresScoreRepository(session)
    checkin_repo = PostgresCheckInRepository(session)
    template_repo = PostgresTaskTemplateRepository(session)
    task = await task_repo.get_by_id(request.scheduled_task_id)
    if task is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Vazifa topilmadi")

    template = await template_repo.get_by_id(task.task_template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Vazifa shabloni topilmadi")

    plan_check = await session.execute(
        select(PlanModel).where(PlanModel.id == template.plan_id)
    )
    plan = plan_check.scalar_one_or_none()
    if plan is None:
        raise HTTPException(status_code=404, detail="Reja topilmadi")

    goal_check = await session.execute(
        select(GoalModel).where(GoalModel.id == plan.goal_id)
    )
    goal = goal_check.scalar_one_or_none()
    if goal is None or goal.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bu vazifa sizga tegishli emas")

    use_case = ProcessCheckInUseCase(task_repo, score_repo, checkin_repo, template_repo)

    checkin, score_event = await use_case.execute(
        scheduled_task_id=request.scheduled_task_id,
        checkin_time=utc_now(),
        method=request.method,
        user_note=request.user_note,
    )

    return {
        "checkin": CheckInResponse.model_validate(checkin).model_dump(),
        "score_event": ScoreEventResponse.model_validate(score_event).model_dump(),
    }
