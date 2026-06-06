from .registration import router as registration_router
from .program_handlers import router as program_router
from .workout_handlers import router as workout_router
from .progress_handlers import router as progress_router
from .analytics_handlers import router as analytics_router
from .timer_handlers import router as timer_router
from .exercise_database_handlers import router as exercise_database_router
from .strength_calculator_handlers import router as strength_calculator_router
from .favorites_records_handlers import router as favorites_records_router
from .nutrition_handlers import router as nutrition_router

__all__ = [
    "registration_router",
    "program_router",
    "workout_router",
    "progress_router",
    "analytics_router",
    "timer_router",
    "exercise_database_router",
    "strength_calculator_router",
    "favorites_records_router",
    "nutrition_router"
]
