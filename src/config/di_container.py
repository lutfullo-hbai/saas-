"""Dependency Injection container — barcha bog'liqliklarni markaziy boshqarish."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import settings
from src.infrastructure.db.repositories.goal_repository import PostgresGoalRepository
from src.infrastructure.db.repositories.plan_repository import PostgresPlanRepository
from src.infrastructure.db.repositories.scheduled_task_repository import (
    PostgresScheduledTaskRepository,
)
from src.infrastructure.db.repositories.score_repository import PostgresScoreRepository
from src.infrastructure.db.repositories.checkin_repository import PostgresCheckInRepository
from src.infrastructure.db.repositories.task_template_repository import (
    PostgresTaskTemplateRepository,
)
from src.infrastructure.llm.claude_provider import ClaudeProvider
from src.infrastructure.llm.ollama_provider import OllamaProvider


class Container:
    """DI konteyner — repository va xizmatlarni yaratadi.

    Usage:
        container = Container(session)
        goal_repo = container.goal_repository
        use_case = container.create_goal_use_case
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    @property
    def goal_repository(self) -> PostgresGoalRepository:
        return PostgresGoalRepository(self._session)

    @property
    def plan_repository(self) -> PostgresPlanRepository:
        return PostgresPlanRepository(self._session)

    @property
    def task_template_repository(self) -> PostgresTaskTemplateRepository:
        return PostgresTaskTemplateRepository(self._session)

    @property
    def scheduled_task_repository(self) -> PostgresScheduledTaskRepository:
        return PostgresScheduledTaskRepository(self._session)

    @property
    def score_repository(self) -> PostgresScoreRepository:
        return PostgresScoreRepository(self._session)

    @property
    def checkin_repository(self) -> PostgresCheckInRepository:
        return PostgresCheckInRepository(self._session)

    @property
    def llm_provider(self):
        """LLM provayderini sozlashlardan yaratish."""
        if settings.llm_provider == "ollama":
            return OllamaProvider(base_url=settings.ollama_base_url)
        return ClaudeProvider(api_key=settings.anthropic_api_key)

    @property
    def create_goal_use_case(self):
        from src.application.use_cases.create_goal import CreateGoalUseCase

        return CreateGoalUseCase(self.goal_repository)

    @property
    def create_plan_use_case(self):
        from src.application.use_cases.create_plan import CreatePlanManuallyUseCase

        return CreatePlanManuallyUseCase(self.plan_repository)

    @property
    def add_task_template_use_case(self):
        from src.application.use_cases.add_task_template import AddTaskTemplateUseCase

        return AddTaskTemplateUseCase(self.task_template_repository)

    @property
    def process_checkin_use_case(self):
        from src.application.use_cases.process_checkin import ProcessCheckInUseCase

        return ProcessCheckInUseCase(
            self.scheduled_task_repository,
            self.score_repository,
            self.checkin_repository,
            self.task_template_repository,
        )

    @property
    def generate_insight_use_case(self):
        from src.application.use_cases.generate_insight import GenerateWeeklyInsightUseCase

        return GenerateWeeklyInsightUseCase(self.llm_provider)

    @property
    def generate_plan_use_case(self):
        from src.application.use_cases.generate_plan import GeneratePlanUseCase

        return GeneratePlanUseCase(self.llm_provider)
