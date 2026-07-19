"""CheckIn domain entity."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.domain.exceptions import InvalidEntityError

VALID_CHECKIN_METHODS = {"telegram", "web", "api"}


@dataclass
class CheckIn:
    """Bajarilish tasdig'i — foydalanuvchi bot orqali "bajardim" deb belgilashi."""

    id: UUID = field(default_factory=uuid4)
    scheduled_task_id: UUID = field(default_factory=uuid4)
    checkin_time: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    method: str = "telegram"
    user_note: str = ""
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    def __post_init__(self) -> None:
        if self.method not in VALID_CHECKIN_METHODS:
            raise InvalidEntityError(
                f"Noto'g'ri method: {self.method}. " f"Mavjud: {VALID_CHECKIN_METHODS}"
            )
