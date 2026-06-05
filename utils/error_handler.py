"""Global error handling and logging"""
import logging
import traceback
from functools import wraps
from typing import Callable, Any
from aiogram import Bot
from aiogram.types import Message, CallbackQuery, Update
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramNotFound
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError


logger = logging.getLogger(__name__)


class BotError(Exception):
    """Base exception for bot errors"""
    def __init__(self, message: str, user_message: str = None):
        self.message = message
        self.user_message = user_message or "❌ Виникла помилка. Спробуй пізніше."
        super().__init__(self.message)


class DatabaseError(BotError):
    """Database related errors"""
    pass


class ValidationError(BotError):
    """Validation related errors"""
    pass


def handle_db_errors(func: Callable) -> Callable:
    """
    Decorator for handling database errors.

    Usage:
        @handle_db_errors
        async def some_db_function():
            # DB operations
    """
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except IntegrityError as e:
            logger.error(f"Database integrity error in {func.__name__}: {e}")
            raise DatabaseError(
                f"Integrity error: {e}",
                "❌ Помилка збереження даних. Можливо такий запис вже існує."
            )
        except OperationalError as e:
            logger.error(f"Database operational error in {func.__name__}: {e}")
            raise DatabaseError(
                f"Operational error: {e}",
                "❌ База даних недоступна. Спробуй пізніше."
            )
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error in {func.__name__}: {e}")
            raise DatabaseError(
                f"Database error: {e}",
                "❌ Помилка роботи з базою даних."
            )
    return wrapper


def handle_telegram_errors(func: Callable) -> Callable:
    """
    Decorator for handling Telegram API errors.

    Usage:
        @handle_telegram_errors
        async def message_handler(message: Message):
            # Handler logic
    """
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except TelegramBadRequest as e:
            logger.warning(f"Telegram bad request in {func.__name__}: {e}")
            # Silently ignore bad requests (e.g., message to edit not found)
            return None
        except TelegramForbiddenError as e:
            logger.warning(f"Bot was blocked by user in {func.__name__}: {e}")
            # User blocked the bot - nothing we can do
            return None
        except TelegramNotFound as e:
            logger.warning(f"Telegram entity not found in {func.__name__}: {e}")
            return None
    return wrapper


def safe_handler(func: Callable) -> Callable:
    """
    Combined decorator for safe handler execution.
    Catches all exceptions and notifies user.

    Usage:
        @safe_handler
        async def my_handler(message: Message):
            # Handler logic
    """
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except BotError as e:
            # Known bot errors - show user message
            logger.error(f"Bot error in {func.__name__}: {e.message}")
            await _notify_user_about_error(args, e.user_message)
        except TelegramBadRequest as e:
            logger.warning(f"Telegram bad request in {func.__name__}: {e}")
        except TelegramForbiddenError as e:
            logger.warning(f"Bot blocked in {func.__name__}: {e}")
        except SQLAlchemyError as e:
            logger.error(f"Database error in {func.__name__}: {e}\n{traceback.format_exc()}")
            await _notify_user_about_error(
                args,
                "❌ Помилка роботи з базою даних. Спробуй пізніше."
            )
        except Exception as e:
            # Unexpected errors - log full traceback
            logger.error(
                f"Unexpected error in {func.__name__}: {e}\n{traceback.format_exc()}"
            )
            await _notify_user_about_error(
                args,
                "❌ Виникла несподівана помилка. Спробуй /start або зв'яжись з підтримкою."
            )
    return wrapper


async def _notify_user_about_error(args: tuple, error_message: str):
    """Helper to notify user about error"""
    for arg in args:
        if isinstance(arg, Message):
            try:
                await arg.answer(error_message)
            except Exception:
                pass
            break
        elif isinstance(arg, CallbackQuery):
            try:
                await arg.message.answer(error_message)
                await arg.answer()
            except Exception:
                pass
            break


class StructuredLogger:
    """Structured logging with context"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log_user_action(
        self,
        user_id: int,
        action: str,
        details: dict = None,
        level: str = "info"
    ):
        """Log user action with context"""
        log_data = {
            "user_id": user_id,
            "action": action,
            "details": details or {}
        }

        log_func = getattr(self.logger, level)
        log_func(f"User action: {log_data}")

    def log_error(
        self,
        error: Exception,
        context: dict = None,
        user_id: int = None
    ):
        """Log error with full context"""
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "user_id": user_id,
            "context": context or {},
            "traceback": traceback.format_exc()
        }

        self.logger.error(f"Error occurred: {error_data}")

    def log_db_operation(
        self,
        operation: str,
        table: str,
        user_id: int = None,
        success: bool = True
    ):
        """Log database operation"""
        log_data = {
            "operation": operation,
            "table": table,
            "user_id": user_id,
            "success": success
        }

        if success:
            self.logger.info(f"DB operation: {log_data}")
        else:
            self.logger.error(f"DB operation failed: {log_data}")


async def setup_error_middleware(dp):
    """
    Setup global error handling middleware.
    Call this in bot.py during initialization.
    """
    @dp.errors()
    async def error_handler(update: Update, exception: Exception):
        """Global error handler"""
        logger.error(
            f"Update {update.update_id} caused error: {exception}\n"
            f"{traceback.format_exc()}"
        )

        # Try to notify user
        if update.message:
            try:
                await update.message.answer(
                    "❌ Виникла помилка при обробці повідомлення.\n"
                    "Спробуй /start або зв'яжись з підтримкою."
                )
            except Exception:
                pass
        elif update.callback_query:
            try:
                await update.callback_query.message.answer(
                    "❌ Виникла помилка при обробці.\n"
                    "Спробуй /start або зв'яжись з підтримкою."
                )
                await update.callback_query.answer()
            except Exception:
                pass

        return True  # Mark error as handled


def configure_logging(level: str = "INFO"):
    """Configure structured logging for the bot"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Reduce noise from libraries
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
