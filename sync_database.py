# Sync wrapper для Flask веб-додатку
# Адаптує async моделі для синхронної роботи з Flask

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from database import Base
import os
from dotenv import load_dotenv

load_dotenv()

# Конвертуємо async URL в sync
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///training_bot.db")
if "sqlite+aiosqlite" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("sqlite+aiosqlite", "sqlite")

# Створюємо sync engine
sync_engine = create_engine(DATABASE_URL, echo=False)

# Session factory
SessionLocal = scoped_session(sessionmaker(bind=sync_engine))


def init_sync_db():
    """Ініціалізація таблиць для sync Flask додатку"""
    Base.metadata.create_all(bind=sync_engine)
    print("Sync database initialized")


def get_db():
    """Отримати db session для Flask"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
