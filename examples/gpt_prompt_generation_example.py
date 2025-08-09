#!/usr/bin/env python3
"""
Приклад використання GPT генерації промптів на основі Swagger специфікації
"""

import json
import os
import sys
from pathlib import Path

# Додаємо шлях до модуля
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gpt_prompt_generator import generate_prompts_with_gpt, generate_smart_suggestions_with_gpt


def main():
    """Приклад використання GPT генерації промптів."""

    print("🤖 Приклад GPT генерації промптів на основі Swagger специфікації")
    print("=" * 70)

    # Шлях до Swagger файлу
    swagger_file = "examples/swagger_specs/shop_api.json"

    if not os.path.exists(swagger_file):
        print(f"❌ Файл не знайдено: {swagger_file}")
        print("💡 Переконайтеся, що файл існує або вкажіть правильний шлях")
        return

    # OpenAI API ключ (опціонально)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ OpenAI API ключ не знайдено в змінних середовища")
        print("💡 Встановіть OPENAI_API_KEY для повної функціональності")
        print("💡 Без API ключа система буде використовувати базові промпти")

    try:
        # Читаємо Swagger файл
        with open(swagger_file, "r", encoding="utf-8") as f:
            swagger_data = json.load(f)

        print(f"📁 Завантажено Swagger файл: {swagger_file}")
        print(f"🔍 Аналізую {len(swagger_data.get('paths', {}))} endpoints...")

        # 1. Генеруємо промпти через GPT
        print("\n🎯 Генерація промптів через GPT...")
        generated_prompts = generate_prompts_with_gpt(swagger_data, api_key)

        if generated_prompts:
            print(f"✅ Згенеровано {len(generated_prompts)} промптів")

            # Показуємо деталі згенерованих промптів
            print("\n📋 Деталі згенерованих промптів:")
            for i, prompt in enumerate(generated_prompts, 1):
                print(f"\n{i}. {prompt.name}")
                print(f"   ID: {prompt.id}")
                print(f"   Категорія: {prompt.category}")
                print(f"   Ресурс: {prompt.resource_type}")
                print(f"   Endpoint: {prompt.http_method} {prompt.endpoint_path}")
                print(f"   Теги: {', '.join(prompt.tags)}")
                print(f"   Опис: {prompt.description}")
        else:
            print("❌ Не вдалося згенерувати промпти")

        # 2. Генеруємо розумні підказки
        print("\n🎯 Генерація розумних підказок...")
        suggestions = generate_smart_suggestions_with_gpt(swagger_data, api_key)

        if suggestions:
            print(f"✅ Згенеровано {len(suggestions)} підказок")

            # Показуємо підказки
            print("\n📋 Згенеровані підказки:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"\n{i}. {suggestion.get('title', 'Підказка')}")
                print(f"   Категорія: {suggestion.get('category', 'Інші')}")
                print(f"   Складність: {suggestion.get('difficulty', 'medium')}")
                if suggestion.get("description"):
                    print(f"   Опис: {suggestion['description']}")
                if suggestion.get("example_query"):
                    print(f"   Приклад: {suggestion['example_query']}")
        else:
            print("❌ Не вдалося згенерувати підказки")

        # 3. Зберігаємо згенеровані промпти в YAML файл
        if generated_prompts:
            output_file = "examples/generated_prompts.yaml"
            print(f"\n💾 Зберігаю промпти в файл: {output_file}")

            from src.swagger_prompt_generator import save_generated_prompts_to_yaml

            save_generated_prompts_to_yaml(generated_prompts, output_file)
            print(f"✅ Промпти збережено в {output_file}")

        print("\n🎉 Генерація завершена!")
        print("\n💡 Тепер ви можете:")
        print("  1. Використовувати згенеровані промпти в системі")
        print("  2. Імпортувати їх через API")
        print("  3. Налаштувати їх під свої потреби")

    except Exception as e:
        print(f"❌ Помилка: {e}")
        print("💡 Перевірте:")
        print("  - Чи правильно вказаний шлях до Swagger файлу")
        print("  - Чи встановлений OpenAI API ключ")
        print("  - Чи доступне інтернет-з'єднання")


def demo_cli_usage():
    """Демонстрація використання через CLI."""
    print("\n🖥️ Демонстрація використання через CLI:")
    print("=" * 50)

    print("\n1. Генерація промптів з Swagger файлу:")
    print("   python cli_tester.py generate-prompts --file examples/swagger_specs/shop_api.json")

    print("\n2. Генерація підказок:")
    print(
        "   python cli_tester.py generate-suggestions --file examples/swagger_specs/shop_api.json"
    )

    print("\n3. Автоматична генерація для користувача:")
    print("   python cli_tester.py auto-generate --swagger-spec-id your_spec_id")

    print("\n4. З API ключем:")
    print(
        "   python cli_tester.py generate-prompts --file examples/swagger_specs/shop_api.json --api-key your_openai_key"
    )


def demo_streamlit_usage():
    """Демонстрація використання через Streamlit."""
    print("\n🌐 Демонстрація використання через Streamlit:")
    print("=" * 50)

    print("\n1. Запустіть Streamlit фронтенд:")
    print("   streamlit run streamlit_frontend.py")

    print("\n2. У веб-інтерфейсі:")
    print("   - Створіть демо користувача")
    print("   - Завантажте Swagger файл")
    print("   - Натисніть 'Згенерувати промпти через GPT'")
    print("   - Перегляньте згенеровані підказки")


if __name__ == "__main__":
    main()
    demo_cli_usage()
    demo_streamlit_usage()
