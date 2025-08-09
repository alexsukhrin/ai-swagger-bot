#!/usr/bin/env python3
"""
Скрипт для діагностики проблем з сесіями чату
Допомагає зрозуміти чому переключаються чати
"""

import json
import os
import sys
from datetime import datetime, timedelta

import requests

# Додаємо шлях до src для імпорту модулів
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from cli_tester import APITester


def debug_sessions():
    """Діагностика сесій користувача"""
    print("🔍 Діагностика проблем з сесіями чату")
    print("=" * 50)

    # Створюємо тестер
    tester = APITester("http://localhost:8000")

    # Створюємо демо користувача
    print("👤 Створюємо демо користувача...")
    user_data = tester.create_demo_user()
    if not user_data:
        print("❌ Не вдалося створити демо користувача")
        return

    print(f"✅ Користувач створений: {user_data['email']}")

    # Отримуємо інформацію про сесії
    print("\n📊 Аналіз сесій...")
    try:
        response = requests.get(
            "http://localhost:8000/debug/sessions",
            headers={"Authorization": f"Bearer {user_data['token']}"},
        )

        if response.status_code == 200:
            sessions_data = response.json()
            print(f"👥 Користувач: {sessions_data['user_id']}")
            print(f"📈 Всього сесій: {sessions_data['total_sessions']}")
            print(f"🟢 Активних сесій: {sessions_data['active_sessions']}")

            if sessions_data["sessions"]:
                print("\n📋 Детальна інформація про сесії:")
                for i, session in enumerate(sessions_data["sessions"], 1):
                    status = "🟢 Активна" if session["is_active"] else "🔴 Неактивна"
                    print(f"  {i}. {status} - {session['session_id']}")
                    print(f"     Назва: {session['session_name']}")
                    print(f"     Створена: {session['created_at']}")
                    print(f"     Оновлена: {session['updated_at']}")
                    print(f"     Повідомлень: {session['messages_count']}")
                    if session["swagger_spec_id"]:
                        print(f"     Swagger ID: {session['swagger_spec_id']}")
                    print()
            else:
                print("📭 Сесій не знайдено")
        else:
            print(f"❌ Помилка отримання сесій: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Помилка: {e}")

    # Тестуємо створення повідомлень
    print("\n💬 Тестування створення повідомлень...")

    # Завантажуємо Swagger файл
    swagger_file = "examples/swagger_specs/simple_api.json"
    if os.path.exists(swagger_file):
        print(f"📁 Завантажуємо Swagger файл: {swagger_file}")

        with open(swagger_file, "rb") as f:
            files = {"file": f}
            response = requests.post(
                "http://localhost:8000/upload-swagger",
                headers={"Authorization": f"Bearer {user_data['token']}"},
                files=files,
            )

            if response.status_code == 200:
                swagger_data = response.json()
                print(f"✅ Swagger завантажено: {swagger_data['swagger_id']}")

                # Відправляємо повідомлення
                print("\n🤖 Відправляємо тестове повідомлення...")
                chat_response = requests.post(
                    "http://localhost:8000/chat",
                    headers={
                        "Authorization": f"Bearer {user_data['token']}",
                        "Content-Type": "application/json",
                    },
                    json={"message": "Покажи доступні endpoints"},
                )

                if chat_response.status_code == 200:
                    print("✅ Повідомлення відправлено успішно")

                    # Перевіряємо сесії після повідомлення
                    print("\n🔍 Перевіряємо сесії після повідомлення...")
                    sessions_response = requests.get(
                        "http://localhost:8000/debug/sessions",
                        headers={"Authorization": f"Bearer {user_data['token']}"},
                    )

                    if sessions_response.status_code == 200:
                        sessions_data = sessions_response.json()
                        print(f"📊 Після повідомлення:")
                        print(f"   Всього сесій: {sessions_data['total_sessions']}")
                        print(f"   Активних сесій: {sessions_data['active_sessions']}")

                        # Показуємо останню сесію
                        if sessions_data["sessions"]:
                            latest_session = sessions_data["sessions"][0]
                            print(f"   Остання сесія: {latest_session['session_id']}")
                            print(f"   Активна: {latest_session['is_active']}")
                            print(f"   Повідомлень: {latest_session['messages_count']}")
                    else:
                        print(f"❌ Помилка перевірки сесій: {sessions_response.status_code}")
                else:
                    print(f"❌ Помилка відправки повідомлення: {chat_response.status_code}")
                    print(chat_response.text)
            else:
                print(f"❌ Помилка завантаження Swagger: {response.status_code}")
                print(response.text)
    else:
        print(f"❌ Файл не знайдено: {swagger_file}")

    print("\n✅ Діагностика завершена!")


if __name__ == "__main__":
    debug_sessions()
