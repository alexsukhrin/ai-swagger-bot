"""
CLI демо для демонстрації AI Error Handler функціональності
"""

import os
import sys
from typing import Any, Dict

from ai_error_handler import get_ai_error_handler
from clickone_shop_agent import ClickoneShopAgent, get_clickone_shop_agent


def print_banner():
    """Виводить банер програми"""
    print("🤖" + "=" * 60 + "🤖")
    print("           AI SWAGGER BOT - ERROR HANDLER DEMO")
    print("🤖" + "=" * 60 + "🤖")
    print()


def print_menu():
    """Виводить меню програми"""
    print("\n📋 **Меню програми:**")
    print("1. 🔍 Тест AI аналізу помилки")
    print("2. 📝 Тест створення категорії з помилкою")
    print("3. 🔄 Автоматичне виправлення та повторна спроба")
    print("4. 📋 Отримати правила валідації від AI")
    print("5. 🗂️ Переглянути статистику кешу помилок")
    print("6. 🧹 Очистити кеш помилок")
    print("0. 🚪 Вихід")
    print()


def test_ai_error_analysis(agent: ClickoneShopAgent):
    """Тест AI аналізу помилки"""
    print("\n🔍 **Тест AI аналізу помилки**")

    # Приклади помилок для тестування
    error_examples = [
        {
            "message": "Category name must contain only letters (no numbers or special characters)",
            "data": {"name": "Test Category 123", "slug": "test-123"},
        },
        {
            "message": "Slug must be unique",
            "data": {"name": "Test Category", "slug": "existing-slug"},
        },
        {
            "message": "Description is too long (max 500 characters)",
            "data": {"name": "Test", "slug": "test", "description": "A" * 600},
        },
    ]

    for i, example in enumerate(error_examples, 1):
        print(f"\n📝 **Приклад {i}:**")
        print(f"Помилка: {example['message']}")
        print(f"Дані: {example['data']}")

        # Отримуємо AI аналіз
        analysis = agent.get_ai_error_analysis(example["message"], example["data"])
        print(f"\n🤖 **AI аналіз:**")
        print(analysis)

        if i < len(error_examples):
            input("\n⏸️  Натисніть Enter для наступного прикладу...")


def test_category_creation_with_error(agent: ClickoneShopAgent):
    """Тест створення категорії з помилкою"""
    print("\n📝 **Тест створення категорії з помилкою**")

    # Тестові дані з помилкою
    invalid_data = {
        "name": "Test Category 123",  # Містить числа
        "slug": "test-category-123",
        "description": "Test category with numbers and special characters #@!",
    }

    print(f"📤 Відправляю дані: {invalid_data}")

    try:
        # Спробуємо створити категорію
        response = agent.create_category(invalid_data)

        if not response.success:
            print(f"\n❌ **Помилка API:**")
            print(response.error)

            # Перевіряємо AI виправлення
            if "ai_fix" in (response.data or {}):
                ai_fix = response.data["ai_fix"]
                print(f"\n🤖 **AI виправлення знайдено:**")
                print(f"Виправлені дані: {ai_fix.get('fixed_data', {})}")
                print(f"Пояснення: {ai_fix.get('explanation', 'Немає')}")
                print(f"Впевненість: {ai_fix.get('confidence', 0):.1%}")

                suggestions = ai_fix.get("suggestions", [])
                if suggestions:
                    print("Поради:")
                    for j, suggestion in enumerate(suggestions, 1):
                        print(f"  {j}. {suggestion}")
            else:
                print("⚠️ AI виправлення не знайдено")
        else:
            print("✅ Категорія створена успішно (неочікувано)")

    except Exception as e:
        print(f"❌ Помилка: {e}")


def test_automatic_fix_and_retry(agent: ClickoneShopAgent):
    """Тест автоматичного виправлення та повторної спроби"""
    print("\n🔄 **Тест автоматичного виправлення та повторної спроби**")

    # Тестові дані з помилкою
    invalid_data = {
        "name": "Test Category 456",  # Містить числа
        "slug": "test-category-456",
        "description": "Test category with numbers",
    }

    print(f"📤 Відправляю дані: {invalid_data}")

    try:
        # Перша спроба
        response = agent.create_category(invalid_data)

        if not response.success:
            print(f"\n❌ **Перша спроба невдала:**")
            print(response.error)

            # Спробуємо автоматично виправити
            print(f"\n🔄 **Спроба автоматичного виправлення...**")
            retry_response = agent.retry_with_ai_fix(response)

            if retry_response.success:
                print("✅ **AI успішно виправив помилку!**")
                print(f"Результат: {retry_response.data}")
            else:
                print("⚠️ **AI виправлення не спрацювало**")
                print(f"Помилка: {retry_response.error}")
        else:
            print("✅ Категорія створена успішно (неочікувано)")

    except Exception as e:
        print(f"❌ Помилка: {e}")


