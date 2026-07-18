"""Insights API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.models.goal import GoalModel
from src.infrastructure.db.models.scheduled_task import ScheduledTaskModel
from src.presentation.api.dependencies import CurrentUser, get_current_user
from src.presentation.schemas.progress import ProgressResponse

router = APIRouter(prefix="/users", tags=["Progress"])


@router.get("/{user_id}/progress", response_model=ProgressResponse)
async def get_progress(
    user_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(),  # type: ignore
) -> ProgressResponse:
    """Foydalanuvchi progressini olish."""
    if user_id != current_user.user_id:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ruxsat yo'q",
        )

    goals_result = await session.execute(
        select(GoalModel).where(GoalModel.user_id == user_id)
    )
    goals = goals_result.scalars().all()
    total_goals = len(goals)
    active_goals = sum(1 for g in goals if g.status == "active")

    return ProgressResponse(
        user_id=user_id,
        total_goals=total_goals,
        active_goals=active_goals,
        total_tasks=0,
        completed_tasks=0,
        avg_score=0.0,
    )
