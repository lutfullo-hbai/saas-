"""Feedback FSM states."""

from aiogram.fsm.state import State, StatesGroup


class FeedbackStates(StatesGroup):
    """Feedback suhbat holatlari."""

    waiting_for_type = State()
    waiting_for_content = State()
