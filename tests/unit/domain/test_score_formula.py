"""ScoreFormula value object testlari."""

from src.domain.value_objects.score_formula import calculate_score


class TestScoreFormula:
    """Precision Scoring Engine formulasi testlari."""

    def test_on_time_gives_full_score(self):
        """O'z vaqtida bajarilgan vazifa — to'liq ball."""
        result = calculate_score(
            scheduled_time_minutes=870.0,  # 14:30
            checkin_time_minutes=872.0,  # 14:32
            tolerance_minutes=10.0,
            task_weight=1.0,
        )
        assert result == 1.0

    def test_within_tolerance_gives_full_score(self):
        """Tolerantlik ichida — to'liq ball."""
        result = calculate_score(
            scheduled_time_minutes=870.0,
            checkin_time_minutes=875.0,  # 5 daqiqa kech
            tolerance_minutes=10.0,
            task_weight=1.0,
        )
        assert result == 1.0

    def test_late_beyond_tolerance_decays(self):
        """Kech qolgan — ball pasayadi."""
        result = calculate_score(
            scheduled_time_minutes=870.0,
            checkin_time_minutes=990.0,  # 2 soat kech
            tolerance_minutes=10.0,
            task_weight=1.0,
        )
        assert 0 < result < 0.5

    def test_very_late_gives_near_zero(self):
        """Juda kech qolgan — deyarli nol."""
        result = calculate_score(
            scheduled_time_minutes=870.0,
            checkin_time_minutes=1200.0,  # 5.5 soat kech
            tolerance_minutes=10.0,
            task_weight=1.0,
        )
        assert result < 0.1

    def test_early_bonus(self):
        """Erta bajarilgan — kichik bonus (tolerance dan tashqari)."""
        result_on_time = calculate_score(
            scheduled_time_minutes=870.0,
            checkin_time_minutes=870.0,
            tolerance_minutes=10.0,
            task_weight=1.0,
        )
        result_early = calculate_score(
            scheduled_time_minutes=870.0,
            checkin_time_minutes=850.0,  # 20 daqiqa erta (tolerance 10)
            tolerance_minutes=10.0,
            task_weight=1.0,
        )
        assert result_early > result_on_time
        assert result_early <= 1.15  # bonus_cap = 0.15

    def test_task_weight_affects_score(self):
        """Vazifa og'irligi ballga ta'sir qiladi."""
        result_heavy = calculate_score(
            scheduled_time_minutes=870.0,
            checkin_time_minutes=870.0,
            tolerance_minutes=10.0,
            task_weight=1.0,
        )
        result_light = calculate_score(
            scheduled_time_minutes=870.0,
            checkin_time_minutes=870.0,
            tolerance_minutes=10.0,
            task_weight=0.3,
        )
        assert result_heavy > result_light
        assert result_light == 0.3
