from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    age = State()
    height = State()
    weight = State()
    gender = State()
    experience = State()
    workouts_per_week = State()
