from datetime import datetime
from sqlalchemy import BigInteger, String, Integer, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from database import Base


class ExerciseHistory(Base):
    """Історія виконання вправ для трекінгу прогресу"""
    __tablename__ = "exercise_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), nullable=False, index=True)
    exercise_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    # Дані про виконання
    avg_weight: Mapped[float] = mapped_column(Float, nullable=False)  # Середня вага у підходах
    max_weight: Mapped[float] = mapped_column(Float, nullable=False)  # Максимальна вага
    total_reps: Mapped[int] = mapped_column(Integer, nullable=False)  # Загальна кількість повторень
    total_sets: Mapped[int] = mapped_column(Integer, nullable=False)  # Кількість підходів

    # Розрахункові метрики
    volume: Mapped[float] = mapped_column(Float, nullable=False)  # Об'єм (вага * повторення)
    estimated_1rm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Розрахунковий 1RM

    # Рекомендації
    suggested_weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Рекомендована вага на наступне тренування
    progression_status: Mapped[str] = mapped_column(String(50), nullable=False)  # ready_to_increase, maintain, deload

    workout_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('ix_exercise_history_user_exercise_date', 'user_id', 'exercise_name', 'workout_date'),
    )
