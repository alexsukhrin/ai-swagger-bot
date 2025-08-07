"""
Приклад використання покращеної системи промптів.
"""

import sys
import os
from dotenv import load_dotenv

# Завантажуємо змінні середовища
load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.enhanced_prompt_manager import EnhancedPromptManager, EnhancedPromptTemplate
from src.prompt_descriptions import PromptDescriptions, PromptCategory

def main():
    """Основний приклад використання покращеної системи промптів."""
    
    print("🚀 Приклад використання покращеної системи промптів")
    print("=" * 60)
    
    # 1. Створюємо покращений менеджер
    print("\n1️⃣ Створення покращеного менеджера промптів...")
    manager = EnhancedPromptManager()
    print("✅ Менеджер готовий!")
    
    # 2. Додаємо промпти з описів
    print("\n2️⃣ Додавання промптів з описів...")
    
    # Системний промпт
    system_desc = PromptDescriptions.get_system_prompt_description()
    system_prompt = EnhancedPromptTemplate(
        name="Enhanced System Prompt",
        description=system_desc.description,
        prompt_text="""
Ти - експерт з API та Swagger/OpenAPI специфікаціями. Твоя задача - допомогти користувачам взаємодіяти з API через природну мову.

Ти маєш доступ до:
- Swagger/OpenAPI специфікації API
- Історії попередніх взаємодій з користувачем
- Можливості виконувати API виклики
- Аналізу помилок сервера

Твої основні функції:
1. Розуміти запити користувача природною мовою
2. Знаходити відповідні API endpoints
3. Формувати правильні API запити
4. Аналізувати помилки сервера
5. Запитувати додаткову інформацію при необхідності
6. Повторно виконувати запити з новою інформацією

Завжди відповідай українською мовою та будь корисним та дружелюбним.
Використовуй емодзі для кращого сприйняття та структуруй відповіді зрозуміло.
        """,
        category=system_desc.category.value,
        tags=system_desc.tags,
        description_object=system_desc
    )
    
    system_id = manager.add_enhanced_prompt(system_prompt)
    print(f"✅ Додано системний промпт з ID: {system_id}")
    
    # Промпт для аналізу наміру
    intent_desc = PromptDescriptions.get_intent_analysis_description()
    intent_prompt = EnhancedPromptTemplate(
        name="Enhanced Intent Analysis",
        description=intent_desc.description,
        prompt_text="""
Ти - експерт з API. Аналізуй запит користувача та визначай:
1. Тип операції (GET, POST, PUT, DELETE)
2. Ресурс або endpoint
3. Параметри та дані
4. Мета або ціль запиту

Контекст попередніх взаємодій:
{context}

Запит користувача: {user_query}

Відповідай у форматі JSON:
{{
    "operation": "GET|POST|PUT|DELETE",
    "resource": "назва ресурсу",
    "parameters": {{"param1": "value1"}},
    "data": {{"field1": "value1"}},
    "intent": "опис мети запиту"
}}
        """,
        category=intent_desc.category.value,
        tags=intent_desc.tags,
        description_object=intent_desc
    )
    
    intent_id = manager.add_enhanced_prompt(intent_prompt)
    print(f"✅ Додано промпт аналізу наміру з ID: {intent_id}")
    
    # 3. Створюємо промпт з шаблону
    print("\n3️⃣ Створення промпту з шаблону...")
    
    template_id = manager.create_prompt_from_template(
        "error_handling",
        name="Custom Error Handler",
        prompt_text="""
Проаналізуй помилку сервера та згенеруй корисний запит на додаткову інформацію.

Помилка сервера: {error_message}
Оригінальний запит: {original_query}
API запит: {api_request}

Типи помилок:
- Валідація: потрібні додаткові поля
- Авторизація: проблеми з токеном
- Не знайдено: неправильний ID або шлях
- Конфлікт: запис вже існує

Створи зрозумілий запит українською мовою, який допоможе користувачу надати недостатню інформацію.

Відповідь має бути дружелюбною та конкретною, з емодзі для кращого сприйняття.
        """,
        tags=["custom", "error", "user_friendly"]
    )
    
    print(f"✅ Створено промпт з шаблону з ID: {template_id}")
    
    # 4. Отримуємо пропозиції промптів
    print("\n4️⃣ Отримання пропозицій промптів...")
    
    test_queries = [
        "Покажи всі товари",
        "Створи новий товар",
        "Онови товар з ID 123",
        "Видали товар з ID 456",
        "Помилка при створенні товару"
    ]
    
    for query in test_queries:
        suggestions = manager.get_prompt_suggestions(query)
        print(f"\n📝 Запит: {query}")
        print(f"🎯 Знайдено {len(suggestions)} пропозицій:")
        
        for i, suggestion in enumerate(suggestions[:2], 1):
            print(f"  {i}. {suggestion['name']} (релевантність: {suggestion['relevance_score']:.2f})")
    
    # 5. Отримуємо статистику
    print("\n5️⃣ Статистика промптів...")
    
    stats = manager.get_prompt_statistics()
    print(f"📊 Загальна статистика:")
    print(f"  • Всього промптів: {stats['total_prompts']}")
    print(f"  • Активних промптів: {stats['active_prompts']}")
    print(f"  • Середня успішність: {stats['avg_success_rate']:.2%}")
    print(f"  • Загальне використання: {stats['total_usage']}")
    
    print(f"\n📈 Статистика по категоріях:")
    for category, cat_stats in stats['category_details'].items():
        if cat_stats['count'] > 0:
            print(f"  • {category}: {cat_stats['count']} промптів, "
                  f"успішність: {cat_stats['avg_success_rate']:.2%}")
    
    # 6. Експортуємо конфігурацію
    print("\n6️⃣ Експорт конфігурації...")
    
    manager.save_prompt_config()
    print("✅ Конфігурація збережена в prompt_config.json")
    
    # Експорт в JSON файл
    manager.export_prompts_to_file("exported_prompts.json", "json")
    
    # 7. Демонстрація роботи з метаданими
    print("\n7️⃣ Робота з метаданими...")
    
    # Отримуємо промпт з метаданими
    if system_id > 0:
        enhanced_prompt = manager.get_prompt_with_metadata(system_id)
        if enhanced_prompt:
            print(f"📋 Промпт: {enhanced_prompt.name}")
            print(f"📊 Метадані: {enhanced_prompt.metadata}")
    
    # Отримуємо промпти за категорією з метаданими
    system_prompts = manager.get_prompts_by_category_with_metadata("system")
    print(f"\n🔧 Системних промптів: {len(system_prompts)}")
    
    for prompt in system_prompts:
        print(f"  • {prompt.name} (використання: {prompt.metadata.get('usage_count', 0)})")
    
    print("\n✅ Приклад завершено!")


