"""Check-in handler with inline keyboard buttons."""

from datetime import datetime
from uuid import UUID

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()


@router.message(Command("tasks"))
async def cmd_tasks(message: Message) -> None:
    """Bugungi vazifalarni ko'rsatish."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Bajardim",
        callback_data="checkin_done",
    )
    builder.button(
        text="❌ Bajarmadim",
        callback_data="checkin_missed",
    )
    builder.adjust(2)

    await message.answer(
        "📋 **Bugungi vazifalar**\n\n"
        "1. 📖 Ingliz tili — 50 ta so'z yodlash (14:30)\n"
        "2. 🏃 Sport — 30 daqiqa yugurish (17:00)\n"
        "3. 📚 Kitob — 20 sahifa o'qish (20:00)\n\n"
        "Vazifani bajarasizmi?",
        reply_markup=builder.as_markup(),
    )


@router.callback_query(lambda c: c.data.startswith("checkin_"))
async def handle_checkin(callback: CallbackQuery) -> None:
    """Check-in tugmasi bosilganda."""
    action = callback.data.split("_")[1]

    if action == "done":
        score = 0.95
        await callback.message.edit_text(
            f"✅ **Vazifa bajarildi!**\n\n"
            f"🎯 Ball: +{score}\n"
            f"⏰ Vaqt: {datetime.now().strftime('%H:%M')}\n\n"
            f"Ajoyib! Davom eting!"
        )
    elif action == "missed":
        await callback.message.edit_text(
            f"❌ **Vazifa bajarilmadi**\n\n"
            f"Keyingi safar albatta bajaring!\n"
            f"Sababini yozing (ixtiyoriy):"
        )

    await callback.answer()
