from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from models import User, Program, Workout, ExerciseLog
from typing import Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Сервіс для роботи з користувачами"""

    @staticmethod
    async def get_or_create_user(session: AsyncSession, telegram_id: int, username: str = None) -> User:
        """Отримує або створює користувача"""
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()

        if not user:
            user = User(telegram_id=telegram_id, username=username)
            session.add(user)
            await session.commit()
            await session.refresh(user)

        return user

    @staticmethod
    async def update_user_profile(
        session: AsyncSession,
        telegram_id: int,
        age: int = None,
        height: float = None,
        weight: float = None,
        gender: str = None,
        experience: str = None,
        workouts_per_week: int = None
    ) -> User:
        """Оновлює профіль користувача"""
        try:
            result = await session.execute(select(User).where(User.telegram_id == telegram_id))
            user = result.scalar_one_or_none()

            if user:
                if age is not None:
                    user.age = age
                if height is not None:
                    user.height = height
                if weight is not None:
                    user.weight = weight
                if gender is not None:
                    user.gender = gender
                if experience is not None:
                    user.experience = experience
                if workouts_per_week is not None:
                    user.workouts_per_week = workouts_per_week

                user.updated_at = datetime.utcnow()
                await session.commit()
                await session.refresh(user)

            return user
        except Exception as e:
            logger.error(f"Помилка при оновленні профілю користувача: {e}")
            await session.rollback()
            raise

    @staticmethod
    async def get_user(session: AsyncSession, telegram_id: int) -> Optional[User]:
        """Отримує користувача"""
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()


class ProgramService:
    """Сервіс для роботи з програмами"""

    @staticmethod
    async def create_program(
        session: AsyncSession,
        user_id: int,
        goal: str,
        split_type: str,
        workouts_per_week: int,
        program_data: dict
    ) -> Program:
        """Створює нову програму"""
        try:
            # Деактивуємо всі попередні програми
            await session.execute(
                update(Program)
                .where(Program.user_id == user_id)
                .values(is_active=False)
            )

            program = Program(
                user_id=user_id,
                goal=goal,
                split_type=split_type,
                workouts_per_week=workouts_per_week,
                program_data=program_data,
                is_active=True
            )
            session.add(program)
            await session.commit()
            await session.refresh(program)

            return program
        except Exception as e:
            logger.error(f"Помилка при створенні програми: {e}")
            await session.rollback()
            raise

    @staticmethod
    async def get_active_program(session: AsyncSession, user_id: int) -> Optional[Program]:
        """Отримує активну програму користувача"""
        result = await session.execute(
            select(Program)
            .where(Program.user_id == user_id, Program.is_active.is_(True))
            .order_by(Program.created_at.desc())
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_program_weeks(session: AsyncSession, program_id: int, weeks: int):
        """Оновлює кількість завершених тижнів"""
        await session.execute(
            update(Program)
            .where(Program.id == program_id)
            .values(weeks_completed=weeks, updated_at=datetime.utcnow())
        )
        await session.commit()


class WorkoutService:
    """Сервіс для роботи з тренуваннями"""

    @staticmethod
    async def create_workout(
        session: AsyncSession,
        user_id: int,
        program_id: int,
        workout_name: str
    ) -> Workout:
        """Створює нове тренування"""
        # Перевіряємо чи існує програма
        result = await session.execute(select(Program).where(Program.id == program_id))
        program = result.scalar_one_or_none()

        if not program:
            raise ValueError(f"Program with id {program_id} not found")

        if program.user_id != user_id:
            raise ValueError(f"Program {program_id} does not belong to user {user_id}")

        workout = Workout(
            user_id=user_id,
            program_id=program_id,
            workout_name=workout_name,
            workout_date=datetime.utcnow()
        )
        session.add(workout)
        await session.commit()
        await session.refresh(workout)

        return workout

    @staticmethod
    async def get_user_workouts(
        session: AsyncSession,
        user_id: int,
        limit: int = 10
    ) -> List[Workout]:
        """Отримує останні тренування користувача"""
        result = await session.execute(
            select(Workout)
            .where(Workout.user_id == user_id)
            .order_by(Workout.workout_date.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_workout_by_id(session: AsyncSession, workout_id: int) -> Optional[Workout]:
        """Отримує тренування за ID"""
        result = await session.execute(select(Workout).where(Workout.id == workout_id))
        return result.scalar_one_or_none()


class ExerciseLogService:
    """Сервіс для роботи з логами вправ"""

    @staticmethod
    async def log_exercise(
        session: AsyncSession,
        workout_id: int,
        exercise_name: str,
        set_number: int,
        reps: int,
        weight: float,
        rir: int = None,
        notes: str = None
    ) -> ExerciseLog:
        """Логує виконання вправи"""
        try:
            log = ExerciseLog(
                workout_id=workout_id,
                exercise_name=exercise_name,
                set_number=set_number,
                reps=reps,
                weight=weight,
                rir=rir,
                notes=notes
            )
            session.add(log)
            await session.commit()
            await session.refresh(log)

            return log
        except Exception as e:
            logger.error(f"Помилка при логуванні вправи: {e}")
            await session.rollback()
            raise

    @staticmethod
    async def get_exercise_history(
        session: AsyncSession,
        user_id: int,
        exercise_name: str,
        limit: int = 20
    ) -> List[ExerciseLog]:
        """Отримує історію виконання вправи"""
        result = await session.execute(
            select(ExerciseLog)
            .join(Workout)
            .where(
                Workout.user_id == user_id,
                ExerciseLog.exercise_name == exercise_name
            )
            .order_by(ExerciseLog.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_workout_logs(session: AsyncSession, workout_id: int) -> List[ExerciseLog]:
        """Отримує всі логи для тренування"""
        result = await session.execute(
            select(ExerciseLog)
            .where(ExerciseLog.workout_id == workout_id)
            .order_by(ExerciseLog.set_number)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_last_exercise_performance(
        session: AsyncSession,
        user_id: int,
        exercise_name: str
    ) -> List[ExerciseLog]:
        """Отримує останнє виконання вправи"""
        # Отримуємо останнє тренування з цією вправою
        result = await session.execute(
            select(Workout.id)
            .join(ExerciseLog)
            .where(
                Workout.user_id == user_id,
                ExerciseLog.exercise_name == exercise_name
            )
            .order_by(Workout.workout_date.desc())
            .limit(1)
        )
        last_workout_id = result.scalar_one_or_none()

        if not last_workout_id:
            return []

        # Отримуємо всі підходи з останнього тренування
        result = await session.execute(
            select(ExerciseLog)
            .where(
                ExerciseLog.workout_id == last_workout_id,
                ExerciseLog.exercise_name == exercise_name
            )
            .order_by(ExerciseLog.set_number)
        )
        return list(result.scalars().all())
