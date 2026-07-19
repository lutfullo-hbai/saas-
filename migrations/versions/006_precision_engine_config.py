"""add precision engine config

Revision ID: 006_precision_engine_config
Revises: 005_add_feedbacks
Create Date: 2026-07-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "006_precision_engine_config"
down_revision: Union[str, None] = "005_add_feedbacks"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "precision_engine_config",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("decay_const", sa.Float, nullable=False, server_default="0.05"),
        sa.Column("early_bonus_rate", sa.Float, nullable=False, server_default="0.01"),
        sa.Column("bonus_cap", sa.Float, nullable=False, server_default="0.15"),
        sa.Column("tolerance_default", sa.Float, nullable=False, server_default="10.0"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("version", sa.String(50), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # Default konfiguratsiya qo'shish
    op.execute(
        """
        INSERT INTO precision_engine_config (id, decay_const, early_bonus_rate, bonus_cap, tolerance_default, is_active, version)
        VALUES ('00000000-0000-0000-0000-000000000001', 0.05, 0.01, 0.15, 10.0, true, '1')
        """
    )


def downgrade() -> None:
    op.drop_table("precision_engine_config")
