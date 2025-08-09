#!/usr/bin/env python3

import json

import requests


def test_admin_filters():
    """Тестує фільтри в адмін панелі"""

    base_url = "http://localhost:8000"

    print("🔍 Тестування фільтрів в адмін панелі...")

    # Перевіряємо доступність адмін панелі
    try:
        response = requests.get(f"{base_url}/admin/")
        if response.status_code == 200:
            print("✅ Адмін панель доступна")
        else:
            print(f"❌ Адмін панель недоступна: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Помилка підключення до адмін панелі: {e}")
        return

    # Тестуємо фільтри для промпт-шаблонів
    print("\n📋 Тестування фільтрів для промпт-шаблонів:")

    # Перевіряємо сторінку з фільтрами
    try:
        response = requests.get(f"{base_url}/admin/prompt-template/list")
        if response.status_code == 200:
            print("✅ Сторінка промпт-шаблонів доступна")

            # Перевіряємо наявність фільтрів
            if "user_id" in response.text.lower():
                print("✅ Фільтр по користувачу присутній")
            else:
                print("❌ Фільтр по користувачу не знайдено")

            if "category" in response.text.lower():
                print("✅ Фільтр по категорії присутній")
            else:
                print("❌ Фільтр по категорії не знайдено")

            if "is_public" in response.text.lower():
                print("✅ Фільтр по публічності присутній")
            else:
                print("❌ Фільтр по публічності не знайдено")

        else:
            print(f"❌ Сторінка промпт-шаблонів недоступна: {response.status_code}")
    except Exception as e:
        print(f"❌ Помилка при тестуванні промпт-шаблонів: {e}")

    # Тестуємо фільтри для Swagger специфікацій
    print("\n📋 Тестування фільтрів для Swagger специфікацій:")
    try:
        response = requests.get(f"{base_url}/admin/swagger-spec/list")
        if response.status_code == 200:
            print("✅ Сторінка Swagger специфікацій доступна")

            if "user_id" in response.text.lower():
                print("✅ Фільтр по користувачу присутній")
            else:
                print("❌ Фільтр по користувачу не знайдено")
        else:
            print(f"❌ Сторінка Swagger специфікацій недоступна: {response.status_code}")
    except Exception as e:
        print(f"❌ Помилка при тестуванні Swagger специфікацій: {e}")

    # Тестуємо фільтри для сесій чату
    print("\n📋 Тестування фільтрів для сесій чату:")
    try:
        response = requests.get(f"{base_url}/admin/chat-session/list")
        if response.status_code == 200:
            print("✅ Сторінка сесій чату доступна")

            if "user_id" in response.text.lower():
                print("✅ Фільтр по користувачу присутній")
            else:
                print("❌ Фільтр по користувачу не знайдено")
        else:
            print(f"❌ Сторінка сесій чату недоступна: {response.status_code}")
    except Exception as e:
        print(f"❌ Помилка при тестуванні сесій чату: {e}")

    # Тестуємо фільтри для API викликів
    print("\n📋 Тестування фільтрів для API викликів:")
    try:
        response = requests.get(f"{base_url}/admin/api-call/list")
        if response.status_code == 200:
            print("✅ Сторінка API викликів доступна")

            if "user_id" in response.text.lower():
                print("✅ Фільтр по користувачу присутній")
            else:
                print("❌ Фільтр по користувачу не знайдено")

            if "method" in response.text.lower():
                print("✅ Фільтр по методу присутній")
            else:
                print("❌ Фільтр по методу не знайдено")
        else:
            print(f"❌ Сторінка API викликів недоступна: {response.status_code}")
    except Exception as e:
        print(f"❌ Помилка при тестуванні API викликів: {e}")

    print("\n✅ Тестування фільтрів завершено!")


if __name__ == "__main__":
    test_admin_filters()
