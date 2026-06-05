from .registration import router as registration_router
from .program_handlers import router as program_router
from .workout_handlers import router as workout_router
from .progress_handlers import router as progress_router
from .analytics_handlers import router as analytics_router
from .timer_handlers import router as timer_router
from .exercise_database_handlers import router as exercise_database_router

__all__ = [
    "registration_router",
    "program_router",
    "workout_router",
    "progress_router",
    "analytics_router",
    "timer_router",
    "exercise_database_router"
]
