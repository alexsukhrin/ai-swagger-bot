#!/usr/bin/env python3
"""
Демонстраційний скрипт для CLI тестера AI Swagger Bot API
Показує всі можливості та функції
"""

import sys
import time

from cli_tester import APITester


def print_demo_header():
    """Виводить заголовок демонстрації"""
    print("\n" + "=" * 70)
    print("🤖 AI SWAGGER BOT - ДЕМОНСТРАЦІЯ CLI ТЕСТЕРА")
    print("=" * 70)
    print("📋 Цей скрипт показує всі можливості CLI тестера")
    print("🎯 Мета: протестувати всі API endpoints без браузера")
    print("⚡ Переваги: швидкість, автоматизація, детальне логування")
    print("=" * 70)


def demo_health_check(tester):
    """Демонстрація health check"""
    print("\n🏥 ДЕМОНСТРАЦІЯ: Health Check")
    print("-" * 50)
    tester.health_check()
    time.sleep(2)


def demo_demo_user(tester):
    """Демонстрація створення демо користувача"""
    print("\n👤 ДЕМОНСТРАЦІЯ: Створення демо користувача")
    print("-" * 50)
    tester.create_demo_user()
    time.sleep(2)


def demo_prompts(tester):
    """Демонстрація роботи з промптами"""
    print("\n📝 ДЕМОНСТРАЦІЯ: Робота з промптами")
    print("-" * 50)

    print("1️⃣ Перегляд всіх промптів:")
    tester.get_prompts()
    time.sleep(1)

    print("\n2️⃣ Промпти за категорією 'system':")
    tester.get_prompts(category="system")
    time.sleep(1)

    print("\n3️⃣ Категорії промптів:")
    tester.get_prompt_categories()
    time.sleep(1)

    print("\n4️⃣ Статистика промптів:")
    tester.get_prompt_statistics()
    time.sleep(1)


def demo_custom_prompt(tester):
    """Демонстрація створення кастомного промпту"""
    print("\n✨ ДЕМОНСТРАЦІЯ: Створення кастомного промпту")
    print("-" * 50)

    tester.create_custom_prompt(
        "Демо промпт",
        "Промпт для демонстрації CLI тестера",
        "Ти експерт з API. Користувач запитує: {user_query}. Відповідай українською мовою.",
        "user_defined",
    )
    time.sleep(2)


def demo_search_prompts(tester):
    """Демонстрація пошуку промптів"""
    print("\n🔍 ДЕМОНСТРАЦІЯ: Пошук промптів")
    print("-" * 50)

    print("1️⃣ Пошук за словом 'створення':")
    tester.search_prompts("створення")
    time.sleep(1)

    print("\n2️⃣ Пошук за словом 'система':")
    tester.search_prompts("система")
    time.sleep(1)

    print("\n3️⃣ Пропозиції для запиту 'Створи нову категорію':")
    tester.get_prompt_suggestions("Створи нову категорію")
    time.sleep(1)


def demo_format_prompt(tester):
    """Демонстрація форматування промпту"""
    print("\n🔧 ДЕМОНСТРАЦІЯ: Форматування промпту")
    print("-" * 50)

    parameters = {
        "user_query": "Покажи всі доступні endpoints",
        "context": "Користувач хоче побачити список всіх API endpoints",
    }

    tester.format_prompt("system_base", **parameters)
    time.sleep(2)


def demo_export_prompts(tester):
    """Демонстрація експорту промптів"""
    print("\n📤 ДЕМОНСТРАЦІЯ: Експорт промптів")
    print("-" * 50)

    tester.export_prompts(include_custom=True)
    time.sleep(2)


def demo_user_info(tester):
    """Демонстрація інформації про користувача"""
    print("\n👤 ДЕМОНСТРАЦІЯ: Інформація про користувача")
    print("-" * 50)

    tester.get_user_info()
    time.sleep(2)


def demo_swagger_upload(tester):
    """Демонстрація завантаження Swagger"""
    print("\n📁 ДЕМОНСТРАЦІЯ: Завантаження Swagger файлу")
    print("-" * 50)

    # Перевіряємо чи існує файл
    import os

    swagger_file = "examples/swagger_specs/shop_api.json"

    if os.path.exists(swagger_file):
        print(f"✅ Знайдено файл: {swagger_file}")
        tester.upload_swagger(swagger_file)
    else:
        print(f"❌ Файл не знайдено: {swagger_file}")
        print("💡 Створіть файл або використайте інший шлях")

    time.sleep(2)


