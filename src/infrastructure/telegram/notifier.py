"""Telegram notification sender for scheduled tasks."""

import logging
from uuid import UUID

logger = logging.getLogger(__name__)


async def send_task_notification(
    scheduled_task_id: UUID,
    task_template_id: UUID,
) -> None:
    """Scheduled task uchun Telegram notification yuborish.

    Bu yerda aiogram bot orqali xabar yuboriladi.
    """
    from src.infrastructure.telegram.bot import bot

    logger.info(
        f"Sending notification for task {scheduled_task_id}, "
        f"template {task_template_id}"
    )

    text = (
        f"🔔 **Eslatma:**\n\n"
        f"Vazifangiz boshlanishiga 15 daqiqa qoldi!\n"
        f"Keyin 'Bajardim' yoki 'Bajarmadim' tugmasini bosing."
    )

    try:
        await bot.send_message(
            chat_id=123456789,
            text=text,
            parse_mode="Markdown",
        )
        logger.info(f"Notification sent for task {scheduled_task_id}")
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        raise
