"""Referral and invite domain models and re-exports."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Referral:
    """Referral ma'lumotlari."""

    code: str
    referrer_id: UUID
    created_at: datetime
    uses: int = 0
    max_uses: int = 10


from src.infrastructure.db.referral_service import ReferralService  # noqa: E402

__all__ = ["Referral", "ReferralService"]
