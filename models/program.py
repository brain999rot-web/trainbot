from datetime import datetime
from sqlalchemy import BigInteger, String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from database import Base


class Program(Base):
    __tablename__ = "programs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    goal: Mapped[str] = mapped_column(String(100), nullable=False)
    split_type: Mapped[str] = mapped_column(String(50), nullable=False)
    workouts_per_week: Mapped[int] = mapped_column(Integer, nullable=False)
    program_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    weeks_completed: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="programs")
    workouts: Mapped[list["Workout"]] = relationship("Workout", back_populates="program", cascade="all, delete-orphan")
