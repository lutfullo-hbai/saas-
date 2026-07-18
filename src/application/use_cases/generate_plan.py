"""Plan generation use case — LLM orqali reja tuzish."""

import json
import logging
from dataclasses import dataclass

from src.application.interfaces.llm import ILLMProvider

logger = logging.getLogger(__name__)


@dataclass
class TaskSuggestion:
    """Taklif qilingan vazifa."""

    title: str
    recurrence: str
    time: str
    weight: float


@dataclass
class GeneratedPlan:
    """Generatsiya qilingan reja."""

    tasks: list[TaskSuggestion]
    raw_response: str
    tokens_used: int
    cost_usd: float


PLAN_PROMPT_TEMPLATE = """
Maqsad: {goal_title}
Tavsif: {goal_description}
Joriy daraja: {current_level}
Mavjud vaqt: {available_hours} soat/kun
Muddat: {target_date}

Faqat quyidagi JSON formatda javob ber, boshqa hech narsa yozma:
{{
    "tasks": [
        {{
            "title": "Vazifa nomi",
            "recurrence": "FREQ=DAILY",
            "time": "09:00",
            "weight": 0.8
        }}
    ]
}}

Recurrence formatlari:
- FREQ=DAILY — har kuni
- FREQ=WEEKLY;BYDAY=MO,WE,FR — haftada 3 marta
- FREQ=MONTHLY;BYMONTHDAY=1 — oyda 1 marta
"""


class GeneratePlanUseCase:
    """LLM orqali reja generatsiya qilish."""

    def __init__(self, llm_provider: ILLMProvider):
        self.llm = llm_provider

    async def execute(
        self,
        goal_title: str,
        goal_description: str,
        current_level: str = "boshlang'ich",
        available_hours: float = 2.0,
        target_date: str = "2026-12-31",
    ) -> GeneratedPlan:
        """Reja generatsiya qilish."""
        prompt = PLAN_PROMPT_TEMPLATE.format(
            goal_title=goal_title,
            goal_description=goal_description,
            current_level=current_level,
            available_hours=available_hours,
            target_date=target_date,
        )

        response = await self.llm.generate_plan(prompt)

        tasks = self._parse_response(response.content)

        return GeneratedPlan(
            tasks=tasks,
            raw_response=response.content,
            tokens_used=response.tokens_used,
            cost_usd=response.cost_usd,
        )

    def _parse_response(self, content: str) -> list[TaskSuggestion]:
        """LLM javobini JSON formatga parse qilish."""
        try:
            data = json.loads(content)
            tasks = []

            for task in data.get("tasks", []):
                tasks.append(
                    TaskSuggestion(
                        title=task.get("title", ""),
                        recurrence=task.get("recurrence", "FREQ=DAILY"),
                        time=task.get("time", "09:00"),
                        weight=float(task.get("weight", 1.0)),
                    )
                )

            return tasks

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            return []

        except Exception as e:
            logger.error(f"Error parsing plan: {e}")
            return []
