"""
Приклад використання YAML системи промптів
"""

import json
import os
import sys

# Додаємо шлях до модуля
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.yaml_prompt_manager import PromptCategory, YAMLPromptManager


def main():
    """Основний приклад використання YAML менеджера промптів."""

    print("🎯 Приклад використання YAML системи промптів")
    print("=" * 50)

    # 1. Створюємо менеджер
    print("\n1️⃣ Ініціалізація менеджера...")
    manager = YAMLPromptManager("prompts/base_prompts.yaml")

    # 2. Отримуємо статистику
    print("\n2️⃣ Статистика промптів:")
    stats = manager.get_statistics()
    print(f"   📊 Всього промптів: {stats['total_prompts']}")
    print(f"   ✅ Активних промптів: {stats['active_prompts']}")
    print(f"   🌐 Публічних промптів: {stats['public_prompts']}")

    print("\n   📂 Категорії:")
    for category, count in stats["categories"].items():
        print(f"      • {category}: {count} промптів")

    # 3. Отримуємо промпти за категорією
    print("\n3️⃣ Промпти за категоріями:")

    system_prompts = manager.get_prompts_by_category("system")
    print(f"   🖥️ Системні промпти ({len(system_prompts)}):")
    for prompt in system_prompts:
        print(f"      • {prompt.name} (пріоритет: {prompt.priority})")

    creation_prompts = manager.get_prompts_by_category("data_creation")
    print(f"   🛠️ Промпти створення ({len(creation_prompts)}):")
    for prompt in creation_prompts:
        print(f"      • {prompt.name} (пріоритет: {prompt.priority})")

    # 4. Пошук промптів
    print("\n4️⃣ Пошук промптів:")

    search_results = manager.search_prompts("створення")
    print(f"   🔍 Результати пошуку 'створення' ({len(search_results)}):")
    for prompt in search_results:
        print(f"      • {prompt.name} ({prompt.category})")

    # 5. Пропозиції промптів
    print("\n5️⃣ Пропозиції промптів:")

    suggestions = manager.get_prompt_suggestions("Створи нову категорію")
    print(f"   💡 Пропозиції для 'Створи нову категорію' ({len(suggestions)}):")
    for prompt in suggestions:
        print(f"      • {prompt.name} (категорія: {prompt.category}, пріоритет: {prompt.priority})")

    # 6. Форматування промптів
    print("\n6️⃣ Форматування промптів:")

    # Знаходимо системний промпт
    system_prompt = manager.get_prompt("system_base")
    if system_prompt:
        formatted = manager.format_prompt(
            "system_base", user_query="Покажи всі категорії", context="Попередній контекст"
        )
        print(f"   📝 Відформатований системний промпт:")
        print(f"      {formatted[:100]}...")

    # 7. Додавання кастомного промпту
    print("\n7️⃣ Додавання кастомного промпту:")

    custom_prompt_data = {
        "name": "Мій кастомний промпт",
        "description": "Промпт для тестування кастомних функцій",
        "template": """
Ти - експерт з API. Користувач запитує: {user_query}

Контекст: {context}

Правила:
1. Відповідай українською мовою
2. Використовуй емодзі для кращого сприйняття
3. Будь дружелюбним та корисним

Відповідь:
""",
        "category": "user_defined",
        "tags": ["custom", "test", "example"],
        "is_active": True,
        "is_public": False,
        "priority": 100,
    }

    prompt_id = manager.add_custom_prompt(custom_prompt_data, user_id="example_user")
    print(f"   ✅ Додано кастомний промпт з ID: {prompt_id}")

    # 8. Оновлення промпту
    print("\n8️⃣ Оновлення промпту:")

    update_data = {
        "name": "Оновлений кастомний промпт",
        "description": "Оновлений опис промпту",
        "template": "Оновлений шаблон: {user_query}",
        "category": "system",
    }

    success = manager.update_prompt(prompt_id, update_data)
    if success:
        print(f"   ✅ Промпт оновлено успішно")

        # Перевіряємо оновлення
        updated_prompt = manager.get_prompt(prompt_id)
        print(f"   📝 Нова назва: {updated_prompt.name}")
        print(f"   📝 Нова категорія: {updated_prompt.category}")

    # 9. Тестування форматування кастомного промпту
    print("\n9️⃣ Тестування кастомного промпту:")

    formatted_custom = manager.format_prompt(
        prompt_id, user_query="Створи нову категорію", context="Попередній контекст"
    )
    print(f"   📝 Відформатований кастомний промпт:")
    print(f"      {formatted_custom[:100]}...")

    # 10. Експорт промптів
    print("\n🔟 Експорт промптів:")

    export_file = "examples/prompts_export_example.yaml"
    manager.export_prompts_to_yaml(export_file, include_custom=True)
    print(f"   📤 Промпти експортовано в: {export_file}")

    # 11. Фінальна статистика
    print("\n📊 Фінальна статистика:")
    final_stats = manager.get_statistics()
    print(f"   📈 Всього промптів: {final_stats['total_prompts']}")
    print(f"   📈 Активних промптів: {final_stats['active_prompts']}")

    print("\n   📂 Джерела промптів:")
    for source, count in final_stats["sources"].items():
        print(f"      • {source}: {count} промптів")

    # 12. Видалення тестового промпту
    print("\n🗑️ Видалення тестового промпту:")

    delete_success = manager.delete_prompt(prompt_id)
    if delete_success:
        print(f"   ✅ Тестовий промпт видалено")

    print("\n✅ Приклад завершено!")


