"""Progress command handler."""

from datetime import date, timedelta

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import func, select

from src.infrastructure.db.models.goal import GoalModel
from src.infrastructure.db.models.plan import PlanModel
from src.infrastructure.db.models.task_template import TaskTemplateModel
from src.infrastructure.db.models.scheduled_task import ScheduledTaskModel
from src.infrastructure.db.models.score_event import ScoreEventModel
from src.infrastructure.db.models.checkin import CheckInModel
from src.infrastructure.db.models.user import UserModel
from src.infrastructure.db.session import async_session_factory

router = Router()


@router.message(Command("progress"))
async def cmd_progress(message: Message) -> None:
    """Foydalanuvchi progressini ko'rsatish."""
    telegram_id = str(message.from_user.id)
    user_name = message.from_user.first_name or "Foydalanuvchi"

    async with async_session_factory() as session:
        result = await session.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            await message.answer(
                "❌ Siz hali ro'yxatdan o'tmaganiz.\n"
                "Avval /start buyrug'ini bosing."
            )
            return

        user_id = user.id

        goals_result = await session.execute(
            select(GoalModel).where(GoalModel.user_id == user_id)
        )
        goals = goals_result.scalars().all()
        total_goals = len(goals)
        active_goals = sum(1 for g in goals if g.status == "active")
        completed_goals = sum(1 for g in goals if g.status == "completed")

        today = date.today()
        week_start = today - timedelta(days=today.weekday())

        tasks_result = await session.execute(
            select(ScheduledTaskModel)
            .join(TaskTemplateModel, TaskTemplateModel.id == ScheduledTaskModel.task_template_id)
            .join(PlanModel, PlanModel.id == TaskTemplateModel.plan_id)
            .join(GoalModel, GoalModel.id == PlanModel.goal_id)
            .where(GoalModel.user_id == user_id)
        )
        all_tasks = tasks_result.scalars().all()
        total_tasks = len(all_tasks)
        completed_tasks = sum(1 for t in all_tasks if t.status == "completed")
        missed_tasks = sum(1 for t in all_tasks if t.status == "missed")

        score_result = await session.execute(
            select(func.avg(ScoreEventModel.computed_score))
            .join(CheckInModel, CheckInModel.id == ScoreEventModel.checkin_id)
            .join(ScheduledTaskModel, ScheduledTaskModel.id == CheckInModel.scheduled_task_id)
            .join(TaskTemplateModel, TaskTemplateModel.id == ScheduledTaskModel.task_template_id)
            .join(PlanModel, PlanModel.id == TaskTemplateModel.plan_id)
            .join(GoalModel, GoalModel.id == PlanModel.goal_id)
            .where(GoalModel.user_id == user_id)
        )
        avg_score = score_result.scalar() or 0.0

        weekly_result = await session.execute(
            select(ScheduledTaskModel.status, func.count())
            .join(TaskTemplateModel, TaskTemplateModel.id == ScheduledTaskModel.task_template_id)
            .join(PlanModel, PlanModel.id == TaskTemplateModel.plan_id)
            .join(GoalModel, GoalModel.id == PlanModel.goal_id)
            .where(
                GoalModel.user_id == user_id,
                ScheduledTaskModel.scheduled_date >= week_start,
            )
            .group_by(ScheduledTaskModel.status)
        )
        weekly_stats = dict(weekly_result.all())

        weekly_completed = weekly_stats.get("completed", 0)
        weekly_total = sum(weekly_stats.values())
        weekly_pct = (
            round((weekly_completed / weekly_total * 100), 1) if weekly_total > 0 else 0
        )

    days = [
        ("Dushanba", 0),
        ("Seshanba", 1),
        ("Chorshanba", 2),
        ("Payshanba", 3),
        ("Juma", 4),
        ("Shanba", 5),
        ("Yakshanba", 6),
    ]

    week_text = ""
    for day_name, day_offset in days:
        day_date = week_start + timedelta(days=day_offset)
        if day_date > today:
            week_text += f"{day_name}: ⏳ Kutilmoqda\n"
        elif day_date == today:
            week_text += f"{day_name}: 🔄 Bugun\n"
        else:
            week_text += f"{day_name}: ✅\n"

    await message.answer(
        f"📊 **{user_name} — Progress**\n\n"
        f"🎯 **Maqsadlar:** {total_goals} ta "
        f"({active_goals} faol, {completed_goals} bajarilgan)\n\n"
        f"📈 **Umumiy ball:** {round(avg_score * 100, 1)}%\n"
        f"✅ **Bajarilgan:** {completed_tasks}/{total_tasks} vazifa\n"
        f"❌ **Bajarilmagan:** {missed_tasks}/{total_tasks} vazifa\n\n"
        f"📅 **Bu hafta:** {weekly_completed}/{weekly_total} — {weekly_pct}%\n\n"
        f"{week_text}\n"
        f"💡 **Tavsiya:** Davom eting! Har kuni bir oz yaxshiroq bo'ling."
    )
