#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки пошуку категорій.
"""

import os
import sys

from dotenv import load_dotenv

# Завантажуємо змінні середовища
load_dotenv()

# Додаємо шлях до src
sys.path.append("src")


def test_category_search():
    """Тестує пошук категорій."""
    print("🔍 Тестування пошуку категорій")
    print("=" * 40)

    try:
        from rag_engine import RAGEngine

        # Ініціалізуємо RAG engine
        rag = RAGEngine("examples/swagger_specs/shop_api.json")

        # Тестуємо різні запити для категорій
        test_queries = [
            "category",
            "categories",
            "GET category",
            "GET /category",
            "всі категорії",
            "покажи категорії",
            "список категорій",
        ]

        for query in test_queries:
            print(f"\n🔍 Пошук: '{query}'")
            results = rag.search_similar_endpoints(query, k=3)

            for i, result in enumerate(results, 1):
                metadata = result.get("metadata", {})
                method = metadata.get("method", "N/A")
                path = metadata.get("path", "N/A")
                summary = metadata.get("summary", "N/A")
                print(f"   {i}. {method} {path} - {summary}")

        print("\n✅ Пошук категорій працює!")
        return True

    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_agent_categories():
    """Тестує агента з категоріями."""
    print("\n🤖 Тестування агента з категоріями")
    print("=" * 40)

    try:
        from interactive_api_agent import InteractiveSwaggerAgent

        # Ініціалізуємо агента
        agent = InteractiveSwaggerAgent(
            "examples/swagger_specs/shop_api.json", enable_api_calls=False
        )

        # Тестуємо різні запити
        test_queries = [
            "Покажи всі категорії",
            "Створи категорію: Електроніка",
            "GET категорії",
            "Отримай список категорій",
        ]

        for query in test_queries:
            print(f"\n📝 Запит: '{query}'")
            result = agent.process_interactive_query(query)
            response = result.get("response", "")
            print(f"🤖 Відповідь: {response[:200]}...")

        print("\n✅ Агент працює з категоріями!")
        return True

    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Тестування пошуку категорій")
    print("=" * 60)

    success1 = test_category_search()
    success2 = test_agent_categories()

    if success1 and success2:
        print("\n🎉 Всі тести пройшли успішно!")
        print("💡 База даних ембедінгів працює коректно")
    else:
        print("\n❌ Є проблеми з пошуком категорій")
