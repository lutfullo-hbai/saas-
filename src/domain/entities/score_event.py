"""ScoreEvent domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class ScoreEvent:
    """Ball hodisasi — Precision Engine natijasi."""

    id: UUID = field(default_factory=uuid4)
    checkin_id: UUID = field(default_factory=uuid4)
    raw_delta_minutes: float = 0.0
    computed_score: float = 0.0
    formula_version: str = "v1"
    calculation_meta: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
