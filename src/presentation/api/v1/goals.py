"""Goals API endpoints."""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.create_goal import CreateGoalUseCase
from src.infrastructure.db.repositories.goal_repository import PostgresGoalRepository
from src.presentation.api.dependencies import CurrentUser, get_current_user
from src.presentation.schemas.goal import GoalCreate, GoalResponse

router = APIRouter(prefix="/goals", tags=["Goals"])


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    request: GoalCreate,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(),  # type: ignore
) -> GoalResponse:
    """Yangi maqsad yaratish."""
    goal_repo = PostgresGoalRepository(session)
    use_case = CreateGoalUseCase(goal_repo)
    goal = await use_case.execute(
        user_id=current_user.user_id,
        title=request.title,
        description=request.description,
        target_date=request.target_date,
    )
    return GoalResponse.model_validate(goal)


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(),  # type: ignore
) -> GoalResponse:
    """Maqsadni olish."""
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
    return GoalResponse.model_validate(goal)


@router.get("", response_model=list[GoalResponse])
async def list_goals(
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(),  # type: ignore
) -> list[GoalResponse]:
    """Foydalanuvchining barcha maqsadlarini olish."""
    goal_repo = PostgresGoalRepository(session)
    goals = await goal_repo.get_by_user_id(current_user.user_id)
    return [GoalResponse.model_validate(g) for g in goals]
