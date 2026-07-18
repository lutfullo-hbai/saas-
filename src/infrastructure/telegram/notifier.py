"""Telegram notification sender for scheduled tasks."""

import logging
from uuid import UUID

from sqlalchemy import select

from src.infrastructure.db.models.user import UserModel
from src.infrastructure.db.session import async_session_factory

logger = logging.getLogger(__name__)


async def send_task_notification(
    scheduled_task_id: UUID,
    task_template_id: UUID,
    telegram_id: str,
) -> None:
    """Scheduled task uchun Telegram notification yuborish."""
    from src.infrastructure.telegram.bot import bot

    logger.info(
        f"Sending notification for task {scheduled_task_id}, "
        f"template {task_template_id}"
    )

    text = (
        "🔔 **Eslatma:**\n\n"
        "Vazifangiz boshlanishiga 15 daqiqa qoldi!\n"
        "Keyin 'Bajardim' yoki 'Bajarmadim' tugmasini bosing."
    )

    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=text,
            parse_mode="Markdown",
        )
        logger.info(f"Notification sent for task {scheduled_task_id}")
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        raise


async def get_user_telegram_id(user_id: UUID) -> str | None:
    """User ID dan Telegram chat_id ni olish."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user = result.scalar_one_or_none()
        return user.telegram_id if user else None
