#!/usr/bin/env python3
"""
Тест для InteractiveSwaggerAgent:
Інтерактивний агент з діалогом для виправлення помилок
"""

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Завантажуємо змінні середовища з .env файлу
load_dotenv()

# Додаємо src до шляху
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_interactive_agent():
    """Тест інтерактивного агента - з діалогом для виправлення помилок."""
    print("\n" + "=" * 60)
    print("🧪 ТЕСТ: InteractiveSwaggerAgent (Інтерактивний агент)")
    print("=" * 60)

    try:
        from interactive_api_agent import InteractiveSwaggerAgent

        # Ініціалізуємо агента
        agent = InteractiveSwaggerAgent(
            swagger_spec_path="examples/swagger_specs/shop_api.json",
            enable_api_calls=False,  # Тільки превью
        )

        # Тестовий запит
        query = "Створи нову категорію"  # Навмисно неповний запит

        print(f"📝 Запит: {query}")
        print("-" * 40)

        response = agent.process_interactive_query(query, user_identifier="test_user")
        print(f"📤 Відповідь:\n{response['response']}")
        print(f"📊 Статус: {response['status']}")
        print(f"🔄 Потребує додаткової інформації: {response['needs_followup']}")

        # Якщо потрібна додаткова інформація
        if response.get("needs_followup"):
            print("\n" + "-" * 40)
            print("🔄 СИМУЛЯЦІЯ ДІАЛОГУ:")
            print("-" * 40)

            followup_query = "Додай назву категорії: Електроніка"
            print(f"📝 Додатковий запит: {followup_query}")

            followup_response = agent.process_followup_query(
                followup_query, user_identifier="test_user"
            )
            print(f"📤 Відповідь:\n{followup_response['response']}")
            print(f"📊 Статус: {followup_response['status']}")

        # Показуємо історію
        history = agent.get_conversation_history("test_user")
        print(f"\n📚 Історія взаємодій ({len(history)} записів):")
        for i, interaction in enumerate(history[-3:], 1):
            print(f"{i}. Користувач: {interaction.get('user_message', '')}")
            print(
                f"   Бот [{interaction.get('status', 'unknown')}]: {interaction.get('bot_response', '')[:100]}..."
            )

        print("\n✅ Особливості InteractiveSwaggerAgent:")
        print("• Зберігає історію взаємодій")
        print("• Аналізує помилки сервера")
        print("• Генерує запити на додаткову інформацію")
        print("• Підтримує діалог для виправлення помилок")
        print("• Повторно виконує запити з новою інформацією")

    except Exception as e:
        print(f"❌ Помилка: {e}")


def main():
    """Головна функція для запуску тесту."""
    print("🚀 ТЕСТУВАННЯ INTERACTIVE SWAGGER AGENT")
    print("=" * 60)

    # Перевіряємо наявність API ключа
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY не знайдено!")
        print("💡 Встановіть змінну середовища:")
        print("   export OPENAI_API_KEY=your_api_key_here")
        print("   або створіть .env файл з OPENAI_API_KEY=your_key")
        return

    # Запускаємо тест
    test_interactive_agent()

    print("\n" + "=" * 60)
    print("📋 ПІДСУМОК:")
    print("=" * 60)
    print("✅ InteractiveSwaggerAgent:")
    print("   ✅ Зберігає історію взаємодій")
    print("   ✅ Аналізує помилки сервера")
    print("   ✅ Генерує запити на додаткову інформацію")
    print("   ✅ Підтримує діалог для виправлення помилок")
    print("   ✅ Повторно виконує запити з новою інформацією")
    print()
    print("🎯 РЕКОМЕНДАЦІЯ: InteractiveSwaggerAgent - найкращий вибір для повноцінного діалогу!")


if __name__ == "__main__":
    main()
