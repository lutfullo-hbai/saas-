"""Goals list handler for Telegram bot."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select

from src.infrastructure.db.models.goal import GoalModel
from src.infrastructure.db.models.user import UserModel
from src.infrastructure.db.session import async_session_factory

router = Router()


@router.message(Command("goals"))
async def cmd_goals(message: Message) -> None:
    """Foydalanuvchining barcha maqsadlarini ko'rsatish."""
    telegram_id = str(message.from_user.id)

    async with async_session_factory() as session:
        result = await session.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            await message.answer(
                "❌ Siz hali ro'yxatdan o'tmaganiz.\n" "Avval /start buyrug'ini bosing."
            )
            return

        goals_result = await session.execute(
            select(GoalModel).where(GoalModel.user_id == user.id)
        )
        goals = goals_result.scalars().all()

    if not goals:
        await message.answer(
            "📋 **Maqsadlar**\n\n"
            "Sizda hali maqsadlar yo'q.\n\n"
            "Yangi maqsad qo'shish uchun /newgoal buyrug'ini bosing."
        )
        return

    status_icons = {
        "active": "🟢",
        "completed": "✅",
        "paused": "⏸️",
        "cancelled": "❌",
    }

    text = "📋 **Sizning maqsadlaringiz**\n\n"

    for i, goal in enumerate(goals, 1):
        icon = status_icons.get(goal.status, "❓")
        date_str = (
            goal.target_date.strftime("%d.%m.%Y")
            if goal.target_date
            else "sana belgilanmagan"
        )
        text += f"{i}. {icon} **{goal.title}**\n"
        text += f"   📅 {date_str} | 📌 {goal.status}\n\n"

    text += "Yangi maqsad qo'shish uchun /newgoal buyrug'ini bosing."

    await message.answer(text)
