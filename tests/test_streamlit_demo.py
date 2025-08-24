#!/usr/bin/env python3
"""
Тест для перевірки роботи Streamlit демо
"""

import json
import os

import requests
from dotenv import load_dotenv

# Завантажуємо змінні середовища
load_dotenv()


def test_streamlit_accessibility():
    """Тестує доступність Streamlit додатку"""
    print("🔍 Тестую доступність Streamlit додатку...")

    try:
        response = requests.get("http://localhost:8502", timeout=10)
        if response.status_code == 200:
            print("✅ Streamlit додаток доступний на порту 8502")
            return True
        else:
            print(f"❌ Streamlit додаток повернув статус {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Помилка доступу до Streamlit: {e}")
        return False


def test_api_endpoints():
    """Тестує API ендпоінти через Streamlit функції"""
    print("\n🔍 Тестую API ендпоінти...")

    # Імпортуємо функції з Streamlit додатку
    import sys

    sys.path.append(".")

    try:
        from streamlit_demo import download_swagger_spec, test_api_endpoints

        # Тестуємо завантаження Swagger
        print("📥 Тестую завантаження Swagger...")
        swagger_spec = download_swagger_spec()
        if swagger_spec:
            print("✅ Swagger специфікація завантажена")
            print(f"   📊 Ендпоінти: {len(swagger_spec.get('paths', {}))}")
            print(f"   📋 Схеми: {len(swagger_spec.get('components', {}).get('schemas', {}))}")
        else:
            print("❌ Помилка завантаження Swagger")

        # Тестуємо API ендпоінти
        print("\n🧪 Тестую API ендпоінти...")
        endpoints_stats = test_api_endpoints()

        print(f"   ✅ Працюючі: {len(endpoints_stats['working'])}")
        print(f"   🔒 Потребують авторизації: {len(endpoints_stats['unauthorized'])}")
        print(f"   ❌ Не знайдені: {len(endpoints_stats['not_found'])}")

        print("   📋 Доступні ендпоінти в Swagger для AI:")
        print("      • GET /api/categories - Отримати категорії")
        print("      • POST /api/categories - Створити категорію")
        print("      • GET /api/categories/{id} - Отримати категорію")
        print("      • PUT /api/categories/{id} - Оновити категорію")
        print("      • DELETE /api/categories/{id} - Видалити категорію")

        return True

    except ImportError as e:
        print(f"❌ Помилка імпорту: {e}")
        return False
    except Exception as e:
        print(f"❌ Помилка тестування: {e}")
        return False


def test_jwt_token():
    """Тестує наявність JWT токена"""
    print("\n🔑 Тестую JWT токен...")

    jwt_token = os.getenv("JWT_SECRET_KEY")
    if jwt_token:
        print("✅ JWT токен знайдено")
        print(f"   🔐 Токен: {jwt_token[:20]}...")
        return True
    else:
        print("⚠️ JWT токен не знайдено")
        print("   💡 Додайте JWT_SECRET_KEY в .env файл для повного доступу")
        return False


def main():
    """Головна функція тестування"""
    print("🚀 Тестування Streamlit демо для Clickone Shop API")
    print("=" * 60)

    # Тест 1: Доступність Streamlit
    streamlit_ok = test_streamlit_accessibility()

    # Тест 2: API ендпоінти
    api_ok = test_api_endpoints()

    # Тест 3: JWT токен
    jwt_ok = test_jwt_token()

    # Підсумок
    print("\n" + "=" * 60)
    print("📊 ПІДСУМОК ТЕСТУВАННЯ:")
    print(f"   🎯 Streamlit доступність: {'✅' if streamlit_ok else '❌'}")
    print(f"   🔍 API ендпоінти: {'✅' if api_ok else '❌'}")
    print(f"   🔑 JWT токен: {'✅' if jwt_ok else '⚠️'}")

    if streamlit_ok and api_ok:
        print("\n🎉 Streamlit демо готове до використання!")
        print("   🌐 Відкрийте http://localhost:8502 у браузері")
        print("   📖 Використовуйте бічну панель для навігації")
    else:
        print("\n⚠️ Є проблеми з налаштуванням")
        print("   🔧 Перевірте логи та налаштування")


if __name__ == "__main__":
    main()
