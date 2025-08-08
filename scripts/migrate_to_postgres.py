#!/usr/bin/env python3
"""
Скрипт для міграції даних з SQLite в PostgreSQL
"""

import os
import sys
from pathlib import Path

# Додаємо кореневу директорію до шляху
sys.path.append(str(Path(__file__).parent.parent))

from src.postgres_prompt_manager import PostgresPromptManager


def main():
    """Основна функція міграції."""
    print("🚀 Початок міграції з SQLite в PostgreSQL")

    # Перевіряємо чи існує SQLite база
    sqlite_path = "prompts.db"
    if not os.path.exists(sqlite_path):
        print(f"❌ Файл {sqlite_path} не знайдено")
        return

    print(f"📁 Знайдено SQLite базу: {sqlite_path}")

    try:
        # Створюємо менеджер PostgreSQL
        postgres_manager = PostgresPromptManager()

        # Мігруємо дані
        postgres_manager.migrate_from_sqlite(sqlite_path)

        # Показуємо статистику
        stats = postgres_manager.get_statistics()
        print("\n📊 Статистика після міграції:")
        print(f"   Загальна кількість промптів: {stats['total_prompts']}")
        print(f"   Активних промптів: {stats['active_prompts']}")
        print(f"   Середній успіх: {stats['avg_success_rate']:.2%}")
        print(f"   Загальне використання: {stats['total_usage']}")

        print("\n✅ Міграція завершена успішно!")
        print("💡 Тепер система використовує PostgreSQL для зберігання промптів")

    except Exception as e:
        print(f"❌ Помилка міграції: {e}")
        return


if __name__ == "__main__":
    main()
