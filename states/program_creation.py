from aiogram.fsm.state import State, StatesGroup


class ProgramCreationStates(StatesGroup):
    choose_goal = State()
    confirm_program = State()
