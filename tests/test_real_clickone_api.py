#!/usr/bin/env python3
"""
Тестування роботи з реальними даними Clickone Shop API
"""

import json
import os
from datetime import datetime

import requests
from dotenv import load_dotenv

# Завантажуємо змінні середовища
load_dotenv()

# Конфігурація
CLICKONE_SHOP_API_URL = "https://api.oneshop.click"
CLICKONE_SHOP_SWAGGER_URL = "https://api.oneshop.click/docs/ai-json"
JWT_TOKEN = os.getenv("CLICKONE_JWT_TOKEN")


def print_banner():
    """Виводить банер програми"""
    print("🚀" * 50)
    print("🔍 ТЕСТУВАННЯ REAL CLICKONE SHOP API")
    print("🚀" * 50)
    print()


def test_swagger_download():
    """Тестує завантаження Swagger специфікації"""
    print("📋 Тестую завантаження Swagger специфікації...")

    try:
        response = requests.get(
            CLICKONE_SHOP_SWAGGER_URL, timeout=30, headers={"User-Agent": "AI-Swagger-Bot/1.0"}
        )

        if response.status_code == 200:
            swagger_spec = response.json()
            print(f"✅ Swagger специфікацію завантажено успішно!")
            print(f"   📊 API: {swagger_spec.get('info', {}).get('title', 'Unknown')}")
            print(f"   📊 Версія: {swagger_spec.get('info', {}).get('version', 'Unknown')}")
            print(f"   📊 Ендпоінти: {len(swagger_spec.get('paths', {}))}")

            # Показуємо кілька ендпоінтів
            paths = list(swagger_spec.get("paths", {}).keys())[:5]
            print(f"   📊 Приклади ендпоінтів: {', '.join(paths)}")

            return swagger_spec
        else:
            print(f"❌ Помилка завантаження: HTTP {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ Помилка завантаження: {e}")
        return None


def test_api_connection():
    """Тестує з'єднання з API"""
    print("\n🔌 Тестую з'єднання з Clickone Shop API...")

    try:
        # Спробуємо отримати базову інформацію
        response = requests.get(
            f"{CLICKONE_SHOP_API_URL}/health",
            timeout=10,
            headers={"User-Agent": "AI-Swagger-Bot/1.0"},
        )

        if response.status_code == 200:
            print("✅ З'єднання з API працює")
            return True
        else:
            print(f"⚠️ API повернув статус {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Помилка з'єднання: {e}")
        return False


def test_categories_endpoint():
    """Тестує ендпоінт категорій"""
    print("\n📂 Тестую ендпоінт категорій...")

    if not JWT_TOKEN:
        print("⚠️ JWT токен не знайдено в .env файлі")
        return None

    try:
        headers = {
            "Authorization": f"Bearer {JWT_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "AI-Swagger-Bot/1.0",
        }

        # Отримуємо список категорій
        response = requests.get(
            f"{CLICKONE_SHOP_API_URL}/api/categories", headers=headers, timeout=30
        )

        print(f"📊 GET /api/categories: HTTP {response.status_code}")

        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Отримано {len(categories)} категорій")

            # Показуємо перші кілька категорій
            for i, category in enumerate(categories[:3]):
                print(
                    f"   {i+1}. {category.get('name', 'Unknown')} (ID: {category.get('id', 'Unknown')})"
                )

            return categories
        else:
            print(f"❌ Помилка: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Помилка запиту: {e}")
        return None


