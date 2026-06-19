"""Handlers for 1RM strength calculator"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states import StrengthCalculatorStates
from utils.strength_calculator import StrengthCalculator
from utils.validators import InputValidator, ValidationError
from utils.error_handler import safe_handler, StructuredLogger

router = Router()
logger = StructuredLogger(__name__)


@router.message(F.text == "🏆 Калькулятор 1RM")
@safe_handler
async def start_1rm_calculator(message: Message, state: FSMContext):
    """Початок роботи з калькулятором 1RM"""
    logger.log_user_action(message.from_user.id, "start_1rm_calculator")

    await message.answer(
        "🏋️ **Калькулятор одноповторного максимуму (1RM, parse_mode="Markdown")**\n\n"
        "Введи назву вправи для розрахунку:\n"
        "Наприклад: Жим лежа, Присідання, Станова тяга\n\n"
        "💡 Введіть /cancel щоб скасувати"
    )
    await state.set_state(StrengthCalculatorStates.exercise_name)


@router.message(StrengthCalculatorStates.exercise_name)
@safe_handler
async def process_exercise_name(message: Message, state: FSMContext):
    """Обробка назви вправи"""
    exercise_name = InputValidator.sanitize_string(message.text, max_length=100)

    if len(exercise_name) < 3:
        await message.answer("❌ Назва вправи занадто коротка. Спробуй ще раз.")
        return

    await state.update_data(exercise_name=exercise_name)

    await message.answer(
        f"✅ Вправа: **{exercise_name}**\n\n"
        "Який вагу ти підняв? (у кг, parse_mode="Markdown")\n"
        "Наприклад: 100 або 75.5\n\n"
        "💡 Введіть /cancel щоб скасувати",
        parse_mode="Markdown"
    )
    await state.set_state(StrengthCalculatorStates.weight)


@router.message(StrengthCalculatorStates.weight)
@safe_handler
async def process_weight(message: Message, state: FSMContext):
    """Обробка ваги"""
    try:
        weight = float(message.text.strip().replace(',', '.'))

        if not (InputValidator.MIN_WEIGHT_KG <= weight <= InputValidator.MAX_WEIGHT_KG):
            await message.answer(
                f"❌ Вага повинна бути від {InputValidator.MIN_WEIGHT_KG} "
                f"до {InputValidator.MAX_WEIGHT_KG} кг"
            )
            return

        await state.update_data(weight=weight)

        await message.answer(
            f"✅ Вага: **{weight}кг**\n\n"
            "Скільки повторень ти виконав?\n"
            "Введи число від 1 до 12\n\n"
            "💡 Для точності формули краще використовувати 1-12 повторень\n\n"
            "💡 Введіть /cancel щоб скасувати",
            parse_mode="Markdown"
        )
        await state.set_state(StrengthCalculatorStates.reps)

    except ValueError:
        await message.answer("❌ Введи вагу числом, наприклад: 100 або 75.5")


@router.message(StrengthCalculatorStates.reps)
@safe_handler
async def process_reps(message: Message, state: FSMContext):
    """Обробка кількості повторень та розрахунок 1RM"""
    try:
        reps = int(message.text.strip())

        if not (1 <= reps <= 50):
            await message.answer("❌ Кількість повторень повинна бути від 1 до 50")
            return

        # Отримуємо всі дані
        data = await state.get_data()
        exercise_name = data['exercise_name']
        weight = data['weight']

        # Розраховуємо 1RM
        results = StrengthCalculator.calculate_average_1rm(weight, reps)
        one_rm = results['average']

        # Форматуємо результати
        message_text = StrengthCalculator.format_1rm_results(
            exercise_name, weight, reps, results
        )

        # Створюємо клавіатуру
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="📊 Тренувальні ваги",
                callback_data=f"training_weights_{one_rm}"
            )],
            [InlineKeyboardButton(
                text="🎯 Рекомендації по повтореннях",
                callback_data=f"rep_recommendations_{one_rm}"
            )],
            [InlineKeyboardButton(
                text="🔄 Новий розрахунок",
                callback_data="new_1rm_calculation"
            )]
        ])

        await message.answer(message_text, reply_markup=keyboard, parse_mode="Markdown")
        await state.clear()

        logger.log_user_action(
            message.from_user.id,
            "calculated_1rm",
            {"exercise": exercise_name, "weight": weight, "reps": reps, "1rm": one_rm}
        )

    except ValueError:
        await message.answer("❌ Введи кількість повторень числом від 1 до 50")


@router.callback_query(F.data.startswith("training_weights_"))
@safe_handler
async def show_training_weights(callback: CallbackQuery):
    """Показує тренувальні ваги"""
    try:
        parts = callback.data.split("_")
        if len(parts) < 3:
            await callback.answer("❌ Помилка даних", show_alert=True)
            return

        one_rm = float(parts[2])

        message_text = StrengthCalculator.format_training_weights(one_rm)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_1rm_results")]
        ])

        await callback.message.edit_text(
            message_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        await callback.answer()
    except (ValueError, IndexError) as e:
        logger.logger.error(f"Error in show_training_weights: {e}")
        await callback.answer("❌ Помилка обробки даних", show_alert=True)


@router.callback_query(F.data.startswith("rep_recommendations_"))
@safe_handler
async def show_rep_recommendations(callback: CallbackQuery):
    """Показує рекомендації по повтореннях"""
    try:
        parts = callback.data.split("_")
        if len(parts) < 3:
            await callback.answer("❌ Помилка даних", show_alert=True)
            return

        one_rm = float(parts[2])

        message_text = StrengthCalculator.format_rep_recommendations(one_rm)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_1rm_results")]
        ])

        await callback.message.edit_text(
            message_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        await callback.answer()
    except (ValueError, IndexError) as e:
        logger.logger.error(f"Error in show_rep_recommendations: {e}")
        await callback.answer("❌ Помилка обробки даних", show_alert=True)


@router.callback_query(F.data == "new_1rm_calculation")
@safe_handler
async def new_1rm_calculation(callback: CallbackQuery, state: FSMContext):
    """Починає новий розрахунок 1RM"""
    await callback.message.edit_text(
        "🏋️ **Калькулятор одноповторного максимуму (1RM, parse_mode="Markdown")**\n\n"
        "Введи назву вправи для розрахунку:\n"
        "Наприклад: Жим лежа, Присідання, Станова тяга\n\n"
        "💡 Введіть /cancel щоб скасувати"
    )
    await state.set_state(StrengthCalculatorStates.exercise_name)
    await callback.answer()
