"""Automated backup Celery task — kunlik PostgreSQL backup.

Celery Beat orqali har kuni tunda ishga tushadi.
Backup natijasi admin ga xabar beriladi.
"""

import subprocess
from datetime import datetime

from src.config.logging import get_logger
from src.config.settings import settings
from src.infrastructure.scheduler.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=300,
)
def run_daily_backup(self) -> dict:
    """Kunlik PostgreSQL backup.

    scripts/backup.sh skriptini ishga tushiradi.
    """
    from src.config.logging import setup_logging

    setup_logging()

    logger.info("daily_backup_started")

    try:
        result = subprocess.run(
            ["bash", "scripts/backup.sh"],
            capture_output=True,
            text=True,
            timeout=600,  # 10 daqiqa timeout
            env={
                **__import__("os").environ,
                "DB_HOST": "db",
                "DB_PORT": "5432",
                "POSTGRES_DB": settings.database_url.split("/")[-1].split("?")[0],
                "POSTGRES_USER": settings.database_url.split("://")[1].split(":")[0],
            },
        )

        if result.returncode == 0:
            logger.info("daily_backup_completed", output=result.stdout)
            return {
                "status": "success",
                "timestamp": datetime.utcnow().isoformat(),
                "output": result.stdout,
            }
        else:
            logger.error("daily_backup_failed", error=result.stderr)
            return {
                "status": "failed",
                "timestamp": datetime.utcnow().isoformat(),
                "error": result.stderr,
            }

    except subprocess.TimeoutExpired:
        logger.error("daily_backup_timeout")
        raise
    except Exception as e:
        logger.error("daily_backup_error", error=str(e))
        raise


@celery_app.task(
    bind=True,
    max_retries=2,
    default_retry_delay=600,
)
def verify_backup(self) -> dict:
    """Oxirgi backup'ning to'g'riligini tekshirish.

    Backup faylini topib, uning hajmini va yaratilgan vaqtini tekshiradi.
    """
    import os
    import glob

    from src.config.logging import setup_logging

    setup_logging()

    logger.info("backup_verification_started")

    backup_dir = "/backups"

    try:
        # Oxirgi backup faylini topish
        pattern = f"{backup_dir}/*.sql.gz"
        files = glob.glob(pattern)

        if not files:
            logger.warning("no_backups_found")
            return {
                "status": "no_backups",
                "timestamp": datetime.utcnow().isoformat(),
            }

        # Eng so'nggi backup
        latest = max(files, key=os.path.getctime)
        file_size = os.path.getsize(latest)
        file_time = datetime.fromtimestamp(os.path.getctime(latest))

        # Hajm tekshirish (kamida 1KB bo'lishi kerak)
        if file_size < 1024:
            logger.warning("backup_too_small", file=latest, size=file_size)
            return {
                "status": "warning",
                "message": "Backup file is suspiciously small",
                "file": latest,
                "size": file_size,
            }

        logger.info(
            "backup_verification_completed",
            file=latest,
            size=file_size,
            created_at=file_time.isoformat(),
        )

        return {
            "status": "ok",
            "file": latest,
            "size_bytes": file_size,
            "created_at": file_time.isoformat(),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error("backup_verification_error", error=str(e))
        raise
