"""Global test fixtures."""

import os
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Test muhitini oldindan o'rnatish — RateLimitMiddleware o'chiriladi
os.environ["APP_ENV"] = "testing"

from src.config.settings import settings
from src.infrastructure.db.models.base import Base
from src.infrastructure.db.session import async_session_factory
from src.presentation.api.app import app
from src.presentation.api.dependencies import get_db


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def mock_db_session():
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.flush = AsyncMock()
    session.execute = AsyncMock()
    session.add = AsyncMock()
    return session


@pytest.fixture
def sample_user_id():
    return uuid4()


@pytest.fixture
def sample_goal_id():
    return uuid4()


@pytest.fixture
def sample_plan_id():
    return uuid4()


@pytest.fixture
def sample_task_template_id():
    return uuid4()


@pytest.fixture
def sample_scheduled_task_id():
    return uuid4()


_TEST_PREFIXES = (
    "integ_%",
    "auth_%",
    "goals_%",
    "plans_%",
    "tmpl_%",
    "loadtest_%",
)


async def _cleanup_test_data() -> None:
    """DB'dagi test ma'lumotlarini tozalash — JOIN ishlatiladi."""
    try:
        async with async_session_factory() as session:
            for prefix in _TEST_PREFIXES:
                for stmt in (
                    "DELETE FROM score_events WHERE checkin_id IN "
                    "(SELECT ci.id FROM check_ins ci "
                    "JOIN scheduled_tasks st ON ci.scheduled_task_id = st.id "
                    "JOIN task_templates tt ON st.task_template_id = tt.id "
                    "JOIN plans pl ON tt.plan_id = pl.id "
                    "JOIN goals g ON pl.goal_id = g.id "
                    "JOIN users u ON g.user_id = u.id "
                    "WHERE u.telegram_id LIKE :p)",
                    "DELETE FROM check_ins WHERE scheduled_task_id IN "
                    "(SELECT st.id FROM scheduled_tasks st "
                    "JOIN task_templates tt ON st.task_template_id = tt.id "
                    "JOIN plans pl ON tt.plan_id = pl.id "
                    "JOIN goals g ON pl.goal_id = g.id "
                    "JOIN users u ON g.user_id = u.id "
                    "WHERE u.telegram_id LIKE :p)",
                    "DELETE FROM scheduled_tasks WHERE task_template_id IN "
                    "(SELECT tt.id FROM task_templates tt "
                    "JOIN plans pl ON tt.plan_id = pl.id "
                    "JOIN goals g ON pl.goal_id = g.id "
                    "JOIN users u ON g.user_id = u.id "
                    "WHERE u.telegram_id LIKE :p)",
                    "DELETE FROM task_templates WHERE plan_id IN "
                    "(SELECT pl.id FROM plans pl "
                    "JOIN goals g ON pl.goal_id = g.id "
                    "JOIN users u ON g.user_id = u.id "
                    "WHERE u.telegram_id LIKE :p)",
                    "DELETE FROM plans WHERE goal_id IN "
                    "(SELECT g.id FROM goals g "
                    "JOIN users u ON g.user_id = u.id "
                    "WHERE u.telegram_id LIKE :p)",
                    "DELETE FROM insights WHERE user_id IN "
                    "(SELECT id FROM users WHERE telegram_id LIKE :p)",
                    "DELETE FROM feedbacks WHERE user_id IN "
                    "(SELECT id FROM users WHERE telegram_id LIKE :p)",
                    "DELETE FROM subscriptions WHERE user_id IN "
                    "(SELECT id FROM users WHERE telegram_id LIKE :p)",
                    "DELETE FROM goals WHERE user_id IN "
                    "(SELECT id FROM users WHERE telegram_id LIKE :p)",
                    "DELETE FROM users WHERE telegram_id LIKE :p",
                ):
                    await session.execute(text(stmt), {"p": prefix})
            await session.commit()
    except Exception:
        pass


@pytest.fixture(autouse=True)
async def clean_test_data():
    """Har testdan oldin va keyin test foydalanuvchilarini tozalash."""
    await _cleanup_test_data()
    yield
    await _cleanup_test_data()
