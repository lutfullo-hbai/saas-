"""Integration test configuration — ensure DB engine uses the test event loop."""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config.settings import settings


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _recreate_engine():
    """Recreate SQLAlchemy async engine on the test event loop.

    The module-level engine in session.py is created at import time, which
    binds its connection pool to a different event loop. Disposing and
    recreating it here ensures all DB connections use the pytest-asyncio loop.
    """
    import src.infrastructure.db.session as db_session

    await db_session.engine.dispose()

    db_session.engine = create_async_engine(
        settings.database_url,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
    )
    db_session.async_session_factory = async_sessionmaker(
        db_session.engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    yield
    await db_session.engine.dispose()
