"""Feedback handler for Telegram bot."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.infrastructure.telegram.states.feedback import FeedbackStates

router = Router()


@router.message(Command("feedback"))
async def cmd_feedback(message: Message, state: FSMContext) -> None:
    """Feedback yuborish."""
    await state.set_state(FeedbackStates.waiting_for_type)
    await message.answer(
        "📝 **Feedback yuborish**\n\n"
        "Qanday turdagi feedback?",
        reply_markup=_get_feedback_type_keyboard(),
    )


def _get_feedback_type_keyboard():
    """Feedback turini tanlash klaviaturasi."""
    builder = InlineKeyboardBuilder()
    builder.button(text="💡 Taklif", callback_data="fb_type_suggestion")
    builder.button(text="🐛 Xato", callback_data="fb_type_bug")
    builder.button(text="👍 Ijobiy", callback_data="fb_type_positive")
    builder.button(text="💬 Boshqa", callback_data="fb_type_other")
    builder.adjust(2)
    return builder


@router.callback_query(FeedbackStates.waiting_for_type)
async def process_feedback_type(callback, state: FSMContext) -> None:
    """Feedback turini qabul qilish."""
    feedback_type = callback.data.replace("fb_type_", "")

    type_names = {
        "suggestion": "Taklif",
        "bug": "Xato",
        "positive": "Ijobiy",
        "other": "Boshqa",
    }

    await state.update_data(feedback_type=feedback_type)
    await callback.message.edit_text(
        f"Tur: **{type_names.get(feedback_type, 'Noma\'lum')}**\n\n"
        "Feedbackingizni yozing:"
    )
    await state.set_state(FeedbackStates.waiting_for_content)


@router.message(FeedbackStates.waiting_for_content)
async def process_feedback_content(message: Message, state: FSMContext) -> None:
    """Feedback kontentini qabul qilish."""
    content = message.text.strip()

    if len(content) < 10:
        await message.answer("Feedback juda qisqa. Kamida 10 ta belgi yozing.")
        return

    if len(content) > 1000:
        await message.answer("Feedback juda uzun. Maksimal 1000 ta belgi.")
        return

    data = await state.get_data()
    feedback_type = data.get("feedback_type", "other")

    # Feedbackni saqlash (placeholder)
    await message.answer(
        "✅ **Rahmat!** Feedbackingiz qabul qilindi.\n\n"
        "Sizning fikringiz biz uchun muhim. "
        "Agar qo'shimcha ma'lumot kerak bo'lsa, siz bilan bog'lanamiz."
    )
    await state.clear()


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    """Bot statistikasi (admin uchun)."""
    # Placeholder - haqiqiy DB so'rovi
    await message.answer(
        "📊 **Bot Statistikasi**\n\n"
        "👥 Foydalanuvchilar: 150\n"
        "🎯 Maqsadlar: 450\n"
        "✅ Check-inlar: 3,200\n"
        "📈 Faollik: 85%\n\n"
        "Beta guruh: 18/20 ishtirokchi"
    )
