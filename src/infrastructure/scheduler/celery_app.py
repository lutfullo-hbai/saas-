"""Celery application configuration."""

from celery import Celery

from src.config.settings import settings

celery_app = Celery(
    "disipl",
    broker=settings.redis_url,
    backend=settings.redis_url,
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
        "generate-weekly-insights": {
            "task": "src.infrastructure.scheduler.tasks_insight.generate_weekly_insights",
            "schedule": 604800.0,
            "args": (),
        },
        # Alerting tasks
        "check-notification-delivery": {
            "task": "src.infrastructure.scheduler.tasks_alerting.check_notification_delivery",
            "schedule": 300.0,  # Har 5 daqiqada
            "args": (),
        },
        "check-service-health": {
            "task": "src.infrastructure.scheduler.tasks_alerting.check_service_health",
            "schedule": 300.0,  # Har 5 daqiqada
            "args": (),
        },
        "check-pending-tasks-backlog": {
            "task": "src.infrastructure.scheduler.tasks_alerting.check_pending_tasks_backlog",
            "schedule": 600.0,  # Har 10 daqiqada
            "args": (),
        },
        # Backup tasks
        "daily-backup": {
            "task": "src.infrastructure.scheduler.tasks_backup.run_daily_backup",
            "schedule": 86400.0,  # Har kuni (tunda)
            "args": (),
        },
        "verify-backup-weekly": {
            "task": "src.infrastructure.scheduler.tasks_backup.verify_backup",
            "schedule": 604800.0,  # Haftada bir marta
            "args": (),
        },
    },
)

celery_app.autodiscover_tasks(
    [
        "src.infrastructure.scheduler.tasks",
        "src.infrastructure.scheduler.tasks_alerting",
        "src.infrastructure.scheduler.tasks_backup",
        "src.infrastructure.scheduler.tasks_insight",
    ]
)
