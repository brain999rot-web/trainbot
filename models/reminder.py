from datetime import datetime
from sqlalchemy import BigInteger, String, Integer, DateTime, Boolean, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from database import Base


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"), nullable=False, index=True)
    reminder_time: Mapped[str] = mapped_column(String(5), nullable=False)  # HH:MM формат
    days_of_week: Mapped[str] = mapped_column(String(20), nullable=False)  # "1,3,5" для Пн, Ср, Пт
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    message: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    last_sent_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)  # Для уникнення дублювання
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
