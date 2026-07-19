"""Integration test configuration — ensure DB engine uses the test event loop."""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.config.settings import settings


@pytest_asyncio.fixture(autouse=True)
async def _setup_engine():
    """Recreate SQLAlchemy engine per test with NullPool.

    NullPool creates fresh connections for each request, avoiding event-loop
    binding issues when each pytest test runs on a different asyncio loop
    (CI environment without session-scoped loop support).
    """
    import src.infrastructure.db.session as db_session

    await db_session.engine.dispose()

    db_session.engine = create_async_engine(
        settings.database_url,
        echo=False,
        poolclass=NullPool,
    )
    db_session.async_session_factory = async_sessionmaker(
        db_session.engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    yield
    await db_session.engine.dispose()
