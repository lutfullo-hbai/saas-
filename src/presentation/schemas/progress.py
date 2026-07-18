"""Progress Pydantic schemas."""

from uuid import UUID

from pydantic import BaseModel


class ProgressResponse(BaseModel):
    """Progress javobi."""

    user_id: UUID
    total_goals: int
    active_goals: int
    total_tasks: int
    completed_tasks: int
    avg_score: float
