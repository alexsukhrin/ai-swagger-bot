#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки RAG engine.
"""

import os
import sys

from dotenv import load_dotenv

# Завантажуємо змінні середовища
load_dotenv()

# Додаємо шлях до src
sys.path.append("src")


def test_rag_engine():
    """Тестує RAG engine."""
    print("🧪 Тестування RAG Engine")
    print("=" * 40)

    try:
        from rag_engine import RAGEngine

        # Ініціалізуємо RAG engine
        print("1. Ініціалізація RAG Engine...")
        rag = RAGEngine("examples/swagger_specs/shop_api.json")
        print("✅ RAG Engine ініціалізовано")

        # Отримуємо всі endpoints
        print("2. Отримання endpoints...")
        endpoints = rag.get_all_endpoints()
        print(f"✅ Знайдено {len(endpoints)} endpoints")

        # Тестуємо пошук
        print("3. Тестування пошуку...")
        search_results = rag.search_similar_endpoints("products", k=3)
        print(f"✅ Пошук працює: знайдено {len(search_results)} результатів")

        # Показуємо результати
        for i, result in enumerate(search_results, 1):
            metadata = result.get("metadata", {})
            method = metadata.get("method", "N/A")
            path = metadata.get("path", "N/A")
            print(f"   {i}. {method} {path}")

        print("\n🎉 RAG Engine працює коректно!")
        return True

    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_rag_engine()
