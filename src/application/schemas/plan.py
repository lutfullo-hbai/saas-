"""Pydantic schemas for plan generation."""

from pydantic import BaseModel, Field


class PlanRequest(BaseModel):
    """Reja generatsiya qilish uchun so'rov."""

    goal_title: str = Field(..., min_length=3, max_length=200)
    goal_description: str = Field(default="")
    current_level: str = Field(default="boshlang'ich")
    available_hours: float = Field(default=2.0, ge=0.5, le=12.0)
    target_date: str = Field(default="2026-12-31")


class TaskSuggestionSchema(BaseModel):
    """Taklif qilingan vazifa."""

    title: str
    recurrence: str
    time: str
    weight: float = Field(ge=0.0, le=1.0)


class PlanResponse(BaseModel):
    """Generatsiya qilingan reja."""

    tasks: list[TaskSuggestionSchema]
    tokens_used: int
    cost_usd: float
