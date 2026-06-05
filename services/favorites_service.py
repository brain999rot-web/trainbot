"""Service for favorites and personal records"""
from datetime import datetime
from typing import List, Optional, Dict
from sqlalchemy import select, and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.favorite_exercise import FavoriteExercise
from models.personal_record import PersonalRecord
from utils.strength_calculator import StrengthCalculator
import logging

logger = logging.getLogger(__name__)


class FavoritesService:
    """Сервіс для роботи з улюбленими вправами"""

    @staticmethod
    async def add_to_favorites(
        session: AsyncSession,
        user_id: int,
        exercise_name: str
    ) -> bool:
        """Додає вправу в улюблені"""
        try:
            # Перевіряємо чи вже є
            stmt = select(FavoriteExercise).where(
                and_(
                    FavoriteExercise.user_id == user_id,
                    FavoriteExercise.exercise_name == exercise_name
                )
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                return False  # Вже є в улюблених

            favorite = FavoriteExercise(
                user_id=user_id,
                exercise_name=exercise_name
            )
            session.add(favorite)
            await session.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding to favorites: {e}")
            await session.rollback()
            return False

    @staticmethod
    async def remove_from_favorites(
        session: AsyncSession,
        user_id: int,
        exercise_name: str
    ) -> bool:
        """Видаляє вправу з улюблених"""
        stmt = select(FavoriteExercise).where(
            and_(
                FavoriteExercise.user_id == user_id,
                FavoriteExercise.exercise_name == exercise_name
            )
        )
        result = await session.execute(stmt)
        favorite = result.scalar_one_or_none()

        if favorite:
            await session.delete(favorite)
            await session.commit()
            return True
        return False

    @staticmethod
    async def is_favorite(
        session: AsyncSession,
        user_id: int,
        exercise_name: str
    ) -> bool:
        """Перевіряє чи вправа в улюблених"""
        stmt = select(FavoriteExercise).where(
            and_(
                FavoriteExercise.user_id == user_id,
                FavoriteExercise.exercise_name == exercise_name
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def get_user_favorites(
        session: AsyncSession,
        user_id: int
    ) -> List[FavoriteExercise]:
        """Отримує всі улюблені вправи користувача"""
        stmt = select(FavoriteExercise).where(
            FavoriteExercise.user_id == user_id
        ).order_by(desc(FavoriteExercise.created_at))

        result = await session.execute(stmt)
        return list(result.scalars().all())


class RecordsService:
    """Сервіс для роботи з особистими рекордами"""

    @staticmethod
    async def update_record_if_better(
        session: AsyncSession,
        user_id: int,
        exercise_name: str,
        weight: float,
        reps: int,
        workout_id: Optional[int] = None
    ) -> Dict:
        """
        Оновлює рекорд якщо новий результат кращий

        Returns:
            dict з інформацією чи встановлено новий рекорд
        """
        try:
            # Розраховуємо 1RM для нового результату
            new_1rm = StrengthCalculator.calculate_1rm_brzycki(weight, reps)

            # Отримуємо поточний рекорд
            stmt = select(PersonalRecord).where(
                and_(
                    PersonalRecord.user_id == user_id,
                    PersonalRecord.exercise_name == exercise_name
                )
            )
            result = await session.execute(stmt)
            current_record = result.scalar_one_or_none()

            is_new_record = False
            record_type = None

            if not current_record:
                # Перший рекорд
                new_record = PersonalRecord(
                    user_id=user_id,
                    exercise_name=exercise_name,
                    best_weight=weight,
                    best_reps=reps,
                    estimated_1rm=new_1rm,
                    achieved_at=datetime.utcnow(),
                    workout_id=workout_id
                )
                session.add(new_record)
                await session.commit()
                is_new_record = True
                record_type = "first"
            elif new_1rm > current_record.estimated_1rm:
                # Новий рекорд
                current_record.best_weight = weight
                current_record.best_reps = reps
                current_record.estimated_1rm = new_1rm
                current_record.achieved_at = datetime.utcnow()
                current_record.workout_id = workout_id
                await session.commit()
                is_new_record = True
                record_type = "improved"

            return {
                "is_new_record": is_new_record,
                "record_type": record_type,
                "new_1rm": new_1rm,
                "old_1rm": current_record.estimated_1rm if current_record else None,
                "improvement": new_1rm - current_record.estimated_1rm if current_record else None
            }
        except Exception as e:
            logger.error(f"Error updating record: {e}")
            await session.rollback()
            # Повертаємо безпечний результат
            return {
                "is_new_record": False,
                "record_type": None,
                "new_1rm": 0,
                "old_1rm": None,
                "improvement": None
            }

    @staticmethod
    async def get_user_record(
        session: AsyncSession,
        user_id: int,
        exercise_name: str
    ) -> Optional[PersonalRecord]:
        """Отримує рекорд користувача для вправи"""
        stmt = select(PersonalRecord).where(
            and_(
                PersonalRecord.user_id == user_id,
                PersonalRecord.exercise_name == exercise_name
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_user_records(
        session: AsyncSession,
        user_id: int,
        limit: int = 50
    ) -> List[PersonalRecord]:
        """Отримує всі рекорди користувача"""
        stmt = select(PersonalRecord).where(
            PersonalRecord.user_id == user_id
        ).order_by(desc(PersonalRecord.estimated_1rm)).limit(limit)

        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_top_records(
        session: AsyncSession,
        user_id: int,
        top_n: int = 5
    ) -> List[PersonalRecord]:
        """Отримує топ N рекордів користувача"""
        stmt = select(PersonalRecord).where(
            PersonalRecord.user_id == user_id
        ).order_by(desc(PersonalRecord.estimated_1rm)).limit(top_n)

        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_records_count(
        session: AsyncSession,
        user_id: int
    ) -> int:
        """Повертає кількість рекордів користувача"""
        stmt = select(func.count(PersonalRecord.id)).where(
            PersonalRecord.user_id == user_id
        )
        result = await session.execute(stmt)
        return result.scalar_one()

    @staticmethod
    def format_record_message(record: PersonalRecord) -> str:
        """Форматує повідомлення про рекорд"""
        message = f"🏋️ **{record.exercise_name}**\n\n"
        message += f"🏆 Рекорд: **{record.best_weight}кг × {record.best_reps} повт.**\n"
        message += f"💪 Розрахунковий 1RM: **{record.estimated_1rm:.1f}кг**\n"
        message += f"📅 Встановлено: {record.achieved_at.strftime('%d.%m.%Y')}\n"

        return message

    @staticmethod
    def format_new_record_notification(
        exercise_name: str,
        record_info: Dict
    ) -> str:
        """Форматує повідомлення про новий рекорд"""
        # Перевірка на валідність даних
        if not record_info or not record_info.get('record_type'):
            return ""

        if record_info['record_type'] == 'first':
            return (
                f"🎉 **ПЕРШИЙ РЕКОРД!**\n\n"
                f"🏋️ {exercise_name}\n"
                f"💪 Розрахунковий 1RM: **{record_info['new_1rm']:.1f}кг**\n\n"
                f"Так тримати! Продовжуй у тому ж дусі! 💪"
            )
        elif record_info['record_type'] == 'improved':
            improvement = record_info.get('improvement', 0)
            old_1rm = record_info.get('old_1rm', 0)
            new_1rm = record_info.get('new_1rm', 0)

            if old_1rm == 0:
                return ""

            improvement_percent = (improvement / old_1rm * 100) if old_1rm > 0 else 0

            return (
                f"🎉 **НОВИЙ РЕКОРД!**\n\n"
                f"🏋️ {exercise_name}\n"
                f"📈 Старий 1RM: {old_1rm:.1f}кг\n"
                f"💪 Новий 1RM: **{new_1rm:.1f}кг**\n"
                f"⬆️ Поліпшення: **+{improvement:.1f}кг** ({improvement_percent:.1f}%)\n\n"
                f"Чудова робота! 🔥"
            )
        return ""
