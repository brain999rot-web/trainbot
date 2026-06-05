from datetime import datetime
from sqlalchemy import BigInteger, String, Integer, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from database import Base


class PersonalRecord(Base):
    """Особисті рекорди користувача по вправах"""
    __tablename__ = "personal_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), nullable=False, index=True)
    exercise_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    # Рекорди
    best_weight: Mapped[float] = mapped_column(Float, nullable=False)  # Найкраща вага
    best_reps: Mapped[int] = mapped_column(Integer, nullable=False)  # Повторень з цією вагою
    estimated_1rm: Mapped[float] = mapped_column(Float, nullable=False)  # Розрахунковий 1RM

    # Коли встановлено
    achieved_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    workout_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("workouts.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('ix_personal_records_user_exercise', 'user_id', 'exercise_name'),
    )
