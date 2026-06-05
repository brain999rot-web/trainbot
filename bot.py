import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from database import init_db
from handlers import (
    registration,
    program_handlers,
    workout_handlers,
    progress_handlers,
    analytics_handlers,
    timer_handlers,
    exercise_database_handlers,
    strength_calculator_handlers,
    favorites_records_handlers
)
from services.reminder_service import ReminderService
from utils.error_handler import configure_logging, setup_error_middleware

# Налаштування логування
configure_logging("INFO")
logger = logging.getLogger(__name__)


async def main():
    """Головна функція запуску бота"""
    logger.info("Запуск бота...")

    # Ініціалізація бази даних
    try:
        await init_db()
        logger.info("База даних ініціалізована")
    except Exception as e:
        logger.error(f"Помилка ініціалізації БД: {e}")
        return

    # Ініціалізація бота та диспетчера
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Налаштування глобальної обробки помилок
    await setup_error_middleware(dp)

    # Реєстрація роутерів
    dp.include_router(registration.router)
    dp.include_router(program_handlers.router)
    dp.include_router(workout_handlers.router)
    dp.include_router(progress_handlers.router)
    dp.include_router(analytics_handlers.router)
    dp.include_router(timer_handlers.router)
    dp.include_router(exercise_database_handlers.router)
    dp.include_router(strength_calculator_handlers.router)
    dp.include_router(favorites_records_handlers.router)

    logger.info("Роутери зареєстровані")

    # Запуск сервісу нагадувань
    reminder_service = ReminderService(bot)
    reminder_task = asyncio.create_task(reminder_service.start())

    # Запуск бота
    try:
        logger.info("Бот запущено успішно!")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Критична помилка при роботі бота: {e}")
    finally:
        await reminder_service.stop()
        reminder_task.cancel()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот зупинено")
