"""Тест для перевірки роботи кнопок"""
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from database import init_db

# Імпортуємо всі роутери
from handlers import (
    registration,
    program_handlers,
    workout_handlers,
    progress_handlers,
    analytics_handlers,
    timer_handlers,
    exercise_database_handlers,
    strength_calculator_handlers,
    favorites_records_handlers,
    nutrition_handlers
)


async def main():
    """Тестовий запуск бота"""
    print("Perevirka roboty obrobnykiv knopok...\n")

    # Ініціалізація БД
    await init_db()

    # Ініціалізація бота
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
    dp.include_router(strength_calculator_handlers.router)
    dp.include_router(favorites_records_handlers.router)
    dp.include_router(nutrition_handlers.router)

    # Перевірка зареєстрованих обробників
    print("Registered message handlers:")
    for i, handler in enumerate(dp.message.handlers, 1):
        print(f"  {i}. {handler.callback.__name__}")

    print("\nBot started. Test buttons in Telegram...")
    print("Press Ctrl+C to stop\n")

    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        print("\nBot stopped")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
