"""Handlers for nutrition tracking"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from datetime import date
from database import async_session
from services.nutrition_service import NutritionService
from services.database_service import UserService
from utils.nutrition_calculator import NutritionCalculator
from states.nutrition import NutritionCalculatorStates, NutritionLoggingStates
from utils.error_handler import safe_handler, StructuredLogger
from utils.validators import InputValidator

router = Router()
logger = StructuredLogger(__name__)


@router.message(F.text == "🍽 Калькулятор TDEE")
@safe_handler
async def start_tdee_calculator(message: Message, state: FSMContext):
    """Початок розрахунку TDEE"""
    logger.log_user_action(message.from_user.id, "start_tdee_calculator")

    # Отримуємо дані користувача
    async with async_session() as session:
        user = await UserService.get_user(session, message.from_user.id)

        if not user or not user.weight or not user.height or not user.age:
            await message.answer(
                "❌ Для розрахунку TDEE потрібні твої дані.\n\n"
                "Заповни профіль через ⚙ Налаштування",
                parse_mode="Markdown"
            )
            return

        # Зберігаємо дані користувача в стейт
        await state.update_data(
            weight=user.weight,
            height=user.height,
            age=user.age,
            gender=user.gender
        )

    # Клавіатура вибору рівня активності
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛋 Сидячий (1-2 тренування/тиждень)", callback_data="activity_light")],
        [InlineKeyboardButton(text="🚶 Помірний (3-5 тренувань/тиждень)", callback_data="activity_moderate")],
        [InlineKeyboardButton(text="🏃 Активний (6-7 тренувань/тиждень)", callback_data="activity_active")],
        [InlineKeyboardButton(text="🏋️ Дуже активний (2+ тренування/день)", callback_data="activity_very_active")]
    ])

    await message.answer(
        "🍽 **Калькулятор TDEE**\n\n"
        "Оберіть ваш рівень активності:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await state.set_state(NutritionCalculatorStates.activity_level)


@router.callback_query(F.data.startswith("activity_"))
@safe_handler
async def process_activity_level(callback: CallbackQuery, state: FSMContext):
    """Обробка рівня активності"""
    activity_map = {
        "activity_light": "light",
        "activity_moderate": "moderate",
        "activity_active": "active",
        "activity_very_active": "very_active"
    }

    activity = activity_map.get(callback.data, "moderate")
    await state.update_data(activity_level=activity)

    # Клавіатура вибору мети
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💪 Набір маси", callback_data="goal_bulk")],
        [InlineKeyboardButton(text="🏋️ Чистий набір (+10%)", callback_data="goal_lean_bulk")],
        [InlineKeyboardButton(text="⚖️ Підтримка ваги", callback_data="goal_maintain")],
        [InlineKeyboardButton(text="🔥 Схуднення (-15%)", callback_data="goal_cut")],
        [InlineKeyboardButton(text="⚡ Швидке схуднення (-25%)", callback_data="goal_aggressive_cut")]
    ])

    await callback.message.edit_text(
        "🎯 **Обери свою мету:**\n\n"
        "Це вплине на розрахунок калорій",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await state.set_state(NutritionCalculatorStates.goal)
    await callback.answer()


@router.callback_query(F.data.startswith("goal_"))
@safe_handler
async def process_goal(callback: CallbackQuery, state: FSMContext):
    """Обробка мети та розрахунок TDEE"""
    goal_map = {
        "goal_bulk": "bulk",
        "goal_lean_bulk": "lean_bulk",
        "goal_maintain": "maintain",
        "goal_cut": "cut",
        "goal_aggressive_cut": "aggressive_cut"
    }

    goal = goal_map.get(callback.data, "maintain")
    data = await state.get_data()

    # Розрахунки
    bmr = NutritionCalculator.calculate_bmr(
        data['weight'],
        data['height'],
        data['age'],
        data['gender']
    )

    tdee = NutritionCalculator.calculate_tdee(bmr, data['activity_level'])
    target_calories = NutritionCalculator.calculate_target_calories(tdee, goal)
    macros = NutritionCalculator.calculate_macros(target_calories, data['weight'], goal)

    # Зберігаємо в БД
    async with async_session() as session:
        await NutritionService.create_or_update_profile(
            session=session,
            user_id=callback.from_user.id,
            bmr=bmr,
            tdee=tdee,
            activity_multiplier=NutritionCalculator.ACTIVITY_LEVELS[data['activity_level']],
            goal=goal,
            target_calories=target_calories,
            target_protein=macros['protein'],
            target_carbs=macros['carbs'],
            target_fats=macros['fats']
        )

    # Форматуємо результат
    result_text = NutritionCalculator.format_nutrition_plan(
        bmr, tdee, target_calories, macros, goal
    )

    # Додаємо рекомендації
    recommendations = NutritionCalculator.get_recommendations(goal, tdee, target_calories)
    result_text += "\n" + recommendations

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Записати сьогоднішню їжу", callback_data="log_today_nutrition")],
        [InlineKeyboardButton(text="🔄 Перерахувати", callback_data="recalculate_tdee")]
    ])

    await callback.message.edit_text(
        result_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await state.clear()

    logger.log_user_action(
        callback.from_user.id,
        "calculated_tdee",
        {"bmr": bmr, "tdee": tdee, "target": target_calories, "goal": goal}
    )


@router.callback_query(F.data == "recalculate_tdee")
@safe_handler
async def recalculate_tdee(callback: CallbackQuery, state: FSMContext):
    """Перерахувати TDEE"""
    await callback.answer()
    await start_tdee_calculator(callback.message, state)


@router.message(F.text == "📝 Записати їжу")
@router.callback_query(F.data == "log_today_nutrition")
@safe_handler
async def start_nutrition_logging(event, state: FSMContext):
    """Початок логування харчування"""
    message = event.message if hasattr(event, 'message') else event
    user_id = event.from_user.id

    if isinstance(event, CallbackQuery):
        await event.answer()

    # Перевіряємо чи є профіль
    async with async_session() as session:
        profile = await NutritionService.get_profile(session, user_id)
        today_log = await NutritionService.get_today_log(session, user_id)

    if not profile:
        await message.answer(
            "❌ Спочатку розрахуй свій план харчування!\n\n"
            "Натисни 🍽 Калькулятор TDEE",
            parse_mode="Markdown"
        )
        return

    prompt = f"📝 **Логування харчування**\n\n"
    prompt += f"🎯 Твоя ціль: {profile.target_calories:.0f} ккал\n\n"

    if today_log:
        prompt += f"📊 **Сьогодні вже записано:**\n"
        prompt += f"• {today_log.calories:.0f} ккал\n"
        prompt += f"• {today_log.protein:.0f}г білка\n\n"
        prompt += "Новий запис перезапише старий.\n\n"

    prompt += "Введи кількість калорій за сьогодні:\n"
    prompt += "Наприклад: 2000\n\n"
    prompt += "💡 /cancel щоб скасувати"

    await message.answer(prompt, parse_mode="Markdown")
    await state.set_state(NutritionLoggingStates.calories)


@router.message(NutritionLoggingStates.calories)
@safe_handler
async def process_calories(message: Message, state: FSMContext):
    """Обробка калорій"""
    try:
        calories = float(message.text.strip().replace(',', '.'))

        if not (InputValidator.MIN_CALORIES <= calories <= InputValidator.MAX_CALORIES):
            await message.answer(
                f"❌ Калорії повинні бути від {InputValidator.MIN_CALORIES} "
                f"до {InputValidator.MAX_CALORIES}"
            )
            return

        await state.update_data(calories=calories)

        await message.answer(
            f"✅ Калорії: **{calories:.0f} ккал**\n\n"
            f"Тепер введи кількість білка (в грамах):\n"
            f"Наприклад: 150\n\n"
            f"💡 /cancel щоб скасувати",
            parse_mode="Markdown"
        )
        await state.set_state(NutritionLoggingStates.protein)

    except ValueError:
        await message.answer("❌ Введи число, наприклад: 2000")


@router.message(NutritionLoggingStates.protein)
@safe_handler
async def process_protein(message: Message, state: FSMContext):
    """Обробка білка"""
    try:
        protein = float(message.text.strip().replace(',', '.'))

        if not (0 <= protein <= 500):
            await message.answer("❌ Білок повинен бути від 0 до 500г")
            return

        data = await state.get_data()
        today = date.today()

        # Зберігаємо в БД
        async with async_session() as session:
            log = await NutritionService.log_nutrition(
                session=session,
                user_id=message.from_user.id,
                log_date=today,
                calories=data['calories'],
                protein=protein
            )

            profile = await NutritionService.get_profile(session, message.from_user.id)

        # Формуємо відповідь
        response = "✅ **Харчування записано!**\n\n"
        response += f"📅 Дата: {today.strftime('%d.%m.%Y')}\n"
        response += f"🔥 Калорії: {log.calories:.0f} ккал\n"
        response += f"🥩 Білок: {log.protein:.0f}г\n\n"

        if profile:
            cal_diff = log.calories - profile.target_calories
            prot_diff = log.protein - profile.target_protein

            response += "📊 **Відхилення від плану:**\n"

            if abs(cal_diff) < 50:
                response += f"• Калорії: 🟢 в цілі!\n"
            else:
                sign = "+" if cal_diff > 0 else ""
                emoji = "🔴" if abs(cal_diff) > 200 else "🟡"
                response += f"• Калорії: {emoji} {sign}{cal_diff:.0f} ккал\n"

            if abs(prot_diff) < 10:
                response += f"• Білок: 🟢 в цілі!\n"
            else:
                sign = "+" if prot_diff > 0 else ""
                emoji = "🔴" if abs(prot_diff) > 30 else "🟡"
                response += f"• Білок: {emoji} {sign}{prot_diff:.0f}г\n"

        await message.answer(response, parse_mode="Markdown")
        await state.clear()

        logger.log_user_action(
            message.from_user.id,
            "logged_nutrition",
            {"calories": log.calories, "protein": log.protein}
        )

    except ValueError:
        await message.answer("❌ Введи число, наприклад: 150")


@router.message(F.text == "📊 Статистика харчування")
@safe_handler
async def show_nutrition_stats(message: Message):
    """Показати статистику харчування"""
    async with async_session() as session:
        profile = await NutritionService.get_profile(session, message.from_user.id)
        logs = await NutritionService.get_logs(session, message.from_user.id, days=7)
        weekly_avg = await NutritionService.get_weekly_average(session, message.from_user.id)
        adherence = await NutritionService.get_adherence_rate(session, message.from_user.id, days=7)

    stats_text = NutritionService.format_nutrition_stats(logs, profile, weekly_avg, adherence)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Записати сьогодні", callback_data="log_today_nutrition")],
        [InlineKeyboardButton(text="🔄 Оновити план", callback_data="recalculate_tdee")]
    ])

    await message.answer(stats_text, reply_markup=keyboard, parse_mode="Markdown")
