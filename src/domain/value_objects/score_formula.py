"""ScoreFormula value object — Precision Scoring Engine."""

import math


def calculate_score(
    scheduled_time_minutes: float,
    checkin_time_minutes: float,
    tolerance_minutes: float,
    task_weight: float,
    decay_const: float = 0.05,
    early_bonus_rate: float = 0.01,
    bonus_cap: float = 0.15,
) -> float:
    """Ball hisoblash formulasi.

    Args:
        scheduled_time_minutes: Vazifa uchun belgilangan vaqt (daqiqada).
        checkin_time_minutes: Foydalanuvchi tasdiqlagan vaqt (daqiqada).
        tolerance_minutes: Tolerantlik oralig'i (daqiqa).
        task_weight: Vazifaning og'irligi (0.0-1.0).
        decay_const: Eksponensial pasayish doirasi.
        early_bonus_rate: Erta bajarish bonusi stavkasi.
        bonus_cap: Maksimal bonus chegarasi.

    Returns:
        Hisoblangan ball (0.0 - task_weight).
    """
    delta_minutes = checkin_time_minutes - scheduled_time_minutes

    if abs(delta_minutes) <= tolerance_minutes:
        # O'z vaqtida — to'liq ball
        return 1.0 * task_weight

    elif delta_minutes > tolerance_minutes:
        # Kech qolgan — eksponensial jazo
        lateness = delta_minutes - tolerance_minutes
        penalty = 1 - math.exp(-decay_const * lateness)
        return max(0.0, (1 - penalty)) * task_weight

    else:
        # Erta bajargan — tolerance dan tashqari qismi bonus oladi
        earliness = abs(delta_minutes) - tolerance_minutes
        bonus = min(bonus_cap, earliness * early_bonus_rate)
        return (1.0 + bonus) * task_weight
