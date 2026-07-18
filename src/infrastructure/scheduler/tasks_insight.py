"""Weekly insight generation Celery task."""

import asyncio
import logging
from datetime import datetime, timedelta

from src.infrastructure.scheduler.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    max_retries=2,
    default_retry_delay=300,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def generate_weekly_insights() -> dict:
    """Har yakshanba kechasi barcha foydalanuvchilar uchun insight generatsiya qilish."""
    logger.info("Generating weekly insights...")

    from src.config.settings import settings
    from src.application.use_cases.generate_insight import GenerateWeeklyInsightUseCase
    from src.infrastructure.llm import ClaudeProvider

    try:
        if not settings.anthropic_api_key:
            logger.error("ANTHROPIC_API_KEY not configured, skipping insight generation")
            return {"error": "API key not configured"}

        provider = ClaudeProvider(api_key=settings.anthropic_api_key)
        use_case = GenerateWeeklyInsightUseCase(llm_provider=provider)

        weekly_breakdown = """
        Dushanba: 3/3 — 100%
        Seshanba: 2/3 — 67%
        Chorshanba: 3/3 — 100%
        Payshanba: 1/3 — 33%
        Juma: 3/3 — 100%
        Shanba: 2/3 — 67%
        Yakshanba: 0/3 — 0%
        """

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, use_case.execute(
                        goals_count=3,
                        active_goals=2,
                        completed_goals=1,
                        overall_score=87.5,
                        completed_tasks=15,
                        total_tasks=20,
                        weekly_breakdown=weekly_breakdown,
                    ))
                    insight = future.result(timeout=120)
            else:
                insight = loop.run_until_complete(use_case.execute(
                    goals_count=3,
                    active_goals=2,
                    completed_goals=1,
                    overall_score=87.5,
                    completed_tasks=15,
                    total_tasks=20,
                    weekly_breakdown=weekly_breakdown,
                ))
        except RuntimeError:
            insight = asyncio.run(use_case.execute(
                goals_count=3,
                active_goals=2,
                completed_goals=1,
                overall_score=87.5,
                completed_tasks=15,
                total_tasks=20,
                weekly_breakdown=weekly_breakdown,
            ))

        logger.info(f"Weekly insight generated: {insight.summary[:100]}...")

        return {
            "summary": insight.summary,
            "tokens_used": insight.tokens_used,
            "cost_usd": insight.cost_usd,
        }

    except Exception as e:
        logger.error(f"Error generating weekly insights: {e}")
        raise
