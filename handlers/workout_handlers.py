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
from services.progression_service import ProgressionService
from services.favorites_service import RecordsService
from keyboards.main_keyboards import (
    get_workout_selection_keyboard,
    get_exercise_selection_keyboard
)
from states import WorkoutLoggingStates
from utils.validators import InputValidator, ValidationError
from utils.error_handler import safe_handler, StructuredLogger
import logging

router = Router()
logger = StructuredLogger(__name__)


@router.message(F.text == "➕ Записати тренування")
@safe_handler
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

        logger.log_user_action(message.from_user.id, "start_workout_logging")

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
@safe_handler
async def choose_workout(callback: CallbackQuery, state: FSMContext):
    """Вибір тренування"""
    await callback.answer("🏋️ Починаємо!", show_alert=False)

    try:
        workout_idx = int(callback.data.split("_")[1])
    except (ValueError, IndexError):
        await callback.answer("❌ Помилка вибору тренування", show_alert=True)
        return

    data = await state.get_data()
    workouts = data.get("workouts", [])

    if workout_idx >= len(workouts):
        await callback.answer("❌ Невірний індекс тренування", show_alert=True)
        return

    selected_workout = workouts[workout_idx]

    async with async_session() as session:
        try:
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
                reply_markup=get_exercise_selection_keyboard(selected_workout["exercises"], parse_mode="Markdown"),
                parse_mode="Markdown"
            )
            await state.set_state(WorkoutLoggingStates.choose_exercise)
        except ValueError as e:
            logger.logger.error(f"Error creating workout: {e}")
            await callback.message.answer(
                "❌ Помилка створення тренування. Можливо програма була видалена."
            )
            await state.clear()


@router.callback_query(WorkoutLoggingStates.choose_exercise, F.data.startswith("exercise_"))
@safe_handler
async def choose_exercise(callback: CallbackQuery, state: FSMContext):
    """Вибір вправи для логування"""
    await callback.answer("📝 Завантажую історію...", show_alert=False)

    try:
        exercise_idx = int(callback.data.split("_")[1])
    except (ValueError, IndexError):
        await callback.answer("❌ Помилка вибору вправи", show_alert=True)
        return

    data = await state.get_data()
    selected_workout = data.get("selected_workout")

    if not selected_workout or "exercises" not in selected_workout:
        await callback.message.answer("❌ Помилка: дані тренування втрачено. Почни заново.")
        await state.clear()
        return

    exercises = selected_workout["exercises"]
    if exercise_idx >= len(exercises):
        await callback.answer("❌ Невірний індекс вправи", show_alert=True)
        return

    exercise = exercises[exercise_idx]

    await state.update_data(
        current_exercise=exercise,
        current_exercise_idx=exercise_idx,
        current_set=1,
        logged_sets=[]
    )

    # Показуємо останнє виконання та рекомендовану вагу
    async with async_session() as session:
        last_performance = await ExerciseLogService.get_last_exercise_performance(
            session,
            callback.from_user.id,
            exercise["name"]
        )

        # Отримуємо рекомендовану вагу з історії
        suggested_weight = await ProgressionService.get_suggested_weight(
            session,
            callback.from_user.id,
            exercise["name"]
        )

    last_perf_text = ""
    if last_performance:
        last_perf_text = "\n\n📊 **Минулого разу:**\n"
        for log in last_performance:
            last_perf_text += f"Підхід {log.set_number}: {log.weight}кг x {log.reps} повт.\n"

    suggested_text = ""
    if suggested_weight:
        suggested_text = f"\n\n💡 **Рекомендована вага:** {suggested_weight}кг"

    await callback.message.edit_text(
        f"🏋️ **{exercise['name']}**\n\n"
        f"📋 План: {exercise['sets']} x {exercise['reps']} (RIR {exercise['rir']})\n"
        f"{last_perf_text}"
        f"{suggested_text}\n\n"
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
        # Використовуємо валідатор
        weight, reps = InputValidator.validate_weight_reps(message.text)

        data = await state.get_data()
        workout_id = data.get("workout_id")
        exercise = data.get("current_exercise")
        current_set = data.get("current_set", 1)
        logged_sets = data.get("logged_sets", [])

        # Перевірка наявності необхідних даних
        if not workout_id or not exercise:
            await message.answer(
                "❌ Помилка: дані тренування втрачено. Почни заново через меню."
            )
            await state.clear()
            return

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
                logger.logger.error(f"Помилка при збереженні логу: {e}")
                await message.answer("❌ Помилка при збереженні. Спробуй ще раз.")
                return

        logged_sets.append({"weight": weight, "reps": reps, "set": current_set})

        # Перевіряємо чи є ще підходи
        total_sets = exercise.get("sets", 3)
        if current_set < total_sets:
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
            , parse_mode="Markdown")
        else:
            # Всі підходи виконано - аналіз прогресії з новим сервісом
            logged_text = "\n".join([f"Підхід {s['set']}: {s['weight']}кг x {s['reps']} повт." for s in logged_sets])

            # Отримуємо логи з БД та аналізуємо прогресію
            async with async_session() as session:
                # Отримуємо логи цієї вправи
                from sqlalchemy import select
                from models.exercise_log import ExerciseLog

                stmt = select(ExerciseLog).where(
                    ExerciseLog.workout_id == workout_id,
                    ExerciseLog.exercise_name == exercise["name"]
                )
                result = await session.execute(stmt)
                exercise_logs = list(result.scalars().all())

                # Аналізуємо прогресію та зберігаємо історію
                analysis = await ProgressionService.analyze_workout_and_save_history(
                    session,
                    message.from_user.id,
                    exercise["name"],
                    exercise_logs,
                    exercise["reps"]
                )

                progression_message = ProgressionService.format_progression_message(analysis)

                # Перевіряємо та оновлюємо рекорди
                if logged_sets:
                    best_set = max(logged_sets, key=lambda s: s['weight'])
                    record_info = await RecordsService.update_record_if_better(
                        session,
                        message.from_user.id,
                        exercise["name"],
                        best_set['weight'],
                        best_set['reps'],
                        workout_id
                    )
                else:
                    record_info = {"is_new_record": False}

            await message.answer(
                f"✅ Вправа завершена!\n\n"
                f"📝 **{exercise['name']}**\n{logged_text}\n\n"
                f"{progression_message}"
            , parse_mode="Markdown")

            # Якщо новий рекорд - повідомляємо
            if record_info['is_new_record']:
                record_message = RecordsService.format_new_record_notification(
                    exercise["name"],
                    record_info
                )
                await message.answer(record_message, parse_mode="Markdown")

            # Повертаємось до вибору вправи
            selected_workout = data["selected_workout"]
            await message.answer(
                "Обери наступну вправу або завершуй тренування:",
                reply_markup=get_exercise_selection_keyboard(selected_workout["exercises"])
            )
            await state.set_state(WorkoutLoggingStates.choose_exercise)

    except ValidationError as e:
        await message.answer(str(e))


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
