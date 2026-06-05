from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import async_session
from services.database_service import (
    UserService,
    WorkoutService,
    ExerciseLogService
)
from models import Workout, ExerciseLog
from collections import defaultdict
from datetime import datetime, timedelta
import logging

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "📈 Мій прогрес")
async def show_progress(message: Message):
    """Показати прогрес користувача"""
    async with async_session() as session:
        user = await UserService.get_user(session, message.from_user.id)

        if not user:
            await message.answer("❌ Користувача не знайдено")
            return

        # Отримуємо статистику тренувань
        workouts = await WorkoutService.get_user_workouts(session, message.from_user.id, limit=30)

        if not workouts:
            await message.answer(
                "📊 У тебе ще немає записаних тренувань.\n\n"
                "Почни тренуватися: ➕ Записати тренування"
            )
            return

        # Загальна статистика
        total_workouts = len(workouts)

        # Тренування за останні 7 днів
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_workouts = [w for w in workouts if w.workout_date >= week_ago]

        # Отримуємо список унікальних вправ
        result = await session.execute(
            select(ExerciseLog.exercise_name)
            .join(Workout)
            .where(Workout.user_id == message.from_user.id)
            .distinct()
        )
        unique_exercises = result.scalars().all()

        progress_text = f"📈 **Твій прогрес**\n\n"
        progress_text += f"💪 Всього тренувань: {total_workouts}\n"
        progress_text += f"🔥 За останній тиждень: {len(recent_workouts)}\n"
        progress_text += f"🏋️ Унікальних вправ: {len(unique_exercises)}\n\n"

        # Останні 5 тренувань
        progress_text += "📋 **Останні тренування:**\n"
        for workout in workouts[:5]:
            date_str = workout.workout_date.strftime("%d.%m.%Y")
            progress_text += f"• {workout.workout_name} - {date_str}\n"

        await message.answer(progress_text)

        # Пропонуємо показати детальний прогрес по вправі
        if unique_exercises:
            exercises_list = "\n".join([f"• {ex}" for ex in unique_exercises[:10]])
            await message.answer(
                f"📊 **Детальний прогрес по вправі:**\n\n"
                f"Щоб переглянути прогрес по конкретній вправі, "
                f"відправ її назву.\n\n"
                f"Доступні вправи:\n{exercises_list}"
            )


@router.message(F.text)
async def show_exercise_progress(message: Message):
    """Показати прогрес по конкретній вправі"""
    exercise_name = message.text.strip()

    async with async_session() as session:
        # Перевіряємо чи це назва вправи
        history = await ExerciseLogService.get_exercise_history(
            session,
            message.from_user.id,
            exercise_name,
            limit=50
        )

        if not history or len(history) < 2:
            return  # Не вправа або недостатньо даних, ігноруємо

        # Групуємо по тренуванням
        workouts_dict = defaultdict(list)
        workout_dates = {}
        for log in history:
            workouts_dict[log.workout_id].append(log)
            if log.workout_id not in workout_dates:
                workout_dates[log.workout_id] = log.created_at

        # Сортуємо по даті
        sorted_workouts = sorted(
            workouts_dict.items(),
            key=lambda x: workout_dates[x[0]],
            reverse=True
        )

        progress_text = f"📊 **Прогрес: {exercise_name}**\n\n"

        # Останні 10 тренувань
        for i, (workout_id, logs) in enumerate(sorted_workouts[:10], 1):
            # Отримуємо дату тренування
            workout_result = await session.execute(
                select(Workout).where(Workout.id == workout_id)
            )
            workout = workout_result.scalar_one_or_none()

            if workout:
                date_str = workout.workout_date.strftime("%d.%m")
                progress_text += f"**{i}. {date_str}:**\n"

                for log in sorted(logs, key=lambda x: x.set_number):
                    progress_text += f"  Підхід {log.set_number}: {log.weight}кг x {log.reps} повт.\n"

                progress_text += "\n"

        # Аналіз прогресії
        if len(sorted_workouts) >= 2:
            latest_logs = sorted_workouts[0][1]
            previous_logs = sorted_workouts[1][1]

            latest_max_weight = max(log.weight for log in latest_logs)
            previous_max_weight = max(log.weight for log in previous_logs)

            if latest_max_weight > previous_max_weight:
                diff = latest_max_weight - previous_max_weight
                progress_text += f"📈 **Прогрес:** +{diff}кг з минулого разу! 💪"
            elif latest_max_weight == previous_max_weight:
                # Перевіряємо повторення
                latest_total_reps = sum(log.reps for log in latest_logs)
                previous_total_reps = sum(log.reps for log in previous_logs)

                if latest_total_reps > previous_total_reps:
                    diff = latest_total_reps - previous_total_reps
                    progress_text += f"📈 **Прогрес:** +{diff} повторень! 💪"
                else:
                    progress_text += "✅ Тримаєш вагу стабільно!"
            else:
                progress_text += "⚠️ Вага впала. Можливо потрібен відпочинок?"

        await message.answer(progress_text)
