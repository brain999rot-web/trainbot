"""
Webhook інтеграція бота з Flask
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update
from config import BOT_TOKEN
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

logger = logging.getLogger(__name__)

# Глобальні змінні для бота
bot = None
dp = None


async def setup_bot():
    """Ініціалізація бота для webhook"""
    global bot, dp

    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Реєстрація роутерів
    dp.include_router(registration.router)
    dp.include_router(program_handlers.router)
    dp.include_router(workout_handlers.router)
    dp.include_router(analytics_handlers.router)
    dp.include_router(timer_handlers.router)
    dp.include_router(exercise_database_handlers.router)
    dp.include_router(strength_calculator_handlers.router)
    dp.include_router(favorites_records_handlers.router)
    dp.include_router(nutrition_handlers.router)
    # progress_handlers має бути ОСТАННІМ, бо там є загальний F.text handler
    dp.include_router(progress_handlers.router)

    logger.info("Бот ініціалізовано для webhook")
    return bot, dp


async def process_update(update_data: dict):
    """Обробка одного update від Telegram"""
    global bot, dp

    if bot is None or dp is None:
        await setup_bot()

    update = Update(**update_data)
    await dp.feed_update(bot, update)


async def set_webhook(webhook_url: str):
    """Встановлення webhook"""
    global bot

    if bot is None:
        bot, _ = await setup_bot()

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(webhook_url)
    logger.info(f"Webhook встановлено: {webhook_url}")


async def remove_webhook():
    """Видалення webhook"""
    global bot

    if bot is None:
        bot = Bot(token=BOT_TOKEN)

    await bot.delete_webhook()
    logger.info("Webhook видалено")
