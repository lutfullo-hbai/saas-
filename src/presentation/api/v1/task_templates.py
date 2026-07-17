"""Task Templates API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.add_task_template import AddTaskTemplateUseCase
from src.infrastructure.db.repositories.task_template_repository import (
    PostgresTaskTemplateRepository,
)
from src.presentation.api.dependencies import CurrentUser, get_current_user
from src.presentation.schemas.task_template import (
    TaskTemplateCreate,
    TaskTemplateResponse,
)

router = APIRouter(prefix="/plans/{plan_id}/task-templates", tags=["Task Templates"])


@router.post("", response_model=TaskTemplateResponse, status_code=status.HTTP_201_CREATED)
async def add_task_template(
    plan_id: UUID,
    request: TaskTemplateCreate,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(),  # type: ignore
) -> TaskTemplateResponse:
    """Rejaga vazifa shabloni qo'shish."""
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
