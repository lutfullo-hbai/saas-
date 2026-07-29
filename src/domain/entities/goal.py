"""Goal domain entity."""

from dataclasses import dataclass, field
from src.domain.exceptions import InvalidEntityError
from src.utils.datetime_utils import utc_now

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
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.title:
            raise InvalidEntityError("Goal title bo'sh bo'lishi mumkin emas")
        if self.status not in VALID_GOAL_STATUSES:
            raise InvalidEntityError(
                f"Noto'g'ri status: {self.status}. " f"Mavjud: {VALID_GOAL_STATUSES}"
            )
