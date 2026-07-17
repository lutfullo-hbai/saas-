"""Goal domain entity."""

from dataclasses import dataclass, field
from datetime import date, datetime
from uuid import UUID, uuid4


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
