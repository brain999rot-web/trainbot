from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from models import Workout, ExerciseLog, Program
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict


class RecommendationService:
    """Сервіс розумних рекомендацій"""

    @staticmethod
    async def check_deload_needed(
        session: AsyncSession,
        user_id: int
    ) -> Dict:
        """Перевіряє чи потрібен делод"""
        # Отримуємо активну програму
        result = await session.execute(
            select(Program)
            .where(
                and_(
                    Program.user_id == user_id,
                    Program.is_active == True
                )
            )
            .order_by(Program.created_at.desc())
        )
        program = result.scalar_one_or_none()

        if not program:
            return {"needed": False, "reason": "Немає активної програми"}

        weeks_completed = program.weeks_completed
        weeks_since_creation = (datetime.utcnow() - program.created_at).days // 7

        # Рекомендуємо делод через 6-10 тижнів
        if weeks_since_creation >= 6:
            if weeks_since_creation >= 10:
                return {
                    "needed": True,
                    "urgency": "high",
                    "reason": f"Ти тренуєшся {weeks_since_creation} тижнів без делоду. Час відновитися!",
                    "recommendation": "Зменш об'єм на 40-60% та вагу на 10% на 1 тиждень"
                }
            else:
                return {
                    "needed": True,
                    "urgency": "medium",
                    "reason": f"Пройшло {weeks_since_creation} тижнів. Розглянь делод на цьому тижні.",
                    "recommendation": "Зменш об'єм на 40-50% та вагу на 5-10%"
                }

        return {
            "needed": False,
            "reason": f"Делод не потрібен (минуло {weeks_since_creation} тижнів)"
        }

    @staticmethod
    async def check_progress_stall(
        session: AsyncSession,
        user_id: int,
        exercise_name: str
    ) -> Dict:
        """Перевіряє застій прогресу по вправі"""
        # Отримуємо останні 6 тренувань з цією вправою
        result = await session.execute(
            select(Workout.id, Workout.workout_date)
            .join(ExerciseLog)
            .where(
                and_(
                    Workout.user_id == user_id,
                    ExerciseLog.exercise_name == exercise_name
                )
            )
            .order_by(Workout.workout_date.desc())
            .limit(6)
        )
        workout_ids = [(row[0], row[1]) for row in result.all()]

        if len(workout_ids) < 4:
            return {"stalled": False, "reason": "Недостатньо даних"}

        # Отримуємо максимальну вагу з кожного тренування
        max_weights = []
        for workout_id, workout_date in workout_ids:
            weight_result = await session.execute(
                select(ExerciseLog.weight)
                .where(
                    and_(
                        ExerciseLog.workout_id == workout_id,
                        ExerciseLog.exercise_name == exercise_name
                    )
                )
                .order_by(ExerciseLog.weight.desc())
                .limit(1)
            )
            max_weight = weight_result.scalar()
            if max_weight:
                max_weights.append((max_weight, workout_date))

        if len(max_weights) < 4:
            return {"stalled": False, "reason": "Недостатньо даних"}

        # Перевіряємо чи є прогрес
        latest_weight = max_weights[0][0]
        previous_weights = [w[0] for w in max_weights[1:4]]

        if all(latest_weight <= w for w in previous_weights):
            weeks_stalled = (max_weights[0][1] - max_weights[3][1]).days // 7

            if weeks_stalled >= 3:
                return {
                    "stalled": True,
                    "weeks": weeks_stalled,
                    "recommendation": (
                        f"Немає прогресу {weeks_stalled} тижні.\n"
                        "Рекомендації:\n"
                        "• Зменш вагу на 10% та працюй над технікою\n"
                        "• Збільш об'єм (додай 1-2 підходи)\n"
                        "• Заміни вправу на варіацію\n"
                        "• Перевір відновлення та сон"
                    )
                }

        return {"stalled": False, "reason": "Прогрес є"}

    @staticmethod
    async def check_overtraining(
        session: AsyncSession,
        user_id: int
    ) -> Dict:
        """Перевіряє ознаки перетренованості"""
        # Отримуємо тренування за останні 2 тижні
        two_weeks_ago = datetime.utcnow() - timedelta(days=14)

        result = await session.execute(
            select(Workout)
            .where(
                and_(
                    Workout.user_id == user_id,
                    Workout.workout_date >= two_weeks_ago
                )
            )
            .order_by(Workout.workout_date)
        )
        recent_workouts = result.scalars().all()

        if len(recent_workouts) < 8:
            return {"risk": "low", "reason": "Нормальна частота"}

        # Рахуємо загальний об'єм
        total_sets = 0
        for workout in recent_workouts:
            logs_result = await session.execute(
                select(ExerciseLog)
                .where(ExerciseLog.workout_id == workout.id)
            )
            total_sets += len(logs_result.scalars().all())

        # Перевіряємо інтенсивність
        workouts_per_week = len(recent_workouts) / 2
        avg_sets_per_workout = total_sets / len(recent_workouts)

        warnings = []

        if workouts_per_week > 6:
            warnings.append("Занадто багато тренувань на тиждень (>6)")

        if avg_sets_per_workout > 30:
            warnings.append("Дуже великий об'єм на тренування (>30 підходів)")

        # Перевіряємо регресію ваг
        result = await session.execute(
            select(ExerciseLog.exercise_name, ExerciseLog.weight, Workout.workout_date)
            .join(Workout)
            .where(
                and_(
                    Workout.user_id == user_id,
                    Workout.workout_date >= two_weeks_ago
                )
            )
            .order_by(Workout.workout_date)
        )
        logs = result.all()

        # Групуємо по вправах
        exercise_trends = defaultdict(list)
        for exercise_name, weight, date in logs:
            exercise_trends[exercise_name].append(weight)

        # Перевіряємо тренд
        declining_exercises = 0
        for exercise, weights in exercise_trends.items():
            if len(weights) >= 4:
                # Перевіряємо чи вага падає
                recent_avg = sum(weights[-2:]) / 2
                previous_avg = sum(weights[-4:-2]) / 2
                if recent_avg < previous_avg * 0.95:
                    declining_exercises += 1

        if declining_exercises >= 3:
            warnings.append(f"Регресія ваг у {declining_exercises} вправах")

        if warnings:
            return {
                "risk": "high",
                "warnings": warnings,
                "recommendation": (
                    "⚠️ Ознаки перетренованості!\n\n"
                    "Рекомендації:\n"
                    "• Зроби делод тиждень\n"
                    "• Зменш частоту тренувань\n"
                    "• Збільш час відпочинку\n"
                    "• Перевір сон та харчування"
                )
            }

        return {"risk": "low", "reason": "Все в нормі"}

    @staticmethod
    async def get_all_recommendations(
        session: AsyncSession,
        user_id: int
    ) -> List[Dict]:
        """Отримує всі рекомендації для користувача"""
        recommendations = []

        # Перевіряємо делод
        deload_check = await RecommendationService.check_deload_needed(session, user_id)
        if deload_check["needed"]:
            recommendations.append({
                "type": "deload",
                "urgency": deload_check["urgency"],
                "title": "⏸ Час для делоду",
                "message": deload_check["reason"],
                "action": deload_check["recommendation"]
            })

        # Перевіряємо перетренованість
        overtraining_check = await RecommendationService.check_overtraining(session, user_id)
        if overtraining_check["risk"] == "high":
            recommendations.append({
                "type": "overtraining",
                "urgency": "high",
                "title": "⚠️ Ризик перетренованості",
                "message": "\n".join(overtraining_check["warnings"]),
                "action": overtraining_check["recommendation"]
            })

        # Перевіряємо застій по основних вправах
        # Отримуємо топ-5 найчастіших вправ
        result = await session.execute(
            select(ExerciseLog.exercise_name, func.count(ExerciseLog.id).label('count'))
            .join(Workout)
            .where(Workout.user_id == user_id)
            .group_by(ExerciseLog.exercise_name)
            .order_by(func.count(ExerciseLog.id).desc())
            .limit(5)
        )

        top_exercises = [row[0] for row in result.all()]

        for exercise in top_exercises:
            stall_check = await RecommendationService.check_progress_stall(
                session, user_id, exercise
            )
            if stall_check["stalled"]:
                recommendations.append({
                    "type": "stall",
                    "urgency": "medium",
                    "title": f"📊 Застій у {exercise}",
                    "message": f"Немає прогресу {stall_check['weeks']} тижні",
                    "action": stall_check["recommendation"]
                })

        return recommendations
