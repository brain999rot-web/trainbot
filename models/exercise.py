from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from database import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    equipment: Mapped[str] = mapped_column(String(100), nullable=False)
    primary_muscle: Mapped[str] = mapped_column(String(50), nullable=False)
    secondary_muscles: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
