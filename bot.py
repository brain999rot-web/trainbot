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
    exercise_database_handlers
)
from services.reminder_service import ReminderService

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Головна функція запуску бота"""
    logger.info("Запуск бота...")

    # Ініціалізація бази даних
    await init_db()
    logger.info("База даних ініціалізована")

    # Ініціалізація бота та диспетчера
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Реєстрація роутерів
    dp.include_router(registration.router)
    dp.include_router(program_handlers.router)
    dp.include_router(workout_handlers.router)
    dp.include_router(progress_handlers.router)
    dp.include_router(analytics_handlers.router)
    dp.include_router(timer_handlers.router)
    dp.include_router(exercise_database_handlers.router)

    logger.info("Роутери зареєстровані")

    # Запуск сервісу нагадувань
    reminder_service = ReminderService(bot)
    reminder_task = asyncio.create_task(reminder_service.start())

    # Запуск бота
    try:
        logger.info("Бот запущено успішно!")
        await dp.start_polling(bot)
    finally:
        await reminder_service.stop()
        reminder_task.cancel()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот зупинено")
