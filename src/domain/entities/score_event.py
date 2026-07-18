"""ScoreEvent domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from src.domain.exceptions import InvalidEntityError


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

    def __post_init__(self) -> None:
        if not (0.0 <= self.computed_score <= 1.0):
            raise InvalidEntityError(
                f"Computed_score 0.0-1.0 orasida bo'lishi kerak, "
                f"hozir: {self.computed_score}"
            )
        if not self.formula_version:
            raise InvalidEntityError("Formula_version bo'sh bo'lishi mumkin emas")
