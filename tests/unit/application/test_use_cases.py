"""Use case unit testlari."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.application.use_cases.add_task_template import AddTaskTemplateUseCase
from src.application.use_cases.create_goal import CreateGoalUseCase
from src.application.use_cases.create_plan import CreatePlanManuallyUseCase
from src.application.use_cases.process_checkin import ProcessCheckInUseCase
from src.domain.entities.goal import Goal
from src.domain.entities.plan import Plan
from src.domain.entities.scheduled_task import ScheduledTask
from src.domain.entities.task_template import TaskTemplate
from src.domain.exceptions import AlreadyCheckedInError


class TestCreateGoalUseCase:
    """CreateGoalUseCase testlari."""

    def test_creates_goal_with_title(self):
        mock_repo = AsyncMock()
        use_case = CreateGoalUseCase(mock_repo)
        user_id = uuid4()

        goal = Goal(user_id=user_id, title="Test maqsad")
        mock_repo.create.return_value = goal

        import asyncio

        result = asyncio.run(
            use_case.execute(user_id=user_id, title="Test maqsad")
        )

        assert result.title == "Test maqsad"
        assert result.user_id == user_id
        mock_repo.create.assert_called_once()

    def test_creates_goal_with_description(self):
        mock_repo = AsyncMock()
        use_case = CreateGoalUseCase(mock_repo)
        user_id = uuid4()

        goal = Goal(user_id=user_id, title="Test", description="Tavsif")
        mock_repo.create.return_value = goal

        import asyncio

        result = asyncio.run(
            use_case.execute(user_id=user_id, title="Test", description="Tavsif")
        )

        assert result.description == "Tavsif"


class TestCreatePlanManuallyUseCase:
    """CreatePlanManuallyUseCase testlari."""

    def test_creates_plan_for_goal(self):
        mock_repo = AsyncMock()
        use_case = CreatePlanManuallyUseCase(mock_repo)
        goal_id = uuid4()

        plan = Plan(goal_id=goal_id, source="manual")
        mock_repo.create.return_value = plan

        import asyncio

        result = asyncio.run(use_case.execute(goal_id=goal_id))

        assert result.goal_id == goal_id
        assert result.source == "manual"
        mock_repo.create.assert_called_once()

    def test_creates_ai_plan(self):
        mock_repo = AsyncMock()
        use_case = CreatePlanManuallyUseCase(mock_repo)
        goal_id = uuid4()

        plan = Plan(goal_id=goal_id, source="ai")
        mock_repo.create.return_value = plan

        import asyncio

        result = asyncio.run(
            use_case.execute(goal_id=goal_id, source="ai")
        )

        assert result.source == "ai"


class TestAddTaskTemplateUseCase:
    """AddTaskTemplateUseCase testlari."""

    def test_adds_template_to_plan(self):
        mock_repo = AsyncMock()
        use_case = AddTaskTemplateUseCase(mock_repo)
        plan_id = uuid4()

        template = TaskTemplate(
            plan_id=plan_id,
            title="50 ta so'z yodlash",
            tolerance_minutes=15,
            task_weight=0.8,
        )
        mock_repo.create.return_value = template

        import asyncio

        result = asyncio.run(
            use_case.execute(
                plan_id=plan_id,
                title="50 ta so'z yodlash",
                tolerance_minutes=15,
                task_weight=0.8,
            )
        )

        assert result.title == "50 ta so'z yodlash"
        assert result.tolerance_minutes == 15
        assert result.task_weight == 0.8


class TestProcessCheckInUseCase:
    """ProcessCheckInUseCase testlari."""

    def test_processes_checkinSuccessfully(self):
        mock_task_repo = AsyncMock()
        mock_score_repo = AsyncMock()
        use_case = ProcessCheckInUseCase(mock_task_repo, mock_score_repo)

        task_id = uuid4()
        task = ScheduledTask(
            id=task_id,
            task_template_id=uuid4(),
            scheduled_datetime=datetime(2026, 1, 1, 14, 30),
            status="pending",
        )
        mock_task_repo.get_by_id.return_value = task
        mock_task_repo.update_status.return_value = ScheduledTask(
            id=task_id, status="completed"
        )

        import asyncio

        checkin, score = asyncio.run(
            use_case.execute(
                scheduled_task_id=task_id,
                checkin_time=datetime(2026, 1, 1, 14, 32),
            )
        )

        assert checkin.scheduled_task_id == task_id
        assert score.computed_score >= 0
        mock_task_repo.update_status.assert_called_once_with(task_id, "completed")

    def test_rejects_already_completed_task(self):
        mock_task_repo = AsyncMock()
        mock_score_repo = AsyncMock()
        use_case = ProcessCheckInUseCase(mock_task_repo, mock_score_repo)

        task = ScheduledTask(
            id=uuid4(),
            task_template_id=uuid4(),
            status="completed",
        )
        mock_task_repo.get_by_id.return_value = task

        with pytest.raises(AlreadyCheckedInError):
            import asyncio

            asyncio.run(
                use_case.execute(
                    scheduled_task_id=task.id,
                    checkin_time=datetime.utcnow(),
                )
            )
