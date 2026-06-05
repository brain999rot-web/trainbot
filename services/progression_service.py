"""Service for tracking exercise history and auto-progression"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from models.exercise_history import ExerciseHistory
from models.exercise_log import ExerciseLog
from models.workout import Workout
import logging

logger = logging.getLogger(__name__)


class ProgressionService:
    """Сервіс для аналізу прогресії та рекомендацій"""

    # Константи для прогресії
    PROGRESSION_THRESHOLD = 0.95  # Якщо виконано 95%+ від цільових повторень
    WEIGHT_INCREASE_PERCENT = 2.5  # Збільшення ваги на 2.5%
    MIN_WEIGHT_INCREASE = 2.5  # Мінімальне збільшення 2.5кг
    DELOAD_WEEKS = 8  # Рекомендувати делод через 8 тижнів

    @staticmethod
    async def analyze_workout_and_save_history(
        session: AsyncSession,
        user_id: int,
        exercise_name: str,
        exercise_logs: List[ExerciseLog],
        target_reps_range: str
    ) -> Dict:
        """
        Аналізує виконане тренування та зберігає історію.
        Повертає рекомендації для користувача.
        """
        if not exercise_logs:
            return {"status": "no_data"}

        # Розраховуємо метрики
        total_sets = len(exercise_logs)
        total_reps = sum(log.reps for log in exercise_logs)
        avg_weight = sum(log.weight for log in exercise_logs) / total_sets
        max_weight = max(log.weight for log in exercise_logs)
        volume = sum(log.weight * log.reps for log in exercise_logs)

        # Розраховуємо 1RM (формула Brzycki)
        estimated_1rm = ProgressionService._calculate_1rm(max_weight, max(log.reps for log in exercise_logs))

        # Аналізуємо прогресію
        min_reps, max_reps = ProgressionService._parse_reps_range(target_reps_range)
        progression_status, suggested_weight = await ProgressionService._analyze_progression(
            session, user_id, exercise_name, exercise_logs, max_reps, avg_weight
        )

        # Зберігаємо історію
        history = ExerciseHistory(
            user_id=user_id,
            exercise_name=exercise_name,
            avg_weight=avg_weight,
            max_weight=max_weight,
            total_reps=total_reps,
            total_sets=total_sets,
            volume=volume,
            estimated_1rm=estimated_1rm,
            suggested_weight=suggested_weight,
            progression_status=progression_status,
            workout_date=datetime.utcnow()
        )

        session.add(history)
        await session.commit()

        return {
            "status": "success",
            "progression_status": progression_status,
            "suggested_weight": suggested_weight,
            "volume": volume,
            "estimated_1rm": estimated_1rm,
            "avg_weight": avg_weight
        }

    @staticmethod
    def _calculate_1rm(weight: float, reps: int) -> float:
        """Розраховує 1RM за формулою Brzycki"""
        if reps == 1:
            return weight
        if reps > 12:
            reps = 12  # Формула неточна для >12 повторень
        return weight * (36 / (37 - reps))

    @staticmethod
    def _parse_reps_range(reps_range: str) -> Tuple[int, int]:
        """Парсить діапазон повторень (наприклад "8-12")"""
        try:
            if "-" in reps_range:
                parts = reps_range.split("-")
                min_reps = int(parts[0].strip())
                max_reps = int(parts[1].strip())
                return min_reps, max_reps
            else:
                reps = int(reps_range.strip())
                return reps, reps
        except (ValueError, IndexError) as e:
            logger.error(f"Error parsing reps range '{reps_range}': {e}")
            # Повертаємо стандартний діапазон
            return 8, 12

    @staticmethod
    async def _analyze_progression(
        session: AsyncSession,
        user_id: int,
        exercise_name: str,
        current_logs: List[ExerciseLog],
        target_max_reps: int,
        current_avg_weight: float
    ) -> Tuple[str, Optional[float]]:
        """
        Аналізує чи користувач готовий до збільшення ваги.

        Returns:
            (progression_status, suggested_weight)
            progression_status: ready_to_increase, maintain, deload
        """
        # Перевіряємо чи всі підходи досягли верхньої межі повторень
        all_at_max = all(log.reps >= target_max_reps for log in current_logs)

        if all_at_max:
            # Готовий збільшувати вагу
            increase = max(
                ProgressionService.MIN_WEIGHT_INCREASE,
                current_avg_weight * (ProgressionService.WEIGHT_INCREASE_PERCENT / 100)
            )
            suggested_weight = round(current_avg_weight + increase, 1)
            return "ready_to_increase", suggested_weight

        # Перевіряємо чи потрібен делод (8+ тижнів без прогресу)
        last_increase = await ProgressionService._get_last_weight_increase(
            session, user_id, exercise_name
        )

        if last_increase and last_increase > ProgressionService.DELOAD_WEEKS:
            return "deload", round(current_avg_weight * 0.85, 1)

        # Продовжуємо з поточною вагою
        return "maintain", current_avg_weight

    @staticmethod
    async def _get_last_weight_increase(
        session: AsyncSession,
        user_id: int,
        exercise_name: str
    ) -> Optional[int]:
        """Повертає скільки тижнів минуло з останнього збільшення ваги"""
        stmt = select(ExerciseHistory).where(
            and_(
                ExerciseHistory.user_id == user_id,
                ExerciseHistory.exercise_name == exercise_name,
                ExerciseHistory.progression_status == "ready_to_increase"
            )
        ).order_by(desc(ExerciseHistory.workout_date)).limit(1)

        result = await session.execute(stmt)
        last_increase = result.scalar_one_or_none()

        if not last_increase:
            return None

        weeks_since = (datetime.utcnow() - last_increase.workout_date).days // 7
        return weeks_since

    @staticmethod
    async def get_exercise_history(
        session: AsyncSession,
        user_id: int,
        exercise_name: str,
        limit: int = 10
    ) -> List[ExerciseHistory]:
        """Отримує історію виконання вправи"""
        stmt = select(ExerciseHistory).where(
            and_(
                ExerciseHistory.user_id == user_id,
                ExerciseHistory.exercise_name == exercise_name
            )
        ).order_by(desc(ExerciseHistory.workout_date)).limit(limit)

        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_suggested_weight(
        session: AsyncSession,
        user_id: int,
        exercise_name: str
    ) -> Optional[float]:
        """Отримує рекомендовану вагу для вправи"""
        stmt = select(ExerciseHistory).where(
            and_(
                ExerciseHistory.user_id == user_id,
                ExerciseHistory.exercise_name == exercise_name
            )
        ).order_by(desc(ExerciseHistory.workout_date)).limit(1)

        result = await session.execute(stmt)
        last_history = result.scalar_one_or_none()

        if not last_history:
            return None

        return last_history.suggested_weight

    @staticmethod
    async def get_progress_summary(
        session: AsyncSession,
        user_id: int,
        days: int = 30
    ) -> Dict:
        """Отримує загальний прогрес користувача за період"""
        since_date = datetime.utcnow() - timedelta(days=days)

        stmt = select(ExerciseHistory).where(
            and_(
                ExerciseHistory.user_id == user_id,
                ExerciseHistory.workout_date >= since_date
            )
        ).order_by(ExerciseHistory.workout_date)

        result = await session.execute(stmt)
        history = list(result.scalars().all())

        if not history:
            return {"total_workouts": 0, "total_volume": 0, "exercises_progressed": 0}

        # Розрахунки
        total_volume = sum(h.volume for h in history)
        total_workouts = len(set(h.workout_date.date() for h in history))

        # Вправи з прогресом
        exercises_progressed = len([
            h for h in history if h.progression_status == "ready_to_increase"
        ])

        # Середній приріст ваги
        exercise_groups = {}
        for h in history:
            if h.exercise_name not in exercise_groups:
                exercise_groups[h.exercise_name] = []
            exercise_groups[h.exercise_name].append(h)

        weight_increases = []
        for exercise, records in exercise_groups.items():
            if len(records) >= 2:
                first_weight = records[0].avg_weight
                last_weight = records[-1].avg_weight
                increase = ((last_weight - first_weight) / first_weight) * 100
                weight_increases.append(increase)

        avg_weight_increase = sum(weight_increases) / len(weight_increases) if weight_increases else 0

        return {
            "total_workouts": total_workouts,
            "total_volume": round(total_volume, 1),
            "exercises_progressed": exercises_progressed,
            "avg_weight_increase_percent": round(avg_weight_increase, 1),
            "period_days": days
        }

    @staticmethod
    def format_progression_message(analysis: Dict) -> str:
        """Форматує повідомлення з рекомендаціями"""
        if analysis.get("status") != "success":
            return "Недостатньо даних для аналізу прогресії."

        status = analysis["progression_status"]
        suggested = analysis.get("suggested_weight")

        if status == "ready_to_increase":
            return (
                f"🎯 **ГОТОВИЙ ДО ПРОГРЕСІЇ!**\n\n"
                f"Ти досяг верхньої межі повторень у всіх підходах!\n"
                f"Наступного разу спробуй: **{suggested}кг**\n\n"
                f"📈 Об'єм: {analysis['volume']:.1f}кг\n"
                f"💪 Розрахунковий 1RM: {analysis['estimated_1rm']:.1f}кг"
            )
        elif status == "deload":
            return (
                f"⚠️ **РЕКОМЕНДОВАНО ДЕЛОД**\n\n"
                f"Ти тренуєшся без прогресії вже 8+ тижнів.\n"
                f"Зроби тиждень делоду з вагою: **{suggested}кг** (85%)\n\n"
                f"Це допоможе відновитися та знову прогресувати!"
            )
        else:
            return (
                f"✅ **Продовжуй у тому ж діапазоні**\n\n"
                f"Вага: **{suggested}кг**\n"
                f"📈 Об'єм: {analysis['volume']:.1f}кг\n"
                f"💪 Розрахунковий 1RM: {analysis['estimated_1rm']:.1f}кг\n\n"
                f"Коли досягнеш верхньої межі повторень у всіх підходах - збільшуй вагу!"
            )
