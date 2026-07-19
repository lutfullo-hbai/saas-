"""Referral bot handler — /refer buyrug'i, referral link yaratish."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select

from src.config.logging import get_logger
from src.infrastructure.db.models.referral import ReferralModel
from src.infrastructure.db.models.user import UserModel
from src.infrastructure.db.session import async_session_factory

logger = get_logger(__name__)

router = Router()


@router.message(Command("refer"))
async def cmd_refer(message: Message) -> None:
    """Referral link olish va do'stlarni taklif qilish."""
    telegram_id = str(message.from_user.id)

    async with async_session_factory() as session:
        # Foydalanuvchini topish
        result = await session.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            await message.answer(
                "❌ Siz hali ro'yxatdan o'tmaganiz.\n" "Avval /start buyrug'ini bosing."
            )
            return

        # Referral kodini olish yoki yaratish
        ref_result = await session.execute(
            select(ReferralModel).where(ReferralModel.referrer_id == user.id)
        )
        referral = ref_result.scalar_one_or_none()

        if not referral:
            import secrets

            code = secrets.token_urlsafe(8)
            referral = ReferralModel(
                referrer_id=user.id,
                code=code,
                status="active",
            )
            session.add(referral)
            await session.commit()
            logger.info("referral_code_created", user_id=str(user.id), code=code)

        # Referral linkni yaratish
        bot_username = (await message.bot.get_me()).username
        referral_link = f"https://t.me/{bot_username}?start={referral.code}"

        # Statistika
        from sqlalchemy import func

        count_result = await session.execute(
            select(func.count(ReferralModel.id)).where(
                ReferralModel.referrer_id == user.id,
                ReferralModel.referred_id.isnot(None),
            )
        )
        uses_count = count_result.scalar() or 0

    # Xabar yuborish
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📤 Referral linkni ulashish",
        url=referral_link,
    )
    builder.adjust(1)

    await message.answer(
        f"🔗 **Sizning referral linkingiz**\n\n"
        f"📝 Kod: `{referral.code}`\n"
        f"🔗 Link: {referral_link}\n\n"
        f"📊 Statistika:\n"
        f"• Ishlatilgan: {uses_count}/10 marta\n"
        f"• Qolgan: {10 - uses_count} ta joy\n\n"
        f"💡 **Qanday ishlaydi?**\n"
        f"1. Do'stingizga shu linkni yuboring\n"
        f"2. U /start buyrug'ini bossin\n"
        f"3. Siz 10 tagacha do'stni taklif qila olasiz\n"
        f"4. Har bir taklif qilingan do'st uchun bonus berasiz!\n\n"
        f"⚠️ Maksimal 10 ta referral. Kod: `{referral.code}`",
        reply_markup=builder.as_markup(),
    )


@router.message(Command("referstats"))
async def cmd_refer_stats(message: Message) -> None:
    """Referral statistikasini ko'rish."""
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

        # Referral kodini topish
        ref_result = await session.execute(
            select(ReferralModel).where(ReferralModel.referrer_id == user.id)
        )
        referral = ref_result.scalar_one_or_none()

        if not referral:
            await message.answer(
                "📊 **Referral statistikasi**\n\n"
                "Siz hali referral link yaratmaganiz.\n"
                "/refer buyrug'ini bosib, referral link oling!"
            )
            return

        # Ishlatilgan sonini hisoblash
        from sqlalchemy import func

        count_result = await session.execute(
            select(func.count(ReferralModel.id)).where(
                ReferralModel.referrer_id == user.id,
                ReferralModel.referred_id.isnot(None),
            )
        )
        uses_count = count_result.scalar() or 0

    await message.answer(
        f"📊 **Referral statistikasi**\n\n"
        f"🔗 Kod: `{referral.code}`\n"
        f"✅ Ishlatilgan: {uses_count}/10 marta\n"
        f"⏳ Qolgan: {10 - uses_count} ta joy\n"
        f"📅 Yaratilgan: {referral.created_at.strftime('%d.%m.%Y') if referral.created_at else 'Noma\'lum'}\n\n"
        f"💡 Linkni do'stlaringizga yuboring!\n"
        f"/refer — linkni olish"
    )
