#!/usr/bin/env python3
"""
Швидкий демо-скрипт для Streamlit
"""

import json
import os

import requests
from dotenv import load_dotenv

# Завантажуємо змінні середовища
load_dotenv()


def quick_demo():
    """Швидкий демо тест"""
    print("🚀 Швидкий демо Streamlit для Clickone Shop API")
    print("=" * 50)

    # Тестуємо доступність
    try:
        response = requests.get("http://localhost:8502", timeout=5)
        if response.status_code == 200:
            print("✅ Streamlit доступний на http://localhost:8502")
        else:
            print(f"❌ Streamlit повернув статус {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Streamlit недоступний: {e}")
        print("💡 Запустіть: make streamlit-up")
        return

    # Тестуємо API
    print("\n🔍 Тестую API ендпоінти...")

    print("📋 Доступні ендпоінти в Swagger для AI:")
    print("   • GET /api/categories - Отримати категорії")
    print("   • POST /api/categories - Створити категорію")
    print("   • GET /api/categories/{id} - Отримати категорію")
    print("   • PUT /api/categories/{id} - Оновити категорію")
    print("   • DELETE /api/categories/{id} - Видалити категорію")

    # Тестуємо тільки категорії
    endpoints = ["/api/categories"]

    # Перевіряємо JWT токен
    jwt_token = os.getenv("JWT_SECRET_KEY")
    if jwt_token:
        print(f"🔑 JWT токен знайдено: {jwt_token[:20]}...")
    else:
        print("⚠️ JWT токен не знайдено (JWT_SECRET_KEY)")

    for endpoint in endpoints:
        try:
            response = requests.get(f"https://api.oneshop.click{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {endpoint}")
            elif response.status_code == 401:
                print(f"🔒 {endpoint} (потребує токен)")
            else:
                print(f"⚠️ {endpoint} (HTTP {response.status_code})")
        except Exception:
            print(f"❌ {endpoint} (помилка)")

    print("\n🎉 Демо завершено!")
    print("🌐 Відкрийте http://localhost:8502 у браузері")


if __name__ == "__main__":
    quick_demo()
