"""TaskTemplate domain entity."""

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class TaskTemplate:
    """Vazifa shabloni — takrorlanuvchi vazifa ta'rifi."""

    id: UUID = field(default_factory=uuid4)
    plan_id: UUID = field(default_factory=uuid4)
    title: str = ""
    recurrence_rule: str = "FREQ=DAILY"
    scheduled_time: str = "09:00"
    tolerance_minutes: int = 10
    task_weight: float = 1.0
    is_active: bool = True
