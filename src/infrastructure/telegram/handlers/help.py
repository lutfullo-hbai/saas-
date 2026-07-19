"""Help command handler."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Yordam buyrug'i."""
    await message.answer(
        "📋 **Disipl — Buyruqlar ro'yxati**\n\n"
        "/start — Botni ishga tushirish\n"
        "/newgoal — Yangi maqsad qo'shish\n"
        "/goals — Maqsadlarni ko'rish\n"
        "/progress — Progressni ko'rish\n"
        "/help — Shu yordam\n\n"
        "💡 Maqsad qo'shish uchun /newgoal buyrug'ini yuboring."
    )
