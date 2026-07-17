"""Score Pydantic schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ScoreEventResponse(BaseModel):
    """Ball hodisasi javobi."""

    id: UUID
    checkin_id: UUID
    raw_delta_minutes: float
    computed_score: float
    formula_version: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CheckInWithScoreResponse(BaseModel):
    """Check-in natijasi bilan javob."""

    checkin: CheckInResponse
    score_event: ScoreEventResponse
