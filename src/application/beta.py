"""Beta test group domain models and re-exports."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class BetaStatus(Enum):
    """Beta ishtirokchisi holati."""

    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"


@dataclass
class BetaParticipant:
    """Beta ishtirokchisi."""

    user_id: UUID
    username: str
    joined_at: datetime
    status: BetaStatus = BetaStatus.ACTIVE
    notes: str | None = None


from src.infrastructure.db.beta_manager import BetaGroupManager  # noqa: E402

__all__ = ["BetaStatus", "BetaParticipant", "BetaGroupManager"]
