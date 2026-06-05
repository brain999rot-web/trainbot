from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from database import async_session
from services.database_service import (
    UserService,
    ProgramService,
    WorkoutService,
    ExerciseLogService
)
from keyboards.main_keyboards import (
    get_workout_selection_keyboard,
    get_exercise_selection_keyboard
)
from states import WorkoutLoggingStates
import logging
import re

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "➕ Записати тренування")
async def start_workout_logging(message: Message, state: FSMContext):
    """Початок логування тренування"""
    async with async_session() as session:
        program = await ProgramService.get_active_program(session, message.from_user.id)

        if not program:
            await message.answer(
                "❌ У тебе немає активної програми.\n\n"
                "Створи програму: 🏋 Створити програму"
            )
            return

        # Показуємо список тренувань
        workouts = program.program_data.get("workouts", [])
        workout_names = [w["name"] for w in workouts]

        await state.update_data(
            program_id=program.id,
            workouts=workouts
        )

        await message.answer(
            "📝 Обери тренування, яке виконуєш:",
            reply_markup=get_workout_selection_keyboard(workout_names)
        )
        await state.set_state(WorkoutLoggingStates.choose_workout)


@router.callback_query(WorkoutLoggingStates.choose_workout, F.data.startswith("workout_"))
async def choose_workout(callback: CallbackQuery, state: FSMContext):
    """Вибір тренування"""
    await callback.answer("🏋️ Починаємо!", show_alert=False)

    workout_idx = int(callback.data.split("_")[1])
    data = await state.get_data()
    workouts = data["workouts"]
    selected_workout = workouts[workout_idx]

    async with async_session() as session:
        # Створюємо новий workout запис
        workout = await WorkoutService.create_workout(
            session,
            user_id=callback.from_user.id,
            program_id=data["program_id"],
            workout_name=selected_workout["name"]
        )

        await state.update_data(
            workout_id=workout.id,
            selected_workout=selected_workout,
            current_exercise_idx=0
        )

        await callback.message.edit_text(
            f"✅ Тренування: **{selected_workout['name']}**\n\n"
            "Обери вправу для логування:",
            reply_markup=get_exercise_selection_keyboard(selected_workout["exercises"]),
            parse_mode="Markdown"
        )
        await state.set_state(WorkoutLoggingStates.choose_exercise)


@router.callback_query(WorkoutLoggingStates.choose_exercise, F.data.startswith("exercise_"))
async def choose_exercise(callback: CallbackQuery, state: FSMContext):
    """Вибір вправи для логування"""
    await callback.answer("📝 Завантажую історію...", show_alert=False)

    exercise_idx = int(callback.data.split("_")[1])
    data = await state.get_data()
    selected_workout = data["selected_workout"]
    exercise = selected_workout["exercises"][exercise_idx]

    await state.update_data(
        current_exercise=exercise,
        current_exercise_idx=exercise_idx,
        current_set=1,
        logged_sets=[]
    )

    # Показуємо останнє виконання цієї вправи
    async with async_session() as session:
        last_performance = await ExerciseLogService.get_last_exercise_performance(
            session,
            callback.from_user.id,
            exercise["name"]
        )

    last_perf_text = ""
    if last_performance:
        last_perf_text = "\n\n📊 **Минулого разу:**\n"
        for log in last_performance:
            last_perf_text += f"Підхід {log.set_number}: {log.weight}кг x {log.reps} повт.\n"

    await callback.message.edit_text(
        f"🏋️ **{exercise['name']}**\n\n"
        f"📋 План: {exercise['sets']} x {exercise['reps']} (RIR {exercise['rir']})\n"
        f"{last_perf_text}\n\n"
        f"**Підхід 1/{exercise['sets']}**\n\n"
        "Введи результат у форматі:\n"
        "`вага повторення`\n\n"
        "Приклад: `50 10`",
        parse_mode="Markdown"
    )
    await state.set_state(WorkoutLoggingStates.log_sets)


