"""TaskTemplate Pydantic schemas."""

from uuid import UUID

from pydantic import BaseModel, Field


class TaskTemplateCreate(BaseModel):
    """Vazifa shabloni yaratish so'rovi."""

    title: str = Field(..., min_length=1, max_length=500)
    recurrence_rule: str = Field(default="FREQ=DAILY", pattern=r"^FREQ=")
    scheduled_time: str = Field(default="09:00", pattern=r"^\d{2}:\d{2}$")
    tolerance_minutes: int = Field(default=10, ge=0)
    task_weight: float = Field(default=1.0, ge=0.0, le=1.0)


class TaskTemplateResponse(BaseModel):
    """Vazifa shabloni javobi."""

    id: UUID
    plan_id: UUID
    title: str
    recurrence_rule: str
    scheduled_time: str
    tolerance_minutes: int
    task_weight: float
    is_active: bool

    model_config = {"from_attributes": True}
