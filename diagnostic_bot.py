"""
Тестовий бот для діагностики - логує всі вхідні повідомлення
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Catch-all обробник для ВСІХ повідомлень
    @dp.message()
    async def log_all_messages(message: Message):
        logger.info(f"Received message from {message.from_user.id}: {repr(message.text)}")
        await message.answer(f"Received: {message.text}")

    logger.info("Starting diagnostic bot...")
    logger.info("Send any message to see if bot receives it")

    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Bot stopped")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
