"""CheckIn domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class CheckIn:
    """Bajarilish tasdig'i — foydalanuvchi bot orqali "bajardim" deb belgilashi."""

    id: UUID = field(default_factory=uuid4)
    scheduled_task_id: UUID = field(default_factory=uuid4)
    checkin_time: datetime = field(default_factory=datetime.utcnow)
    method: str = "telegram"
    user_note: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
