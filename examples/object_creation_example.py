"""
Приклад використання функціоналу створення об'єктів з автоматичним заповненням полів.
"""

import sys
import os
from dotenv import load_dotenv

# Завантажуємо змінні середовища
load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.interactive_api_agent import InteractiveSwaggerAgent

def test_object_creation():
    """Тестує створення об'єктів з автоматичним заповненням полів."""
    
    print("🚀 Тестування створення об'єктів з автоматичним заповненням")
    print("=" * 60)
    
    # Створюємо агента
    agent = InteractiveSwaggerAgent(
        swagger_spec_path="examples/swagger_specs/shop_api.json",
        enable_api_calls=False  # Без викликів API для демонстрації
    )
    
    # Тестові запити на створення
    creation_queries = [
        "Створи нову категорію Електроніка",
        "Створи товар з назвою Телефон",
        "Створи товар з назвою Ноутбук",
        "Створи категорію Одяг",
        "Створи користувача Іван Петренко",
        "Додай новий товар з назвою Планшет"
    ]
    
    print("📝 Тестові запити на створення:")
    for i, query in enumerate(creation_queries, 1):
        print(f"  {i}. {query}")
    
    print("\n" + "="*60 + "\n")
    
    # Тестуємо кожен запит
    for i, query in enumerate(creation_queries, 1):
        print(f"🔧 ТЕСТ {i}: {query}")
        print("-" * 40)
        
        # Обробляємо запит
        result = agent.process_interactive_query(query, f"test_user_{i}")
        
        print(f"📊 Статус: {result.get('status', 'unknown')}")
        print(f"✅ Успіх: {result.get('success', False)}")
        print(f"🤖 Відповідь:")
        print(result.get('response', 'Немає відповіді'))
        print("\n" + "="*60 + "\n")

def test_error_handling():
    """Тестує обробку помилок при створенні."""
    
    print("🔄 Тестування обробки помилок при створенні")
    print("=" * 50)
    
    # Створюємо агента
    agent = InteractiveSwaggerAgent(
        swagger_spec_path="examples/swagger_specs/shop_api.json",
        enable_api_calls=False
    )
    
    # Тестові запити з потенційними помилками
    error_queries = [
        "Створи товар",  # Без назви
        "Створи категорію",  # Без назви
        "Створи щось незрозуміле",  # Невідомий тип
        "Створи товар з ціною 1000",  # Неправильний формат
    ]
    
    for i, query in enumerate(error_queries, 1):
        print(f"🔧 ТЕСТ ПОМИЛКИ {i}: {query}")
        print("-" * 40)
        
        result = agent.process_interactive_query(query, f"error_user_{i}")
        
        print(f"📊 Статус: {result.get('status', 'unknown')}")
        print(f"✅ Успіх: {result.get('success', False)}")
        print(f"🤖 Відповідь:")
        print(result.get('response', 'Немає відповіді'))
        print("\n" + "="*50 + "\n")

def test_conversation_context():
    """Тестує використання контексту розмови."""
    
    print("💬 Тестування контексту розмови")
    print("=" * 50)
    
    # Створюємо агента
    agent = InteractiveSwaggerAgent(
        swagger_spec_path="examples/swagger_specs/shop_api.json",
        enable_api_calls=False
    )
    
    user_id = "context_test_user"
    
    # Симулюємо діалог
    conversation_steps = [
        "Покажи всі категорії",
        "Створи товар з назвою Телефон",
        "Створи ще один товар з назвою Навушники",
        "Створи категорію Аксесуари"
    ]
    
    for i, query in enumerate(conversation_steps, 1):
        print(f"💬 КРОК {i}: {query}")
        print("-" * 30)
        
        result = agent.process_interactive_query(query, user_id)
        
        print(f"📊 Статус: {result.get('status', 'unknown')}")
        print(f"✅ Успіх: {result.get('success', False)}")
        print(f"🤖 Відповідь:")
        print(result.get('response', 'Немає відповіді'))
        print("\n" + "="*50 + "\n")

def show_expected_behavior():
    """Показує очікувану поведінку системи."""
    
    print("🎯 Очікувана поведінка системи")
    print("=" * 50)
    
    expected_behaviors = {
        "Створи товар з назвою Телефон": {
            "auto_fill": {
                "name": "Телефон",
                "description": "Сучасний смартфон з високоякісними характеристиками",
                "price": 15000.00,
                "category": "Електроніка",
                "brand": "Samsung",
                "model": "Galaxy S23",
                "color": "Чорний",
                "in_stock": True
            },
            "response": """
✅ **Товар успішно створено!**

📋 **Деталі створення:**
• Назва: Телефон
• Опис: Сучасний смартфон з високоякісними характеристиками
• Ціна: 15000.00 UAH
• Категорія: Електроніка
• Бренд: Samsung
• Модель: Galaxy S23
• Колір: Чорний
• Статус: В наявності

🔗 **API Запит:**
• URL: /api/products
• Метод: POST
• Статус: ✅ Успішно
            """
        },
        
        "Створи категорію Електроніка": {
            "auto_fill": {
                "name": "Електроніка",
                "description": "Категорія для електронних пристроїв та гаджетів",
                "slug": "electronics",
                "status": "active",
                "icon": "📱"
            },
            "response": """
✅ **Категорія успішно створена!**

📋 **Деталі створення:**
• Назва: Електроніка
• Опис: Категорія для електронних пристроїв та гаджетів
• Slug: electronics
• Статус: active
• Іконка: 📱

🔗 **API Запит:**
• URL: /api/categories
• Метод: POST
• Статус: ✅ Успішно
            """
        },
        
        "Помилка валідації": {
            "error": "Field 'price' is required",
            "response": """
❌ **Помилка валідації при створенні:**
Field 'price' is required

💡 **Запропоновані дані:**
• Назва: Телефон
• Опис: Сучасний смартфон...
• Ціна: 15000.00 UAH

🔄 **Рішення:**
Будь ласка, уточніть необхідні поля або спробуйте ще раз.
            """
        }
    }
    
    for query, behavior in expected_behaviors.items():
        print(f"\n📝 ЗАПИТ: {query}")
        print("📤 ОЧІКУВАНА ВІДПОВІДЬ:")
        
        if "auto_fill" in behavior:
            print("🔧 Автоматичне заповнення:")
            for key, value in behavior["auto_fill"].items():
                print(f"  • {key}: {value}")
        
        if "response" in behavior:
            print("🤖 Відповідь:")
            print(behavior["response"])
        
        if "error" in behavior:
            print("❌ Помилка:")
            print(behavior["error"])
        
        print("-" * 50)

def main():
    """Основний приклад."""
    
    print("🚀 Приклад створення об'єктів з автоматичним заповненням полів")
    print("=" * 70)
    
    # Тестуємо створення об'єктів
    test_object_creation()
    
    # Тестуємо обробку помилок
    test_error_handling()
    
    # Тестуємо контекст розмови
    test_conversation_context()
    
    # Показуємо очікувану поведінку
    show_expected_behavior()
    
    print("\n✅ Приклад завершено!")

if __name__ == "__main__":
    main()
