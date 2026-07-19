"""Alerting Celery tasks — notification kechiksa yoki server qulasa xabar berish.

Har 5 daqiqada ishga tushadi:
1. Notification kechikkanini tekshiradi
2. DB/Redis ulanishini tekshiradi
3. Celery worker holatini tekshiradi
4. Muammo topilsa, admin ga Telegram xabar yuboradi
"""

from datetime import UTC, datetime, timedelta

import httpx
from sqlalchemy import func, select, text

from src.config.logging import get_logger
from src.config.settings import settings
from src.infrastructure.db.models.scheduled_task import ScheduledTaskModel
from src.infrastructure.db.session import async_session_factory
from src.infrastructure.scheduler.celery_app import celery_app

logger = get_logger(__name__)

# Alert uchun admin Telegram ID (env'dan olish kerak)
# Hozircha bot token'dan foydalanamiz, lekin admin chat ID kerak


def _get_alert_chat_id() -> str | None:
    """Alert yuboriladigan chat ID ni olish.

    ALERT_CHAT_ID env'da aniqlangan bo'lishi kerak.
    Agar yo'q bo'lsa, alert yuborilmaydi.
    """
    import os

    return os.environ.get("ALERT_CHAT_ID")


async def _send_telegram_alert(message: str) -> bool:
    """Telegram orqali alert xabar yuborish."""
    chat_id = _get_alert_chat_id()
    if not chat_id:
        logger.warning("alert_chat_id_not_configured")
        return False

    token = settings.telegram_bot_token
    if not token:
        logger.warning("telegram_bot_token_not_set")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": f"🚨 *DISIPL ALERT*\n\n{message}",
        "parse_mode": "Markdown",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info("alert_sent_successfully", chat_id=chat_id)
                return True
            else:
                logger.error(
                    "alert_send_failed",
                    status_code=response.status_code,
                    response=response.text,
                )
                return False
    except Exception as e:
        logger.error("alert_send_error", error=str(e))
        return False


@celery_app.task(
    bind=True,
    max_retries=2,
    default_retry_delay=60,
)
def check_notification_delivery(self) -> dict:
    """Notification yetkazilishini tekshirish.

    Agar ScheduledTask vaqti 5 daqiqa o'tgan bo'lsa,
    lekin notification_sent_at hali bo'lmasa — alert.
    """
    from src.config.logging import setup_logging

    setup_logging()

    threshold = datetime.now(UTC) - timedelta(minutes=5)

    try:
        import asyncio

        from src.infrastructure.db.session import async_session_factory

        async def _check():
            async with async_session_factory() as session:
                result = await session.execute(
                    select(func.count(ScheduledTaskModel.id)).where(
                        ScheduledTaskModel.status == "pending",
                        ScheduledTaskModel.scheduled_datetime < threshold,
                        ScheduledTaskModel.notification_sent_at.is_(None),
                    )
                )
                overdue_count = result.scalar() or 0
                return overdue_count

        overdue_count = asyncio.run(_check())

        if overdue_count > 0:
            message = (
                f"⚠️ *Notification kechikdi!*\n\n"
                f"{overdue_count} ta vazifa uchun notification hali yuborilmagan.\n"
                f"Vaqt: {datetime.now(UTC).isoformat()}\n"
                f"Chegaradan o'tgan: 5+ daqiqa"
            )
            asyncio.run(_send_telegram_alert(message))
            logger.warning("notifications_overdue", count=overdue_count)

        return {
            "overdue": overdue_count,
            "checked_at": datetime.now(UTC).isoformat(),
        }

    except Exception as e:
        logger.error("notification_check_failed", error=str(e))
        raise


@celery_app.task(
    bind=True,
    max_retries=2,
    default_retry_delay=60,
)
def check_service_health(self) -> dict:
    """Xizmatlar sog'lig'ini tekshirish.

    DB va Redis ulanishini tekshiradi.
    Agar ulanmasa — alert yuboradi.
    """
    from src.config.logging import setup_logging

    setup_logging()

    import asyncio

    import redis.asyncio as aioredis

    issues = []

    async def _check_db():
        try:
            async with async_session_factory() as session:
                await session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            issues.append(f"DB: {e}")
            return False

    async def _check_redis():
        try:
            client = aioredis.from_url(settings.redis_url)
            await client.ping()
            await client.aclose()
            return True
        except Exception as e:
            issues.append(f"Redis: {e}")
            return False

    try:
        asyncio.run(asyncio.gather(_check_db(), _check_redis()))

        if issues:
            message = (
                "🔴 *Xizmatlar xatosi!*\n\n"
                "Quyidagi xizmatlarda muammo:\n"
                + "\n".join(f"• {issue}" for issue in issues)
                + f"\n\nVaqt: {datetime.now(UTC).isoformat()}"
            )
            asyncio.run(_send_telegram_alert(message))
            logger.error("service_health_issues", issues=issues)

        return {
            "healthy": len(issues) == 0,
            "issues": issues,
            "checked_at": datetime.now(UTC).isoformat(),
        }

    except Exception as e:
        logger.error("health_check_failed", error=str(e))
        raise


@celery_app.task(
    bind=True,
    max_retries=2,
    default_retry_delay=60,
)
def check_pending_tasks_backlog(self) -> dict:
    """Katta miqdordagi bajarilmagan vazifalarni tekshirish.

    Agar pending vazifalar soni 100+ bo'lsa — alert.
    Bu Celery worker to'xtab qolganligi belgisi bo'lishi mumkin.
    """
    from src.config.logging import setup_logging

    setup_logging()

    import asyncio

    try:

        async def _check():
            async with async_session_factory() as session:
                result = await session.execute(
                    select(func.count(ScheduledTaskModel.id)).where(
                        ScheduledTaskModel.status == "pending",
                    )
                )
                pending_count = result.scalar() or 0
                return pending_count

        pending_count = asyncio.run(_check())

        if pending_count > 100:
            message = (
                f"⚠️ *Vazifalar to'plandi!*\n\n"
                f"{pending_count} ta bajarilmagan vazifa mavjud.\n"
                f"Celery worker to'xtab qolgan bo'lishi mumkin.\n"
                f"Vaqt: {datetime.now(UTC).isoformat()}"
            )
            asyncio.run(_send_telegram_alert(message))
            logger.warning("task_backlog_detected", count=pending_count)

        return {
            "pending_count": pending_count,
            "alert": pending_count > 100,
            "checked_at": datetime.now(UTC).isoformat(),
        }

    except Exception as e:
        logger.error("backlog_check_failed", error=str(e))
        raise
