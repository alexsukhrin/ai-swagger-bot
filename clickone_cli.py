#!/usr/bin/env python3
"""
CLI інтерфейс для роботи з Clickone Shop API
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
    print("🔍 CLICKONE SHOP API CLI")
    print("🚀" * 50)
    print()


def print_menu():
    """Виводить меню програми"""
    print("\n🎯 Виберіть опцію:")
    print("1. 📋 Завантажити Swagger специфікацію")
    print("2. 🔍 Аналізувати структуру API")
    print("3. 📂 Отримати список категорій")
    print("4. ➕ Створити нову категорію")
    print("5. 📦 Отримати список продуктів")
    print("6. 🔌 Перевірити з'єднання з API")
    print("7. 📊 Статистика API")
    print("8. 🔍 Тестувати реальні ендпоінти API")
    print("0. 🚪 Вихід")
    print()


def download_swagger_spec():
    """Завантажує Swagger специфікацію"""
    print("📋 Завантажую Swagger специфікацію...")

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
            return swagger_spec
        else:
            print(f"❌ Помилка завантаження: HTTP {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ Помилка завантаження: {e}")
        return None


def analyze_api_structure(swagger_spec):
    """Аналізує структуру API"""
    if not swagger_spec:
        print("❌ Спочатку завантажіть Swagger специфікацію")
        return

    print("🔍 Аналізую структуру API...")

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
        for endpoint in endpoints[:5]:  # Показуємо перші 5
            print(f"      • {endpoint}")
        if len(endpoints) > 5:
            print(f"      ... та ще {len(endpoints) - 5}")

    # Аналізуємо схеми
    components = swagger_spec.get("components", {})
    schemas = components.get("schemas", {})
    print(f"\n📊 Кількість схем даних: {len(schemas)}")

    # Показуємо кілька схем
    schema_names = list(schemas.keys())[:10]
    print(f"📊 Приклади схем: {', '.join(schema_names)}")


def get_categories():
    """Отримує список категорій"""
    if not JWT_TOKEN:
        print("❌ JWT токен не знайдено в .env файлі")
        return

    print("📂 Отримую список категорій...")

    try:
        headers = {
            "Authorization": f"Bearer {JWT_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "AI-Swagger-Bot/1.0",
        }

        response = requests.get(
            f"{CLICKONE_SHOP_API_URL}/api/categories", headers=headers, timeout=30
        )

        print(f"📊 GET /api/categories: HTTP {response.status_code}")

        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Отримано {len(categories)} категорій")

            for i, category in enumerate(categories[:10]):  # Показуємо перші 10
                print(
                    f"   {i+1}. {category.get('name', 'Unknown')} (ID: {category.get('id', 'Unknown')})"
                )
                if category.get("description"):
                    print(f"      📝 {category.get('description')}")
                print(f"      🏷️  Slug: {category.get('slug', 'Unknown')}")
                print(f"      📊 Активна: {'Так' if category.get('isActive') else 'Ні'}")
                print()

            if len(categories) > 10:
                print(f"   ... та ще {len(categories) - 10} категорій")
        else:
            print(f"❌ Помилка: {response.text}")

    except Exception as e:
        print(f"❌ Помилка запиту: {e}")


def create_category():
    """Створює нову категорію"""
    if not JWT_TOKEN:
        print("❌ JWT токен не знайдено в .env файлі")
        return

    print("➕ Створення нової категорії...")

    try:
        # Запитуємо дані від користувача
        name = input("📝 Введіть назву категорії: ").strip()
        if not name:
            print("❌ Назва категорії не може бути порожньою")
            return

        slug = input("🏷️  Введіть slug (або натисніть Enter для автогенерації): ").strip()
        if not slug:
            slug = f"test-category-{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        description = input("📄 Введіть опис (або натисніть Enter для пропуску): ").strip()

        # Дані для створення категорії
        category_data = {"name": name, "slug": slug, "isActive": True, "sortOrder": 999}

        if description:
            category_data["description"] = description

        print(f"\n📊 Дані для створення:")
        print(json.dumps(category_data, ensure_ascii=False, indent=2))

        confirm = input("\n❓ Продовжити створення? (y/N): ").strip().lower()
        if confirm != "y":
            print("❌ Створення скасовано")
            return

        headers = {
            "Authorization": f"Bearer {JWT_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "AI-Swagger-Bot/1.0",
        }

        response = requests.post(
            f"{CLICKONE_SHOP_API_URL}/api/categories",
            headers=headers,
            json=category_data,
            timeout=30,
        )

        print(f"📊 POST /api/categories: HTTP {response.status_code}")

        if response.status_code == 201:
            created_category = response.json()
            print(f"✅ Категорію створено успішно!")
            print(f"   📊 ID: {created_category.get('id', 'Unknown')}")
            print(f"   📊 Назва: {created_category.get('name', 'Unknown')}")
            print(f"   📊 Slug: {created_category.get('slug', 'Unknown')}")
        else:
            print(f"❌ Помилка створення: {response.text}")

    except Exception as e:
        print(f"❌ Помилка запиту: {e}")


def get_products():
    """Отримує список продуктів"""
    if not JWT_TOKEN:
        print("❌ JWT токен не знайдено в .env файлі")
        return

    print("📦 Отримую список продуктів...")

    try:
        headers = {
            "Authorization": f"Bearer {JWT_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "AI-Swagger-Bot/1.0",
        }

        response = requests.get(
            f"{CLICKONE_SHOP_API_URL}/api/products", headers=headers, timeout=30
        )

        print(f"📊 GET /api/products: HTTP {response.status_code}")

        if response.status_code == 200:
            products = response.json()
            print(f"✅ Отримано {len(products)} продуктів")

            for i, product in enumerate(products[:10]):  # Показуємо перші 10
                print(
                    f"   {i+1}. {product.get('name', 'Unknown')} (ID: {product.get('id', 'Unknown')})"
                )
                if product.get("price"):
                    print(
                        f"      💰 Ціна: {product.get('price', 'Unknown')} {product.get('currency', '')}"
                    )
                if product.get("status"):
                    print(f"      📊 Статус: {product.get('status', 'Unknown')}")
                if product.get("sku"):
                    print(f"      🏷️  SKU: {product.get('sku', 'Unknown')}")
                print()

            if len(products) > 10:
                print(f"   ... та ще {len(products) - 10} продуктів")
        else:
            print(f"❌ Помилка: {response.text}")

    except Exception as e:
        print(f"❌ Помилка запиту: {e}")


def check_api_connection():
    """Перевіряє з'єднання з API"""
    print("🔌 Перевіряю з'єднання з Clickone Shop API...")

    try:
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


