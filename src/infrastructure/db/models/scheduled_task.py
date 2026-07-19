"""ScheduledTask SQLAlchemy model."""

import uuid
from datetime import date, datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.models.base import Base


class ScheduledTaskModel(Base):
    """Rejalashtirilgan vazifa jadvali."""

    __tablename__ = "scheduled_tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    task_template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("task_templates.id"),
        nullable=False,
        index=True,
    )
    scheduled_date: Mapped[date] = mapped_column(nullable=False, index=True)
    scheduled_datetime: Mapped[datetime] = mapped_column(nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending", index=True
    )
    notification_sent_at: Mapped[datetime | None] = mapped_column(nullable=True)