def demo_search_and_suggestions():
    """Демонстрація пошуку та пропозицій."""

    print("\n🔍 Демонстрація пошуку та пропозицій")
    print("=" * 40)

    manager = YAMLPromptManager("prompts/base_prompts.yaml")

    # Тестові запити
    test_queries = [
        "Створи нову категорію",
        "Покажи всі товари",
        "Онови користувача",
        "Видали категорію",
        "Помилка при створенні",
    ]

    for query in test_queries:
        print(f"\n🔍 Запит: '{query}'")

        # Пошук
        search_results = manager.search_prompts(query)
        print(f"   📋 Пошук ({len(search_results)} результатів):")
        for prompt in search_results[:3]:  # Показуємо перші 3
            print(f"      • {prompt.name} ({prompt.category})")

        # Пропозиції
        suggestions = manager.get_prompt_suggestions(query)
        print(f"   💡 Пропозиції ({len(suggestions)}):")
        for prompt in suggestions[:3]:  # Показуємо перші 3
            print(f"      • {prompt.name} (пріоритет: {prompt.priority})")


def demo_formatting():
    """Демонстрація форматування промптів."""

    print("\n📝 Демонстрація форматування промптів")
    print("=" * 40)

    manager = YAMLPromptManager("prompts/base_prompts.yaml")

    # Тестові сценарії
    test_scenarios = [
        {
            "prompt_id": "intent_analysis_base",
            "parameters": {
                "user_query": "Створи нову категорію з назвою 'Електроніка'",
                "context": "Попередній контекст: користувач працює з категоріями",
            },
        },
        {
            "prompt_id": "error_analysis_base",
            "parameters": {
                "error_message": "Validation error: description is required",
                "original_query": "Створи категорію Електроніка",
                "api_request": {
                    "url": "http://localhost:3030/api/categories",
                    "method": "POST",
                    "data": {"name": "Електроніка"},
                },
            },
        },
        {
            "prompt_id": "api_response_processing_base",
            "parameters": {
                "user_query": "Покажи тільки назви категорій",
                "api_response": {
                    "categories": [
                        {"id": 1, "name": "Одяг", "description": "Категорія одягу"},
                        {"id": 2, "name": "Взуття", "description": "Категорія взуття"},
                        {"id": 3, "name": "Аксесуари", "description": "Категорія аксесуарів"},
                    ]
                },
                "processing_type": "filtered",
                "available_fields": ["id", "name", "description"],
            },
        },
    ]

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📝 Сценарій {i}: {scenario['prompt_id']}")

        try:
            formatted = manager.format_prompt(scenario["prompt_id"], **scenario["parameters"])
            print(f"   ✅ Успішно відформатовано")
            print(f"   📄 Перші 200 символів:")
            print(f"      {formatted[:200]}...")
        except Exception as e:
            print(f"   ❌ Помилка форматування: {e}")


def demo_categories():
    """Демонстрація роботи з категоріями."""

    print("\n📂 Демонстрація роботи з категоріями")
    print("=" * 40)

    manager = YAMLPromptManager("prompts/base_prompts.yaml")

    # Отримуємо всі категорії
    stats = manager.get_statistics()

    print("📊 Статистика за категоріями:")
    for category, count in stats["categories"].items():
        if count > 0:
            print(f"   • {category}: {count} промптів")

    print("\n🔍 Детальний огляд категорій:")
    for category in PromptCategory:
        prompts = manager.get_prompts_by_category(category.value)
        if prompts:
            print(f"\n   📂 {category.value.upper()}:")
            for prompt in prompts:
                print(f"      • {prompt.name} (пріоритет: {prompt.priority})")


if __name__ == "__main__":
    # Запускаємо основні демонстрації
    main()
    demo_search_and_suggestions()
    demo_formatting()
    demo_categories()

    print("\n🎉 Всі демонстрації завершено!")
