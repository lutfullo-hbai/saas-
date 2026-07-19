"""CheckIn Pydantic schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CheckInCreate(BaseModel):
    """Check-in yaratish so'rovi."""

    scheduled_task_id: UUID
    method: str = Field(default="telegram", pattern="^(telegram|web|api)$")
    user_note: str = ""


class CheckInResponse(BaseModel):
    """Check-in javobi."""

    id: UUID
    scheduled_task_id: UUID
    checkin_time: datetime
    method: str
    user_note: str
    created_at: datetime

    model_config = {"from_attributes": True}
