"""Precision Engine configuration DB model."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.models.base import Base


class PrecisionEngineConfig(Base):
    """Precision Engine sozlamalari — DB'da saqlanadi.

    Admin panel orqali DECAY_CONST, bonus rate va boshqa
    parametrlarni kod o'zgartirmasdan sozlash imkonini beradi.
    """

    __tablename__ = "precision_engine_config"

    id: Mapped[uuid4] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    decay_const: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.05,
        comment="Eksponensial pasayish doirasi (0.01-1.0)"
    )
    early_bonus_rate: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.01,
        comment="Erta bajarish bonusi stavkasi (0.0-0.1)"
    )
    bonus_cap: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.15,
        comment="Maksimal bonus chegarasi (0.0-0.5)"
    )
    tolerance_default: Mapped[int] = mapped_column(
        Float, nullable=False, default=10.0,
        comment="Standart tolerantlik (daqiqa)"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True,
        comment="Faol konfiguratsiya"
    )
    version: Mapped[int] = mapped_column(
        String(50), nullable=False, default="1",
        comment="Konfiguratsiya versiyasi"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
