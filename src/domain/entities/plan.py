"""Plan domain entity."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.exceptions import InvalidEntityError

VALID_PLAN_SOURCES = {"manual", "ai"}


@dataclass
class Plan:
    """Reja — maqsadga erishish uchun reja."""

    id: UUID = field(default_factory=uuid4)
    goal_id: UUID = field(default_factory=uuid4)
    version: int = 1
    source: str = "manual"  # "manual" yoki "ai"
    is_active: bool = True
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    def __post_init__(self) -> None:
        if self.version < 1:
            raise InvalidEntityError("Plan version 1 dan kichik bo'lishi mumkin emas")
        if self.source not in VALID_PLAN_SOURCES:
            raise InvalidEntityError(
                f"Noto'g'ri source: {self.source}. " f"Mavjud: {VALID_PLAN_SOURCES}"
            )
