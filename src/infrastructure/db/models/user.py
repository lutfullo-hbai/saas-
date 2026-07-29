"""User SQLAlchemy model."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.db.models.base import Base
from src.utils.datetime_utils import utc_now


class UserModel(Base):
    """Foydalanuvchi jadvali — email-based auth."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, default="member"
    )  # admin, member, viewer
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    timezone: Mapped[str] = mapped_column(String(50), nullable=False, default="UTC")
    notification_prefs: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=utc_now)
    updated_at: Mapped[datetime | None] = mapped_column(nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(nullable=True)
    last_login_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)

    # Telegram integration (optional)
    telegram_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True, index=True
    )

    # Relationships
    sessions = relationship(
        "UserSessionModel", back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_users_email_active", "email", "is_active"),)


class UserSessionModel(Base):
    """Foydalanuvchi sessiyasi — refresh token tracking."""

    __tablename__ = "user_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    refresh_token_jti: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True
    )
    device_info: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=utc_now)
    last_used_at: Mapped[datetime] = mapped_column(nullable=False, default=utc_now)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)

    # Relationship
    user = relationship("UserModel", back_populates="sessions")

    __table_args__ = (
        Index("ix_sessions_user_active", "user_id", "is_active"),
        Index("ix_sessions_jti", "refresh_token_jti"),
    )
