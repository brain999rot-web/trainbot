from datetime import datetime
from sqlalchemy import BigInteger, String, Integer, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from database import Base


class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    experience: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    workouts_per_week: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    current_goal: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    programs: Mapped[List["Program"]] = relationship("Program", back_populates="user", cascade="all, delete-orphan")
    workouts: Mapped[List["Workout"]] = relationship("Workout", back_populates="user", cascade="all, delete-orphan")
