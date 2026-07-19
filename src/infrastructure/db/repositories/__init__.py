"""Repository implementations package."""

from src.infrastructure.db.repositories.goal_repository import PostgresGoalRepository
from src.infrastructure.db.repositories.scheduled_task_repository import (
    PostgresScheduledTaskRepository,
)
from src.infrastructure.db.repositories.score_repository import PostgresScoreRepository
from src.infrastructure.db.repositories.user_repository import PostgresUserRepository

from datetime import date, datetime, timezone
from uuid import UUID

from sqlalchemy import select

from src.config.logging import get_logger
from src.infrastructure.db.models.checkin import CheckInModel
from src.infrastructure.db.models.scheduled_task import ScheduledTaskModel
from src.infrastructure.db.models.score_event import ScoreEventModel
from src.infrastructure.db.models.task_template import TaskTemplateModel
from src.infrastructure.db.session import async_session_factory

logger = get_logger(__name__)

__all__ = [
    "PostgresGoalRepository",
    "PostgresScheduledTaskRepository",
    "PostgresScoreRepository",
    "PostgresUserRepository",
]


async def get_active_task_templates() -> list[dict]:
    """Get all active task templates."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(TaskTemplateModel).where(TaskTemplateModel.is_active == True)
        )
        templates = result.scalars().all()
        return [
            {
                "id": t.id,
                "title": t.title,
                "recurrence_rule": t.recurrence_rule,
                "scheduled_time": t.scheduled_time,
                "tolerance_minutes": t.tolerance_minutes,
                "task_weight": t.task_weight,
            }
            for t in templates
        ]


async def get_scheduled_tasks_by_date(
    task_template_id: UUID,
    date_from: date,
    date_to: date,
) -> list[dict]:
    """Check if a scheduled task already exists for the given template and date."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(ScheduledTaskModel).where(
                ScheduledTaskModel.task_template_id == task_template_id,
                ScheduledTaskModel.scheduled_date >= date_from,
                ScheduledTaskModel.scheduled_date <= date_to,
            )
        )
        tasks = result.scalars().all()
        return [
            {
                "id": t.id,
                "task_template_id": t.task_template_id,
                "scheduled_date": t.scheduled_date,
                "scheduled_datetime": t.scheduled_datetime,
                "status": t.status,
            }
            for t in tasks
        ]


async def create_scheduled_task(
    task_template_id: UUID,
    scheduled_date: date,
    scheduled_datetime: datetime,
) -> dict:
    """Create a new scheduled task."""
    async with async_session_factory() as session:
        task = ScheduledTaskModel(
            task_template_id=task_template_id,
            scheduled_date=scheduled_date,
            scheduled_datetime=scheduled_datetime,
            status="pending",
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)
        logger.info(
            f"Created scheduled task {task.id} for template {task_template_id} "
            f"at {scheduled_datetime}"
        )
        return {
            "id": task.id,
            "task_template_id": task.task_template_id,
            "scheduled_date": task.scheduled_date,
            "scheduled_datetime": task.scheduled_datetime,
            "status": task.status,
        }


async def get_pending_scheduled_tasks_in_window(
    window_start: datetime,
    window_end: datetime,
) -> list[dict]:
    """Get pending tasks within the notification window."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(ScheduledTaskModel).where(
                ScheduledTaskModel.status == "pending",
                ScheduledTaskModel.scheduled_datetime >= window_start,
                ScheduledTaskModel.scheduled_datetime <= window_end,
            )
        )
        tasks = result.scalars().all()
        return [
            {
                "id": t.id,
                "task_template_id": t.task_template_id,
                "scheduled_datetime": t.scheduled_datetime,
                "status": t.status,
                "notification_sent_at": t.notification_sent_at,
            }
            for t in tasks
        ]


async def mark_notification_sent(task_id: UUID) -> None:
    """Mark that a notification has been sent for a task."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(ScheduledTaskModel).where(ScheduledTaskModel.id == task_id)
        )
        task = result.scalar_one_or_none()
        if task:
            task.notification_sent_at = datetime.now(timezone.utc).replace(tzinfo=None)
            await session.commit()
            logger.info(f"Marking notification sent for task {task_id}")


async def get_overdue_pending_tasks(threshold: datetime) -> list[dict]:
    """Get pending tasks that are overdue (past threshold)."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(ScheduledTaskModel).where(
                ScheduledTaskModel.status == "pending",
                ScheduledTaskModel.scheduled_datetime < threshold,
            )
        )
        tasks = result.scalars().all()
        return [
            {
                "id": t.id,
                "task_template_id": t.task_template_id,
                "scheduled_datetime": t.scheduled_datetime,
                "status": t.status,
            }
            for t in tasks
        ]


async def mark_task_missed(task_id: UUID) -> None:
    """Mark a task as missed."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(ScheduledTaskModel).where(ScheduledTaskModel.id == task_id)
        )
        task = result.scalar_one_or_none()
        if task:
            task.status = "missed"
            await session.commit()
            logger.info(f"Marking task {task_id} as missed")


async def create_missed_score_event(
    scheduled_task_id: UUID,
    score: float = 0.0,
    event_type: str = "auto_missed",
) -> None:
    """Create a checkin + score event for a missed task.

    ScoreEvent requires checkin_id, so we first create a CheckIn record.
    """
    async with async_session_factory() as session:
        checkin = CheckInModel(
            scheduled_task_id=scheduled_task_id,
            checkin_time=datetime.now(timezone.utc).replace(tzinfo=None),
            method="auto_missed",
            user_note="",
        )
        session.add(checkin)
        await session.flush()

        event = ScoreEventModel(
            checkin_id=checkin.id,
            raw_delta_minutes=0,
            computed_score=score,
            formula_version="v1",
            calculation_meta={"event_type": event_type},
        )
        session.add(event)
        await session.commit()
        logger.info(
            f"Creating missed score event for task {scheduled_task_id} "
            f"with score {score} (checkin_id={checkin.id})"
        )
