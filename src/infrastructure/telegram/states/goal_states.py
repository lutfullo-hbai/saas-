"""Goal creation FSM states."""

from aiogram.fsm.state import State, StatesGroup


class GoalCreationStates(StatesGroup):
    """Maqsad yaratish holatlari."""

    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_target_date = State()
    confirmation = State()
