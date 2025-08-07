#!/usr/bin/env python3
"""
Тест різних URL конфігурацій для API серверів.
"""

import json
import os
import sys

from dotenv import load_dotenv

# Завантажуємо змінні середовища
load_dotenv()

# Додаємо src до шляху
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))


def test_url_configurations():
    """Тестуємо різні URL конфігурації."""
    print("🌐 Тестування URL конфігурацій")
    print("=" * 50)

    # Приклади різних URL
    test_urls = [
        {
            "name": "Development (localhost)",
            "url": "http://localhost:3030/api",
            "description": "Локальна розробка",
        },
        {
            "name": "Staging",
            "url": "https://staging-api.yourdomain.com/api",
            "description": "Тестове середовище",
        },
        {
            "name": "Production",
            "url": "https://api.yourdomain.com/api",
            "description": "Продакшн сервер",
        },
        {
            "name": "Custom Domain",
            "url": "https://api.myshop.com/api",
            "description": "Кастомний домен",
        },
    ]

    for config in test_urls:
        print(f"\n📋 {config['name']}")
        print(f"🔗 URL: {config['url']}")
        print(f"📝 Опис: {config['description']}")

        # Показуємо приклад запиту
        test_path = "/category"
        full_url = config["url"].rstrip("/") + test_path
        print(f"✅ Приклад запиту: {full_url}")

        # Показуємо як це налаштувати в Swagger
        print(f"📝 Налаштування в Swagger:")
        print(
            f'  "servers": [{{"url": "{config["url"]}", "description": "{config["description"]}"}}]'
        )

    print("\n🔧 Як змінити URL:")
    print("1. Відкрийте файл: examples/swagger_specs/shop_api.json")
    print("2. Знайдіть секцію 'servers'")
    print("3. Змініть 'url' на потрібний")
    print("4. Збережіть файл")
    print("5. Перезапустіть агента")

    print("\n🧪 Тестування:")
    print("python demo_real_api.py")
    print("python test_langchain.py")


if __name__ == "__main__":
    test_url_configurations()
