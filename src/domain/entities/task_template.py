"""TaskTemplate domain entity."""

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from src.domain.exceptions import InvalidEntityError


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

    def __post_init__(self) -> None:
        if not self.title:
            raise InvalidEntityError("TaskTemplate title bo'sh bo'lishi mumkin emas")
        if self.tolerance_minutes < 0:
            raise InvalidEntityError(
                "Tolerance_minutes manfiy bo'lishi mumkin emas"
            )
        if not (0.0 <= self.task_weight <= 1.0):
            raise InvalidEntityError(
                f"Task_weight 0.0-1.0 orasida bo'lishi kerak, "
                f"hozir: {self.task_weight}"
            )
        if not self.recurrence_rule.startswith("FREQ="):
            raise InvalidEntityError(
                "Recurrence_rule FREQ= bilan boshlanishi kerak"
            )