@router.message(WorkoutLoggingStates.log_sets)
async def log_set(message: Message, state: FSMContext):
    """Логування підходу"""
    try:
        # Використовуємо regex для кращої валідації
        match = re.match(r'(\d+(?:[.,]\d+)?)\s+(\d+)', message.text.strip())
        if not match:
            await message.answer("❌ Неправильний формат. Використай: `вага повторення`\nПриклад: `50 10`")
            return

        weight = float(match.group(1).replace(',', '.'))
        reps = int(match.group(2))

        # Валідація значень
        if weight <= 0 or weight > 500:
            await message.answer("❌ Вага повинна бути від 0 до 500 кг")
            return

        if reps <= 0 or reps > 100:
            await message.answer("❌ Повторення повинні бути від 1 до 100")
            return

        data = await state.get_data()
        workout_id = data["workout_id"]
        exercise = data["current_exercise"]
        current_set = data["current_set"]
        logged_sets = data.get("logged_sets", [])

        # Зберігаємо лог
        async with async_session() as session:
            try:
                await ExerciseLogService.log_exercise(
                    session,
                    workout_id=workout_id,
                    exercise_name=exercise["name"],
                    set_number=current_set,
                    reps=reps,
                    weight=weight
                )
            except Exception as e:
                logger.error(f"Помилка при збереженні логу: {e}")
                await message.answer("❌ Помилка при збереженні. Спробуй ще раз.")
                return

        logged_sets.append({"weight": weight, "reps": reps, "set": current_set})

        # Перевіряємо чи є ще підходи
        if current_set < exercise["sets"]:
            next_set = current_set + 1
            await state.update_data(
                current_set=next_set,
                logged_sets=logged_sets
            )

            # Показуємо що записано
            logged_text = "\n".join([f"Підхід {s['set']}: {s['weight']}кг x {s['reps']} повт." for s in logged_sets])

            await message.answer(
                f"✅ Записано: {weight}кг x {reps} повт.\n\n"
                f"📝 **Записані підходи:**\n{logged_text}\n\n"
                f"**Підхід {next_set}/{exercise['sets']}**\n\n"
                "Введи результат наступного підходу:"
            )
        else:
            # Всі підходи виконано
            logged_text = "\n".join([f"Підхід {s['set']}: {s['weight']}кг x {s['reps']} повт." for s in logged_sets])

            # Аналіз прогресії
            progression_advice = _analyze_progression(logged_sets, exercise, message.from_user.id)

            await message.answer(
                f"✅ Вправа завершена!\n\n"
                f"📝 **{exercise['name']}**\n{logged_text}\n\n"
                f"{progression_advice}"
            )

            # Повертаємось до вибору вправи
            selected_workout = data["selected_workout"]
            await message.answer(
                "Обери наступну вправу або завершуй тренування:",
                reply_markup=get_exercise_selection_keyboard(selected_workout["exercises"])
            )
            await state.set_state(WorkoutLoggingStates.choose_exercise)

    except ValueError:
        await message.answer("❌ Неправильний формат. Використай числа.\nПриклад: `50 10`")


@router.callback_query(WorkoutLoggingStates.choose_exercise, F.data == "finish_workout")
async def finish_workout(callback: CallbackQuery, state: FSMContext):
    """Завершення тренування"""
    await callback.answer("🎉 Чудова робота!", show_alert=False)
    await callback.message.edit_text(
        "✅ **Тренування завершено!**\n\n"
        "Відмінна робота! 💪\n\n"
        "Переглянути прогрес: 📈 Мій прогрес",
        parse_mode="Markdown"
    )
    await state.clear()


def _analyze_progression(logged_sets: list, exercise: dict, user_id: int) -> str:
    """Аналізує прогресію та дає рекомендації"""
    target_reps_range = exercise["reps"]

    # Парсимо діапазон повторень
    if "-" in target_reps_range:
        min_reps, max_reps = map(int, target_reps_range.split("-"))
    else:
        min_reps = max_reps = int(target_reps_range)

    # Перевіряємо чи всі підходи в верхній межі
    all_at_top = all(s["reps"] >= max_reps for s in logged_sets)

    if all_at_top:
        weight_increase = logged_sets[0]["weight"] * 0.025  # 2.5% збільшення
        return (
            f"🎯 **Рекомендація: ЗБІЛЬШУЙ ВАГУ!**\n\n"
            f"Ти досяг верхньої межі повторень у всіх підходах!\n"
            f"Наступного разу спробуй: {logged_sets[0]['weight'] + weight_increase:.1f}кг"
        )

    # Перевіряємо чи є прогрес
    all_in_range = all(min_reps <= s["reps"] <= max_reps for s in logged_sets)

    if all_in_range:
        return "✅ Чудово! Продовжуй у тому ж діапазоні."
    else:
        return "⚠️ Деякі підходи за межами цільового діапазону. Спробуй підібрати вагу."
