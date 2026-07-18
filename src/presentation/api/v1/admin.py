"""Admin panel API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["admin"])


class PrecisionEngineParams(BaseModel):
    """Precision Engine parametrlari."""
    decay_constant: float = 0.95
    bonus_multiplier: float = 1.5
    streak_bonus: float = 0.1
    max_penalty: float = 0.5


class SystemStats(BaseModel):
    """Tizim statistikasi."""
    total_users: int
    active_users: int
    total_goals: int
    total_tasks: int
    pro_users: int
    revenue_usd: float


@router.get("/stats", response_model=SystemStats)
async def get_system_stats() -> SystemStats:
    """Tizim statistikasini olish."""
    # Placeholder - haqiqiy DB so'rovlari
    return SystemStats(
        total_users=150,
        active_users=120,
        total_goals=450,
        total_tasks=3200,
        pro_users=45,
        revenue_usd=449.55,
    )


@router.get("/precision-engine")
async def get_precision_engine_params() -> PrecisionEngineParams:
    """Precision Engine parametrlarini olish."""
    return PrecisionEngineParams()


@router.put("/precision-engine")
async def update_precision_engine_params(params: PrecisionEngineParams) -> dict:
    """Precision Engine parametrlarini yangilash."""
    # Placeholder - haqiqiy DB update
    return {
        "status": "updated",
        "params": params.dict(),
        "message": "Precision Engine params updated successfully",
    }


@router.get("/users")
async def list_users(page: int = 1, limit: int = 20) -> dict:
    """Foydalanuvchilar ro'yxati."""
    return {
        "users": [],
        "total": 150,
        "page": page,
        "limit": limit,
    }


@router.get("/users/{user_id}")
async def get_user_details(user_id: int) -> dict:
    """Foydalanuvchi tafsilotlari."""
    return {
        "user_id": user_id,
        "username": "example_user",
        "tier": "pro",
        "goals_count": 3,
        "tasks_completed": 45,
        "score": 87.5,
    }


@router.post("/users/{user_id}/ban")
async def ban_user(user_id: int) -> dict:
    """Foydalanuvchini bloklash."""
    return {
        "status": "banned",
        "user_id": user_id,
        "message": "User banned successfully",
    }
