"""Celery application configuration."""

from celery import Celery

celery_app = Celery(
    "disipl",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    beat_schedule={
        "generate-daily-tasks": {
            "task": "src.infrastructure.scheduler.tasks.generate_scheduled_tasks",
            "schedule": 86400.0,
            "args": (),
        },
        "send-notifications-every-minute": {
            "task": "src.infrastructure.scheduler.tasks.send_notifications",
            "schedule": 60.0,
            "args": (),
        },
        "mark-missed-checkins-every-hour": {
            "task": "src.infrastructure.scheduler.tasks.mark_missed_checkins",
            "schedule": 3600.0,
            "args": (),
        },
    },
)
