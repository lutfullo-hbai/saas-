"""Celery tasks for scheduler and notifications."""

import asyncio
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


def _run_async(coro):
    """Sync kontekstdan async funksiyani ishga tushirish."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result(timeout=120)
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
)
def generate_scheduled_tasks(self) -> dict:
    """Ertaga uchun barcha faol TaskTemplate'lardan ScheduledTask yaratish."""
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
        templates = _run_async(get_active_task_templates())
        created_count = 0

        for template in templates:
            existing = _run_async(
                get_scheduled_tasks_by_date(
                    task_template_id=template["id"],
                    date_from=tomorrow_start.date(),
                    date_to=tomorrow_end.date(),
                )
            )
            if existing:
                logger.debug(
                    f"TaskTemplate {template['id']} already has scheduled task for tomorrow"
                )
                continue

            occurrences = get_next_occurrences(
                recurrence_rule=template["recurrence_rule"],
                dtstart=tomorrow_start,
                count=1,
            )

            if occurrences:
                scheduled_dt = occurrences[0]
                scheduled_time = template["scheduled_time"]
                hour, minute = map(int, scheduled_time.split(":"))
                scheduled_dt = scheduled_dt.replace(hour=hour, minute=minute, second=0)

                _run_async(
                    create_scheduled_task(
                        task_template_id=template["id"],
                        scheduled_date=tomorrow,
                        scheduled_datetime=scheduled_dt,
                    )
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
    """Yaqinlashgan vazifalar uchun Telegram notification yuborish."""
    logger.info("Checking for tasks needing notifications...")

    now = datetime.now()
    window_start = now
    window_end = now + timedelta(minutes=15)

    from src.infrastructure.db.repositories import (
        get_pending_scheduled_tasks_in_window,
        mark_notification_sent,
    )
    from src.infrastructure.telegram.notifier import (
        send_task_notification,
        get_user_telegram_id_for_task,
    )

    try:
        tasks = _run_async(
            get_pending_scheduled_tasks_in_window(
                window_start=window_start,
                window_end=window_end,
            )
        )

        sent_count = 0
        for task in tasks:
            if task.get("notification_sent_at") is not None:
                logger.debug(f"Task {task['id']} already notified")
                continue

            try:
                telegram_id = _run_async(
                    get_user_telegram_id_for_task(task["id"])
                )
                if not telegram_id:
                    logger.warning(
                        f"No telegram_id found for task {task['id']}, skipping"
                    )
                    continue

                _run_async(
                    send_task_notification(
                        scheduled_task_id=task["id"],
                        task_template_id=task["task_template_id"],
                        telegram_id=telegram_id,
                    )
                )
                _run_async(mark_notification_sent(task_id=task["id"]))
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send notification for task {task['id']}: {e}")
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
    """Vaqti o'tgan va hali javob berilmagan vazifalarni 'missed' deb belgilash."""
    logger.info("Marking missed checkins...")

    threshold = datetime.now() - timedelta(hours=3)

    from src.infrastructure.db.repositories import (
        get_overdue_pending_tasks,
        mark_task_missed,
        create_missed_score_event,
    )

    try:
        tasks = _run_async(get_overdue_pending_tasks(threshold=threshold))
        missed_count = 0

        for task in tasks:
            _run_async(mark_task_missed(task_id=task["id"]))
            _run_async(
                create_missed_score_event(
                    scheduled_task_id=task["id"],
                    score=0.0,
                    event_type="auto_missed",
                )
            )
            missed_count += 1

        logger.info(f"Marked {missed_count} tasks as missed")
        return {"missed": missed_count}

    except Exception as e:
        logger.error(f"Error marking missed checkins: {e}")
        raise
