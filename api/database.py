"""
Конфігурація бази даних для AI Swagger Bot API
"""

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Імпортуємо моделі
from .models import Base

# Налаштування бази даних
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_swagger_bot.db")  # SQLite для розробки

# Створюємо engine
if DATABASE_URL.startswith("sqlite"):
    # SQLite налаштування
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=True,  # Логування SQL запитів для розробки
    )
else:
    # PostgreSQL налаштування
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=True,  # Логування SQL запитів для розробки
    )

# Створюємо SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Створення таблиць в базі даних"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency для отримання сесії бази даних"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Створюємо таблиці при імпорті модуля
create_tables()