def show_api_statistics():
    """Показує статистику API"""
    print("📊 Статистика API...")

    # Завантажуємо Swagger специфікацію для статистики
    swagger_spec = download_swagger_spec()
    if not swagger_spec:
        return

    paths = swagger_spec.get("paths", {})
    components = swagger_spec.get("components", {})
    schemas = components.get("schemas", {})

    print(f"📊 Загальна статистика:")
    print(f"   🔗 Ендпоінти: {len(paths)}")
    print(f"   📋 Схеми даних: {len(schemas)}")
    print(
        f"   🏷️  Теги: {len(set([tag for path in paths.values() for method in path.values() if isinstance(method, dict) for tag in method.get('tags', [])]))}"
    )

    # Статистика за методами
    methods_count = {}
    for path in paths.values():
        for method in path.keys():
            methods_count[method.upper()] = methods_count.get(method.upper(), 0) + 1

    print(f"\n📊 Методи HTTP:")
    for method, count in methods_count.items():
        print(f"   {method}: {count}")

    # Статистика за тегами
    tags_count = {}
    for path in paths.values():
        for method in path.values():
            if isinstance(method, dict):
                for tag in method.get("tags", []):
                    tags_count[tag] = tags_count.get(tag, 0) + 1

    print(f"\n📊 Ендпоінти за тегами:")
    for tag, count in sorted(tags_count.items(), key=lambda x: x[1], reverse=True):
        print(f"   {tag}: {count}")


def test_real_api_endpoints():
    """Тестує реальні ендпоінти API та показує їх кількість"""
    print("\n🔍 Тестую реальні ендпоінти API...")

    # Список ендпоінтів для тестування
    endpoints_to_test = [
        ("/api/categories", "GET"),
        ("/api/products", "GET"),
        ("/api/brands", "GET"),
        ("/api/orders", "GET"),
        ("/api/customers", "GET"),
        ("/api/users", "GET"),
        ("/api/collections", "GET"),
        ("/api/families", "GET"),
        ("/api/attributes", "GET"),
        ("/api/settings", "GET"),
        ("/api/warehouse", "GET"),
    ]

    working_endpoints = []

    for endpoint, method in endpoints_to_test:
        try:
            response = requests.get(
                f"{CLICKONE_SHOP_API_URL}{endpoint}",
                timeout=10,
                headers={"User-Agent": "AI-Swagger-Bot/1.0"},
            )

            if response.status_code == 200:
                print(f"✅ {method} {endpoint}: HTTP {response.status_code}")
                working_endpoints.append(endpoint)
            elif response.status_code == 401:
                print(
                    f"🔒 {method} {endpoint}: HTTP {response.status_code} (Unauthorized - потребує токен)"
                )
                working_endpoints.append(endpoint)
            elif response.status_code == 404:
                print(f"❌ {method} {endpoint}: HTTP {response.status_code} (Not Found)")
            else:
                print(f"⚠️  {method} {endpoint}: HTTP {response.status_code}")

        except Exception as e:
            print(f"❌ {method} {endpoint}: Помилка - {e}")

    print(f"\n📊 Результат тестування:")
    print(f"   ✅ Працюючі ендпоінти: {len(working_endpoints)}")
    print(f"   📋 Список працюючих ендпоінтів:")
    for endpoint in working_endpoints:
        print(f"      • {endpoint}")

    return working_endpoints


def main():
    """Головна функція"""
    print_banner()

    # Перевіряємо наявність JWT токена
    if not JWT_TOKEN:
        print("⚠️  УВАГА: CLICKONE_JWT_TOKEN не знайдено в .env файлі")
        print("   Деякі функції будуть недоступні без токена")
        print()

    # Головний цикл програми
    while True:
        print_menu()

        try:
            choice = input("🎯 Виберіть опцію (0-7): ").strip()

            if choice == "0":
                print("\n👋 Дякуємо за використання Clickone Shop API CLI!")
                break
            elif choice == "1":
                download_swagger_spec()
            elif choice == "2":
                swagger_spec = download_swagger_spec()
                if swagger_spec:
                    analyze_api_structure(swagger_spec)
            elif choice == "3":
                get_categories()
            elif choice == "4":
                create_category()
            elif choice == "5":
                get_products()
            elif choice == "6":
                check_api_connection()
            elif choice == "7":
                show_api_statistics()
            elif choice == "8":
                test_real_api_endpoints()
            else:
                print("❌ Невірний вибір. Спробуйте ще раз.")

            input("\n⏸️  Натисніть Enter для продовження...")

        except KeyboardInterrupt:
            print("\n\n👋 Програму перервано користувачем")
            break
        except Exception as e:
            print(f"\n❌ Помилка: {e}")
            input("⏸️  Натисніть Enter для продовження...")


if __name__ == "__main__":
    main()
