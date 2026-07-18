"""Domain entity testlari."""

import pathlib
from datetime import date, timedelta
from uuid import uuid4

import pytest

from src.domain.entities import (
    CheckIn,
    Goal,
    Plan,
    ScheduledTask,
    ScoreEvent,
    TaskTemplate,
)
from src.domain.exceptions import InvalidEntityError


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


class TestGoalEntity:
    """Goal entity invariantlari."""

    def test_goal_creation(self):
        goal = Goal(title="Ingliz tilini o'rganaman")
        assert goal.title == "Ingliz tilini o'rganaman"
        assert goal.status == "active"
        assert goal.id is not None

    def test_goal_empty_title_raises(self):
        with pytest.raises(InvalidEntityError, match="title bo'sh"):
            Goal(title="")

    def test_goal_invalid_status_raises(self):
        with pytest.raises(InvalidEntityError, match="Noto'g'ri status"):
            Goal(title="Test", status="invalid")

    def test_goal_past_target_date_raises(self):
        with pytest.raises(InvalidEntityError, match="o'tmishda"):
            Goal(title="Test", target_date=date.today() - timedelta(days=1))

    def test_goal_valid_statuses(self):
        for status in ("active", "completed", "archived", "cancelled"):
            goal = Goal(title="Test", status=status)
            assert goal.status == status


class TestPlanEntity:
    """Plan entity invariantlari."""

    def test_plan_creation(self):
        plan = Plan(goal_id=uuid4(), source="ai")
        assert plan.source == "ai"
        assert plan.version == 1
        assert plan.is_active is True

    def test_plan_invalid_source_raises(self):
        with pytest.raises(InvalidEntityError, match="Noto'g'ri source"):
            Plan(goal_id=uuid4(), source="invalid")

    def test_plan_version_below_one_raises(self):
        with pytest.raises(InvalidEntityError, match="version 1 dan kichik"):
            Plan(goal_id=uuid4(), version=0)


class TestTaskTemplateEntity:
    """TaskTemplate entity invariantlari."""

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

    def test_task_template_empty_title_raises(self):
        with pytest.raises(InvalidEntityError, match="title bo'sh"):
            TaskTemplate(title="")

    def test_task_template_negative_tolerance_raises(self):
        with pytest.raises(InvalidEntityError, match="manfiy"):
            TaskTemplate(title="Test", tolerance_minutes=-1)

    def test_task_template_weight_out_of_range_raises(self):
        with pytest.raises(InvalidEntityError, match="0.0-1.0"):
            TaskTemplate(title="Test", task_weight=1.5)

    def test_task_template_invalid_recurrence_raises(self):
        with pytest.raises(InvalidEntityError, match="FREQ="):
            TaskTemplate(title="Test", recurrence_rule="INVALID")


class TestScheduledTaskEntity:
    """ScheduledTask entity invariantlari."""

    def test_scheduled_task_creation(self):
        task = ScheduledTask(task_template_id=uuid4())
        assert task.status == "pending"
        assert task.notification_sent_at is None

    def test_scheduled_task_invalid_status_raises(self):
        with pytest.raises(InvalidEntityError, match="Noto'g'ri status"):
            ScheduledTask(task_template_id=uuid4(), status="invalid")


class TestCheckInEntity:
    """CheckIn entity invariantlari."""

    def test_checkin_creation(self):
        checkin = CheckIn(scheduled_task_id=uuid4())
        assert checkin.method == "telegram"
        assert checkin.user_note == ""

    def test_checkin_invalid_method_raises(self):
        with pytest.raises(InvalidEntityError, match="Noto'g'ri method"):
            CheckIn(scheduled_task_id=uuid4(), method="invalid")

    def test_checkin_valid_methods(self):
        for method in ("telegram", "web", "api"):
            checkin = CheckIn(scheduled_task_id=uuid4(), method=method)
            assert checkin.method == method


class TestScoreEventEntity:
    """ScoreEvent entity invariantlari."""

    def test_score_event_creation(self):
        event = ScoreEvent(checkin_id=uuid4(), computed_score=0.95)
        assert event.computed_score == 0.95
        assert event.formula_version == "v1"

    def test_score_event_out_of_range_raises(self):
        with pytest.raises(InvalidEntityError, match="0.0-1.0"):
            ScoreEvent(checkin_id=uuid4(), computed_score=1.5)

    def test_score_event_empty_formula_version_raises(self):
        with pytest.raises(InvalidEntityError, match="formula_version bo'sh"):
            ScoreEvent(checkin_id=uuid4(), formula_version="")
