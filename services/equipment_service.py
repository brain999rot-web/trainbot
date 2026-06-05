"""Service for managing user equipment and exercise filtering"""
from typing import List, Set
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from models.user_equipment import UserEquipment
from utils.exercise_database import ExerciseData, EXERCISE_DATABASE
import logging

logger = logging.getLogger(__name__)


class EquipmentService:
    """Сервіс для роботи з обладнанням користувача"""

    # Стандартне обладнання, доступне в більшості залів
    DEFAULT_EQUIPMENT = [
        "гантелі",
        "штанга",
        "лавка",
        "турнік",
        "власна вага"
    ]

    # Додаткове обладнання
    ADVANCED_EQUIPMENT = [
        "Машина Сміта",
        "кросовер",
        "верхній блок",
        "горизонтальний блок",
        "EZ-штанга",
        "Лавка Скотта",
        "Leg Extension",
        "Жим ногами",
        "бруси",
        "паралельні бруси"
    ]

    @staticmethod
    async def get_user_equipment(
        session: AsyncSession,
        user_id: int
    ) -> Set[str]:
        """Отримує список доступного обладнання користувача"""
        stmt = select(UserEquipment).where(
            and_(
                UserEquipment.user_id == user_id,
                UserEquipment.is_available == True
            )
        )

        result = await session.execute(stmt)
        equipment_list = result.scalars().all()

        if not equipment_list:
            # Якщо користувач ще не налаштував - повертаємо стандартний набір
            return set(EquipmentService.DEFAULT_EQUIPMENT)

        return set(eq.equipment_name for eq in equipment_list)

    @staticmethod
    async def set_user_equipment(
        session: AsyncSession,
        user_id: int,
        equipment_list: List[str]
    ):
        """Встановлює обладнання користувача"""
        # Видаляємо старі записи
        stmt = select(UserEquipment).where(UserEquipment.user_id == user_id)
        result = await session.execute(stmt)
        old_equipment = result.scalars().all()

        for eq in old_equipment:
            await session.delete(eq)

        # Додаємо нові
        for equipment_name in equipment_list:
            new_eq = UserEquipment(
                user_id=user_id,
                equipment_name=equipment_name,
                is_available=True
            )
            session.add(new_eq)

        await session.commit()

    @staticmethod
    async def filter_exercises_by_equipment(
        session: AsyncSession,
        user_id: int,
        exercises: List[ExerciseData]
    ) -> List[ExerciseData]:
        """Фільтрує вправи по доступному обладнанню"""
        user_equipment = await EquipmentService.get_user_equipment(session, user_id)

        filtered = []
        for exercise in exercises:
            # Розбиваємо обладнання вправи на окремі елементи
            required_equipment = set(
                eq.strip().lower() for eq in exercise.equipment.split(',')
            )

            # Перевіряємо чи все обладнання доступне
            if required_equipment.issubset(set(eq.lower() for eq in user_equipment)):
                filtered.append(exercise)
            # Або є альтернативне обладнання
            elif exercise.alternative_equipment:
                for alt in exercise.alternative_equipment:
                    alt_set = set(eq.strip().lower() for eq in alt.split(','))
                    if alt_set.issubset(set(eq.lower() for eq in user_equipment)):
                        filtered.append(exercise)
                        break

        return filtered

    @staticmethod
    def get_all_equipment() -> List[str]:
        """Повертає весь список можливого обладнання"""
        return EquipmentService.DEFAULT_EQUIPMENT + EquipmentService.ADVANCED_EQUIPMENT

    @staticmethod
    async def add_equipment(
        session: AsyncSession,
        user_id: int,
        equipment_name: str
    ):
        """Додає одиницю обладнання"""
        # Перевіряємо чи вже є
        stmt = select(UserEquipment).where(
            and_(
                UserEquipment.user_id == user_id,
                UserEquipment.equipment_name == equipment_name
            )
        )
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.is_available = True
        else:
            new_eq = UserEquipment(
                user_id=user_id,
                equipment_name=equipment_name,
                is_available=True
            )
            session.add(new_eq)

        await session.commit()

    @staticmethod
    async def remove_equipment(
        session: AsyncSession,
        user_id: int,
        equipment_name: str
    ):
        """Видаляє обладнання"""
        stmt = select(UserEquipment).where(
            and_(
                UserEquipment.user_id == user_id,
                UserEquipment.equipment_name == equipment_name
            )
        )
        result = await session.execute(stmt)
        equipment = result.scalar_one_or_none()

        if equipment:
            equipment.is_available = False
            await session.commit()
