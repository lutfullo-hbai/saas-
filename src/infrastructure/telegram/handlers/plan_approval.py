"""Plan approval handler — AI rejani tasdiqlash/tahrirlash/tanqid qilish.

Foydalanuvchi AI tomonidan yaratilgan rejani ko'radi, tahrirlaydi
va tasdiqlaydi yoki rad etadi.
"""

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.config.logging import get_logger

logger = get_logger(__name__)

router = Router(name="plan_approval")


class PlanApprovalState(StatesGroup):
    """Reja tasdiqlash holatlari."""

    viewing_plan = State()
    editing_task = State()
    confirming_approve = State()


# Mock data — haqiqiy DB o'rniga
PLANS_APPROVAL = {
    "pending": [
        {
            "id": "plan_1",
            "goal": "Ingliz tilini B2 darajaga ko'tarish",
            "source": "ai",
            "tasks": [
                {"id": "t1", "title": "Kuniga 30 daqiqa vocabulary", "time": "09:00"},
                {"id": "t2", "title": "Grammar exercise (15 daqiqa)", "time": "10:00"},
                {
                    "id": "t3",
                    "title": "Listening practice (20 daqiqa)",
                    "time": "18:00",
                },
                {"id": "t4", "title": "Daily journaling (10 daqiqa)", "time": "21:00"},
            ],
        }
    ]
}


def _format_plan(plan: dict) -> str:
    """Rejani formatlash."""
    lines = [f"🎯 {plan['goal']}", ""]
    for i, task in enumerate(plan["tasks"], 1):
        lines.append(f"{i}. {task['title']} ⏰ {task['time']}")
    lines.append("")
    lines.append("Reja to'g'rimi?")
    return "\n".join(lines)


@router.callback_query(F.data == "plan_review")
async def review_pending_plan(callback: CallbackQuery, state: FSMContext) -> None:
    """AI rejasini ko'rish."""
    plans = PLANS_APPROVAL.get("pending", [])
    if not plans:
        await callback.answer("Tasdiqlash uchun reja yo'q.", show_alert=True)
        return

    plan = plans[0]
    await state.set_state(PlanApprovalState.viewing_plan)
    await state.update_data(plan_id=plan["id"])

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash", callback_data="plan_approve"
                ),
                InlineKeyboardButton(text="✏️ Tahrirlash", callback_data="plan_edit"),
            ],
            [
                InlineKeyboardButton(text="❌ Rad etish", callback_data="plan_reject"),
            ],
        ]
    )

    await callback.message.edit_text(
        _format_plan(plan),
        reply_markup=keyboard,
    )
    await callback.answer()


@router.callback_query(F.data == "plan_approve")
async def approve_plan(callback: CallbackQuery, state: FSMContext) -> None:
    """Rejani tasdiqlash."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    await state.set_state(PlanApprovalState.confirming_approve)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Ha, tasdiqlash", callback_data="plan_confirm_approve"
                ),
                InlineKeyboardButton(text="🔙 Ortga", callback_data="plan_review"),
            ],
        ]
    )

    await callback.message.edit_text(
        "Rejani tasdiqlaysizmi?\n\n"
        "Tasdiqlangandan keyin reja avtomatik ravishda "
        "bajarilishi boshlanadi.",
        reply_markup=keyboard,
    )
    await callback.answer()


@router.callback_query(F.data == "plan_confirm_approve")
async def confirm_approve(callback: CallbackQuery, state: FSMContext) -> None:
    """Tasdiqlashni tasdiqlash."""
    data = await state.get_data()
    plan_id = data.get("plan_id")

    # Haqiqiy kod: DB'da plan statusini yangilash
    logger.info("plan_approved", plan_id=plan_id, user_id=callback.from_user.id)

    await state.clear()
    await callback.message.edit_text(
        "✅ Reja tasdiqlandi!\n\n"
        "Endi har kuni vazifalar sizga yuboriladi.\n"
        "Muvaffaqiyatli bajarishlar tilaymiz!"
    )
    await callback.answer()


@router.callback_query(F.data == "plan_edit")
async def edit_plan(callback: CallbackQuery, state: FSMContext) -> None:
    """Rejani tahrirlash."""
    await state.set_state(PlanApprovalState.editing_task)

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📝 Vazifalarni tahrirlash",
                    callback_data="plan_edit_tasks",
                )
            ],
            [
                InlineKeyboardButton(
                    text="➕ Vazifa qo'shish",
                    callback_data="plan_add_task",
                )
            ],
            [
                InlineKeyboardButton(text="🔙 Ortga", callback_data="plan_review"),
            ],
        ]
    )

    await callback.message.edit_text(
        "Rejani tahrirlash:\n\n"
        "1. Vazifalarni tahrirlash — mavjud vazifalarni o'zgartirish\n"
        "2. Vazifa qo'shish — yangi vazifa qo'shish\n\n"
        "Qaysi amalni bajarasiz?",
        reply_markup=keyboard,
    )
    await callback.answer()


@router.callback_query(F.data == "plan_edit_tasks")
async def edit_tasks(callback: CallbackQuery, state: FSMContext) -> None:
    """Vazifalarni tahrirlash."""
    await callback.message.edit_text(
        "Qaysi vazifani tahrirlash kerak?\n\n"
        "Vazifa raqamini kiriting (masalan: 1)\n"
        "Yoki 'ortga' deb yozing."
    )
    await callback.answer()


@router.callback_query(F.data == "plan_reject")
async def reject_plan(callback: CallbackQuery, state: FSMContext) -> None:
    """Rejani rad etish."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 Yangi reja so'rash",
                    callback_data="generate_plan",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏠 Bosh menyu",
                    callback_data="main_menu",
                )
            ],
        ]
    )

    await callback.message.edit_text(
        "❌ Reja rad etildi.\n\n" "Yangi reja so'rashni xohlaysizmi?",
        reply_markup=keyboard,
    )
    await state.clear()
    await callback.answer()
