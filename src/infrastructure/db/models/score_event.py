"""ScoreEvent SQLAlchemy model."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.models.base import Base
from src.utils.datetime_utils import utc_now


class ScoreEventModel(Base):
    """Ball hodisasi jadvali."""

    __tablename__ = "score_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    checkin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("check_ins.id"),
        nullable=False,
        index=True,
    )
    raw_delta_minutes: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    computed_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    formula_version: Mapped[str] = mapped_column(
        String(50), nullable=False, default="v1"
    )
    calculation_meta: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=utc_now)
