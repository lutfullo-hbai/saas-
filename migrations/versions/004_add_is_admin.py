"""add is_admin to users

Revision ID: 004_add_is_admin
Revises: 003_add_beta_referral
Create Date: 2026-07-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "004_add_is_admin"
down_revision: Union[str, None] = "003_add_beta_referral"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_admin", sa.Boolean, nullable=False, server_default="false"),
    )


def downgrade() -> None:
    op.drop_column("users", "is_admin")
