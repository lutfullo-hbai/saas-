"""Beta test group management."""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class BetaStatus(Enum):
    """Beta ishtirokchisi holati."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"


@dataclass
class BetaParticipant:
    """Beta ishtirokchisi."""
    user_id: int
    username: str
    joined_at: datetime
    status: BetaStatus = BetaStatus.ACTIVE
    feedback_count: int = 0
    last_active: datetime | None = None


class BetaGroupManager:
    """Beta guruhini boshqarish."""

    MAX_PARTICIPANTS = 20

    def __init__(self):
        self.participants: dict[int, BetaParticipant] = {}

    def add_participant(self, user_id: int, username: str) -> bool:
        """Ishtirokchi qo'shish."""
        if len(self.participants) >= self.MAX_PARTICIPANTS:
            logger.warning("Beta group is full")
            return False

        if user_id in self.participants:
            logger.info(f"User {user_id} already in beta group")
            return False

        participant = BetaParticipant(
            user_id=user_id,
            username=username,
            joined_at=datetime.now(),
        )
        self.participants[user_id] = participant

        logger.info(f"User {user_id} added to beta group")
        return True

    def remove_participant(self, user_id: int) -> bool:
        """Ishtirokchini o'chirish."""
        if user_id not in self.participants:
            return False

        self.participants[user_id].status = BetaStatus.DROPPED
        logger.info(f"User {user_id} removed from beta group")
        return True

    def get_stats(self) -> dict:
        """Beta guruh statistikasi."""
        active = sum(
            1 for p in self.participants.values()
            if p.status == BetaStatus.ACTIVE
        )
        total_feedback = sum(p.feedback_count for p in self.participants.values())

        return {
            "total_participants": len(self.participants),
            "active_participants": active,
            "total_feedback": total_feedback,
            "max_capacity": self.MAX_PARTICIPANTS,
            "spots_available": self.MAX_PARTICIPANTS - len(self.participants),
        }

    def get_active_participants(self) -> list[BetaParticipant]:
        """Faol ishtirokchilar ro'yxati."""
        return [
            p for p in self.participants.values()
            if p.status == BetaStatus.ACTIVE
        ]


beta_manager = BetaGroupManager()
