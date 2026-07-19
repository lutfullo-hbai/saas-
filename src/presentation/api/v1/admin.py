"""Admin panel API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.models.goal import GoalModel
from src.infrastructure.db.models.plan import PlanModel
from src.infrastructure.db.models.precision_engine_config import PrecisionEngineConfig
from src.infrastructure.db.models.task_template import TaskTemplateModel
from src.infrastructure.db.models.scheduled_task import ScheduledTaskModel
from src.infrastructure.db.models.user import UserModel
from src.presentation.api.dependencies import (
    CurrentUser,
    get_current_admin_user,
    get_current_user,
    get_db,
)

router = APIRouter(prefix="/admin", tags=["admin"])


class PrecisionEngineParams(BaseModel):
    """Precision Engine parametrlari."""

    decay_const: float = 0.05
    early_bonus_rate: float = 0.01
    bonus_cap: float = 0.15
    tolerance_default: float = 10.0


class SystemStats(BaseModel):
    """Tizim statistikasi."""

    total_users: int
    active_users: int
    total_goals: int
    total_tasks: int


class UserListItem(BaseModel):
    """Foydalanuvchi ro'yxati elementi."""

    id: str
    email: str
    name: str
    role: str
    goals_count: int
    created_at: str


@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    current_user: CurrentUser = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db),
) -> SystemStats:
    """Tizim statistikasini olish."""
    users_result = await session.execute(select(func.count(UserModel.id)))
    total_users = users_result.scalar() or 0

    goals_result = await session.execute(select(func.count(GoalModel.id)))
    total_goals = goals_result.scalar() or 0

    tasks_result = await session.execute(select(func.count(ScheduledTaskModel.id)))
    total_tasks = tasks_result.scalar() or 0

    active_users_result = await session.execute(
        select(func.count(func.distinct(GoalModel.user_id))).where(
            GoalModel.status == "active"
        )
    )
    active_users = active_users_result.scalar() or 0

    return SystemStats(
        total_users=total_users,
        active_users=active_users,
        total_goals=total_goals,
        total_tasks=total_tasks,
    )


@router.get("/precision-engine")
async def get_precision_engine_params(
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> PrecisionEngineParams:
    """Precision Engine parametrlarini DB'dan olish."""
    result = await session.execute(
        select(PrecisionEngineConfig).where(PrecisionEngineConfig.is_active == True)
    )
    config = result.scalar_one_or_none()

    if not config:
        # Default config yaratish
        config = PrecisionEngineConfig(
            decay_const=0.05,
            early_bonus_rate=0.01,
            bonus_cap=0.15,
            tolerance_default=10.0,
        )
        session.add(config)
        await session.flush()

    return PrecisionEngineParams(
        decay_const=config.decay_const,
        early_bonus_rate=config.early_bonus_rate,
        bonus_cap=config.bonus_cap,
        tolerance_default=config.tolerance_default,
    )


@router.put("/precision-engine")
async def update_precision_engine_params(
    params: PrecisionEngineParams,
    current_user: CurrentUser = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Precision Engine parametrlarini DB'ga saqlash.

    Faqat admin foydalanuvchi yangilashi mumkin.
    Har bir yangilash versiya raqamini oshiradi.
    """
    result = await session.execute(
        select(PrecisionEngineConfig).where(PrecisionEngineConfig.is_active == True)
    )
    config = result.scalar_one_or_none()

    if config:
        # Eski config'ni noaktiv qilish
        config.is_active = False

    # Yangi versiya yaratish
    new_version = "1"
    if config and config.version:
        try:
            new_version = str(int(config.version) + 1)
        except ValueError:
            new_version = "1"

    new_config = PrecisionEngineConfig(
        decay_const=params.decay_const,
        early_bonus_rate=params.early_bonus_rate,
        bonus_cap=params.bonus_cap,
        tolerance_default=params.tolerance_default,
        is_active=True,
        version=new_version,
    )
    session.add(new_config)
    await session.flush()

    return {
        "status": "updated",
        "version": new_version,
        "params": params.model_dump(),
        "message": f"Precision Engine config updated to version {new_version}",
    }


@router.get("/users")
async def list_users(
    page: int = 1,
    limit: int = 20,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Foydalanuvchilar ro'yxati."""
    offset = (page - 1) * limit

    users_result = await session.execute(
        select(UserModel).offset(offset).limit(limit)
    )
    users = users_result.scalars().all()

    total_result = await session.execute(select(func.count(UserModel.id)))
    total = total_result.scalar() or 0

    user_list = []
    for user in users:
        goals_result = await session.execute(
            select(func.count(GoalModel.id)).where(GoalModel.user_id == user.id)
        )
        goals_count = goals_result.scalar() or 0

        user_list.append(
            UserListItem(
                id=str(user.id),
                email=user.email,
                name=user.name,
                role=user.role,
                goals_count=goals_count,
                created_at=user.created_at.isoformat() if user.created_at else "",
            )
        )

    return {
        "users": [u.model_dump() for u in user_list],
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.get("/users/{user_id}")
async def get_user_details(
    user_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Foydalanuvchi tafsilotlari."""
    result = await session.execute(
        select(UserModel).where(UserModel.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi topilmadi",
        )

    goals_result = await session.execute(
        select(GoalModel).where(GoalModel.user_id == user_id)
    )
    goals = goals_result.scalars().all()

    tasks_result = await session.execute(
        select(ScheduledTaskModel)
        .join(TaskTemplateModel, TaskTemplateModel.id == ScheduledTaskModel.task_template_id)
        .join(PlanModel, PlanModel.id == TaskTemplateModel.plan_id)
        .join(GoalModel, GoalModel.id == PlanModel.goal_id)
        .where(GoalModel.user_id == user_id)
    )
    tasks = tasks_result.scalars().all()

    completed_tasks = sum(1 for t in tasks if t.status == "completed")

    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "goals_count": len(goals),
        "tasks_completed": completed_tasks,
        "created_at": user.created_at.isoformat() if user.created_at else "",
    }
