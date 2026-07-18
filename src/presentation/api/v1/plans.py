"""Plans API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.create_plan import CreatePlanManuallyUseCase
from src.infrastructure.db.repositories.goal_repository import PostgresGoalRepository
from src.infrastructure.db.repositories.plan_repository import PostgresPlanRepository
from src.presentation.api.dependencies import CurrentUser, get_current_user, get_db
from src.presentation.schemas.plan import PlanCreate, PlanResponse

router = APIRouter(prefix="/goals/{goal_id}/plans", tags=["Plans"])


@router.post("", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    goal_id: UUID,
    request: PlanCreate,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> PlanResponse:
    """Maqsad uchun reja yaratish."""
    goal_repo = PostgresGoalRepository(session)
    goal = await goal_repo.get_by_id(goal_id)
    if goal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maqsad topilmadi",
        )
    if goal.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ruxsat yo'q",
        )

    plan_repo = PostgresPlanRepository(session)
    use_case = CreatePlanManuallyUseCase(plan_repo)
    plan = await use_case.execute(goal_id=goal_id, source=request.source)
    return PlanResponse.model_validate(plan)
