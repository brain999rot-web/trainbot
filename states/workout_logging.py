from aiogram.fsm.state import State, StatesGroup


class WorkoutLoggingStates(StatesGroup):
    choose_workout = State()
    choose_exercise = State()
    log_sets = State()
