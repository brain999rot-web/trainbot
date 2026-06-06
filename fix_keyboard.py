"""
Скрипт для відновлення клавіатури для всіх користувачів
Використовувати якщо користувачі втратили доступ до кнопок
"""
import asyncio
from aiogram import Bot
from config import BOT_TOKEN
from keyboards.main_keyboards import get_main_menu_keyboard
import sqlite3


async def restore_keyboards():
    """Відновлює клавіатуру для всіх користувачів"""
    bot = Bot(token=BOT_TOKEN)

    # Отримуємо всіх користувачів з бази
    conn = sqlite3.connect('training_bot.db')
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT telegram_id FROM users')
        users = cursor.fetchall()

        print(f"Знайдено користувачів: {len(users)}")

        success_count = 0
        error_count = 0

        for (user_id,) in users:
            try:
                await bot.send_message(
                    user_id,
                    "🔄 **Оновлення бота**\n\n"
                    "Клавіатура відновлена! Тепер всі кнопки мають працювати.\n\n"
                    "Якщо у тебе все ще проблеми, напиши /start",
                    reply_markup=get_main_menu_keyboard(),
                    parse_mode="Markdown"
                )
                success_count += 1
                print(f"[OK] Sent to user {user_id}")
                await asyncio.sleep(0.1)  # Щоб не перевищити ліміт
            except Exception as e:
                error_count += 1
                print(f"[ERROR] Failed for user {user_id}: {e}")

        print(f"\n[SUCCESS] Total: {success_count}")
        print(f"[ERRORS] Total: {error_count}")

    finally:
        conn.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(restore_keyboards())
