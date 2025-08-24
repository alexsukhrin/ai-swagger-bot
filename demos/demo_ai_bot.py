#!/usr/bin/env python3
"""
Демо AI бота для роботи з Clickone Shop API
"""

import os
import sys

from dotenv import load_dotenv

# Завантажуємо змінні середовища
load_dotenv()

# Додаємо src до шляху
sys.path.append("src")
sys.path.append(".")


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

    try:
        # Імпортуємо необхідні модулі
        from clickone_shop_agent import ClickoneShopAgent
        from clickone_swagger_service import get_clickone_swagger_service

        print("\n📥 Завантажую Clickone Swagger Service...")
        service = get_clickone_swagger_service()

        print("✅ Сервіс завантажено")
        print(f"📊 Swagger URL: {service.swagger_url}")
        print(f"🌐 API URL: {service.api_url}")

        # Завантажуємо Swagger специфікацію
        print("\n📋 Завантажую Swagger специфікацію...")
        swagger_spec = service.download_swagger_spec()

        if swagger_spec:
            print("✅ Swagger специфікація завантажена")
            print(f"   📊 Ендпоінти: {len(swagger_spec.get('paths', {}))}")
            print(f"   📋 Схеми: {len(swagger_spec.get('components', {}).get('schemas', {}))}")
        else:
            print("❌ Помилка завантаження Swagger")
            return

        # Створюємо AI агента
        print("\n🤖 Створюю AI агента...")
        agent = ClickoneShopAgent()
        print("✅ AI агент створено")

        # Демонструємо роботу з AI
        print("\n🎯 Демонстрація роботи з AI:")
        print("-" * 40)

        # Тест 1: Створення категорії
        print("\n1️⃣ Тест 1: Створення категорії через AI")
        user_query = "Створи категорію 'Електроніка' з описом 'Електронні пристрої та гаджети'"
        print(f"👤 Запит користувача: {user_query}")

        try:
            response = agent.process_user_query(user_query)
            print(f"🤖 Відповідь AI: {response}")
        except Exception as e:
            print(f"❌ Помилка AI: {e}")

        # Тест 2: Отримання категорій
        print("\n2️⃣ Тест 2: Отримання категорій через AI")
        user_query = "Покажи всі доступні категорії"
        print(f"👤 Запит користувача: {user_query}")

        try:
            response = agent.process_user_query(user_query)
            print(f"🤖 Відповідь AI: {response}")
        except Exception as e:
            print(f"❌ Помилка AI: {e}")

        # Тест 3: Оновлення категорії
        print("\n3️⃣ Тест 3: Оновлення категорії через AI")
        user_query = (
            "Онови категорію 'Електроніка' - зміни опис на 'Сучасна електроніка та технології'"
        )
        print(f"👤 Запит користувача: {user_query}")

        try:
            response = agent.process_user_query(user_query)
            print(f"🤖 Відповідь AI: {response}")
        except Exception as e:
            print(f"❌ Помилка AI: {e}")

        # Тест 4: Видалення категорії
        print("\n4️⃣ Тест 4: Видалення категорії через AI")
        user_query = "Видали категорію 'Електроніка'"
        print(f"👤 Запит користувача: {user_query}")

        try:
            response = agent.process_user_query(user_query)
            print(f"🤖 Відповідь AI: {response}")
        except Exception as e:
            print(f"❌ Помилка AI: {e}")

        # Тест 5: Аналіз Swagger
        print("\n5️⃣ Тест 5: Аналіз Swagger через AI")
        user_query = "Опиши структуру API та доступні ендпоінти"
        print(f"👤 Запит користувача: {user_query}")

        try:
            response = agent.process_user_query(user_query)
            print(f"🤖 Відповідь AI: {response}")
        except Exception as e:
            print(f"❌ Помилка AI: {e}")

        print("\n" + "=" * 60)
        print("🎉 Демо AI бота завершено!")
        print("💡 AI бот успішно обробляє запити користувачів та взаємодіє з API")

    except ImportError as e:
        print(f"❌ Помилка імпорту: {e}")
        print("💡 Переконайтеся, що всі модулі встановлені")
    except Exception as e:
        print(f"❌ Помилка: {e}")


def demo_ai_error_handling():
    """Демонстрація обробки помилок AI"""
    print("\n🔧 Демонстрація обробки помилок AI:")
    print("-" * 40)

    try:
        from clickone_shop_agent import ClickoneShopAgent

        agent = ClickoneShopAgent()

        # Тест з неправильним запитом
        print("\n🧪 Тест з неправильним запитом:")
        user_query = "Створи категорію без назви"
        print(f"👤 Запит: {user_query}")

        try:
            response = agent.process_user_query(user_query)
            print(f"🤖 Відповідь: {response}")
        except Exception as e:
            print(f"❌ Помилка: {e}")

        # Тест з неіснуючим ендпоінтом
        print("\n🧪 Тест з неіснуючим ендпоінтом:")
        user_query = "Створи користувача"
        print(f"👤 Запит: {user_query}")

        try:
            response = agent.process_user_query(user_query)
            print(f"🤖 Відповідь: {response}")
        except Exception as e:
            print(f"❌ Помилка: {e}")

    except Exception as e:
        print(f"❌ Помилка демо обробки помилок: {e}")


def main():
    """Головна функція"""
    print("🚀 Запуск демо AI бота...")

    # Основне демо
    demo_ai_bot()

    # Демо обробки помилок
    demo_ai_error_handling()

    print("\n📚 Додаткова інформація:")
    print("   • CLI інтерфейс: python clickone_cli.py")
    print("   • Streamlit демо: make streamlit-up")
    print("   • Тестування: make test")


if __name__ == "__main__":
    main()
