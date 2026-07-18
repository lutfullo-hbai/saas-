"""Check-ins API endpoints."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.process_checkin import ProcessCheckInUseCase
from src.infrastructure.db.repositories.checkin_repository import PostgresCheckInRepository
from src.infrastructure.db.repositories.scheduled_task_repository import (
    PostgresScheduledTaskRepository,
)
from src.infrastructure.db.repositories.score_repository import PostgresScoreRepository
from src.infrastructure.db.repositories.task_template_repository import (
    PostgresTaskTemplateRepository,
)
from src.presentation.api.dependencies import CurrentUser, get_current_user, get_db
from src.presentation.schemas.checkin import CheckInCreate, CheckInResponse
from src.presentation.schemas.score import ScoreEventResponse

router = APIRouter(prefix="/checkins", tags=["Check-ins"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_checkin(
    request: CheckInCreate,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Check-in yaratish va ball olish."""
    task_repo = PostgresScheduledTaskRepository(session)
    score_repo = PostgresScoreRepository(session)
    checkin_repo = PostgresCheckInRepository(session)
    template_repo = PostgresTaskTemplateRepository(session)
    use_case = ProcessCheckInUseCase(task_repo, score_repo, checkin_repo, template_repo)

    checkin, score_event = await use_case.execute(
        scheduled_task_id=request.scheduled_task_id,
        checkin_time=datetime.utcnow(),
        method=request.method,
        user_note=request.user_note,
    )

    return {
        "checkin": CheckInResponse.model_validate(checkin).model_dump(),
        "score_event": ScoreEventResponse.model_validate(score_event).model_dump(),
    }
