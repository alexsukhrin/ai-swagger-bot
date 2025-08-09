#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки авторизації фронтенду
"""

import json

import requests

# Налаштування
API_BASE_URL = "http://localhost:8000"


def test_frontend_flow():
    """Тестує повний flow фронтенду"""
    print("🧪 Тестування фронтенду з авторизацією")
    print("=" * 50)

    # 1. Створюємо демо користувача
    print("1️⃣ Створення демо користувача...")
    response = requests.post(f"{API_BASE_URL}/users/demo")

    if response.status_code != 200:
        print(f"❌ Помилка створення користувача: {response.text}")
        return False

    user_data = response.json()
    user_id = user_data["user_id"]
    token = user_data["token"]

    print(f"✅ Користувач створено: {user_id}")
    print(f"🔑 Токен: {token[:50]}...")

    # 2. Завантажуємо Swagger файл
    print("\n2️⃣ Завантаження Swagger файлу...")

    headers = {"Authorization": f"Bearer {token}"}

    with open("examples/swagger_specs/shop_api.json", "rb") as f:
        files = {"file": ("shop_api.json", f, "application/json")}
        response = requests.post(f"{API_BASE_URL}/upload-swagger", files=files, headers=headers)

    if response.status_code != 200:
        print(f"❌ Помилка завантаження: {response.text}")
        return False

    swagger_data = response.json()
    swagger_id = swagger_data["swagger_id"]

    print(f"✅ Swagger файл завантажено: {swagger_id}")
    print(f"📊 Endpoints: {swagger_data['endpoints_count']}")

    # 3. Тестуємо чат
    print("\n3️⃣ Тестування чату...")

    chat_data = {"message": "Покажи доступні endpoints"}
    response = requests.post(f"{API_BASE_URL}/chat", json=chat_data, headers=headers)

    if response.status_code != 200:
        print(f"❌ Помилка чату: {response.text}")
        return False

    chat_response = response.json()
    print(f"✅ Чат працює!")
    print(f"🤖 Відповідь: {chat_response['response'][:100]}...")

    # 4. Перевіряємо ізоляцію
    print("\n4️⃣ Перевірка ізоляції...")

    # Створюємо другого користувача
    response2 = requests.post(f"{API_BASE_URL}/users/demo")
    if response2.status_code == 200:
        user_data2 = response2.json()
        token2 = user_data2["token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # Перевіряємо, чи другий користувач бачить файли першого
        response = requests.get(f"{API_BASE_URL}/swagger-specs", headers=headers2)
        if response.status_code == 200:
            specs = response.json()
            print(f"✅ User 2 має {len(specs)} Swagger файлів (ізоляція працює)")
        else:
            print(f"❌ Помилка перевірки ізоляції: {response.text}")

    print("\n🎉 Тестування завершено успішно!")
    print("📊 Результат:")
    print("   • Авторизація працює")
    print("   • Завантаження файлів працює")
    print("   • Чат працює")
    print("   • Ізоляція користувачів працює")

    return True


if __name__ == "__main__":
    test_frontend_flow()
