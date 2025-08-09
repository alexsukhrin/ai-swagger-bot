#!/usr/bin/env python3
"""
Тест релевантности embedding поиска
"""
import os
import sys
from typing import Any, Dict, List

# Добавляем путь к src
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import json

from langchain_openai import OpenAIEmbeddings

from postgres_vector_manager import PostgresVectorManager


def test_search_relevance():
    """Тестирует релевантность поиска по embedding'ам"""

    # Инициализируем компоненты
    embeddings = OpenAIEmbeddings()
    vector_manager = PostgresVectorManager()

    # Тестовые запросы и ожидаемые категории
    test_queries = [
        {
            "query": "найти товары",
            "expected_categories": ["Products"],
            "description": "Поиск товаров должен находить /products endpoints",
        },
        {
            "query": "создать продукт",
            "expected_categories": ["Products"],
            "description": "Создание продукта",
        },
        {
            "query": "список категорий",
            "expected_categories": ["Categories"],
            "description": "Работа с категориями",
        },
        {
            "query": "оформить заказ",
            "expected_categories": ["Orders"],
            "description": "Создание заказа",
        },
        {
            "query": "получить заказы",
            "expected_categories": ["Orders"],
            "description": "Получение списка заказов",
        },
        {
            "query": "бренды товаров",
            "expected_categories": ["Brands"],
            "description": "Работа с брендами",
        },
        {
            "query": "коллекции продуктов",
            "expected_categories": ["Collections"],
            "description": "Управление коллекциями",
        },
        {
            "query": "настройки продуктов",
            "expected_categories": ["Settings"],
            "description": "Настройки системы",
        },
        {
            "query": "атрибуты товара",
            "expected_categories": ["Attributes"],
            "description": "Атрибуты продуктов",
        },
        {
            "query": "семейства продуктов",
            "expected_categories": ["Families"],
            "description": "Семейства товаров",
        },
    ]

    print("🧪 ТЕСТИРОВАНИЕ РЕЛЕВАНТНОСТИ EMBEDDING ПОИСКА\n")
    print("=" * 60)

    total_tests = len(test_queries)
    passed_tests = 0

    for i, test_case in enumerate(test_queries, 1):
        print(f"\n📋 ТЕСТ {i}/{total_tests}: {test_case['description']}")
        print(f"🔍 Запрос: '{test_case['query']}'")
        print(f"📍 Ожидаемые категории: {test_case['expected_categories']}")

        try:
            # Создаем embedding для запроса
            query_embedding = embeddings.embed_query(test_case["query"])

            # Ищем похожие endpoints (берем топ-5 для лучшего анализа)
            results = vector_manager.search_similar(
                query_embedding=query_embedding,
                user_id="demo_user_20250809_140721",  # Используем любого пользователя
                limit=5,
            )

            if not results:
                print("❌ Результаты не найдены")
                continue

            print(f"📊 Найдено {len(results)} результатов:")

            found_categories = []
            for j, result in enumerate(results, 1):
                endpoint_path = result["endpoint_path"]
                method = result["method"]

                # Определяем категорию
                if endpoint_path.startswith("/products"):
                    category = "Products"
                elif endpoint_path.startswith("/category"):
                    category = "Categories"
                elif endpoint_path.startswith("/orders"):
                    category = "Orders"
                elif endpoint_path.startswith("/brands"):
                    category = "Brands"
                elif endpoint_path.startswith("/collections"):
                    category = "Collections"
                elif endpoint_path.startswith("/attributes"):
                    category = "Attributes"
                elif endpoint_path.startswith("/settings"):
                    category = "Settings"
                elif endpoint_path.startswith("/families"):
                    category = "Families"
                else:
                    category = "Other"

                found_categories.append(category)

                similarity = result.get("similarity", 0.0)
                print(
                    f"  {j}. {method} {endpoint_path} → {category} (similarity: {similarity:.3f})"
                )

            # Проверяем релевантность
            expected_found = any(
                cat in found_categories for cat in test_case["expected_categories"]
            )
            top_result_relevant = (
                found_categories[0] in test_case["expected_categories"]
                if found_categories
                else False
            )

            if top_result_relevant:
                print("✅ ОТЛИЧНО: Топ результат релевантен!")
                passed_tests += 1
            elif expected_found:
                print("🟡 ХОРОШО: Ожидаемая категория найдена, но не в топе")
                passed_tests += 0.5
            else:
                print("❌ ПЛОХО: Ожидаемая категория не найдена")

        except Exception as e:
            print(f"❌ ОШИБКА: {e}")

    print("\n" + "=" * 60)
    print("📊 ИТОГОВАЯ СТАТИСТИКА:")
    print(f"Пройдено тестов: {passed_tests}/{total_tests}")
    print(f"Процент успеха: {(passed_tests/total_tests)*100:.1f}%")

    if passed_tests >= total_tests * 0.8:
        print("🎉 ОТЛИЧНО: Качество embedding'ов высокое!")
    elif passed_tests >= total_tests * 0.6:
        print("🟡 ХОРОШО: Качество embedding'ов среднее")
    else:
        print("🔴 ПЛОХО: Нужно улучшить качество embedding'ов")


if __name__ == "__main__":
    test_search_relevance()
