"""Plan Pydantic schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PlanCreate(BaseModel):
    """Reja yaratish so'rovi."""

    source: str = Field(default="manual", pattern="^(manual|ai)$")


class PlanResponse(BaseModel):
    """Reja javobi."""

    id: UUID
    goal_id: UUID
    version: int
    source: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
