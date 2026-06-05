import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta
import logging

router = Router()
logger = logging.getLogger(__name__)

# Словник для зберігання активних таймерів
active_timers = {}


@router.callback_query(F.data.startswith("timer_"))
async def start_rest_timer(callback: CallbackQuery, state: FSMContext):
    """Запуск таймера відпочинку"""
    duration = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    await callback.answer(f"⏱ Таймер {duration}с запущено!", show_alert=False)

    # Зберігаємо таймер
    timer_id = f"{user_id}_{duration}_{datetime.utcnow().timestamp()}"
    active_timers[user_id] = {
        "start": datetime.utcnow(),
        "duration": duration,
        "timer_id": timer_id
    }

    # Запускаємо таймер
    await asyncio.sleep(duration)

    # Перевіряємо чи таймер не скасовано
    if user_id in active_timers and active_timers[user_id].get("timer_id") == timer_id:
        await callback.message.answer(
            f"⏰ **Відпочинок закінчено!**\n\n"
            f"Час для наступного підходу 💪"
        )
        del active_timers[user_id]


@router.message(F.text == "⏱ Таймер відпочинку")
async def timer_menu(message: Message):
    """Меню таймера"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="60с", callback_data="timer_60"),
                InlineKeyboardButton(text="90с", callback_data="timer_90"),
                InlineKeyboardButton(text="120с", callback_data="timer_120")
            ],
            [
                InlineKeyboardButton(text="180с", callback_data="timer_180"),
                InlineKeyboardButton(text="300с", callback_data="timer_300")
            ],
            [
                InlineKeyboardButton(text="❌ Скасувати таймер", callback_data="timer_cancel")
            ]
        ]
    )

    await message.answer(
        "⏱ **Таймер відпочинку**\n\n"
        "Обери час відпочинку між підходами:",
        reply_markup=keyboard
    )


@router.callback_query(F.data == "timer_cancel")
async def cancel_timer(callback: CallbackQuery):
    """Скасування таймера"""
    user_id = callback.from_user.id

    if user_id in active_timers:
        del active_timers[user_id]
        await callback.answer("⏱ Таймер скасовано", show_alert=False)
    else:
        await callback.answer("⏱ Немає активного таймера", show_alert=True)

    await callback.message.delete()
