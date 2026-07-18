"""Telegram handlers package."""

from src.infrastructure.telegram.handlers.goal_creation import router as goal_router
from src.infrastructure.telegram.handlers.help import router as help_router
from src.infrastructure.telegram.handlers.start import router as start_router

__all__ = ["goal_router", "help_router", "start_router"]
