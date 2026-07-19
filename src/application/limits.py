"""User limits and tier management."""

from dataclasses import dataclass
from enum import Enum

from src.config.logging import get_logger

logger = get_logger(__name__)


class SubscriptionTier(Enum):
    """Obuna darajasi."""

    FREE = "free"
    PRO = "pro"


@dataclass
class TierLimits:
    """Har bir daraja uchun cheklovlar."""

    max_goals: int
    max_tasks_per_goal: int
    max_checkins_per_day: int
    llm_requests_per_day: int
    insights_per_week: int
    priority_support: bool


TIER_LIMITS = {
    SubscriptionTier.FREE: TierLimits(
        max_goals=3,
        max_tasks_per_goal=5,
        max_checkins_per_day=10,
        llm_requests_per_day=3,
        insights_per_week=1,
        priority_support=False,
    ),
    SubscriptionTier.PRO: TierLimits(
        max_goals=50,
        max_tasks_per_goal=20,
        max_checkins_per_day=100,
        llm_requests_per_day=100,
        insights_per_week=52,
        priority_support=True,
    ),
}


class UserLimits:
    """Foydalanuvchi limitlarini boshqarish."""

    def __init__(self, user_id: int, tier: SubscriptionTier = SubscriptionTier.FREE):
        self.user_id = user_id
        self.tier = tier
        self.limits = TIER_LIMITS[tier]

    def can_create_goal(self, current_goals: int) -> bool:
        """Maqsad qo'shish mumkinligini tekshirish."""
        if current_goals >= self.limits.max_goals:
            logger.warning(
                f"User {self.user_id} reached goal limit: "
                f"{current_goals}/{self.limits.max_goals}"
            )
            return False
        return True

    def can_create_task(self, current_tasks: int) -> bool:
        """Vazifa qo'shish mumkinligini tekshirish."""
        if current_tasks >= self.limits.max_tasks_per_goal:
            logger.warning(
                f"User {self.user_id} reached task limit: "
                f"{current_tasks}/{self.limits.max_tasks_per_goal}"
            )
            return False
        return True

    def can_checkin(self, today_checkins: int) -> bool:
        """Check-in qilish mumkinligini tekshirish."""
        if today_checkins >= self.limits.max_checkins_per_day:
            logger.warning(
                f"User {self.user_id} reached checkin limit: "
                f"{today_checkins}/{self.limits.max_checkins_per_day}"
            )
            return False
        return True

    def can_use_llm(self, today_requests: int) -> bool:
        """LLM ishlatish mumkinligini tekshirish."""
        if today_requests >= self.limits.llm_requests_per_day:
            logger.warning(
                f"User {self.user_id} reached LLM limit: "
                f"{today_requests}/{self.limits.llm_requests_per_day}"
            )
            return False
        return True

    def get_usage_stats(self, usage: dict) -> dict:
        """Foydalanuvchi statistikasini olish."""
        return {
            "tier": self.tier.value,
            "goals": {
                "used": usage.get("goals", 0),
                "limit": self.limits.max_goals,
            },
            "tasks_per_goal": {
                "used": usage.get("tasks", 0),
                "limit": self.limits.max_tasks_per_goal,
            },
            "checkins_today": {
                "used": usage.get("checkins", 0),
                "limit": self.limits.max_checkins_per_day,
            },
            "llm_today": {
                "used": usage.get("llm_requests", 0),
                "limit": self.limits.llm_requests_per_day,
            },
        }

    def get_upgrade_message(self) -> str:
        """Obuna yangilash xabarini olish."""
        return (
            "🚫 Chegirib qo'yildi!\n\n"
            f"Sizning {self.tier.value} darajangiz uchun limit:\n"
            f"• Maqsadlar: {self.limits.max_goals} ta\n"
            f"• Vazifalar: {self.limits.max_tasks_per_goal} ta\n"
            f"• Check-inlar: {self.limits.max_checkins_per_day} ta/kun\n\n"
            "Pro'ga o'tish uchun /upgrade buyrug'ini bosing!"
        )
