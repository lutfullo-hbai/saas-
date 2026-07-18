"""Telegram bot runner."""

import asyncio

from src.config.logging import get_logger, setup_logging
from src.infrastructure.telegram.bot import bot, dp
from src.infrastructure.telegram.handlers import (
    checkin_router,
    feedback_router,
    goal_router,
    goals_list_router,
    help_router,
    onboarding_router,
    progress_router,
    referral_router,
    start_router,
)

logger = get_logger(__name__)


async def main() -> None:
    """Botni ishga tushirish."""
    setup_logging()
    dp.include_router(start_router)
    dp.include_router(help_router)
    dp.include_router(onboarding_router)
    dp.include_router(goal_router)
    dp.include_router(goals_list_router)
    dp.include_router(checkin_router)
    dp.include_router(progress_router)
    dp.include_router(feedback_router)
    dp.include_router(referral_router)

    logger.info("bot_starting")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
