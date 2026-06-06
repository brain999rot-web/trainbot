"""FSM states for nutrition tracking"""
from aiogram.fsm.state import State, StatesGroup


class NutritionCalculatorStates(StatesGroup):
    """States for TDEE calculator"""
    activity_level = State()
    goal = State()


class NutritionLoggingStates(StatesGroup):
    """States for logging daily nutrition"""
    calories = State()
    protein = State()
    carbs = State()
    fats = State()
    notes = State()
