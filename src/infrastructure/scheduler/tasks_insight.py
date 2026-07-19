"""Weekly insight generation Celery task — real DB ma'lumotlari bilan."""

import asyncio
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select

from src.config.logging import get_logger
from src.infrastructure.scheduler.celery_app import celery_app

logger = get_logger(__name__)

DAY_NAMES_UZ = {
    0: "Dushanba",
    1: "Seshanba",
    2: "Chorshanba",
    3: "Payshanba",
    4: "Juma",
    5: "Shanba",
    6: "Yakshanba",
}


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


async def gather_user_weekly_data(user_id: UUID) -> dict | None:
    """Bir foydalanuvchining haftalik ma'lumotlarini yig'ish.

    Returns:
        dict yoki None (agar ma'lumot yetarli bo'lmasa)
    """
    from src.infrastructure.db.models.checkin import CheckInModel
    from src.infrastructure.db.models.goal import GoalModel
    from src.infrastructure.db.models.plan import PlanModel
    from src.infrastructure.db.models.scheduled_task import ScheduledTaskModel
    from src.infrastructure.db.models.score_event import ScoreEventModel
    from src.infrastructure.db.models.task_template import TaskTemplateModel
    from src.infrastructure.db.session import async_session_factory

    async with async_session_factory() as session:
        week_ago = datetime.now() - timedelta(days=7)

        goals_result = await session.execute(
            select(GoalModel).where(GoalModel.user_id == user_id)
        )
        goals = goals_result.scalars().all()
        total_goals = len(goals)
        active_goals = sum(1 for g in goals if g.status == "active")
        completed_goals = sum(1 for g in goals if g.status == "completed")

        tasks_result = await session.execute(
            select(ScheduledTaskModel)
            .join(
                TaskTemplateModel,
                TaskTemplateModel.id == ScheduledTaskModel.task_template_id,
            )
            .join(PlanModel, PlanModel.id == TaskTemplateModel.plan_id)
            .join(GoalModel, GoalModel.id == PlanModel.goal_id)
            .where(
                GoalModel.user_id == user_id,
                ScheduledTaskModel.scheduled_datetime >= week_ago,
            )
        )
        all_tasks = tasks_result.scalars().all()
        total_tasks = len(all_tasks)
        completed_tasks = sum(1 for t in all_tasks if t.status == "completed")
        missed_tasks = sum(1 for t in all_tasks if t.status == "missed")

        if total_tasks == 0:
            return None

        score_result = await session.execute(
            select(func.avg(ScoreEventModel.computed_score))
            .join(CheckInModel, CheckInModel.id == ScoreEventModel.checkin_id)
            .join(
                ScheduledTaskModel,
                ScheduledTaskModel.id == CheckInModel.scheduled_task_id,
            )
            .join(
                TaskTemplateModel,
                TaskTemplateModel.id == ScheduledTaskModel.task_template_id,
            )
            .join(PlanModel, PlanModel.id == TaskTemplateModel.plan_id)
            .join(GoalModel, GoalModel.id == PlanModel.goal_id)
            .where(
                GoalModel.user_id == user_id,
                ScoreEventModel.created_at >= week_ago,
            )
        )
        avg_score = score_result.scalar() or 0.0
        overall_score = round(float(avg_score) * 100, 1)

        weekly_breakdown_lines = []
        for day_offset in range(7):
            day = (datetime.now() - timedelta(days=6 - day_offset)).date()
            day_start = datetime.combine(day, datetime.min.time())
            day_end = datetime.combine(day, datetime.max.time())

            day_tasks_result = await session.execute(
                select(ScheduledTaskModel)
                .join(
                    TaskTemplateModel,
                    TaskTemplateModel.id == ScheduledTaskModel.task_template_id,
                )
                .join(PlanModel, PlanModel.id == TaskTemplateModel.plan_id)
                .join(GoalModel, GoalModel.id == PlanModel.goal_id)
                .where(
                    GoalModel.user_id == user_id,
                    ScheduledTaskModel.scheduled_datetime >= day_start,
                    ScheduledTaskModel.scheduled_datetime <= day_end,
                )
            )
            day_tasks = day_tasks_result.scalars().all()
            day_completed = sum(1 for t in day_tasks if t.status == "completed")
            day_total = len(day_tasks)

            day_name = DAY_NAMES_UZ.get(day.weekday(), str(day.weekday()))
            pct = round(day_completed / day_total * 100) if day_total > 0 else 0
            weekly_breakdown_lines.append(
                f"{day_name}: {day_completed}/{day_total} — {pct}%"
            )

        return {
            "goals_count": total_goals,
            "active_goals": active_goals,
            "completed_goals": completed_goals,
            "overall_score": overall_score,
            "completed_tasks": completed_tasks,
            "total_tasks": total_tasks,
            "missed_tasks": missed_tasks,
            "weekly_breakdown": "\n".join(weekly_breakdown_lines),
        }


