"""Insights API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.models.goal import GoalModel
from src.infrastructure.db.models.scheduled_task import ScheduledTaskModel
from src.infrastructure.db.models.score_event import ScoreEventModel
from src.presentation.api.dependencies import CurrentUser, get_current_user, get_db
from src.presentation.schemas.progress import ProgressResponse

router = APIRouter(prefix="/users", tags=["Progress"])


@router.get("/{user_id}/progress", response_model=ProgressResponse)
async def get_progress(
    user_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> ProgressResponse:
    """Foydalanuvchi progressini olish."""
    if user_id != current_user.user_id:
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

    tasks_result = await session.execute(
        select(ScheduledTaskModel)
        .join(GoalModel, GoalModel.id == ScheduledTaskModel.task_template_id)
        .where(GoalModel.user_id == user_id)
    )
    all_tasks = tasks_result.scalars().all()
    total_tasks = len(all_tasks)
    completed_tasks = sum(1 for t in all_tasks if t.status == "completed")

    score_result = await session.execute(
        select(func.avg(ScoreEventModel.computed_score))
        .join(
            ScheduledTaskModel,
            ScheduledTaskModel.id == ScoreEventModel.scheduled_task_id,
        )
        .join(GoalModel, GoalModel.id == ScheduledTaskModel.task_template_id)
        .where(GoalModel.user_id == user_id)
    )
    avg_score = score_result.scalar() or 0.0

    return ProgressResponse(
        user_id=user_id,
        total_goals=total_goals,
        active_goals=active_goals,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        avg_score=round(float(avg_score), 2),
    )
