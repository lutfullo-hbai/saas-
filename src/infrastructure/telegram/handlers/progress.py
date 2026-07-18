"""Progress command handler."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("progress"))
async def cmd_progress(message: Message) -> None:
    """Foydalanuvchi progressini ko'rsatish."""
    user_name = message.from_user.first_name or "Foydalanuvchi"

    await message.answer(
        f"📊 **{user_name} — Progress**\n\n"
        f"🎯 **Maqsadlar:** 3 ta (2 faol, 1 bajarilgan)\n\n"
        f"📈 **Umumiy ball:** 87.5%\n"
        f"✅ **Bajarilgan:** 15/20 vazifa\n"
        f"❌ **Bajarilmagan:** 5/20 vazifa\n\n"
        f"📅 **Bu hafta:**\n"
        f"Dushanba: ✅ 3/3 — 100%\n"
        f"Seshanba: ✅ 2/3 — 67%\n"
        f"Chorshanba: ✅ 3/3 — 100%\n"
        f"Payshanba: ❌ 1/3 — 33%\n"
        f"Juma: ✅ 3/3 — 100%\n"
        f"Shanba: ⏳ Kutilmoqda\n"
        f"Yakshanba: ⏳ Kutilmoqda\n\n"
        f"💡 **Tavsiya:** Payshanba kuni kamroq bajarilgan. "
        f"Nima sabab bo'lishi mumkin?"
    )
