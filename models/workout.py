from datetime import datetime
from sqlalchemy import BigInteger, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from database import Base


class Workout(Base):
    __tablename__ = "workouts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    program_id: Mapped[int] = mapped_column(Integer, ForeignKey("programs.id"), nullable=False)
    workout_name: Mapped[str] = mapped_column(String(100), nullable=False)
    workout_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    user: Mapped["User"] = relationship("User", back_populates="workouts")
    program: Mapped["Program"] = relationship("Program", back_populates="workouts")
    exercise_logs: Mapped[List["ExerciseLog"]] = relationship("ExerciseLog", back_populates="workout", cascade="all, delete-orphan")
