"""007 — email-based auth, sessions, roles

Revision ID: 007
Revises: 006
Create Date: 2026-07-18
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "007_email_auth"
down_revision = "006_precision_engine_config"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users jadvaliga yangi ustunlar
    op.add_column("users", sa.Column("email", sa.String(255), nullable=True))
    op.add_column("users", sa.Column("password_hash", sa.String(255), nullable=True))
    op.add_column("users", sa.Column("role", sa.String(20), nullable=False, server_default="member"))
    op.add_column("users", sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"))
    op.add_column("users", sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("users", sa.Column("updated_at", sa.DateTime(), nullable=True))
    op.add_column("users", sa.Column("last_login_at", sa.DateTime(), nullable=True))
    op.add_column("users", sa.Column("last_login_ip", sa.String(45), nullable=True))

    # telegram_id ni optional qilish
    op.alter_column("users", "telegram_id", nullable=True)

    # Email unique index
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_email_active", "users", ["email", "is_active"])

    # Foydalanuvchilarga default email yaratish (migration uchun)
    op.execute("""
        UPDATE users 
        SET email = telegram_id || '@disipl.local'
        WHERE email IS NULL
    """)

    # Email ni NOT NULL qilish
    op.alter_column("users", "email", nullable=False)

    # User sessions jadvali
    op.create_table(
        "user_sessions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("refresh_token_jti", sa.String(64), unique=True, nullable=False),
        sa.Column("device_info", sa.String(255), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("last_used_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_sessions_user_active", "user_sessions", ["user_id", "is_active"])
    op.create_index("ix_sessions_jti", "user_sessions", ["refresh_token_jti"])


def downgrade() -> None:
    op.drop_table("user_sessions")
    op.drop_index("ix_users_email_active")
    op.drop_index("ix_users_email")
    op.drop_column("users", "last_login_ip")
    op.drop_column("users", "last_login_at")
    op.drop_column("users", "updated_at")
    op.drop_column("users", "is_verified")
    op.drop_column("users", "is_active")
    op.drop_column("users", "role")
    op.drop_column("users", "password_hash")
    op.drop_column("users", "email")
    op.alter_column("users", "telegram_id", nullable=False)
