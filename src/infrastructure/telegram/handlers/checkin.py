"""Check-in handler with inline keyboard buttons."""

from datetime import date, datetime
from uuid import UUID

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select

from src.application.use_cases.process_checkin import ProcessCheckInUseCase
from src.infrastructure.db.models.scheduled_task import ScheduledTaskModel
from src.infrastructure.db.models.task_template import TaskTemplateModel
from src.infrastructure.db.models.user import UserModel
from src.infrastructure.db.repositories.score_repository import PostgresScoreRepository
from src.infrastructure.db.repositories.scheduled_task_repository import (
    PostgresScheduledTaskRepository,
)
from src.infrastructure.db.session import async_session_factory
from src.infrastructure.telegram.bot import bot

router = Router()


async def _get_user_id(telegram_id: str) -> str | None:
    """Telegram ID dan user ID ni olish."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        return str(user.id) if user else None


async def _get_today_tasks(user_id: str) -> list[dict]:
    """Bugungi scheduled task'larni faqat shu foydalanuvchiga tegishli qilib olish."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(ScheduledTaskModel)
            .join(TaskTemplateModel, TaskTemplateModel.id == ScheduledTaskModel.task_template_id)
            .where(
                ScheduledTaskModel.scheduled_date == date.today(),
                ScheduledTaskModel.status == "pending",
            )
        )
        all_tasks = result.scalars().all()

        task_list = []
        for task in all_tasks:
            template_result = await session.execute(
                select(TaskTemplateModel).where(TaskTemplateModel.id == task.task_template_id)
            )
            template = template_result.scalar_one_or_none()

            if not template:
                continue

            from src.infrastructure.db.models.plan import PlanModel
            from src.infrastructure.db.models.goal import GoalModel

            plan_result = await session.execute(
                select(PlanModel).where(PlanModel.id == template.plan_id)
            )
            plan = plan_result.scalar_one_or_none()
            if not plan:
                continue

            goal_result = await session.execute(
                select(GoalModel).where(
                    GoalModel.id == plan.goal_id,
                    GoalModel.user_id == UUID(user_id),
                )
            )
            goal = goal_result.scalar_one_or_none()
            if not goal:
                continue

            task_list.append(
                {
                    "id": str(task.id),
                    "title": template.title if template else "Noma'lum",
                    "time": task.scheduled_datetime.strftime("%H:%M")
                    if task.scheduled_datetime
                    else "??:??",
                }
            )
        return task_list


@router.message(Command("tasks"))
async def cmd_tasks(message: Message) -> None:
    """Bugungi vazifalarni ko'rsatish."""
    telegram_id = str(message.from_user.id)
    user_id = await _get_user_id(telegram_id)

    if not user_id:
        await message.answer(
            "❌ Siz hali ro'yxatdan o'tmaganiz.\n"
            "Avval /start buyrug'ini bosing."
        )
        return

    tasks = await _get_today_tasks(user_id)

    if not tasks:
        await message.answer(
            "📋 **Bugungi vazifalar**\n\n"
            "Bugun uchun rejalashtirilgan vazifalar yo'q.\n"
            "Yangi maqsad qo'shish uchun /newgoal buyrug'ini bosing."
        )
        return

    text = "📋 **Bugungi vazifalar**\n\n"
    builder = InlineKeyboardBuilder()

    for i, task in enumerate(tasks, 1):
        text += f"{i}. 📖 {task['title']} ({task['time']})\n"
        builder.button(
            text=f"✅ {task['title']}",
            callback_data=f"checkin_done_{task['id']}",
        )

    builder.adjust(1)
    text += "\nVazifani bajarasizmi?"

    await message.answer(text, reply_markup=builder.as_markup())


@router.callback_query(lambda c: c.data.startswith("checkin_done_"))
async def handle_checkin_done(callback: CallbackQuery) -> None:
    """Check-in tugmasi bosilganda — vazifa bajarildi."""
    task_id = callback.data.replace("checkin_done_", "")
    telegram_id = str(callback.from_user.id)
    user_id = await _get_user_id(telegram_id)

    if not user_id:
        await callback.message.edit_text("❌ Foydalanuvchi topilmadi.")
        await callback.answer()
        return

    try:
        async with async_session_factory() as session:
            task_repo = PostgresScheduledTaskRepository(session)
            score_repo = PostgresScoreRepository(session)
            use_case = ProcessCheckInUseCase(task_repo, score_repo, session)

            task_uuid = UUID(task_id)
            task = await task_repo.get_by_id(task_uuid)
            if not task:
                await callback.message.edit_text("❌ Vazifa topilmadi.")
                await callback.answer()
                return

            from src.infrastructure.db.models.task_template import TaskTemplateModel
            from src.infrastructure.db.models.plan import PlanModel
            from src.infrastructure.db.models.goal import GoalModel

            template_result = await session.execute(
                select(TaskTemplateModel).where(
                    TaskTemplateModel.id == task.task_template_id
                )
            )
            template = template_result.scalar_one_or_none()
            if not template:
                await callback.message.edit_text("❌ Vazifa shabloni topilmadi.")
                await callback.answer()
                return

            plan_result = await session.execute(
                select(PlanModel).where(PlanModel.id == template.plan_id)
            )
            plan = plan_result.scalar_one_or_none()
            if not plan:
                await callback.message.edit_text("❌ Reja topilmadi.")
                await callback.answer()
                return

            goal_result = await session.execute(
                select(GoalModel).where(
                    GoalModel.id == plan.goal_id,
                    GoalModel.user_id == UUID(user_id),
                )
            )
            goal = goal_result.scalar_one_or_none()
            if not goal:
                await callback.message.edit_text(
                    "❌ Bu vazifa sizga tegishli emas."
                )
                await callback.answer()
                return

            checkin, score_event = await use_case.execute(
                scheduled_task_id=task_uuid,
                checkin_time=datetime.utcnow(),
                method="telegram",
                user_note="",
            )

            await session.commit()

        score = round(score_event.computed_score, 2) if score_event else 0.0

        await callback.message.edit_text(
            f"✅ **Vazifa bajarildi!**\n\n"
            f"🎯 Ball: +{score}\n"
            f"⏰ Vaqt: {datetime.now().strftime('%H:%M')}\n\n"
            f"Ajoyib! Davom eting!"
        )
    except Exception as e:
        await callback.message.edit_text(
            f"❌ **Xatolik:** {str(e)}\n\n"
            "Qaytadan urinib ko'ring."
        )

    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("checkin_missed_"))
async def handle_checkin_missed(callback: CallbackQuery) -> None:
    """Check-in tugmasi bosilganda — vazifa bajarilmadi."""
    await callback.message.edit_text(
        "❌ **Vazifa bajarilmadi**\n\n"
        "Keyingi safar albatta bajaring!\n"
        "Sababini yozing (ixtiyoriy):"
    )
    await callback.answer()
