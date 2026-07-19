"""Task Templates API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.add_task_template import AddTaskTemplateUseCase
from src.infrastructure.db.repositories.plan_repository import PostgresPlanRepository
from src.infrastructure.db.repositories.task_template_repository import (
    PostgresTaskTemplateRepository,
)
from src.presentation.api.dependencies import CurrentUser, get_current_user, get_db
from src.presentation.schemas.task_template import (
    TaskTemplateCreate,
    TaskTemplateResponse,
)

router = APIRouter(prefix="/plans/{plan_id}/task-templates", tags=["Task Templates"])


@router.get("", response_model=list[TaskTemplateResponse])
async def list_task_templates(
    plan_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[TaskTemplateResponse]:
    """Rejaga tegishli vazifa shablonlarini olish."""
    plan_repo = PostgresPlanRepository(session)
    plan = await plan_repo.get_by_id(plan_id)
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reja topilmadi",
        )

    goal_repo = __import__(
        "src.infrastructure.db.repositories.goal_repository",
        fromlist=["PostgresGoalRepository"],
    ).PostgresGoalRepository(session)
    goal = await goal_repo.get_by_id(plan.goal_id)
    if goal is None or goal.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ruxsat yo'q",
        )

    template_repo = PostgresTaskTemplateRepository(session)
    templates = await template_repo.get_by_plan_id(plan_id)
    return [TaskTemplateResponse.model_validate(t) for t in templates]


@router.post(
    "", response_model=TaskTemplateResponse, status_code=status.HTTP_201_CREATED
)
async def add_task_template(
    plan_id: UUID,
    request: TaskTemplateCreate,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> TaskTemplateResponse:
    """Rejaga vazifa shabloni qo'shish."""
    plan_repo = PostgresPlanRepository(session)
    plan = await plan_repo.get_by_id(plan_id)
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reja topilmadi",
        )

    goal_repo_inner = __import__(
        "src.infrastructure.db.repositories.goal_repository",
        fromlist=["PostgresGoalRepository"],
    ).PostgresGoalRepository(session)
    goal = await goal_repo_inner.get_by_id(plan.goal_id)
    if goal is None or goal.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ruxsat yo'q",
        )

    template_repo = PostgresTaskTemplateRepository(session)
    use_case = AddTaskTemplateUseCase(template_repo)
    template = await use_case.execute(
        plan_id=plan_id,
        title=request.title,
        recurrence_rule=request.recurrence_rule,
        scheduled_time=request.scheduled_time,
        tolerance_minutes=request.tolerance_minutes,
        task_weight=request.task_weight,
    )
    return TaskTemplateResponse.model_validate(template)
