"""Weekly insight generation use case — LLM orqali haftalik tahlil."""

import logging
from dataclasses import dataclass

from src.application.interfaces.llm import ILLMProvider

logger = logging.getLogger(__name__)


@dataclass
class WeeklyInsight:
    """Haftalik insight."""

    summary: str
    weak_days: list[str]
    weak_tasks: list[str]
    recommendation: str
    question: str
    tokens_used: int
    cost_usd: float


INSIGHT_PROMPT_TEMPLATE = """
Foydalanuvchining haftalik ma'lumotlari:

Maqsadlar: {goals_count} ta ({active_goals} faol, {completed_goals} bajarilgan)
Umumiy ball: {overall_score}%
Bajarilgan: {completed_tasks}/{total_tasks} vazifa

Haftalik breakdown:
{weekly_breakdown}

Tahlil qil va quyidagi formatda javob ber:
1. Qaysi kunlar/vazifalar eng ko'p muvaffaqiyatsiz bo'lgan?
2. Nima uchun bo'lishi mumkinligini taxmin qil
3. Foydalanuvchiga bitta aniq savol ber

Javobni qisqacha yoz.
"""


class GenerateWeeklyInsightUseCase:
    """Haftalik insight generatsiya qilish."""

    def __init__(self, llm_provider: ILLMProvider):
        self.llm = llm_provider

    async def execute(
        self,
        goals_count: int,
        active_goals: int,
        completed_goals: int,
        overall_score: float,
        completed_tasks: int,
        total_tasks: int,
        weekly_breakdown: str,
    ) -> WeeklyInsight:
        """Haftalik insight generatsiya qilish."""
        prompt = INSIGHT_PROMPT_TEMPLATE.format(
            goals_count=goals_count,
            active_goals=active_goals,
            completed_goals=completed_goals,
            overall_score=overall_score,
            completed_tasks=completed_tasks,
            total_tasks=total_tasks,
            weekly_breakdown=weekly_breakdown,
        )

        response = await self.llm.analyze_progress(prompt)

        insight = self._parse_response(response.content)

        return WeeklyInsight(
            summary=insight.get("summary", ""),
            weak_days=insight.get("weak_days", []),
            weak_tasks=insight.get("weak_tasks", []),
            recommendation=insight.get("recommendation", ""),
            question=insight.get("question", ""),
            tokens_used=response.tokens_used,
            cost_usd=response.cost_usd,
        )

    def _parse_response(self, content: str) -> dict:
        """LLM javobini parse qilish."""
        lines = content.strip().split("\n")

        result = {
            "summary": "",
            "weak_days": [],
            "weak_tasks": [],
            "recommendation": "",
            "question": "",
        }

        current_key = "summary"
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if "kunlar" in line.lower() or "vazifalar" in line.lower():
                current_key = "weak_tasks"
            elif "tavsiya" in line.lower() or "recommendation" in line.lower():
                current_key = "recommendation"
            elif "?" in line:
                result["question"] = line
            elif current_key == "summary" and not result["summary"]:
                result["summary"] = line
            elif current_key == "weak_tasks":
                result["weak_tasks"].append(line)
            elif current_key == "recommendation":
                result["recommendation"] = line

        return result
