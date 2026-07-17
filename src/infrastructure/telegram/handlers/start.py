"""Start command handler."""

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Bot ishga tushganda /start buyrug'i."""
    user_name = message.from_user.first_name or "Foydalanuvchi"
    await message.answer(
        f"Salom, {user_name}! 👋\n\n"
        f"Men **Disipl** — shaxsiy nazorat botiman.\n\n"
        f"Men sizga maqsadlaringizni bajarishda yordam beraman:\n"
        f"• Maqsad qo'shish\n"
        f"• Kunlik eslatmalar yuborish\n"
        f"• Progressni kuzatish\n\n"
        f"Buyruqlar:\n"
        f"/newgoal — Yangi maqsad qo'shish\n"
        f"/goals — Maqsadlarni ko'rish\n"
        f"/progress — Progressni ko'rish\n"
        f"/help — Yordam",
    )
