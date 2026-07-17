"""initial schema

Revision ID: 001_initial
Revises:
Create Date: 2026-07-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("telegram_id", sa.String(255), unique=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("timezone", sa.String(50), nullable=False, server_default="UTC"),
        sa.Column("notification_prefs", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"])

    # Goals
    op.create_table(
        "goals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("target_date", sa.Date, nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_goals_user_id", "goals", ["user_id"])
    op.create_index("ix_goals_status", "goals", ["status"])

    # Plans
    op.create_table(
        "plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("goal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("goals.id"), nullable=False),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("source", sa.String(50), nullable=False, server_default="manual"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_plans_goal_id", "plans", ["goal_id"])

    # Task Templates
    op.create_table(
        "task_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("plans.id"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("recurrence_rule", sa.String(100), nullable=False, server_default="FREQ=DAILY"),
        sa.Column("scheduled_time", sa.String(10), nullable=False, server_default="09:00"),
        sa.Column("tolerance_minutes", sa.Integer, nullable=False, server_default="10"),
        sa.Column("task_weight", sa.Float, nullable=False, server_default="1.0"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
    )
    op.create_index("ix_task_templates_plan_id", "task_templates", ["plan_id"])

    # Scheduled Tasks
    op.create_table(
        "scheduled_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("task_template_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("task_templates.id"), nullable=False),
        sa.Column("scheduled_date", sa.Date, nullable=False),
        sa.Column("scheduled_datetime", sa.DateTime, nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("notification_sent_at", sa.DateTime, nullable=True),
    )
    op.create_index("ix_scheduled_tasks_task_template_id", "scheduled_tasks", ["task_template_id"])
    op.create_index("ix_scheduled_tasks_scheduled_date", "scheduled_tasks", ["scheduled_date"])
    op.create_index("ix_scheduled_tasks_scheduled_datetime", "scheduled_tasks", ["scheduled_datetime"])
    op.create_index("ix_scheduled_tasks_status", "scheduled_tasks", ["status"])

    # Check-ins
    op.create_table(
        "check_ins",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("scheduled_task_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("scheduled_tasks.id"), nullable=False),
        sa.Column("checkin_time", sa.DateTime, nullable=False),
        sa.Column("method", sa.String(50), nullable=False, server_default="telegram"),
        sa.Column("user_note", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_check_ins_scheduled_task_id", "check_ins", ["scheduled_task_id"])

    # Score Events
    op.create_table(
        "score_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("checkin_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("check_ins.id"), nullable=False),
        sa.Column("raw_delta_minutes", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("computed_score", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("formula_version", sa.String(50), nullable=False, server_default="v1"),
        sa.Column("calculation_meta", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_score_events_checkin_id", "score_events", ["checkin_id"])

    # Progress Snapshots
    op.create_table(
        "progress_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("period_start", sa.Date, nullable=False),
        sa.Column("period_end", sa.Date, nullable=False),
        sa.Column("period_type", sa.String(50), nullable=False, server_default="weekly"),
        sa.Column("aggregate_score", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("breakdown", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_progress_snapshots_user_id", "progress_snapshots", ["user_id"])

    # Insights
    op.create_table(
        "insights",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("goal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("goals.id"), nullable=False),
        sa.Column("insight_type", sa.String(100), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("supporting_data", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_insights_user_id", "insights", ["user_id"])
    op.create_index("ix_insights_goal_id", "insights", ["goal_id"])


def downgrade() -> None:
    op.drop_table("insights")
    op.drop_table("progress_snapshots")
    op.drop_table("score_events")
    op.drop_table("check_ins")
    op.drop_table("scheduled_tasks")
    op.drop_table("task_templates")
    op.drop_table("plans")
    op.drop_table("goals")
    op.drop_table("users")
