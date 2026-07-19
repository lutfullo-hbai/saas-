"""ProgressSnapshot SQLAlchemy model."""

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Float, ForeignKey, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.models.base import Base


class ProgressSnapshotModel(Base):
    """Progress ko'rinishi jadvali."""

    __tablename__ = "progress_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    period_start: Mapped[date] = mapped_column(nullable=False)
    period_end: Mapped[date] = mapped_column(nullable=False)
    period_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="weekly"
    )
    aggregate_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    breakdown: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
