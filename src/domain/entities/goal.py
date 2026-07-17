"""Goal domain entity."""

from dataclasses import dataclass, field
from datetime import date, datetime
from uuid import UUID, uuid4

from src.domain.exceptions import InvalidEntityError

VALID_GOAL_STATUSES = {"active", "completed", "archived", "cancelled"}


@dataclass
class Goal:
    """Maqsad — foydalanuvchining asosiy maqsadi."""

    id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    title: str = ""
    description: str = ""
    target_date: date | None = None
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if not self.title:
            raise InvalidEntityError("Goal title bo'sh bo'lishi mumkin emas")
        if self.status not in VALID_GOAL_STATUSES:
            raise InvalidEntityError(
                f"Noto'g'ri status: {self.status}. "
                f"Mavjud: {VALID_GOAL_STATUSES}"
            )
        if self.target_date and self.target_date < date.today():
            raise InvalidEntityError(
                "Target date o'tmishda bo'lishi mumkin emas"
            )
