"""ScheduledTask domain entity."""

from dataclasses import dataclass, field
from datetime import date, datetime
from uuid import UUID, uuid4


@dataclass
class ScheduledTask:
    """Rejalashtirilgan vazifa — TaskTemplate'ning aniq sana/vaqtdagi nusxasi."""

    id: UUID = field(default_factory=uuid4)
    task_template_id: UUID = field(default_factory=uuid4)
    scheduled_date: date = field(default_factory=date.today)
    scheduled_datetime: datetime = field(default_factory=datetime.utcnow)
    status: str = "pending"  # "pending", "completed", "missed"
    notification_sent_at: datetime | None = None
