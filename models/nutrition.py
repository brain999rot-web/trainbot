"""Nutrition tracking model"""
from datetime import datetime, timezone
from sqlalchemy import BigInteger, Integer, Float, String, DateTime, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class NutritionLog(Base):
    """Daily nutrition log"""
    __tablename__ = "nutrition_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Дата запису
    log_date: Mapped[datetime] = mapped_column(Date, nullable=False, index=True)

    # Фактичні значення за день
    calories: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    protein: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    carbs: Mapped[float] = mapped_column(Float, nullable=True)
    fats: Mapped[float] = mapped_column(Float, nullable=True)

    # Цільові значення (копія з профілю на момент логування)
    target_calories: Mapped[float] = mapped_column(Float, nullable=True)
    target_protein: Mapped[float] = mapped_column(Float, nullable=True)

    # Нотатки (опціонально)
    notes: Mapped[str] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def __repr__(self):
        return f"<NutritionLog(user_id={self.user_id}, date={self.log_date}, cal={self.calories})>"


class NutritionProfile(Base):
    """User nutrition profile with TDEE calculations"""
    __tablename__ = "nutrition_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )

    # Розраховані значення
    bmr: Mapped[float] = mapped_column(Float, nullable=True)  # Basal Metabolic Rate
    tdee: Mapped[float] = mapped_column(Float, nullable=True)  # Total Daily Energy Expenditure

    # Рівень активності (1.2 - 1.9)
    activity_multiplier: Mapped[float] = mapped_column(Float, default=1.5, nullable=False)

    # Мета харчування
    goal: Mapped[str] = mapped_column(String(50), nullable=True)  # bulk, cut, maintain

    # Цільові макронутрієнти
    target_calories: Mapped[float] = mapped_column(Float, nullable=True)
    target_protein: Mapped[float] = mapped_column(Float, nullable=True)
    target_carbs: Mapped[float] = mapped_column(Float, nullable=True)
    target_fats: Mapped[float] = mapped_column(Float, nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def __repr__(self):
        return f"<NutritionProfile(user_id={self.user_id}, tdee={self.tdee}, goal={self.goal})>"