def get_validation_rules_from_ai(agent: ClickoneShopAgent):
    """Отримує правила валідації від AI"""
    print("\n📋 **Отримання правил валідації від AI**")

    entity_types = ["category", "product", "order", "user"]

    for entity_type in entity_types:
        print(f"\n🔍 **Правила для {entity_type}:**")
        try:
            rules = agent.get_validation_rules(entity_type)
            print(rules)
        except Exception as e:
            print(f"❌ Помилка отримання правил: {e}")

        if entity_type != entity_types[-1]:
            input("\n⏸️  Натисніть Enter для наступного типу...")


def show_cache_stats(agent: ClickoneShopAgent):
    """Показує статистику кешу помилок"""
    print("\n🗂️ **Статистика кешу помилок**")

    try:
        stats = agent.ai_error_handler.get_cache_stats()
        print(f"📊 Загальна кількість помилок: {stats['total_errors']}")
        print(f"💾 Розмір кешу: {stats['cache_size']} символів")
        print(f"🤖 Модель AI: {stats['model']}")

        if stats["total_errors"] > 0:
            print(f"\n📋 **Кешовані помилки:**")
            for i, (key, value) in enumerate(agent.ai_error_handler.error_cache.items(), 1):
                print(f"  {i}. {key[:50]}...")
                print(f"     Впевненість: {value.confidence:.1%}")

    except Exception as e:
        print(f"❌ Помилка отримання статистики: {e}")


def clear_error_cache(agent: ClickoneShopAgent):
    """Очищає кеш помилок"""
    print("\n🧹 **Очищення кешу помилок**")

    try:
        agent.ai_error_handler.clear_cache()
        print("✅ Кеш помилок очищено")

        # Показуємо оновлену статистику
        stats = agent.ai_error_handler.get_cache_stats()
        print(f"📊 Нова статистика: {stats['total_errors']} помилок")

    except Exception as e:
        print(f"❌ Помилка очищення кешу: {e}")


def main():
    """Головна функція програми"""
    print_banner()

    # Перевіряємо наявність необхідних змінних середовища
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Помилка: OPENAI_API_KEY не знайдено в .env файлі")
        print("Додайте OPENAI_API_KEY=your_key в .env файл")
        return

    if not os.getenv("CLICKONE_JWT_TOKEN"):
        print("⚠️ Попередження: CLICKONE_JWT_TOKEN не знайдено")
        print("Деякі функції можуть не працювати без JWT токена")
        print("Додайте CLICKONE_JWT_TOKEN=your_token в .env файл")

    try:
        # Ініціалізуємо агент
        print("🚀 Ініціалізація AI Error Handler...")
        agent = get_clickone_shop_agent()

        # Встановлюємо JWT токен, якщо є
        jwt_token = os.getenv("CLICKONE_JWT_TOKEN")
        if jwt_token:
            agent.set_jwt_token(jwt_token)
            print("✅ JWT токен встановлено")

        print("✅ AI Error Handler готовий до роботи!")

        # Головний цикл програми
        while True:
            print_menu()

            try:
                choice = input("🎯 Виберіть опцію (0-6): ").strip()

                if choice == "0":
                    print("\n👋 Дякуємо за використання AI Error Handler Demo!")
                    break
                elif choice == "1":
                    test_ai_error_analysis(agent)
                elif choice == "2":
                    test_category_creation_with_error(agent)
                elif choice == "3":
                    test_automatic_fix_and_retry(agent)
                elif choice == "4":
                    get_validation_rules_from_ai(agent)
                elif choice == "5":
                    show_cache_stats(agent)
                elif choice == "6":
                    clear_error_cache(agent)
                else:
                    print("❌ Невірний вибір. Спробуйте ще раз.")

                input("\n⏸️  Натисніть Enter для продовження...")

            except KeyboardInterrupt:
                print("\n\n👋 Програму перервано користувачем")
                break
            except Exception as e:
                print(f"\n❌ Помилка: {e}")
                input("⏸️  Натисніть Enter для продовження...")

    except Exception as e:
        print(f"❌ Критична помилка ініціалізації: {e}")
        print("Перевірте налаштування .env файлу та підключення до OpenAI")


if __name__ == "__main__":
    main()
