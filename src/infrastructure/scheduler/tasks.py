"""Celery tasks for scheduler and notifications."""

import logging
from datetime import datetime, timedelta
from uuid import UUID

from dateutil.rrule import rrulestr

from src.infrastructure.scheduler.celery_app import celery_app

logger = logging.getLogger(__name__)


def get_next_occurrences(
    recurrence_rule: str, dtstart: datetime, count: int = 1
) -> list[datetime]:
    """RRULE asosida keyingi takrorlanishlarni generatsiya qilish."""
    try:
        rule = rrulestr(recurrence_rule, dtstart=dtstart)
        return list(rule)[:count]
    except ValueError as e:
        logger.error(f"Invalid RRULE: {recurrence_rule}, error: {e}")
        return []


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
)
def generate_scheduled_tasks(self) -> dict:
    """Ertaga uchun barcha faol TaskTemplate'lardan ScheduledTask yaratish.

    Har kuni kechasi ishga tushadi.
    Idempotency: Agar ertaga uchun ScheduledTask allaqachon yaratilgan bo'lsa,
    qayta yaratmaydi.
    """
    logger.info("Generating scheduled tasks for tomorrow...")

    tomorrow = datetime.now().date() + timedelta(days=1)
    tomorrow_start = datetime.combine(tomorrow, datetime.min.time())
    tomorrow_end = datetime.combine(tomorrow, datetime.max.time())

    from src.infrastructure.db.repositories import (
        get_active_task_templates,
        get_scheduled_tasks_by_date,
        create_scheduled_task,
    )

    try:
        templates = get_active_task_templates()
        created_count = 0

        for template in templates:
            existing = get_scheduled_tasks_by_date(
                task_template_id=template.id,
                date_from=tomorrow_start,
                date_to=tomorrow_end,
            )
            if existing:
                logger.debug(
                    f"TaskTemplate {template.id} already has scheduled task for tomorrow"
                )
                continue

            occurrences = get_next_occurrences(
                recurrence_rule=template.recurrence_rule,
                dtstart=tomorrow_start,
                count=1,
            )

            if occurrences:
                scheduled_dt = occurrences[0]
                scheduled_time = template.scheduled_time
                hour, minute = map(int, scheduled_time.split(":"))
                scheduled_dt = scheduled_dt.replace(hour=hour, minute=minute, second=0)

                create_scheduled_task(
                    task_template_id=template.id,
                    scheduled_date=tomorrow,
                    scheduled_datetime=scheduled_dt,
                )
                created_count += 1

        logger.info(f"Created {created_count} scheduled tasks for tomorrow")
        return {"created": created_count, "date": str(tomorrow)}

    except Exception as e:
        logger.error(f"Error generating scheduled tasks: {e}")
        raise


@celery_app.task(
    bind=True,
    max_retries=5,
    default_retry_delay=30,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
)
def send_notifications() -> dict:
    """Yaqinlashgan vazifalar uchun Telegram notification yuborish.

    Har daqiqada ishga tushadi.
    Idempotency: notification_sent_at allaqachon o'rnatilgan bo'lsa,
    qayta yuborilmaydi.
    """
    logger.info("Checking for tasks needing notifications...")

    now = datetime.now()
    window_start = now
    window_end = now + timedelta(minutes=15)

    from src.infrastructure.db.repositories import (
        get_pending_scheduled_tasks_in_window,
        mark_notification_sent,
    )
    from src.infrastructure.telegram.notifier import send_task_notification

    try:
        tasks = get_pending_scheduled_tasks_in_window(
            window_start=window_start,
            window_end=window_end,
        )

        sent_count = 0
        for task in tasks:
            if task.notification_sent_at is not None:
                logger.debug(f"Task {task.id} already notified")
                continue

            try:
                send_task_notification(
                    scheduled_task_id=task.id,
                    task_template_id=task.task_template_id,
                )
                mark_notification_sent(task_id=task.id)
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send notification for task {task.id}: {e}")
                raise

        logger.info(f"Sent {sent_count} notifications")
        return {"sent": sent_count}

    except Exception as e:
        logger.error(f"Error in send_notifications: {e}")
        raise


@celery_app.task(
    bind=True,
    max_retries=2,
    default_retry_delay=120,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def mark_missed_checkins() -> dict:
    """Vaqti o'tgan va hali javob berilmagan vazifalarni "missed" deb belgilash.

    Har soat ishga tushadi.
    Agar scheduled_datetimedan 3 soat o'tsa va hali check-in bo'lmasa,
    avtomatik ScoreEvent(score=0) yaratiladi.
    """
    logger.info("Marking missed checkins...")

    threshold = datetime.now() - timedelta(hours=3)

    from src.infrastructure.db.repositories import (
        get_overdue_pending_tasks,
        mark_task_missed,
        create_score_event,
    )

    try:
        tasks = get_overdue_pending_tasks(threshold=threshold)
        missed_count = 0

        for task in tasks:
            mark_task_missed(task_id=task.id)
            create_score_event(
                scheduled_task_id=task.id,
                score=0.0,
                event_type="auto_missed",
            )
            missed_count += 1

        logger.info(f"Marked {missed_count} tasks as missed")
        return {"missed": missed_count}

    except Exception as e:
        logger.error(f"Error marking missed checkins: {e}")
        raise