async def save_insight(
    user_id: UUID,
    goal_id: UUID,
    insight_type: str,
    content: str,
    supporting_data: dict,
) -> None:
    """Insight ni DB ga saqlash."""
    from src.infrastructure.db.models.insight import InsightModel
    from src.infrastructure.db.session import async_session_factory

    async with async_session_factory() as session:
        insight = InsightModel(
            user_id=user_id,
            goal_id=goal_id,
            insight_type=insight_type,
            content=content,
            supporting_data=supporting_data,
        )
        session.add(insight)
        await session.commit()
        logger.info(f"Insight saved for user {user_id}: {insight_type}")


@celery_app.task(
    bind=True,
    max_retries=2,
    default_retry_delay=300,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def generate_weekly_insights() -> dict:
    """Har yakshanba kechasi barcha faol foydalanuvchilar uchun insight generatsiya qilish.

    Har bir foydalanuvchi uchun:
    1. DB dan haftalik ma'lumotlar yig'iladi
    2. LLM orqali tahlil generatsiya qilinadi
    3. Insight DB ga saqlanadi
    """
    logger.info("Generating weekly insights...")

    from src.application.use_cases.generate_insight import GenerateWeeklyInsightUseCase
    from src.config.settings import settings
    from src.infrastructure.llm import ClaudeProvider

    if not settings.anthropic_api_key:
        logger.error("ANTHROPIC_API_KEY not configured, skipping insight generation")
        return {"error": "API key not configured"}

    provider = ClaudeProvider(api_key=settings.anthropic_api_key)
    use_case = GenerateWeeklyInsightUseCase(llm_provider=provider)

    async def _process_all_users():
        from src.infrastructure.db.models.goal import GoalModel
        from src.infrastructure.db.models.user import UserModel
        from src.infrastructure.db.session import async_session_factory

        async with async_session_factory() as session:
            users_result = await session.execute(select(UserModel))
            users = users_result.scalars().all()

        processed = 0
        errors = 0

        for user in users:
            try:
                data = await gather_user_weekly_data(user.id)
                if data is None:
                    logger.debug(f"User {user.id}: no tasks this week, skipping")
                    continue

                insight = await use_case.execute(**data)

                goals_result = await session.execute(
                    select(GoalModel).where(
                        GoalModel.user_id == user.id,
                        GoalModel.status == "active",
                    )
                )
                active_goals = goals_result.scalars().all()
                goal_id = active_goals[0].id if active_goals else None

                if goal_id:
                    await save_insight(
                        user_id=user.id,
                        goal_id=goal_id,
                        insight_type="weekly_analysis",
                        content=insight.summary,
                        supporting_data={
                            "weak_days": insight.weak_days,
                            "weak_tasks": insight.weak_tasks,
                            "recommendation": insight.recommendation,
                            "question": insight.question,
                            "tokens_used": insight.tokens_used,
                            "cost_usd": insight.cost_usd,
                            "weekly_breakdown": data["weekly_breakdown"],
                            "overall_score": data["overall_score"],
                        },
                    )

                processed += 1
                logger.info(
                    f"Insight generated for user {user.id}: "
                    f"{insight.summary[:80]}..."
                )

            except Exception as e:
                errors += 1
                logger.error(f"Error generating insight for user {user.id}: {e}")

        return {"processed": processed, "errors": errors}

    try:
        result = _run_async(_process_all_users())
        logger.info(f"Weekly insights done: {result}")
        return result

    except Exception as e:
        logger.error(f"Error generating weekly insights: {e}")
        raise
