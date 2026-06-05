from aiogram.fsm.state import State, StatesGroup


class StrengthCalculatorStates(StatesGroup):
    """Стани для калькулятора 1RM"""
    exercise_name = State()
    weight = State()
    reps = State()
