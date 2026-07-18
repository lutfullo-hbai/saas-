"""Referral and invite mechanism."""

import logging
import secrets
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Referral:
    """Referral ma'lumotlari."""
    code: str
    user_id: int
    created_at: datetime
    uses: int = 0
    max_uses: int = 10


class ReferralService:
    """Referral xizmati."""

    def __init__(self):
        self.referrals: dict[str, Referral] = {}
        self.user_referrals: dict[int, str] = {}

    def generate_code(self, user_id: int) -> str:
        """Referral kodi generatsiya qilish."""
        if user_id in self.user_referrals:
            return self.user_referrals[user_id]

        code = secrets.token_urlsafe(8)
        referral = Referral(
            code=code,
            user_id=user_id,
            created_at=datetime.now(),
        )

        self.referrals[code] = referral
        self.user_referrals[user_id] = code

        logger.info(f"Referral code generated for user {user_id}: {code}")
        return code

    def use_code(self, code: str, new_user_id: int) -> bool:
        """Referral kodini ishlatish."""
        if code not in self.referrals:
            logger.warning(f"Invalid referral code: {code}")
            return False

        referral = self.referrals[code]

        if referral.uses >= referral.max_uses:
            logger.warning(f"Referral code {code} reached max uses")
            return False

        if referral.user_id == new_user_id:
            logger.warning("User cannot use their own referral code")
            return False

        referral.uses += 1
        logger.info(f"Referral code {code} used by user {new_user_id}")
        return True

    def get_referral_stats(self, user_id: int) -> dict:
        """Referral statistikasini olish."""
        code = self.user_referrals.get(user_id)
        if not code:
            return {"code": None, "uses": 0, "max_uses": 0}

        referral = self.referrals[code]
        return {
            "code": referral.code,
            "uses": referral.uses,
            "max_uses": referral.max_uses,
            "created_at": referral.created_at.isoformat(),
        }

    def get_referral_link(self, user_id: int) -> str | None:
        """Referral havolasini olish."""
        code = self.user_referrals.get(user_id)
        if not code:
            return None

        return f"https://t.me/disipl_bot?start={code}"


referral_service = ReferralService()
