"""Goals API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.limits import SubscriptionTier, UserLimits
from src.application.use_cases.create_goal import CreateGoalUseCase
from src.infrastructure.db.models.goal import GoalModel
from src.infrastructure.db.models.subscription import SubscriptionModel
from src.infrastructure.db.repositories.goal_repository import PostgresGoalRepository
from src.presentation.api.dependencies import CurrentUser, get_current_user, get_db
from src.presentation.schemas.goal import GoalCreate, GoalResponse

router = APIRouter(prefix="/goals", tags=["Goals"])


async def _get_user_tier(user_id: UUID, session: AsyncSession) -> SubscriptionTier:
    """Foydalanuvchining obuna darajasini aniqlash."""
    result = await session.execute(
        select(SubscriptionModel).where(
            SubscriptionModel.user_id == user_id,
            SubscriptionModel.is_active == True,
        )
    )
    sub = result.scalar_one_or_none()
    if sub and sub.tier == "pro":
        return SubscriptionTier.PRO
    return SubscriptionTier.FREE


async def _check_goal_limit(
    user_id: UUID, session: AsyncSession
) -> None:
    """Maqsad soni limitini tekshirish."""
    tier = await _get_user_tier(user_id, session)

    # Joriy maqsadlar sonini hisoblash
    result = await session.execute(
        select(func.count(GoalModel.id)).where(
            GoalModel.user_id == user_id,
            GoalModel.status == "active",
        )
    )
    current_goals = result.scalar() or 0

    limits = UserLimits(user_id=hash(str(user_id)) % 1000000, tier=tier)
    if not limits.can_create_goal(current_goals):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=limits.get_upgrade_message(),
        )


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    request: GoalCreate,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> GoalResponse:
    """Yangi maqsad yaratish — limitlar tekshiriladi."""
    await _check_goal_limit(current_user.user_id, session)

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
    session: AsyncSession = Depends(get_db),
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
    session: AsyncSession = Depends(get_db),
) -> list[GoalResponse]:
    """Foydalanuvchining barcha maqsadlarini olish."""
    goal_repo = PostgresGoalRepository(session)
    goals = await goal_repo.get_by_user_id(current_user.user_id)
    return [GoalResponse.model_validate(g) for g in goals]


@router.get("/limits/info")
async def get_limits_info(
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Foydalanuvchi limitlari haqida ma'lumot."""
    tier = await _get_user_tier(current_user.user_id, session)

    # Joriy foydalanish
    goals_result = await session.execute(
        select(func.count(GoalModel.id)).where(
            GoalModel.user_id == current_user.user_id,
            GoalModel.status == "active",
        )
    )
    current_goals = goals_result.scalar() or 0

    limits = UserLimits(user_id=0, tier=tier)
    return limits.get_usage_stats({"goals": current_goals})
