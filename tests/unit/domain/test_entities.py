"""Domain entity testlari."""

import pathlib
from uuid import uuid4

from src.domain.entities import Goal, Plan, TaskTemplate, ScheduledTask, CheckIn, ScoreEvent


class TestProjectStructure:
    """Loyiha strukturasini tekshirish."""

    def test_src_directory_exists(self):
        src = pathlib.Path("src")
        assert src.exists()

    def test_domain_directory_exists(self):
        assert pathlib.Path("src/domain").exists()
        assert pathlib.Path("src/domain/entities").exists()
        assert pathlib.Path("src/domain/value_objects").exists()
        assert pathlib.Path("src/domain/exceptions").exists()

    def test_application_directory_exists(self):
        assert pathlib.Path("src/application").exists()
        assert pathlib.Path("src/application/use_cases").exists()
        assert pathlib.Path("src/application/interfaces").exists()

    def test_infrastructure_directory_exists(self):
        assert pathlib.Path("src/infrastructure").exists()
        assert pathlib.Path("src/infrastructure/db").exists()
        assert pathlib.Path("src/infrastructure/llm").exists()
        assert pathlib.Path("src/infrastructure/telegram").exists()
        assert pathlib.Path("src/infrastructure/scheduler").exists()

    def test_presentation_directory_exists(self):
        assert pathlib.Path("src/presentation").exists()
        assert pathlib.Path("src/presentation/api").exists()
        assert pathlib.Path("src/presentation/api/v1").exists()
        assert pathlib.Path("src/presentation/schemas").exists()

    def test_config_directory_exists(self):
        assert pathlib.Path("src/config").exists()

    def test_docs_directory_exists(self):
        assert pathlib.Path("docs").exists()
        assert pathlib.Path("docs/README.md").exists()
        assert pathlib.Path("docs/readmee.md").exists()


class TestDomainEntities:
    """Domain entity obyektlarini tekshirish."""

    def test_goal_creation(self):
        goal = Goal(title="Ingliz tilini o'rganaman")
        assert goal.title == "Ingliz tilini o'rganaman"
        assert goal.status == "active"
        assert goal.id is not None

    def test_plan_creation(self):
        plan = Plan(goal_id=uuid4(), source="ai")
        assert plan.source == "ai"
        assert plan.version == 1
        assert plan.is_active is True

    def test_task_template_creation(self):
        template = TaskTemplate(
            title="50 ta yangi so'z yodlash",
            recurrence_rule="FREQ=DAILY",
            tolerance_minutes=15,
            task_weight=0.8,
        )
        assert template.title == "50 ta yangi so'z yodlash"
        assert template.tolerance_minutes == 15
        assert template.task_weight == 0.8

    def test_scheduled_task_creation(self):
        task = ScheduledTask(task_template_id=uuid4())
        assert task.status == "pending"
        assert task.notification_sent_at is None

    def test_checkin_creation(self):
        checkin = CheckIn(scheduled_task_id=uuid4())
        assert checkin.method == "telegram"
        assert checkin.user_note == ""

    def test_score_event_creation(self):
        event = ScoreEvent(checkin_id=uuid4(), computed_score=0.95)
        assert event.computed_score == 0.95
        assert event.formula_version == "v1"
