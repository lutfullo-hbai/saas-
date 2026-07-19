"""Unit tests for application limits."""

from src.application.limits import SubscriptionTier, UserLimits


class TestUserLimits:
    """UserLimits sinfi testlari."""

    def test_free_tier_can_create_up_to_3_goals(self):
        """FREE tier — 3tagacha maqsad yaratish mumkin."""
        limits = UserLimits(user_id=1, tier=SubscriptionTier.FREE)
        assert limits.can_create_goal(0) is True
        assert limits.can_create_goal(1) is True
        assert limits.can_create_goal(2) is True
        assert limits.can_create_goal(3) is False

    def test_pro_tier_can_create_up_to_50_goals(self):
        """PRO tier — 50tagacha maqsad."""
        limits = UserLimits(user_id=1, tier=SubscriptionTier.PRO)
        assert limits.can_create_goal(49) is True
        assert limits.can_create_goal(50) is False

    def test_free_tier_task_limit_per_goal(self):
        """FREE tier — har bir maqsad uchun 5 ta vazifa."""
        limits = UserLimits(user_id=1, tier=SubscriptionTier.FREE)
        assert limits.can_create_task(4) is True
        assert limits.can_create_task(5) is False

    def test_pro_tier_task_limit_per_goal(self):
        """PRO tier — 20 ta vazifa."""
        limits = UserLimits(user_id=1, tier=SubscriptionTier.PRO)
        assert limits.can_create_task(19) is True
        assert limits.can_create_task(20) is False

    def test_free_tier_checkin_limit(self):
        """FREE tier — kuniga 10 ta check-in."""
        limits = UserLimits(user_id=1, tier=SubscriptionTier.FREE)
        assert limits.can_checkin(9) is True
        assert limits.can_checkin(10) is False

    def test_pro_tier_checkin_limit(self):
        """PRO tier — kuniga 100 ta check-in."""
        limits = UserLimits(user_id=1, tier=SubscriptionTier.PRO)
        assert limits.can_checkin(99) is True
        assert limits.can_checkin(100) is False

    def test_free_tier_llm_limit(self):
        """FREE tier — kuniga 3 ta LLM so'rov."""
        limits = UserLimits(user_id=1, tier=SubscriptionTier.FREE)
        assert limits.can_use_llm(2) is True
        assert limits.can_use_llm(3) is False

    def test_pro_tier_llm_limit(self):
        """PRO tier — kuniga 100 ta LLM so'rov."""
        limits = UserLimits(user_id=1, tier=SubscriptionTier.PRO)
        assert limits.can_use_llm(99) is True
        assert limits.can_use_llm(100) is False

    def test_get_upgrade_message_free(self):
        """FREE tier uchun upgrade xabari."""
        limits = UserLimits(user_id=1, tier=SubscriptionTier.FREE)
        msg = limits.get_upgrade_message()
        assert "Pro" in msg

    def test_get_usage_stats(self):
        """Foydalanish statistikasini olish."""
        limits = UserLimits(user_id=1, tier=SubscriptionTier.FREE)
        stats = limits.get_usage_stats({"goals": 2})
        assert "goals" in stats
        assert stats["goals"]["used"] == 2
        assert stats["goals"]["limit"] == 3
