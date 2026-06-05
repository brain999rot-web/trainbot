import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Reminder
from database import async_session
from aiogram import Bot
import logging

logger = logging.getLogger(__name__)


class ReminderService:
    """Сервіс нагадувань"""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.running = False

    async def start(self):
        """Запуск сервісу нагадувань"""
        self.running = True
        logger.info("Сервіс нагадувань запущено")

        while self.running:
            await self.check_reminders()
            await asyncio.sleep(60)  # Перевіряємо кожну хвилину

    async def stop(self):
        """Зупинка сервісу"""
        self.running = False
        logger.info("Сервіс нагадувань зупинено")

    async def check_reminders(self):
        """Перевіряє чи потрібно відправити нагадування"""
        now = datetime.utcnow()
        current_time = now.strftime("%H:%M")
        current_day = str(now.weekday())  # 0=Понеділок, 6=Неділя
        today = now.date()

        async with async_session() as session:
            result = await session.execute(
                select(Reminder)
                .where(
                    Reminder.is_active.is_(True),
                    Reminder.reminder_time == current_time
                )
            )
            reminders = result.scalars().all()

            for reminder in reminders:
                days = reminder.days_of_week.split(",")
                # Перевіряємо чи потрібно відправити сьогодні і чи не відправляли вже
                if current_day in days and (reminder.last_sent_date is None or reminder.last_sent_date != today):
                    await self.send_reminder(reminder, session, today)

    async def send_reminder(self, reminder: Reminder, session: AsyncSession, today):
        """Відправляє нагадування користувачу"""
        try:
            message = reminder.message or "⏰ Час тренуватися! 💪"
            await self.bot.send_message(
                chat_id=reminder.user_id,
                text=f"{message}\n\nГотовий до тренування? Натисни ➕ Записати тренування"
            )

            # Оновлюємо дату останнього відправлення
            reminder.last_sent_date = today
            await session.commit()

            logger.info(f"Нагадування відправлено користувачу {reminder.user_id}")
        except Exception as e:
            logger.error(f"Помилка при відправці нагадування: {e}")

    @staticmethod
    async def create_reminder(
        session: AsyncSession,
        user_id: int,
        reminder_time: str,
        days_of_week: str,
        message: str = None
    ) -> Reminder:
        """Створює нове нагадування"""
        reminder = Reminder(
            user_id=user_id,
            reminder_time=reminder_time,
            days_of_week=days_of_week,
            message=message,
            is_active=True
        )
        session.add(reminder)
        await session.commit()
        await session.refresh(reminder)
        return reminder

    @staticmethod
    async def get_user_reminders(
        session: AsyncSession,
        user_id: int
    ) -> list[Reminder]:
        """Отримує всі нагадування користувача"""
        result = await session.execute(
            select(Reminder)
            .where(Reminder.user_id == user_id)
            .order_by(Reminder.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def delete_reminder(
        session: AsyncSession,
        reminder_id: int
    ):
        """Видаляє нагадування"""
        result = await session.execute(
            select(Reminder)
            .where(Reminder.id == reminder_id)
        )
        reminder = result.scalar_one_or_none()

        if reminder:
            await session.delete(reminder)
            await session.commit()

    @staticmethod
    async def toggle_reminder(
        session: AsyncSession,
        reminder_id: int
    ):
        """Вмикає/вимикає нагадування"""
        result = await session.execute(
            select(Reminder)
            .where(Reminder.id == reminder_id)
        )
        reminder = result.scalar_one_or_none()

        if reminder:
            reminder.is_active = not reminder.is_active
            await session.commit()
