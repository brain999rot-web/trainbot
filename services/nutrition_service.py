"""Nutrition service for database operations"""
import logging
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from models.nutrition import NutritionLog, NutritionProfile
from models.user import User

logger = logging.getLogger(__name__)


class NutritionService:
    """Service for nutrition tracking operations"""

    @staticmethod
    async def create_or_update_profile(
        session: AsyncSession,
        user_id: int,
        bmr: float,
        tdee: float,
        activity_multiplier: float,
        goal: str,
        target_calories: float,
        target_protein: float,
        target_carbs: float,
        target_fats: float
    ) -> NutritionProfile:
        """Створює або оновлює профіль харчування користувача"""
        try:
            # Перевіряємо чи існує профіль
            stmt = select(NutritionProfile).where(NutritionProfile.user_id == user_id)
            result = await session.execute(stmt)
            profile = result.scalar_one_or_none()

            if profile:
                # Оновлюємо існуючий
                profile.bmr = bmr
                profile.tdee = tdee
                profile.activity_multiplier = activity_multiplier
                profile.goal = goal
                profile.target_calories = target_calories
                profile.target_protein = target_protein
                profile.target_carbs = target_carbs
                profile.target_fats = target_fats
            else:
                # Створюємо новий
                profile = NutritionProfile(
                    user_id=user_id,
                    bmr=bmr,
                    tdee=tdee,
                    activity_multiplier=activity_multiplier,
                    goal=goal,
                    target_calories=target_calories,
                    target_protein=target_protein,
                    target_carbs=target_carbs,
                    target_fats=target_fats
                )
                session.add(profile)

            await session.commit()
            await session.refresh(profile)
            logger.info(f"Nutrition profile saved for user {user_id}")
            return profile

        except Exception as e:
            logger.error(f"Error saving nutrition profile for user {user_id}: {e}")
            await session.rollback()
            raise

    @staticmethod
    async def get_profile(session: AsyncSession, user_id: int) -> Optional[NutritionProfile]:
        """Отримує профіль харчування користувача"""
        stmt = select(NutritionProfile).where(NutritionProfile.user_id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def log_nutrition(
        session: AsyncSession,
        user_id: int,
        log_date: date,
        calories: float,
        protein: float,
        carbs: Optional[float] = None,
        fats: Optional[float] = None,
        notes: Optional[str] = None
    ) -> NutritionLog:
        """Логує харчування за день"""
        try:
            # Отримуємо цільові значення з профілю
            profile = await NutritionService.get_profile(session, user_id)
            target_calories = profile.target_calories if profile else None
            target_protein = profile.target_protein if profile else None

            # Перевіряємо чи вже є запис за цей день
            stmt = select(NutritionLog).where(
                and_(
                    NutritionLog.user_id == user_id,
                    NutritionLog.log_date == log_date
                )
            )
            result = await session.execute(stmt)
            log = result.scalar_one_or_none()

            if log:
                # Оновлюємо існуючий запис
                log.calories = calories
                log.protein = protein
                log.carbs = carbs
                log.fats = fats
                log.notes = notes
                log.target_calories = target_calories
                log.target_protein = target_protein
            else:
                # Створюємо новий
                log = NutritionLog(
                    user_id=user_id,
                    log_date=log_date,
                    calories=calories,
                    protein=protein,
                    carbs=carbs,
                    fats=fats,
                    notes=notes,
                    target_calories=target_calories,
                    target_protein=target_protein
                )
                session.add(log)

            await session.commit()
            await session.refresh(log)
            logger.info(f"Nutrition logged for user {user_id} on {log_date}")
            return log

        except Exception as e:
            logger.error(f"Error logging nutrition for user {user_id}: {e}")
            await session.rollback()
            raise

    @staticmethod
    async def get_logs(
        session: AsyncSession,
        user_id: int,
        days: int = 7
    ) -> List[NutritionLog]:
        """Отримує логи харчування за останні N днів"""
        start_date = date.today() - timedelta(days=days)

        stmt = select(NutritionLog).where(
            and_(
                NutritionLog.user_id == user_id,
                NutritionLog.log_date >= start_date
            )
        ).order_by(NutritionLog.log_date.desc())

        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_today_log(session: AsyncSession, user_id: int) -> Optional[NutritionLog]:
        """Отримує лог харчування за сьогодні"""
        today = date.today()

        stmt = select(NutritionLog).where(
            and_(
                NutritionLog.user_id == user_id,
                NutritionLog.log_date == today
            )
        )

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_weekly_average(session: AsyncSession, user_id: int) -> Dict[str, float]:
        """Розраховує середні значення за тиждень"""
        logs = await NutritionService.get_logs(session, user_id, days=7)

        if not logs:
            return {
                "avg_calories": 0,
                "avg_protein": 0,
                "days_logged": 0
            }

        total_calories = sum(log.calories for log in logs)
        total_protein = sum(log.protein for log in logs)
        days_count = len(logs)

        return {
            "avg_calories": round(total_calories / days_count, 1) if days_count > 0 else 0,
            "avg_protein": round(total_protein / days_count, 1) if days_count > 0 else 0,
            "days_logged": days_count
        }

    @staticmethod
    async def get_adherence_rate(session: AsyncSession, user_id: int, days: int = 7) -> float:
        """
        Розраховує відсоток дотримання плану харчування

        Returns:
            Процент (0-100) наскільки користувач дотримується цільових калорій
        """
        logs = await NutritionService.get_logs(session, user_id, days=days)
        profile = await NutritionService.get_profile(session, user_id)

        if not logs or not profile or not profile.target_calories:
            return 0.0

        # Рахуємо відсоток відхилення від цільових калорій
        total_adherence = 0
        for log in logs:
            if log.target_calories and log.target_calories > 0:
                deviation = abs(log.calories - log.target_calories) / log.target_calories
                adherence = max(0, 100 - (deviation * 100))
                total_adherence += adherence

        avg_adherence = total_adherence / len(logs) if logs else 0
        return round(avg_adherence, 1)

    @staticmethod
    def format_nutrition_stats(
        logs: List[NutritionLog],
        profile: Optional[NutritionProfile],
        weekly_avg: Dict[str, float],
        adherence: float
    ) -> str:
        """Форматує статистику харчування для виводу"""
        if not logs:
            return "📊 **Статистика харчування**\n\nУ тебе ще немає записів.\nПочни логувати їжу! 🍽"

        text = "📊 **СТАТИСТИКА ХАРЧУВАННЯ**\n\n"

        # Цільові значення
        if profile:
            text += f"🎯 **Твої цілі:**\n"
            text += f"• Калорії: {profile.target_calories:.0f} ккал\n"
            text += f"• Білок: {profile.target_protein:.0f}г\n"
            text += f"• Мета: {profile.goal}\n\n"

        # Середні за тиждень
        text += f"📈 **Середнє за тиждень ({weekly_avg['days_logged']} днів):**\n"
        text += f"• Калорії: {weekly_avg['avg_calories']:.0f} ккал\n"
        text += f"• Білок: {weekly_avg['avg_protein']:.0f}г\n\n"

        # Дотримання плану
        if adherence > 0:
            emoji = "🟢" if adherence >= 80 else "🟡" if adherence >= 60 else "🔴"
            text += f"{emoji} **Дотримання плану:** {adherence:.0f}%\n\n"

        # Останні 3 дні
        text += "📅 **Останні записи:**\n"
        for log in logs[:3]:
            date_str = log.log_date.strftime("%d.%m")
            text += f"\n**{date_str}:**\n"
            text += f"• {log.calories:.0f} ккал, {log.protein:.0f}г білка"

            if profile and profile.target_calories:
                diff = log.calories - profile.target_calories
                if abs(diff) > 50:
                    sign = "+" if diff > 0 else ""
                    text += f" ({sign}{diff:.0f})"
            text += "\n"

        return text
