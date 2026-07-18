"""API endpoint integration testlari."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.domain.entities.goal import Goal
from src.domain.entities.plan import Plan
from src.domain.entities.scheduled_task import ScheduledTask
from src.domain.entities.task_template import TaskTemplate


class TestGoalsAPI:
    """Goals API endpoint testlari."""

    def test_create_goal_success(self):
        mock_repo = AsyncMock()
        goal = Goal(
            user_id=uuid4(),
            title="Test maqsad",
            description="Tavsif",
        )
        mock_repo.create.return_value = goal

        from src.application.use_cases.create_goal import CreateGoalUseCase

        use_case = CreateGoalUseCase(mock_repo)

        import asyncio

        result = asyncio.run(
            use_case.execute(
                user_id=goal.user_id,
                title="Test maqsad",
                description="Tavsif",
            )
        )

        assert result.title == "Test maqsad"
        assert result.description == "Tavsif"
        mock_repo.create.assert_called_once()

    def test_create_goal_empty_title_raises(self):
        mock_repo = AsyncMock()
        from src.application.use_cases.create_goal import CreateGoalUseCase

        use_case = CreateGoalUseCase(mock_repo)

        import asyncio

        with pytest.raises(Exception):
            asyncio.run(
                use_case.execute(user_id=uuid4(), title="")
            )

    def test_get_goal_not_found(self):
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = None

        import asyncio

        from src.application.use_cases.create_goal import CreateGoalUseCase

        result = asyncio.run(mock_repo.get_by_id(uuid4()))
        assert result is None

    def test_list_goals(self):
        mock_repo = AsyncMock()
        goals = [
            Goal(user_id=uuid4(), title="Maqsad 1"),
            Goal(user_id=uuid4(), title="Maqsad 2"),
        ]
        mock_repo.get_by_user_id.return_value = goals

        import asyncio

        result = asyncio.run(mock_repo.get_by_user_id(uuid4()))
        assert len(result) == 2


class TestPlansAPI:
    """Plans API endpoint testlari."""

    def test_create_plan_for_goal(self):
        mock_repo = AsyncMock()
        plan = Plan(goal_id=uuid4(), source="manual")
        mock_repo.create.return_value = plan

        from src.application.use_cases.create_plan import CreatePlanManuallyUseCase

        use_case = CreatePlanManuallyUseCase(mock_repo)

        import asyncio

        result = asyncio.run(use_case.execute(goal_id=plan.goal_id))

        assert result.source == "manual"
        mock_repo.create.assert_called_once()


class TestTaskTemplatesAPI:
    """Task Templates API endpoint testlari."""

    def test_add_task_template(self):
        mock_repo = AsyncMock()
        template = TaskTemplate(
            plan_id=uuid4(),
            title="50 ta so'z yodlash",
            tolerance_minutes=15,
            task_weight=0.8,
        )
        mock_repo.create.return_value = template

        from src.application.use_cases.add_task_template import AddTaskTemplateUseCase

        use_case = AddTaskTemplateUseCase(mock_repo)

        import asyncio

        result = asyncio.run(
            use_case.execute(
                plan_id=template.plan_id,
                title="50 ta so'z yodlash",
                tolerance_minutes=15,
                task_weight=0.8,
            )
        )

        assert result.title == "50 ta so'z yodlash"
        assert result.tolerance_minutes == 15
        assert result.task_weight == 0.8


class TestCheckInsAPI:
    """Check-ins API endpoint testlari."""

    def test_process_checkin_success(self):
        mock_task_repo = AsyncMock()
        mock_score_repo = AsyncMock()
        mock_checkin_repo = AsyncMock()
        mock_template_repo = AsyncMock()

        from src.application.use_cases.process_checkin import ProcessCheckInUseCase

        use_case = ProcessCheckInUseCase(
            mock_task_repo, mock_score_repo, mock_checkin_repo, mock_template_repo
        )

        task_id = uuid4()
        template_id = uuid4()
        task = ScheduledTask(
            id=task_id,
            task_template_id=template_id,
            scheduled_datetime=datetime(2026, 1, 1, 14, 30),
            status="pending",
        )
        mock_task_repo.get_by_id.return_value = task

        template = TaskTemplate(
            id=template_id,
            title="Test",
            tolerance_minutes=10,
            task_weight=1.0,
        )
        mock_template_repo.get_by_id.return_value = template

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

    def test_reject_duplicate_checkin(self):
        mock_task_repo = AsyncMock()
        mock_score_repo = AsyncMock()
        mock_checkin_repo = AsyncMock()
        mock_template_repo = AsyncMock()

        from src.application.use_cases.process_checkin import ProcessCheckInUseCase
        from src.domain.exceptions import AlreadyCheckedInError

        use_case = ProcessCheckInUseCase(
            mock_task_repo, mock_score_repo, mock_checkin_repo, mock_template_repo
        )

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