def demo_chat(tester):
    """Демонстрація чату з AI"""
    print("\n💬 ДЕМОНСТРАЦІЯ: Чат з AI")
    print("-" * 50)

    messages = [
        "Покажи всі доступні endpoints",
        "Створи товар з назвою Телефон",
        "Покажи категорії товарів",
        "Як створити нову категорію?",
    ]

    for i, message in enumerate(messages, 1):
        print(f"\n{i}️⃣ Повідомлення: {message}")
        tester.chat(message)
        time.sleep(2)


def demo_chat_history(tester):
    """Демонстрація історії чату"""
    print("\n📜 ДЕМОНСТРАЦІЯ: Історія чату")
    print("-" * 50)

    tester.get_chat_history()
    time.sleep(2)


def demo_status(tester):
    """Демонстрація статусу"""
    print("\n📊 ДЕМОНСТРАЦІЯ: Статус")
    print("-" * 50)

    tester.show_status()
    time.sleep(2)


def demo_reload_prompts(tester):
    """Демонстрація перезавантаження промптів"""
    print("\n🔄 ДЕМОНСТРАЦІЯ: Перезавантаження промптів")
    print("-" * 50)

    tester.reload_prompts()
    time.sleep(2)


def run_full_demo():
    """Запуск повної демонстрації"""
    print_demo_header()

    tester = APITester()

    try:
        # Базові функції
        demo_health_check(tester)
        demo_demo_user(tester)

        # Робота з промптами
        demo_prompts(tester)
        demo_custom_prompt(tester)
        demo_search_prompts(tester)
        demo_format_prompt(tester)
        demo_export_prompts(tester)

        # Інформація про користувача
        demo_user_info(tester)

        # Swagger та чат
        demo_swagger_upload(tester)
        demo_chat(tester)
        demo_chat_history(tester)

        # Додаткові функції
        demo_status(tester)
        demo_reload_prompts(tester)

        print("\n" + "=" * 70)
        print("✅ ДЕМОНСТРАЦІЯ ЗАВЕРШЕНА УСПІШНО!")
        print("=" * 70)
        print("🎯 Що було протестовано:")
        print("   ✅ Health Check")
        print("   ✅ Створення демо користувача")
        print("   ✅ Робота з промптами")
        print("   ✅ Створення кастомних промптів")
        print("   ✅ Пошук та пропозиції промптів")
        print("   ✅ Форматування промптів")
        print("   ✅ Експорт промптів")
        print("   ✅ Інформація про користувача")
        print("   ✅ Завантаження Swagger")
        print("   ✅ Чат з AI")
        print("   ✅ Історія чату")
        print("   ✅ Статус системи")
        print("   ✅ Перезавантаження промптів")
        print("=" * 70)
        print("💡 Тепер можете використовувати CLI тестер для повного тестування!")
        print("🔧 Команди: python cli_tester.py --help")
        print("🎮 Інтерактивний режим: python interactive_cli.py")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Помилка під час демонстрації: {e}")
        print("💡 Перевірте, чи запущений API сервер")
        print("🚀 Запустіть: cd api && uvicorn main:app --reload --host 0.0.0.0 --port 8000")


def main():
    """Головна функція"""
    import argparse

    parser = argparse.ArgumentParser(description="Демонстрація CLI тестера для AI Swagger Bot API")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL API")
    parser.add_argument(
        "--section", help="Запустити тільки конкретну секцію (health, prompts, chat, etc.)"
    )

    args = parser.parse_args()

    try:
        if args.section:
            # Запуск конкретної секції
            tester = APITester(args.url)

            if args.section == "health":
                demo_health_check(tester)
            elif args.section == "prompts":
                demo_prompts(tester)
            elif args.section == "chat":
                demo_chat(tester)
            elif args.section == "user":
                demo_demo_user(tester)
                demo_user_info(tester)
            elif args.section == "swagger":
                demo_swagger_upload(tester)
            else:
                print(f"❌ Невідома секція: {args.section}")
                print("Доступні секції: health, prompts, chat, user, swagger")
        else:
            # Повна демонстрація
            run_full_demo()

    except KeyboardInterrupt:
        print("\n\n👋 Демонстрація перервана користувачем!")
    except Exception as e:
        print(f"❌ Помилка: {e}")


if __name__ == "__main__":
    main()
