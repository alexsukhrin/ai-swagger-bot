"""
Приклад використання промпту для обробки відповідей API сервера.
"""

import sys
import os
import json
from dotenv import load_dotenv

# Завантажуємо змінні середовища
load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.prompt_templates import PromptTemplates
from src.enhanced_prompt_manager import EnhancedPromptManager, EnhancedPromptTemplate
from src.prompt_descriptions import PromptDescriptions

def simulate_api_response():
    """Симулює відповідь API сервера."""
    return {
        "status": "success",
        "data": [
            {
                "id": 1,
                "name": "Синя сукня",
                "category": "Одяг",
                "price": 1500.00,
                "currency": "UAH",
                "description": "Елегантна синя сукня для вечірки",
                "in_stock": True,
                "size": "M",
                "color": "Синій"
            },
            {
                "id": 2,
                "name": "Червона футболка",
                "category": "Одяг",
                "price": 450.00,
                "currency": "UAH",
                "description": "Зручна червона футболка",
                "in_stock": True,
                "size": "L",
                "color": "Червоний"
            },
            {
                "id": 3,
                "name": "Зелена куртка",
                "category": "Одяг",
                "price": 2500.00,
                "currency": "UAH",
                "description": "Тепла зелена куртка",
                "in_stock": False,
                "size": "XL",
                "color": "Зелений"
            },
            {
                "id": 4,
                "name": "Чорні кросівки",
                "category": "Взуття",
                "price": 1800.00,
                "currency": "UAH",
                "description": "Стильні чорні кросівки",
                "in_stock": True,
                "size": "42",
                "color": "Чорний"
            },
            {
                "id": 5,
                "name": "Золота сережка",
                "category": "Аксесуари",
                "price": 800.00,
                "currency": "UAH",
                "description": "Елегантна золота сережка",
                "in_stock": True,
                "size": "One size",
                "color": "Золотий"
            }
        ],
        "total": 5,
        "page": 1,
        "per_page": 10
    }

def test_api_response_processing():
    """Тестує обробку відповідей API."""
    
    print("🚀 Тестування обробки відповідей API")
    print("=" * 50)
    
    # Симулюємо відповідь API
    api_response = simulate_api_response()
    
    # Тестові запити
    test_queries = [
        "Покажи всі товари",
        "Покажи тільки назви товарів",
        "Покажи ID та назву товарів",
        "Покажи категорії товарів",
        "Покажи ціни товарів",
        "Покажи тільки назви та ціни",
        "Покажи товари в наявності",
        "Покажи тільки одяг",
        "Покажи тільки взуття",
        "Покажи тільки аксесуари"
    ]
    
    print(f"📊 JSON відповідь API:")
    print(json.dumps(api_response, ensure_ascii=False, indent=2))
    print("\n" + "="*50 + "\n")
    
    for query in test_queries:
        print(f"📝 ЗАПИТ: {query}")
        print("-" * 30)
        
        # Генеруємо промпт для обробки
        prompt = PromptTemplates.get_api_response_processing_prompt(
            user_query=query,
            api_response=api_response,
            available_fields=["id", "name", "category", "price", "currency", "description", "in_stock", "size", "color"]
        )
        
        print(f"🤖 ПРОМПТ ДЛЯ GPT:")
        print(prompt)
        print("\n" + "="*50 + "\n")

