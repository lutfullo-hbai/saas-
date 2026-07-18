"""Global test fixtures."""

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config.settings import settings
from src.infrastructure.db.models.base import Base
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
