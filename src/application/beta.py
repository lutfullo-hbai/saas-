"""Beta test group management — DB bilan ishlaydi."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from sqlalchemy import func, select

from src.config.logging import get_logger

logger = get_logger(__name__)


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


class BetaGroupManager:
    """Beta guruhini boshqarish — DB bilan."""

    MAX_PARTICIPANTS = 20

    def __init__(self, session=None):
        self._session = session

    async def add_participant(
        self, user_id: UUID, username: str, notes: str | None = None
    ) -> bool:
        """Ishtirokchi qo'shish."""
        if not self._session:
            logger.warning("No DB session provided")
            return False

        from src.infrastructure.db.models.beta_participant import BetaParticipantModel

        count_result = await self._session.execute(
            select(func.count()).select_from(BetaParticipantModel)
        )
        current_count = count_result.scalar() or 0

        if current_count >= self.MAX_PARTICIPANTS:
            logger.warning("Beta group is full")
            return False

        existing = await self._session.execute(
            select(BetaParticipantModel).where(BetaParticipantModel.user_id == user_id)
        )
        if existing.scalar_one_or_none():
            logger.info(f"User {user_id} already in beta group")
            return False

        participant = BetaParticipantModel(
            user_id=user_id,
            status="active",
            notes=notes,
        )
        self._session.add(participant)
        await self._session.flush()

        logger.info(f"User {user_id} added to beta group")
        return True

    async def remove_participant(self, user_id: UUID) -> bool:
        """Ishtirokchini o'chirish."""
        if not self._session:
            return False

        from src.infrastructure.db.models.beta_participant import BetaParticipantModel

        result = await self._session.execute(
            select(BetaParticipantModel).where(BetaParticipantModel.user_id == user_id)
        )
        participant = result.scalar_one_or_none()

        if not participant:
            return False

        participant.status = "dropped"
        await self._session.flush()

        logger.info(f"User {user_id} removed from beta group")
        return True

    async def get_stats(self) -> dict:
        """Beta guruh statistikasi."""
        if not self._session:
            return {
                "total_participants": 0,
                "active_participants": 0,
                "max_capacity": self.MAX_PARTICIPANTS,
                "spots_available": self.MAX_PARTICIPANTS,
            }

        from src.infrastructure.db.models.beta_participant import BetaParticipantModel

        total_result = await self._session.execute(
            select(func.count()).select_from(BetaParticipantModel)
        )
        total = total_result.scalar() or 0

        active_result = await self._session.execute(
            select(func.count())
            .select_from(BetaParticipantModel)
            .where(BetaParticipantModel.status == "active")
        )
        active = active_result.scalar() or 0

        return {
            "total_participants": total,
            "active_participants": active,
            "max_capacity": self.MAX_PARTICIPANTS,
            "spots_available": self.MAX_PARTICIPANTS - total,
        }

    async def get_active_participants(self) -> list[BetaParticipant]:
        """Faol ishtirokchilar ro'yxati."""
        if not self._session:
            return []

        from src.infrastructure.db.models.beta_participant import BetaParticipantModel

        result = await self._session.execute(
            select(BetaParticipantModel).where(BetaParticipantModel.status == "active")
        )
        participants = result.scalars().all()

        return [
            BetaParticipant(
                user_id=p.user_id,
                username="",
                joined_at=p.joined_at,
                status=BetaStatus(p.status),
                notes=p.notes,
            )
            for p in participants
        ]
