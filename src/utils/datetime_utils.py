"""Centralized datetime utility functions."""

from datetime import UTC, datetime


def utc_now() -> datetime:
    """Returns current UTC datetime as naive datetime for consistent storage.

    All datetimes in the system are stored as naive UTC timestamps.
    This is the single source of truth for current time.
    """
    return datetime.now(UTC).replace(tzinfo=None)
