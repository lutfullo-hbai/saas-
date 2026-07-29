"""ScheduledTask domain entity."""

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from src.domain.exceptions import InvalidEntityError
from src.utils.datetime_utils import utc_now

VALID_TASK_STATUSES = {"pending", "completed", "missed"}


@dataclass
class ScheduledTask:
    """Rejalashtirilgan vazifa — TaskTemplate'ning aniq sana/vaqtdagi nusxasi."""

    id: UUID = field(default_factory=uuid4)
    task_template_id: UUID = field(default_factory=uuid4)
    scheduled_date: date = field(default_factory=date.today)
    scheduled_datetime: datetime = field(default_factory=utc_now)
    status: str = "pending"  # "pending", "completed", "missed"
    notification_sent_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.status not in VALID_TASK_STATUSES:
            raise InvalidEntityError(
                f"Noto'g'ri status: {self.status}. " f"Mavjud: {VALID_TASK_STATUSES}"
            )