def demonstrate_enhanced_prompt_manager():
    """Демонструє роботу з покращеним менеджером промптів."""
    
    print("🔄 Демонстрація покращеного менеджера промптів")
    print("=" * 50)
    
    manager = EnhancedPromptManager()
    
    # Додаємо промпт для обробки відповідей API
    api_response_desc = PromptDescriptions.get_api_response_processing_description()
    
    api_response_prompt = EnhancedPromptTemplate(
        name="API Response Processing",
        description=api_response_desc.description,
        prompt_text=PromptTemplates.get_api_response_processing_prompt.__doc__,
        category=api_response_desc.category.value,
        tags=api_response_desc.tags,
        description_object=api_response_desc
    )
    
    prompt_id = manager.add_enhanced_prompt(api_response_prompt)
    print(f"✅ Додано промпт обробки API відповідей з ID: {prompt_id}")
    
    # Тестуємо пропозиції
    test_queries = [
        "Покажи тільки назви товарів",
        "Покажи ID та назву",
        "Покажи категорії",
        "Покажи ціни"
    ]
    
    for query in test_queries:
        suggestions = manager.get_prompt_suggestions(query)
        print(f"\n📝 Запит: {query}")
        print(f"🎯 Знайдено {len(suggestions)} пропозицій:")
        
        for i, suggestion in enumerate(suggestions[:2], 1):
            print(f"  {i}. {suggestion['name']} (релевантність: {suggestion['relevance_score']:.2f})")
    
    # Отримуємо статистику
    stats = manager.get_prompt_statistics()
    print(f"\n📊 Статистика:")
    print(f"  • Всього промптів: {stats['total_prompts']}")
    print(f"  • Активних промптів: {stats['active_prompts']}")
    
    # Експортуємо конфігурацію
    manager.save_prompt_config()
    print("💾 Конфігурація збережена")

def show_expected_outputs():
    """Показує очікувані виходи для різних запитів."""
    
    print("🎯 Очікувані виходи для різних запитів")
    print("=" * 50)
    
    api_response = simulate_api_response()
    
    expected_outputs = {
        "Покажи тільки назви товарів": """
📋 Список назв товарів:
• Синя сукня
• Червона футболка
• Зелена куртка
• Чорні кросівки
• Золота сережка
        """,
        
        "Покажи ID та назву товарів": """
🆔 Товари:
• 1: Синя сукня
• 2: Червона футболка
• 3: Зелена куртка
• 4: Чорні кросівки
• 5: Золота сережка
        """,
        
        "Покажи категорії товарів": """
📂 Доступні категорії:
• Одяг (3 товари)
• Взуття (1 товар)
• Аксесуари (1 товар)
        """,
        
        "Покажи ціни товарів": """
💰 Ціни товарів:
• Синя сукня: 1500.00 UAH
• Червона футболка: 450.00 UAH
• Зелена куртка: 2500.00 UAH
• Чорні кросівки: 1800.00 UAH
• Золота сережка: 800.00 UAH
        """,
        
        "Покажи тільки назви та ціни": """
📋 Назви та ціни товарів:
• Синя сукня - 1500.00 UAH
• Червона футболка - 450.00 UAH
• Зелена куртка - 2500.00 UAH
• Чорні кросівки - 1800.00 UAH
• Золота сережка - 800.00 UAH
        """,
        
        "Покажи товари в наявності": """
✅ Товари в наявності:
• Синя сукня (ID: 1)
• Червона футболка (ID: 2)
• Чорні кросівки (ID: 4)
• Золота сережка (ID: 5)
        """,
        
        "Покажи тільки одяг": """
👕 Одяг:
• Синя сукня (ID: 1) - 1500.00 UAH
• Червона футболка (ID: 2) - 450.00 UAH
• Зелена куртка (ID: 3) - 2500.00 UAH
        """
    }
    
    for query, expected_output in expected_outputs.items():
        print(f"\n📝 ЗАПИТ: {query}")
        print("📤 ОЧІКУВАНИЙ ВИХІД:")
        print(expected_output.strip())
        print("-" * 50)

def main():
    """Основний приклад."""
    
    print("🚀 Приклад обробки відповідей API сервера")
    print("=" * 60)
    
    # Тестуємо обробку відповідей
    test_api_response_processing()
    
    # Демонструємо покращений менеджер
    demonstrate_enhanced_prompt_manager()
    
    # Показуємо очікувані виходи
    show_expected_outputs()
    
    print("\n✅ Приклад завершено!")

if __name__ == "__main__":
    main()
