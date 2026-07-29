"""Referral service infrastructure implementation."""

import secrets
from datetime import datetime
from uuid import UUID

from src.utils.datetime_utils import utc_now

from sqlalchemy import func, select

from src.config.logging import get_logger
from src.infrastructure.db.models.referral import ReferralModel

logger = get_logger(__name__)


class ReferralService:
    """Referral xizmati — DB bilan."""

    def __init__(self, session=None):
        self._session = session

    async def generate_code(self, user_id: UUID) -> str:
        """Referral kodi generatsiya qilish."""
        if not self._session:
            return secrets.token_urlsafe(8)

        existing = await self._session.execute(
            select(ReferralModel).where(ReferralModel.referrer_id == user_id)
        )
        existing_referral = existing.scalar_one_or_none()

        if existing_referral:
            return existing_referral.code

        code = secrets.token_urlsafe(8)
        referral = ReferralModel(
            referrer_id=user_id,
            code=code,
            status="active",
        )
        self._session.add(referral)
        await self._session.flush()

        logger.info(f"Referral code generated for user {user_id}: {code}")
        return code

    async def use_code(self, code: str, new_user_id: UUID) -> bool:
        """Referral kodini ishlatish."""
        if not self._session:
            return False

        result = await self._session.execute(
            select(ReferralModel).where(ReferralModel.code == code)
        )
        referral = result.scalar_one_or_none()

        if not referral:
            logger.warning(f"Invalid referral code: {code}")
            return False

        if referral.referrer_id == new_user_id:
            logger.warning("User cannot use their own referral code")
            return False

        count_result = await self._session.execute(
            select(func.count())
            .select_from(ReferralModel)
            .where(
                ReferralModel.referrer_id == referral.referrer_id,
                ReferralModel.referred_id.isnot(None),
            )
        )
        uses_count = count_result.scalar() or 0

        if uses_count >= 10:
            logger.warning(f"Referral code {code} reached max uses")
            return False

        referral.referred_id = new_user_id
        referral.used_at = utc_now()
        await self._session.flush()

        logger.info(f"Referral code {code} used by user {new_user_id}")
        return True

    async def get_referral_stats(self, user_id: UUID) -> dict:
        """Referral statistikasini olish."""
        if not self._session:
            return {"code": None, "uses": 0, "max_uses": 0}

        result = await self._session.execute(
            select(ReferralModel).where(ReferralModel.referrer_id == user_id)
        )
        referral = result.scalar_one_or_none()

        if not referral:
            return {"code": None, "uses": 0, "max_uses": 0}

        count_result = await self._session.execute(
            select(func.count())
            .select_from(ReferralModel)
            .where(
                ReferralModel.referrer_id == user_id,
                ReferralModel.referred_id.isnot(None),
            )
        )
        uses_count = count_result.scalar() or 0

        return {
            "code": referral.code,
            "uses": uses_count,
            "max_uses": 10,
            "created_at": referral.created_at.isoformat(),
        }

    async def get_referral_link(self, user_id: UUID) -> str | None:
        """Referral havolasini olish."""
        code = await self.generate_code(user_id)
        if not code:
            return None

        return f"https://t.me/disipl_bot?start={code}"
