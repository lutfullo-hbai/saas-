"""Goal creation handler with FSM."""

from datetime import date
from uuid import UUID

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select

from src.application.use_cases.create_goal import CreateGoalUseCase
from src.infrastructure.db.models.user import UserModel
from src.infrastructure.db.repositories.goal_repository import PostgresGoalRepository
from src.infrastructure.db.session import async_session_factory
from src.infrastructure.telegram.states.goal_states import GoalCreationStates

router = Router()


@router.message(Command("newgoal"))
async def cmd_newgoal(message: Message, state: FSMContext) -> None:
    """Yangi maqsad qo'shish — boshlash."""
    await state.set_state(GoalCreationStates.waiting_for_title)
    await message.answer(
        "🎯 **Yangi maqsad qo'shish**\n\n"
        "Maqsadingiz nima? (masalan: 'Ingliz tilini B2 darajasiga o'rganaman')"
    )


@router.message(GoalCreationStates.waiting_for_title)
async def process_title(message: Message, state: FSMContext) -> None:
    """Maqsad sarlavhasini qabul qilish."""
    title = message.text.strip()
    if len(title) < 3:
        await message.answer("Sarlavha juda qisqa. Kamida 3 ta belgi kiriting.")
        return

    await state.update_data(title=title)
    await state.set_state(GoalCreationStates.waiting_for_description)
    await message.answer(
        f"✅ Maqsad: **{title}**\n\n"
        "Endi maqsadning batafsil tavsifini yozing.\n"
        "Yoki /skip buyrug'i bilan o'tkazib yuboring."
    )


@router.message(Command("skip"), GoalCreationStates.waiting_for_description)
async def skip_description(message: Message, state: FSMContext) -> None:
    """Tavsifni o'tkazib yuborish."""
    await state.update_data(description="")
    await state.set_state(GoalCreationStates.waiting_for_target_date)
    await message.answer(
        "📅 Maqsadning bajarilish muddatini kiriting.\n"
        "Format: YYYY-MM-DD (masalan: 2026-12-31)\n"
        "Yoki /skip buyrug'i bilan o'tkazib yuboring."
    )


@router.message(GoalCreationStates.waiting_for_description)
async def process_description(message: Message, state: FSMContext) -> None:
    """Tavsifni qabul qilish."""
    description = message.text.strip()
    await state.update_data(description=description)
    await state.set_state(GoalCreationStates.waiting_for_target_date)
    await message.answer(
        "📅 Maqsadning bajarilish muddatini kiriting.\n"
        "Format: YYYY-MM-DD (masalan: 2026-12-31)\n"
        "Yoki /skip buyrug'i bilan o'tkazib yuboring."
    )


@router.message(Command("skip"), GoalCreationStates.waiting_for_target_date)
async def skip_target_date(message: Message, state: FSMContext) -> None:
    """Muddatni o'tkazib yuborish."""
    await state.update_data(target_date=None)
    data = await state.get_data()
    await _confirm_goal(message, data, state)


@router.message(GoalCreationStates.waiting_for_target_date)
async def process_target_date(message: Message, state: FSMContext) -> None:
    """Muddatni qabul qilish."""
    try:
        target_date = date.fromisoformat(message.text.strip())
        if target_date < date.today():
            await message.answer(
                "Muddat o'tmishda bo'lishi mumkin emas. "
                "Yangi sana kiriting yoki /skip bilan o'tkazib yuboring."
            )
            return
        await state.update_data(target_date=target_date.isoformat())
    except ValueError:
        await message.answer(
            "Noto'g'ri format. YYYY-MM-DD kiriting "
            "(masalan: 2026-12-31) yoki /skip bilan o'tkazib yuboring."
        )
        return

    data = await state.get_data()
    await _confirm_goal(message, data, state)


async def _confirm_goal(message: Message, data: dict, state: FSMContext) -> None:
    """Maqsadni tasdiqlash."""
    title = data.get("title", "")
    description = data.get("description", "")
    target_date = data.get("target_date")

    text = "🎯 **Maqsadni tasdiqlang**\n\n"
    text += f"**Sarlavha:** {title}\n"
    if description:
        text += f"**Tavsif:** {description}\n"
    if target_date:
        text += f"**Muddat:** {target_date}\n"

    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Tasdiqlash", callback_data="goal_confirm_yes")
    builder.button(text="❌ Bekor qilish", callback_data="goal_confirm_no")
    builder.adjust(2)

    await state.set_state(GoalCreationStates.confirmation)
    await message.answer(text, reply_markup=builder.as_markup())


async def _get_or_create_user(telegram_id: str, name: str) -> UUID:
    """Foydalanuvchini DB'dan olish yoki yaratish."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            user = UserModel(telegram_id=telegram_id, name=name)
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user.id


@router.callback_query(
    GoalCreationStates.confirmation, lambda c: c.data == "goal_confirm_yes"
)
async def confirm_goal_yes(callback: CallbackQuery, state: FSMContext) -> None:
    """Maqsad tasdiqlandi — DB'ga saqlanadi."""
    data = await state.get_data()
    title = data.get("title", "")
    description = data.get("description", "")
    target_date_str = data.get("target_date")

    telegram_id = str(callback.from_user.id)
    name = callback.from_user.first_name or "Foydalanuvchi"

    try:
        user_id = await _get_or_create_user(telegram_id, name)

        target_date = None
        if target_date_str:
            target_date = date.fromisoformat(target_date_str)

        async with async_session_factory() as session:
            goal_repo = PostgresGoalRepository(session)
            use_case = CreateGoalUseCase(goal_repo)
            goal = await use_case.execute(
                user_id=user_id,
                title=title,
                description=description or "",
                target_date=target_date,
            )

        await callback.message.edit_text(
            f"✅ **Maqsad yaratildi!**\n\n"
            f"🎯 {title}\n"
            f"📝 {description}\n"
            f"📅 {target_date_str or 'Muddatsiz'}\n\n"
            f"Endi /newgoal buyrug'i bilan boshqa maqsad qo'shishingiz mumkin."
        )
    except Exception as e:
        await callback.message.edit_text(
            f"❌ **Xatolik yuz berdi:** {str(e)}\n\n" "Qaytadan urinib ko'ring."
        )

    await state.clear()
    await callback.answer()


@router.callback_query(
    GoalCreationStates.confirmation, lambda c: c.data == "goal_confirm_no"
)
async def confirm_goal_no(callback: CallbackQuery, state: FSMContext) -> None:
    """Maqsad bekor qilindi."""
    await callback.message.edit_text("❌ Maqsad yaratish bekor qilindi.")
    await state.clear()
    await callback.answer()