def demonstrate_prompt_management():
    """Демонстрація управління промптами."""
    
    print("\n🔄 Демонстрація управління промптами")
    print("=" * 50)
    
    manager = EnhancedPromptManager()
    
    # Додаємо кастомний промпт
    custom_prompt = EnhancedPromptTemplate(
        name="Custom Data Retrieval",
        description="Кастомний промпт для отримання даних",
        prompt_text="""
Ти експерт API. Користувач хоче отримати дані.

ЗАПИТ: {user_query}

ЗАВДАННЯ:
1. Знайди відповідний GET endpoint
2. Перевір параметри
3. Виконай запит
4. Поверни результат

ВІДПОВІДЬ:
{{
    "endpoint": "URL endpoint",
    "method": "GET",
    "parameters": {{}},
    "result": "результат запиту"
}}
        """,
        category="data_retrieval",
        tags=["custom", "data", "retrieval"]
    )
    
    prompt_id = manager.add_enhanced_prompt(custom_prompt)
    print(f"✅ Додано кастомний промпт з ID: {prompt_id}")
    
    # Оновлюємо промпт
    custom_prompt.description = "Оновлений опис кастомного промпту"
    custom_prompt.tags.append("updated")
    
    success = manager.update_prompt(prompt_id, custom_prompt)
    print(f"✅ Промпт оновлено: {success}")
    
    # Шукаємо промпти
    search_results = manager.search_prompts("кастомний")
    print(f"🔍 Знайдено {len(search_results)} промптів по запиту 'кастомний'")
    
    for prompt in search_results:
        print(f"  • {prompt.name} ({prompt.category})")


if __name__ == "__main__":
    main()
    demonstrate_prompt_management()
