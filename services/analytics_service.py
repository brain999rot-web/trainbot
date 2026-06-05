from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from models import Workout, ExerciseLog, Program
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple


class AnalyticsService:
    """Сервіс аналітики тренувань"""

    @staticmethod
    async def get_total_tonnage(
        session: AsyncSession,
        user_id: int,
        days: int = 30
    ) -> float:
        """Розраховує загальний тоннаж за період"""
        start_date = datetime.utcnow() - timedelta(days=days)

        result = await session.execute(
            select(func.sum(ExerciseLog.weight * ExerciseLog.reps))
            .join(Workout)
            .where(
                and_(
                    Workout.user_id == user_id,
                    Workout.workout_date >= start_date
                )
            )
        )
        tonnage = result.scalar() or 0.0
        return tonnage

    @staticmethod
    async def get_most_productive_days(
        session: AsyncSession,
        user_id: int
    ) -> Dict[str, int]:
        """Визначає найпродуктивніші дні тижня"""
        result = await session.execute(
            select(Workout)
            .where(Workout.user_id == user_id)
            .order_by(Workout.workout_date)
        )
        workouts = result.scalars().all()

        # Рахуємо тренування по днях тижня
        days_count = defaultdict(int)
        days_names = {
            0: "Понеділок",
            1: "Вівторок",
            2: "Середа",
            3: "Четвер",
            4: "П'ятниця",
            5: "Субота",
            6: "Неділя"
        }

        for workout in workouts:
            day_of_week = workout.workout_date.weekday()
            days_count[days_names[day_of_week]] += 1

        return dict(sorted(days_count.items(), key=lambda x: x[1], reverse=True))

    @staticmethod
    async def get_average_workout_duration(
        session: AsyncSession,
        user_id: int
    ) -> float:
        """Розраховує середню тривалість тренування"""
        result = await session.execute(
            select(func.avg(Workout.duration_minutes))
            .where(
                and_(
                    Workout.user_id == user_id,
                    Workout.duration_minutes.isnot(None)
                )
            )
        )
        avg_duration = result.scalar() or 0.0
        return avg_duration

    @staticmethod
    async def get_exercise_records(
        session: AsyncSession,
        user_id: int
    ) -> List[Dict]:
        """Отримує рекорди по вправах"""
        # Отримуємо всі вправи користувача
        result = await session.execute(
            select(ExerciseLog.exercise_name)
            .join(Workout)
            .where(Workout.user_id == user_id)
            .distinct()
        )
        exercises = result.scalars().all()

        records = []
        for exercise_name in exercises:
            # Знаходимо максимальну вагу
            max_weight_result = await session.execute(
                select(
                    func.max(ExerciseLog.weight),
                    ExerciseLog.reps,
                    Workout.workout_date
                )
                .join(Workout)
                .where(
                    and_(
                        Workout.user_id == user_id,
                        ExerciseLog.exercise_name == exercise_name
                    )
                )
                .order_by(ExerciseLog.weight.desc())
                .limit(1)
            )
            max_weight_data = max_weight_result.first()

            if max_weight_data:
                max_weight, reps, date = max_weight_data
                records.append({
                    "exercise": exercise_name,
                    "weight": max_weight,
                    "reps": reps,
                    "date": date
                })

        return sorted(records, key=lambda x: x["weight"], reverse=True)

    @staticmethod
    async def get_weekly_volume_by_muscle(
        session: AsyncSession,
        user_id: int
    ) -> Dict[str, int]:
        """Розраховує тижневий об'єм по м'язових групах"""
        week_ago = datetime.utcnow() - timedelta(days=7)

        result = await session.execute(
            select(ExerciseLog)
            .join(Workout)
            .where(
                and_(
                    Workout.user_id == user_id,
                    Workout.workout_date >= week_ago
                )
            )
        )
        logs = result.scalars().all()

        # Мапінг вправ на м'язові групи (спрощена версія)
        muscle_volume = defaultdict(int)

        for log in logs:
            # Визначаємо м'яз по назві вправи (можна покращити)
            if "біцепс" in log.exercise_name.lower() or "підтягування" in log.exercise_name.lower():
                muscle_volume["Біцепс"] += 1
            elif "трицепс" in log.exercise_name.lower() or "жим" in log.exercise_name.lower():
                muscle_volume["Трицепс"] += 1
            elif "груд" in log.exercise_name.lower():
                muscle_volume["Груди"] += 1
            elif "спин" in log.exercise_name.lower() or "тяга" in log.exercise_name.lower():
                muscle_volume["Спина"] += 1
            elif "плеч" in log.exercise_name.lower() or "дельт" in log.exercise_name.lower():
                muscle_volume["Плечі"] += 1
            elif "ніг" in log.exercise_name.lower() or "присід" in log.exercise_name.lower():
                muscle_volume["Ноги"] += 1

        return dict(muscle_volume)

    @staticmethod
    async def get_workout_streak(
        session: AsyncSession,
        user_id: int
    ) -> int:
        """Розраховує поточний streak тренувань"""
        result = await session.execute(
            select(Workout.workout_date)
            .where(Workout.user_id == user_id)
            .order_by(Workout.workout_date.desc())
        )
        workouts = result.scalars().all()

        if not workouts:
            return 0

        streak = 0
        current_date = datetime.utcnow().date()

        # Перевіряємо чи є тренування сьогодні або вчора
        latest_workout = workouts[0].date()
        days_diff = (current_date - latest_workout).days

        if days_diff > 1:
            return 0

        # Рахуємо streak
        for i, workout_date in enumerate(workouts):
            if i == 0:
                streak = 1
                continue

            days_between = (workouts[i-1].date() - workout_date.date()).days
            if days_between <= 2:  # Дозволяємо 1 день відпочинку
                streak += 1
            else:
                break

        return streak
