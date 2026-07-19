"""Telegram handlers package."""

from src.infrastructure.telegram.handlers.checkin import router as checkin_router
from src.infrastructure.telegram.handlers.feedback import router as feedback_router
from src.infrastructure.telegram.handlers.goal_creation import router as goal_router
from src.infrastructure.telegram.handlers.goals_list import router as goals_list_router
from src.infrastructure.telegram.handlers.help import router as help_router
from src.infrastructure.telegram.handlers.onboarding import router as onboarding_router
from src.infrastructure.telegram.handlers.plan_approval import (
    router as plan_approval_router,
)
from src.infrastructure.telegram.handlers.progress import router as progress_router
from src.infrastructure.telegram.handlers.referral import router as referral_router
from src.infrastructure.telegram.handlers.start import router as start_router

__all__ = [
    "checkin_router",
    "feedback_router",
    "goal_router",
    "goals_list_router",
    "help_router",
    "onboarding_router",
    "plan_approval_router",
    "progress_router",
    "referral_router",
    "start_router",
]
