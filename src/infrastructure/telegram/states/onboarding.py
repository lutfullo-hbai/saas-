"""Onboarding FSM states."""

from aiogram.fsm.state import State, StatesGroup


class OnboardingStates(StatesGroup):
    """Onboarding suhbat holatlari."""

    welcome = State()
    goal_selection = State()
    first_goal = State()
