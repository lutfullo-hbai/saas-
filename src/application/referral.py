"""Referral application interface re-exports."""

from src.domain.entities.referral import Referral
from src.infrastructure.db.referral_service import ReferralService

__all__ = ["Referral", "ReferralService"]
