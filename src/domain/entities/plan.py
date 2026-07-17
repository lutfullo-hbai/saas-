"""Plan domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Plan:
    """Reja — maqsadga erishish uchun reja."""

    id: UUID = field(default_factory=uuid4)
    goal_id: UUID = field(default_factory=uuid4)
    version: int = 1
    source: str = "manual"  # "manual" yoki "ai"
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
