"""TimeWindow value object."""

from dataclasses import dataclass
from datetime import UTC, datetime, time


@dataclass(frozen=True)
class TimeWindow:
    """Vaqt oralig'i — boshlanish va tugash vaqti.

    Masalan: TimeWindow(start=time(9, 0), end=time(10, 0)) — "9:00 dan 10:00 gacha".
    """

    start: time
    end: time

    def __post_init__(self) -> None:
        if self.start >= self.end:
            raise ValueError(
                f"Start vaqt end vaqtdan keyin bo'lishi mumkin emas: "
                f"{self.start} >= {self.end}"
            )

    def contains(self, dt: datetime) -> bool:
        """Berilgan vaqt shu oraliqda ekanligini tekshiradi."""
        t = dt.time()
        return self.start <= t <= self.end

    def duration_minutes(self) -> float:
        """Oralikning davomiyligini daqiqada qaytaradi."""
        today = datetime.now(UTC).date()
        start_dt = datetime.combine(today, self.start)
        end_dt = datetime.combine(today, self.end)
        return (end_dt - start_dt).total_seconds() / 60
