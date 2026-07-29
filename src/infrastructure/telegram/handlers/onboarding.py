"""Onboarding flow for new users."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select

from src.infrastructure.db.models.user import UserModel
from src.infrastructure.db.session import async_session_factory
from src.infrastructure.telegram.states.onboarding import OnboardingStates

router = Router()


@router.message(Command("onboarding"))
async def cmd_onboarding(message: Message, state: FSMContext) -> None:
    """Onboarding boshlash."""
    telegram_id = str(message.from_user.id)

    async with async_session_factory() as session:
        result = await session.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        existing = result.scalar_one_or_none()
        if existing:
            await message.answer(
                f"👋 Siz allaqachon ro'yxatdan o'tgansiz, {existing.name}!\n\n"
                "Maqsad qo'shish uchun /newgoal buyrug'ini bosing."
            )
            return

    await state.set_state(OnboardingStates.welcome)
    await message.answer(
        "👋 **Disipl'ga xush kelibsiz!**\n\n"
        "Men sizning shaxsiy discipline coach'ingizman.\n"
        "Keling, birga boshlaylik!\n\n"
        "Avval, ismingiz nima?"
    )


@router.message(OnboardingStates.welcome)
async def process_name(message: Message, state: FSMContext) -> None:
    """Ismni qabul qilish."""
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("Ism juda qisqa. Kamida 2 ta belgi kiriting.")
        return

    await state.update_data(name=name)
    await state.set_state(OnboardingStates.goal_selection)
    await message.answer(
        f"Tanishganligimdan xursandman, {name}! 🎉\n\n"
        "Endi sizning maqsadlaringizni bilib olay.\n"
        "Qaysi sohada o'z yo'nalishingizni belgilamoqchisiz?",
        reply_markup=_get_goal_keyboard(),
    )


def _get_goal_keyboard() -> InlineKeyboardBuilder:
    """Maqsad tanlash klaviaturasi."""
    builder = InlineKeyboardBuilder()
    builder.button(text="📚 Ta'lim", callback_data="onb_goal_education")
    builder.button(text="🏃 Sog'lomlik", callback_data="onb_goal_health")
    builder.button(text="💼 Kasbiy", callback_data="onb_goal_career")
    builder.button(text="🎨 Ijodiy", callback_data="onb_goal_creative")
    builder.button(text="💰 Moliyaviy", callback_data="onb_goal_financial")
    builder.button(text="➡️ O'tkazib yuborish", callback_data="onb_skip")
    builder.adjust(2)
    return builder


@router.callback_query(OnboardingStates.goal_selection)
async def process_goal_selection(callback: CallbackQuery, state: FSMContext) -> None:
    """Maqsad tanlash."""
    goal = callback.data.replace("onb_goal_", "")

    goal_names = {
        "education": "Ta'lim",
        "health": "Sog'lomlik",
        "career": "Kasbiy",
        "creative": "Ijodiy",
        "financial": "Moliyaviy",
    }

    selected = goal_names.get(goal, "Umumiy")
    await state.update_data(goal_category=goal)

    await callback.message.edit_text(
        f"✅ Tanlandi: **{selected}**\n\n"
        "Endi birinchi maqsadingizni kiriting.\n"
        "Masalan: 'Ingliz tilini B2 darajasiga o'rganaman'"
    )
    await state.set_state(OnboardingStates.first_goal)


@router.callback_query(OnboardingStates.goal_selection, lambda c: c.data == "onb_skip")
async def skip_goal(callback: CallbackQuery, state: FSMContext) -> None:
    """Maqsad tanlashni o'tkazib yuborish."""
    await callback.message.edit_text(
        "O'tkazib yuborildi. Keyinroq /newgoal buyrug'i bilan maqsad qo'shishingiz mumkin."
    )
    await _finish_onboarding(callback, state)


@router.message(OnboardingStates.first_goal)
async def process_first_goal(message: Message, state: FSMContext) -> None:
    """Birinchi maqsadni qabul qilish."""
    goal = message.text.strip()
    if len(goal) < 5:
        await message.answer("Maqsad juda qisqa. Batafsil yozing.")
        return

    await state.update_data(first_goal=goal)
    await _finish_onboarding(message, state)


async def _finish_onboarding(
    message: Message | CallbackQuery, state: FSMContext
) -> None:
    """Onboarding yakunlash — foydalanuvchini DB ga saqlash."""
    data = await state.get_data()
    name = data.get("name", "Foydalanuvchi")

    if isinstance(message, Message):
        telegram_id = str(message.from_user.id)
    else:
        telegram_id = str(message.from_user.id)

    async with async_session_factory() as session:
        result = await session.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        existing = result.scalar_one_or_none()

        if not existing:
            user = UserModel(
                telegram_id=telegram_id,
                name=name,
                email=f"tg_{telegram_id}@placeholder.local",
                timezone="UTC",
            )
            session.add(user)
            await session.commit()

    builder = InlineKeyboardBuilder()
    builder.button(text="🎯 Maqsad qo'shish", callback_data="newgoal")
    builder.button(text="📊 Progress ko'rish", callback_data="progress")
    builder.adjust(2)

    if isinstance(message, Message):
        await message.answer(
            f"🎉 **Tabriklaymiz, {name}!**\n\n"
            "Siz muvaffaqiyatli ro'yxatdan o'tdingiz!\n\n"
            "Endi siz:\n"
            "• Maqsadlaringizni qo'sha olasiz\n"
            "• Kunlik vazifalarni bajara olasiz\n"
            "• Progresslaringizni kuzata olasiz\n\n"
            "Boshlash uchun tugmalardan birini bosing:",
            reply_markup=builder.as_markup(),
        )
    else:
        await message.message.edit_text(
            f"🎉 **Tabriklaymiz, {name}!**\n\n"
            "Siz muvaffaqiyatli ro'yxatdan o'tdingiz!\n\n"
            "Endi siz:\n"
            "• Maqsadlaringizni qo'sha olasiz\n"
            "• Kunlik vazifalarni bajara olasiz\n"
            "• Progresslaringizni kuzata olasiz\n\n"
            "Boshlash uchun tugmalardan birini bosing:",
            reply_markup=builder.as_markup(),
        )

    await state.clear()
