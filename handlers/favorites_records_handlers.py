"""Handlers for favorites, search and personal records"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from database import async_session
from services.favorites_service import FavoritesService, RecordsService
from utils.exercise_database import EXERCISE_DATABASE
from utils.error_handler import safe_handler, StructuredLogger

router = Router()
logger = StructuredLogger(__name__)


@router.message(F.text == "⭐ Избранное")
@safe_handler
async def show_favorites(message: Message):
    """Показує улюблені вправи"""
    async with async_session() as session:
        favorites = await FavoritesService.get_user_favorites(session, message.from_user.id)

        if not favorites:
            await message.answer(
                "⭐ **Улюблені вправи**\n\n"
                "У тебе ще немає улюблених вправ.\n\n"
                "Додай вправи в улюблені через базу вправ 📚",
                parse_mode="Markdown"
            )
            return

        text = f"⭐ **Улюблені вправи** ({len(favorites)})\n\n"

        buttons = []
        for fav in favorites:
            buttons.append([
                InlineKeyboardButton(
                    text=f"🏋️ {fav.exercise_name}",
                    callback_data=f"fav_detail_{fav.exercise_name}"
                )
            ])

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data.startswith("fav_detail_"))
@safe_handler
async def show_favorite_detail(callback: CallbackQuery):
    """Показує деталі улюбленої вправи"""
    exercise_name = callback.data.replace("fav_detail_", "")

    if not exercise_name:
        await callback.answer("❌ Невірна вправа", show_alert=True)
        return

    # Знаходимо вправу в базі
    exercise = None
    for ex in EXERCISE_DATABASE:
        if ex.name == exercise_name:
            exercise = ex
            break

    if not exercise:
        await callback.answer("❌ Вправу не знайдено", show_alert=True)
        return

    # Отримуємо рекорд
    async with async_session() as session:
        record = await RecordsService.get_user_record(session, callback.from_user.id, exercise_name)

    text = f"🏋️ **{exercise.name}**\n\n"
    text += f"🎯 **Основний м'яз:** {exercise.primary_muscle}\n"
    text += f"⚙️ **Обладнання:** {exercise.equipment}\n\n"

    if record:
        text += "🏆 **Твій рекорд:**\n"
        text += f"**{record.best_weight}кг × {record.best_reps} повт.**\n"
        text += f"Розрахунковий 1RM: {record.estimated_1rm:.1f}кг\n\n"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="❌ Видалити з улюблених",
            callback_data=f"remove_fav_{exercise_name}"
        )],
        [InlineKeyboardButton(
            text="⬅️ Назад до улюблених",
            callback_data="back_to_favorites"
        )]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("remove_fav_"))
@safe_handler
async def remove_from_favorites(callback: CallbackQuery):
    """Видаляє вправу з улюблених"""
    exercise_name = callback.data.replace("remove_fav_", "")

    async with async_session() as session:
        success = await FavoritesService.remove_from_favorites(
            session, callback.from_user.id, exercise_name
        )

    if success:
        await callback.answer("✅ Видалено з улюблених", show_alert=True)
        # Повертаємось до списку
        await show_favorites_callback(callback)
    else:
        await callback.answer("❌ Помилка при видаленні", show_alert=True)


@router.callback_query(F.data == "back_to_favorites")
@safe_handler
async def show_favorites_callback(callback: CallbackQuery):
    """Повертає до списку улюблених через callback"""
    async with async_session() as session:
        favorites = await FavoritesService.get_user_favorites(session, callback.from_user.id)

        if not favorites:
            await callback.message.edit_text(
                "⭐ **Улюблені вправи**\n\n"
                "У тебе немає улюблених вправ.",
                parse_mode="Markdown"
            )
            await callback.answer()
            return

        text = f"⭐ **Улюблені вправи** ({len(favorites)})\n\n"

        buttons = []
        for fav in favorites:
            buttons.append([
                InlineKeyboardButton(
                    text=f"🏋️ {fav.exercise_name}",
                    callback_data=f"fav_detail_{fav.exercise_name}"
                )
            ])

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await callback.answer()


@router.callback_query(F.data.startswith("add_to_fav_"))
@safe_handler
async def add_to_favorites(callback: CallbackQuery):
    """Додає вправу в улюблені"""
    exercise_name = callback.data.replace("add_to_fav_", "")

    async with async_session() as session:
        success = await FavoritesService.add_to_favorites(
            session, callback.from_user.id, exercise_name
        )

    if success:
        await callback.answer("⭐ Додано в улюблені!", show_alert=True)
    else:
        await callback.answer("❌ Вже в улюблених або помилка", show_alert=True)


@router.message(F.text == "🏅 Особисті рекорди")
@safe_handler
async def show_personal_records(message: Message):
    """Показує особисті рекорди користувача"""
    async with async_session() as session:
        records = await RecordsService.get_all_user_records(session, message.from_user.id)

        if not records:
            await message.answer(
                "🏅 **Особисті рекорди**\n\n"
                "У тебе ще немає записаних рекордів.\n\n"
                "Почни логувати тренування і твої рекорди будуть автоматично відслідковуватись! 💪",
                parse_mode="Markdown"
            )
            return

        text = f"🏅 **Особисті рекорди** ({len(records)})\n\n"
        text += "Топ-10 найкращих результатів:\n\n"

        for i, record in enumerate(records[:10], 1):
            text += f"{i}. **{record.exercise_name}**\n"
            text += f"   {record.best_weight}кг × {record.best_reps} повт. "
            text += f"(1RM: {record.estimated_1rm:.1f}кг)\n\n"

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="📊 Детальна статистика",
                callback_data="detailed_records"
            )]
        ])

        await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "detailed_records")
@safe_handler
async def show_detailed_records(callback: CallbackQuery):
    """Показує детальну статистику рекордів"""
    async with async_session() as session:
        records = await RecordsService.get_all_user_records(session, callback.from_user.id)

        buttons = []
        for record in records[:20]:  # Максимум 20
            buttons.append([
                InlineKeyboardButton(
                    text=f"🏋️ {record.exercise_name} - {record.estimated_1rm:.1f}кг",
                    callback_data=f"record_detail_{record.exercise_name}"
                )
            ])

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        text = "🏅 **Обери вправу для деталей:**\n\n"

        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await callback.answer()


@router.callback_query(F.data.startswith("record_detail_"))
@safe_handler
async def show_record_detail(callback: CallbackQuery):
    """Показує деталі рекорду"""
    exercise_name = callback.data.replace("record_detail_", "")

    async with async_session() as session:
        record = await RecordsService.get_user_record(session, callback.from_user.id, exercise_name)

    if not record:
        await callback.answer("❌ Рекорд не знайдено", show_alert=True)
        return

    text = RecordsService.format_record_message(record)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="⬅️ Назад до рекордів",
            callback_data="back_to_records"
        )]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "back_to_records")
@safe_handler
async def back_to_records(callback: CallbackQuery):
    """Повертає до списку рекордів"""
    await show_detailed_records(callback)
