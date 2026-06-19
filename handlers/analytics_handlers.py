from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from database import async_session
from services.analytics_service import AnalyticsService
from services.recommendation_service import RecommendationService
from keyboards.main_keyboards import get_main_menu_keyboard
import logging

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "📊 Аналітика")
async def show_analytics(message: Message):
    """Показати повну аналітику"""
    async with async_session() as session:
        # Загальний тоннаж за 30 днів
        tonnage_30 = await AnalyticsService.get_total_tonnage(session, message.from_user.id, 30)
        tonnage_7 = await AnalyticsService.get_total_tonnage(session, message.from_user.id, 7)

        # Найпродуктивніші дні
        productive_days = await AnalyticsService.get_most_productive_days(session, message.from_user.id)

        # Середня тривалість
        avg_duration = await AnalyticsService.get_average_workout_duration(session, message.from_user.id)

        # Рекорди
        records = await AnalyticsService.get_exercise_records(session, message.from_user.id)

        # Streak
        streak = await AnalyticsService.get_workout_streak(session, message.from_user.id)

        # Тижневий об'єм по м'язах
        muscle_volume = await AnalyticsService.get_weekly_volume_by_muscle(session, message.from_user.id)

        analytics_text = "📊 **АНАЛІТИКА ТРЕНУВАНЬ**\n\n"

        # Тоннаж
        analytics_text += f"💪 **Загальний тоннаж:**\n"
        analytics_text += f"• За 7 днів: {tonnage_7:.0f} кг\n"
        analytics_text += f"• За 30 днів: {tonnage_30:.0f} кг\n\n"

        # Streak
        if streak > 0:
            analytics_text += f"🔥 **Streak:** {streak} тренувань підряд!\n\n"

        # Продуктивні дні
        if productive_days:
            analytics_text += "📅 **Найпродуктивніші дні:**\n"
            for day, count in list(productive_days.items())[:3]:
                analytics_text += f"• {day}: {count} тренувань\n"
            analytics_text += "\n"

        # Середня тривалість
        if avg_duration > 0:
            analytics_text += f"⏱ **Середня тривалість:** {avg_duration:.0f} хв\n\n"

        # Об'єм по м'язах
        if muscle_volume:
            analytics_text += "🎯 **Тижневий об'єм по м'язах:**\n"
            for muscle, sets in sorted(muscle_volume.items(), key=lambda x: x[1], reverse=True):
                analytics_text += f"• {muscle}: {sets} підходів\n"
            analytics_text += "\n"

        # Топ-3 рекорди
        if records:
            analytics_text += "🏆 **Твої рекорди:**\n"
            for record in records[:3]:
                date_str = record['date'].strftime("%d.%m")
                analytics_text += f"• {record['exercise']}\n"
                analytics_text += f"  {record['weight']}кг x {record['reps']} ({date_str})\n"

        await message.answer(analytics_text, parse_mode="Markdown")


@router.message(F.text == "💡 Рекомендації")
async def show_recommendations(message: Message):
    """Показати розумні рекомендації"""
    async with async_session() as session:
        recommendations = await RecommendationService.get_all_recommendations(
            session,
            message.from_user.id
        )

        if not recommendations:
            await message.answer(
                "✅ **Все чудово!**\n\n"
                "У тебе немає критичних рекомендацій.\n"
                "Продовжуй тренуватися і прогресувати! 💪",
                parse_mode="Markdown"
            )
            return

        # Сортуємо за терміновістю
        urgency_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: urgency_order.get(x.get("urgency", "low"), 2))

        rec_text = "💡 **РОЗУМНІ РЕКОМЕНДАЦІЇ**\n\n"

        for i, rec in enumerate(recommendations, 1):
            rec_text += f"{rec['title']}\n"
            rec_text += f"{rec['message']}\n\n"
            rec_text += f"**Що робити:**\n{rec['action']}\n\n"
            rec_text += "─" * 30 + "\n\n"

        await message.answer(rec_text, parse_mode="Markdown")
