#!/usr/bin/env python3
"""
Інтерактивне демо AI бота для роботи з Clickone Shop API
"""

import os
import sys

from dotenv import load_dotenv

# Завантажуємо змінні середовища
load_dotenv()

# Додаємо src до шляху
sys.path.append("src")
sys.path.append(".")


def interactive_demo():
    """Інтерактивне демо з AI ботом"""
    print("🤖 Інтерактивне демо AI бота для Clickone Shop API")
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

        # Створюємо AI агента
        print("\n🤖 Створюю AI агента...")
        agent = ClickoneShopAgent()
        print("✅ AI агент створено")

        print("\n🎯 Тепер ви можете взаємодіяти з AI ботом!")
        print("💡 Приклади запитів:")
        print("   • 'Створи категорію Електроніка'")
        print("   • 'Покажи всі категорії'")
        print("   • 'Опиши структуру API'")
        print("   • 'exit' для виходу")
        print("-" * 40)

        while True:
            try:
                # Отримуємо запит від користувача
                user_query = input("\n👤 Ваш запит: ").strip()

                if user_query.lower() in ["exit", "quit", "вийти", "вихід"]:
                    print("👋 До побачення!")
                    break

                if not user_query:
                    print("💡 Введіть запит або 'exit' для виходу")
                    continue

                print(f"🤖 Обробляю запит: {user_query}")

                # Обробляємо запит через AI
                response = agent.process_user_query(user_query)
                print(f"🤖 Відповідь AI: {response}")

            except KeyboardInterrupt:
                print("\n\n👋 Демо перервано користувачем")
                break
            except Exception as e:
                print(f"❌ Помилка: {e}")
                print("💡 Спробуйте інший запит")

    except ImportError as e:
        print(f"❌ Помилка імпорту: {e}")
        print("💡 Переконайтеся, що всі модулі встановлені")
    except Exception as e:
        print(f"❌ Помилка: {e}")


def main():
    """Головна функція"""
    print("🚀 Запуск інтерактивного демо AI бота...")

    try:
        interactive_demo()
    except KeyboardInterrupt:
        print("\n\n👋 Демо завершено")

    print("\n📚 Додаткова інформація:")
    print("   • CLI інтерфейс: python clickone_cli.py")
    print("   • Streamlit демо: make streamlit-up")
    print("   • Тестування: make test")


if __name__ == "__main__":
    main()
