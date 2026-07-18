"""Goal Pydantic schemas."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class GoalCreate(BaseModel):
    """Maqsad yaratish so'rovi."""

    title: str = Field(..., min_length=1, max_length=500)
    description: str = ""
    target_date: date | None = None


class GoalResponse(BaseModel):
    """Maqsad javobi."""

    id: UUID
    user_id: UUID
    title: str
    description: str
    target_date: date | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class GoalListResponse(BaseModel):
    """Maqsadlar ro'yxati javobi."""

    goals: list[GoalResponse]
    total: int
