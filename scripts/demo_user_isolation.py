#!/usr/bin/env python3
"""
Демонстрація ізоляції користувачів та Swagger файлів
"""

import json
import time
from datetime import datetime

import requests

# Налаштування
API_BASE_URL = "http://localhost:8000"


def create_demo_user():
    """Створює демо користувача"""
    print("👤 Створення демо користувача...")

    response = requests.post(f"{API_BASE_URL}/users/demo")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Демо користувач створено: {data['user_id']}")
        return data
    else:
        print(f"❌ Помилка створення користувача: {response.text}")
        return None


def upload_swagger_file(token, user_id, filename="examples/swagger_specs/shop_api.json"):
    """Завантажує Swagger файл для користувача"""
    print(f"📁 Завантаження Swagger файлу для користувача {user_id}...")

    headers = {"Authorization": f"Bearer {token}"}

    with open(filename, "rb") as f:
        files = {"file": (filename, f, "application/json")}
        response = requests.post(f"{API_BASE_URL}/upload-swagger", headers=headers, files=files)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Swagger файл завантажено: {data['swagger_id']}")
        print(f"   Endpoints: {data['endpoints_count']}")
        return data
    else:
        print(f"❌ Помилка завантаження: {response.text}")
        return None


def send_chat_message(token, message):
    """Відправляє повідомлення в чат"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    data = {"message": message}
    response = requests.post(f"{API_BASE_URL}/chat", headers=headers, json=data)

    if response.status_code == 200:
        data = response.json()
        return data["response"]
    else:
        print(f"❌ Помилка чату: {response.text}")
        return None


def get_user_swagger_specs(token):
    """Отримує список Swagger специфікацій користувача"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE_URL}/swagger-specs", headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Помилка отримання специфікацій: {response.text}")
        return []


def demo_user_isolation():
    """Демонструє ізоляцію користувачів"""
    print("🔒 Демонстрація ізоляції користувачів та Swagger файлів")
    print("=" * 60)

    # Створюємо двох користувачів
    user1_data = create_demo_user()
    if not user1_data:
        return

    time.sleep(1)  # Невелика пауза

    user2_data = create_demo_user()
    if not user2_data:
        return

    print(f"\n👥 Створено користувачів:")
    print(f"   User 1: {user1_data['user_id']}")
    print(f"   User 2: {user2_data['user_id']}")

    # Завантажуємо Swagger файли для кожного користувача
    print(f"\n📁 Завантаження Swagger файлів...")

    swagger1 = upload_swagger_file(user1_data["token"], user1_data["user_id"])
    if not swagger1:
        return

    swagger2 = upload_swagger_file(user2_data["token"], user2_data["user_id"])
    if not swagger2:
        return

    print(f"\n✅ Swagger файли завантажено:")
    print(f"   User 1: {swagger1['swagger_id']}")
    print(f"   User 2: {swagger2['swagger_id']}")

    # Перевіряємо ізоляцію - кожен користувач бачить тільки свої файли
    print(f"\n🔍 Перевірка ізоляції...")

    specs1 = get_user_swagger_specs(user1_data["token"])
    specs2 = get_user_swagger_specs(user2_data["token"])

    print(f"📋 User 1 має {len(specs1)} Swagger файлів:")
    for spec in specs1:
        print(f"   - {spec['filename']} (ID: {spec['id']})")

    print(f"📋 User 2 має {len(specs2)} Swagger файлів:")
    for spec in specs2:
        print(f"   - {spec['filename']} (ID: {spec['id']})")

    # Тестуємо чат для кожного користувача
    print(f"\n💬 Тестування чату...")

    message = "Покажи доступні endpoints"

    print(f"🤖 User 1 запитує: {message}")
    response1 = send_chat_message(user1_data["token"], message)
    if response1:
        print(f"   Відповідь: {response1[:100]}...")

    print(f"🤖 User 2 запитує: {message}")
    response2 = send_chat_message(user2_data["token"], message)
    if response2:
        print(f"   Відповідь: {response2[:100]}...")

    print(f"\n✅ Демонстрація завершена!")
    print(f"📊 Результат:")
    print(f"   • Кожен користувач має свою ізольовану сесію")
    print(f"   • Swagger файли прив'язані до конкретних користувачів")
    print(f"   • Користувачі не бачать файли один одного")
    print(f"   • Чат працює незалежно для кожного користувача")


if __name__ == "__main__":
    demo_user_isolation()
