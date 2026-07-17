"""TaskTemplate SQLAlchemy model."""

import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.models.base import Base


class TaskTemplateModel(Base):
    """Vazifa shabloni jadvali."""

    __tablename__ = "task_templates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("plans.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    recurrence_rule: Mapped[str] = mapped_column(
        String(100), nullable=False, default="FREQ=DAILY"
    )
    scheduled_time: Mapped[str] = mapped_column(
        String(10), nullable=False, default="09:00"
    )
    tolerance_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    task_weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
