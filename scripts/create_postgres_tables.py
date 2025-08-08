#!/usr/bin/env python3
"""
Скрипт для створення таблиць PostgreSQL
"""

import os
import sys
from pathlib import Path

# Додаємо кореневу директорію до шляху
sys.path.append(str(Path(__file__).parent.parent))

from api.database import create_tables, engine
from api.models import Base
from sqlalchemy import text


def main():
    """Створює таблиці в PostgreSQL."""
    print("🔧 Створення таблиць PostgreSQL...")

    try:
        # Створюємо всі таблиці
        create_tables()
        print("✅ Таблиці створено успішно!")

        # Створюємо системного користувача
        with engine.connect() as conn:
            conn.execute(
                text(
                    """
                INSERT INTO users (id, email, username, hashed_password, is_active)
                VALUES ('system', 'system@ai-swagger-bot.com', 'system', 'system_hash', true)
                ON CONFLICT (id) DO NOTHING
            """
                )
            )
            conn.commit()
            print("✅ Системний користувач створено!")

        print("\n📊 Структура бази даних:")
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """
                )
            )

            tables = result.fetchall()
            for table in tables:
                print(f"  • {table[0]}")

    except Exception as e:
        print(f"❌ Помилка створення таблиць: {e}")
        return


if __name__ == "__main__":
    main()
