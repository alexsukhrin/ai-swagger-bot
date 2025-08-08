#!/usr/bin/env python3
"""
Скрипт для очищення дублікатів embeddings в базі даних.
"""

import os
import sys

# Додаємо шлях до модуля
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.postgres_vector_manager import PostgresVectorManager


def cleanup_duplicates():
    """Очищає дублікати embeddings."""
    print("🧹 Початок очищення дублікатів embeddings...")

    try:
        # Створюємо менеджер векторів
        vector_manager = PostgresVectorManager()

        # Отримуємо статистику до очищення
        stats_before = vector_manager.get_statistics()
        print(f"📊 Статистика до очищення:")
        print(f"   • Всього embeddings: {stats_before.get('total_embeddings', 0)}")
        print(f"   • Унікальних endpoints: {stats_before.get('unique_endpoints', 0)}")

        # Очищаємо дублікати
        deleted_count = vector_manager.cleanup_duplicates()

        # Отримуємо статистику після очищення
        stats_after = vector_manager.get_statistics()
        print(f"📊 Статистика після очищення:")
        print(f"   • Всього embeddings: {stats_after.get('total_embeddings', 0)}")
        print(f"   • Унікальних endpoints: {stats_after.get('unique_endpoints', 0)}")

        if deleted_count > 0:
            print(f"✅ Успішно видалено {deleted_count} дублікатів")
        else:
            print("✅ Дублікатів не знайдено")

        return True

    except Exception as e:
        print(f"❌ Помилка очищення дублікатів: {e}")
        return False


def main():
    """Основна функція."""
    success = cleanup_duplicates()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