def test_create_category():
    """Тестує створення категорії"""
    print("\n➕ Тестую створення категорії...")

    if not JWT_TOKEN:
        print("⚠️ JWT токен не знайдено в .env файлі")
        return None

    try:
        headers = {
            "Authorization": f"Bearer {JWT_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "AI-Swagger-Bot/1.0",
        }

        # Дані для створення категорії
        category_data = {
            "name": f"Test Category {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "slug": f"test-category-{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "description": "Тестова категорія для перевірки API",
            "isActive": True,
            "sortOrder": 999,
        }

        response = requests.post(
            f"{CLICKONE_SHOP_API_URL}/api/categories",
            headers=headers,
            json=category_data,
            timeout=30,
        )

        print(f"📊 POST /api/categories: HTTP {response.status_code}")
        print(f"📊 Дані запиту: {json.dumps(category_data, ensure_ascii=False, indent=2)}")

        if response.status_code == 201:
            created_category = response.json()
            print(f"✅ Категорію створено успішно!")
            print(f"   📊 ID: {created_category.get('id', 'Unknown')}")
            print(f"   📊 Назва: {created_category.get('name', 'Unknown')}")
            print(f"   📊 Slug: {created_category.get('slug', 'Unknown')}")
            return created_category
        else:
            print(f"❌ Помилка створення: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Помилка запиту: {e}")
        return None


def test_products_endpoint():
    """Тестує ендпоінт продуктів"""
    print("\n📦 Тестую ендпоінт продуктів...")

    if not JWT_TOKEN:
        print("⚠️ JWT токен не знайдено в .env файлі")
        return None

    try:
        headers = {
            "Authorization": f"Bearer {JWT_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "AI-Swagger-Bot/1.0",
        }

        # Отримуємо список продуктів
        response = requests.get(
            f"{CLICKONE_SHOP_API_URL}/api/products", headers=headers, timeout=30
        )

        print(f"📊 GET /api/products: HTTP {response.status_code}")

        if response.status_code == 200:
            products = response.json()
            print(f"✅ Отримано {len(products)} продуктів")

            # Показуємо перші кілька продуктів
            for i, product in enumerate(products[:3]):
                print(
                    f"   {i+1}. {product.get('name', 'Unknown')} (ID: {product.get('id', 'Unknown')})"
                )
                print(
                    f"      💰 Ціна: {product.get('price', 'Unknown')} {product.get('currency', '')}"
                )
                print(f"      📊 Статус: {product.get('status', 'Unknown')}")

            return products
        else:
            print(f"❌ Помилка: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Помилка запиту: {e}")
        return None


def analyze_swagger_structure(swagger_spec):
    """Аналізує структуру Swagger специфікації"""
    print("\n🔍 Аналізую структуру Swagger специфікації...")

    if not swagger_spec:
        print("❌ Немає Swagger специфікації для аналізу")
        return

    # Аналізуємо ендпоінти
    paths = swagger_spec.get("paths", {})
    print(f"📊 Загальна кількість ендпоінтів: {len(paths)}")

    # Групуємо за тегами
    endpoints_by_tag = {}
    for path, methods in paths.items():
        for method, details in methods.items():
            if isinstance(details, dict):
                tags = details.get("tags", ["Без тегу"])
                for tag in tags:
                    if tag not in endpoints_by_tag:
                        endpoints_by_tag[tag] = []
                    endpoints_by_tag[tag].append(f"{method.upper()} {path}")

    print("\n📊 Ендпоінти за тегами:")
    for tag, endpoints in endpoints_by_tag.items():
        print(f"   🏷️  {tag}: {len(endpoints)} ендпоінтів")
        for endpoint in endpoints[:3]:  # Показуємо перші 3
            print(f"      • {endpoint}")
        if len(endpoints) > 3:
            print(f"      ... та ще {len(endpoints) - 3}")

    # Аналізуємо схеми
    components = swagger_spec.get("components", {})
    schemas = components.get("schemas", {})
    print(f"\n📊 Кількість схем даних: {len(schemas)}")

    # Показуємо кілька схем
    schema_names = list(schemas.keys())[:5]
    print(f"📊 Приклади схем: {', '.join(schema_names)}")


def main():
    """Головна функція"""
    print_banner()

    # Перевіряємо наявність JWT токена
    if not JWT_TOKEN:
        print("⚠️  УВАГА: CLICKONE_JWT_TOKEN не знайдено в .env файлі")
        print("   Додайте токен в .env файл для повного тестування API")
        print()

    # 1. Тестуємо завантаження Swagger
    swagger_spec = test_swagger_download()

    # 2. Тестуємо з'єднання з API
    api_connection = test_api_connection()

    # 3. Аналізуємо структуру Swagger
    if swagger_spec:
        analyze_swagger_structure(swagger_spec)

    # 4. Тестуємо ендпоінти (тільки якщо є JWT токен)
    if JWT_TOKEN:
        test_categories_endpoint()
        test_create_category()
        test_products_endpoint()
    else:
        print("\n⚠️  Пропуск тестування API ендпоінтів (немає JWT токена)")

    print("\n" + "🚀" * 50)
    print("✅ ТЕСТУВАННЯ ЗАВЕРШЕНО")
    print("🚀" * 50)


if __name__ == "__main__":
    main()
