#!/usr/bin/env python3
"""
Робочий демо AI бота для роботи з Clickone Shop API
"""

import json
import os

import requests
from dotenv import load_dotenv

# Завантажуємо змінні середовища
load_dotenv()


def demo_ai_bot():
    """Демонстрація роботи AI бота"""
    print("🤖 Демо AI бота для Clickone Shop API")
    print("=" * 60)

    # Перевіряємо наявність JWT токена
    jwt_token = os.getenv("JWT_SECRET_KEY")
    if not jwt_token:
        print("❌ JWT токен не знайдено")
        print("💡 Додайте JWT_SECRET_KEY в .env файл")
        return

    print("✅ JWT токен знайдено")
    print(f"🔐 Токен: {jwt_token[:20]}...")

    # Конфігурація API
    API_URL = "https://api.oneshop.click"
    SWAGGER_URL = "https://api.oneshop.click/docs/ai-json"

    print(f"\n🌐 API URL: {API_URL}")
    print(f"📋 Swagger URL: {SWAGGER_URL}")

    # Тест 1: Завантаження Swagger специфікації
    print("\n1️⃣ Тест 1: Завантаження Swagger специфікації")
    try:
        response = requests.get(SWAGGER_URL, timeout=30)
        if response.status_code == 200:
            swagger_spec = response.json()
            print("✅ Swagger специфікація завантажена")
            print(f"   📊 Ендпоінти: {len(swagger_spec.get('paths', {}))}")
            print(f"   📋 Схеми: {len(swagger_spec.get('components', {}).get('schemas', {}))}")
        else:
            print(f"❌ Помилка завантаження: HTTP {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return

    # Тест 2: Отримання категорій (потребує JWT)
    print("\n2️⃣ Тест 2: Отримання категорій через API")
    try:
        headers = {"Authorization": f"Bearer {jwt_token}", "Content-Type": "application/json"}

        response = requests.get(f"{API_URL}/api/categories", headers=headers, timeout=30)
        if response.status_code == 200:
            categories = response.json()
            print("✅ Категорії отримано")
            print(f"   📊 Кількість: {len(categories) if isinstance(categories, list) else 'N/A'}")

            # Показуємо деталі категорій
            if isinstance(categories, list) and categories:
                print("   📋 Деталі категорій:")
                for i, category in enumerate(categories[:3]):  # Показуємо перші 3
                    print(
                        f"      {i+1}. {category.get('name', 'Unknown')} (ID: {category.get('id', 'N/A')})"
                    )
        elif response.status_code == 401:
            print("🔒 Потребує авторизації (JWT токен)")
        else:
            print(f"⚠️ Статус: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Помилка: {e}")

    # Тест 3: Створення категорії
    print("\n3️⃣ Тест 3: Створення категорії через API")
    try:
        category_data = {
            "name": "ТестоваКатегорія",  # Без пробілів та спецсимволів
            "slug": "test-category-demo",
            "description": "Категорія створена для демо AI бота",
            "isActive": True,
            "sortOrder": 100,
        }

        response = requests.post(
            f"{API_URL}/api/categories", headers=headers, json=category_data, timeout=30
        )

        if response.status_code == 201:
            created_category = response.json()
            print("✅ Категорію створено")
            print(f"   🆔 ID: {created_category.get('id', 'N/A')}")
            print(f"   📝 Назва: {created_category.get('name', 'N/A')}")
            print(f"   🔗 Slug: {created_category.get('slug', 'N/A')}")
        elif response.status_code == 401:
            print("🔒 Потребує авторизації")
        elif response.status_code == 400:
            print("⚠️ Помилка валідації даних")
            try:
                error_data = response.json()
                print(f"   📋 Повідомлення: {error_data.get('message', 'Unknown error')}")
                print(f"   🚨 Тип помилки: {error_data.get('error', 'Unknown')}")
            except:
                print(f"   📋 Відповідь: {response.text}")
        else:
            print(f"⚠️ Статус: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Помилка: {e}")

    # Тест 4: Аналіз доступних ендпоінтів
    print("\n4️⃣ Тест 4: Аналіз доступних ендпоінтів")
    endpoints_to_test = [
        ("/api/categories", "GET"),
        ("/api/categories", "POST"),
        ("/api/products", "GET"),
        ("/api/brands", "GET"),
        ("/api/customers", "GET"),
        ("/api/collections", "GET"),
        ("/api/families", "GET"),
        ("/api/settings", "GET"),
    ]

    working = []
    unauthorized = []
    not_found = []

    for endpoint, method in endpoints_to_test:
        try:
            if method == "GET":
                response = requests.get(f"{API_URL}{endpoint}", timeout=10)
            else:
                response = requests.post(f"{API_URL}{endpoint}", headers=headers, timeout=10)

            if response.status_code == 200:
                working.append(f"{method} {endpoint}")
            elif response.status_code == 401:
                unauthorized.append(f"{method} {endpoint}")
            elif response.status_code == 404:
                not_found.append(f"{method} {endpoint}")

        except Exception:
            not_found.append(f"{method} {endpoint}")

    print(f"   ✅ Працюючі: {len(working)}")
    print(f"   🔒 Потребують авторизації: {len(unauthorized)}")
    print(f"   ❌ Не знайдені: {len(not_found)}")

    if working:
        print("   📋 Працюючі ендпоінти:")
        for endpoint in working:
            print(f"      • {endpoint}")

    # Тест 5: Симуляція AI обробки
    print("\n5️⃣ Тест 5: Симуляція AI обробки запитів")

    # Симулюємо AI аналіз запиту
    user_queries = [
        "Створи категорію 'Електроніка'",
        "Покажи всі категорії",
        "Онови категорію з ID 1",
        "Видали категорію 'Тестова'",
    ]

    for i, query in enumerate(user_queries, 1):
        print(f"   🤖 Запит {i}: {query}")

        # Простий AI аналіз
        if "створи" in query.lower():
            print(f"      📝 AI аналіз: Запит на створення категорії")
            print(f"      🔗 Ендпоінт: POST /api/categories")
            print(f"      📊 Дія: Створити нову категорію")
        elif "покажи" in query.lower():
            print(f"      📝 AI аналіз: Запит на отримання даних")
            print(f"      🔗 Ендпоінт: GET /api/categories")
            print(f"      📊 Дія: Отримати список категорій")
        elif "онов" in query.lower():
            print(f"      📝 AI аналіз: Запит на оновлення")
            print(f"      🔗 Ендпоінт: PATCH /api/categories/{{id}}")
            print(f"      📊 Дія: Оновити існуючу категорію")
        elif "видали" in query.lower():
            print(f"      📝 AI аналіз: Запит на видалення")
            print(f"      🔗 Ендпоінт: DELETE /api/categories/{{id}}")
            print(f"      📊 Дія: Видалити категорію")

        print()

    print("\n" + "=" * 60)
    print("🎉 Демо AI бота завершено!")
    print("💡 Це демонструє роботу з API та симуляцію AI обробки")


def demo_swagger_analysis():
    """Демонстрація аналізу Swagger"""
    print("\n🔍 Демонстрація аналізу Swagger специфікації:")
    print("-" * 40)

    SWAGGER_URL = "https://api.oneshop.click/docs/ai-json"

    try:
        response = requests.get(SWAGGER_URL, timeout=30)
        if response.status_code == 200:
            swagger_spec = response.json()

            # Аналіз ендпоінтів
            paths = swagger_spec.get("paths", {})
            print(f"📊 Доступні ендпоінти ({len(paths)}):")
            for path, methods in paths.items():
                for method, details in methods.items():
                    if isinstance(details, dict):
                        summary = details.get("summary", "No summary")
                        print(f"   • {method.upper()} {path}: {summary}")

            # Аналіз схем
            schemas = swagger_spec.get("components", {}).get("schemas", {})
            print(f"\n📋 Доступні схеми ({len(schemas)}):")
            for name, schema in list(schemas.items())[:10]:  # Показуємо перші 10
                properties = len(schema.get("properties", {}))
                required = len(schema.get("required", []))
                print(f"   • {name}: {properties} властивостей, {required} обов'язкових")

            if len(schemas) > 10:
                print(f"   ... та ще {len(schemas) - 10} схем")

        else:
            print(f"❌ Помилка завантаження: HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ Помилка аналізу: {e}")


def main():
    """Головна функція"""
    print("🚀 Запуск робочого демо AI бота...")

    # Основне демо
    demo_ai_bot()

    # Аналіз Swagger
    demo_swagger_analysis()

    print("\n📚 Додаткова інформація:")
    print("   • CLI інтерфейс: python clickone_cli.py")
    print("   • Streamlit демо: make streamlit-up")
    print("   • Тестування: make test")
    print("   • Простий демо: make ai-simple")


if __name__ == "__main__":
    main()
