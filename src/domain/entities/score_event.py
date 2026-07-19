"""ScoreEvent domain entity."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
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
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    def __post_init__(self) -> None:
        if not self.formula_version:
            raise InvalidEntityError("Formula_version bo'sh bo'lishi mumkin emas")
