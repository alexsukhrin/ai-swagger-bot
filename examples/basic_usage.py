"""
Простий приклад використання Swagger агента.
"""

import sys
import os
from dotenv import load_dotenv

# Завантажуємо змінні середовища з .env файлу
load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.interactive_api_agent import InteractiveSwaggerAgent as SwaggerAgent


def main():
    """Основний приклад використання."""
    
    print("🚀 Приклад використання AI Swagger Bot")
    print("=" * 50)
    
    # Перевіряємо наявність API ключа
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY не знайдено!")
        print("💡 Встановіть змінну середовища:")
        print("   export OPENAI_API_KEY=your_api_key_here")
        print("   або створіть .env файл з OPENAI_API_KEY=your_key")
        return
    
    # 1. Ініціалізація агента
    print("\n1️⃣ Ініціалізація агента...")
    agent = SwaggerAgent(
        swagger_spec_path="examples/swagger_specs/shop_api.json",
        enable_api_calls=False  # Без викликів API для демонстрації
    )
    print("✅ Агент готовий!")
    
    # 2. Приклад запиту
    print("\n2️⃣ Обробка запиту...")
    user_query = "Додай товар: синя сукня, розмір 22, кількість 10"
    print(f"📝 Запит: {user_query}")
    
    response = agent.process_interactive_query(user_query)
    print(f"🤖 Відповідь:\n{response['response']}")
    print(f"📊 Статус: {response['status']}")
    
    # 3. Інші приклади
    print("\n3️⃣ Додаткові приклади...")
    
    examples = [
        "Створи новий товар - червона сукня, розмір 44, 5 штук",
        "Покажи всі товари",
        "Отримай товар з ID 123"
    ]
    
    for example in examples:
        print(f"\n📝 Запит: {example}")
        response = agent.process_interactive_query(example)
        print(f"🤖 Відповідь: {response['response'][:100]}...")
        print(f"📊 Статус: {response['status']}")
    
    # 4. Інформація про доступні endpoints
    print("\n4️⃣ Доступні endpoints:")
    endpoints = agent.get_available_endpoints()
    
    for endpoint in endpoints[:3]:  # Показуємо перші 3
        metadata = endpoint['metadata']
        method = metadata.get('method', 'GET')
        path = metadata.get('path', '')
        summary = metadata.get('summary', 'Без опису')
        
        print(f"  • {method} {path} - {summary}")
    
    print(f"\n📊 Всього endpoints: {len(endpoints)}")
    
    print("\n✅ Приклад завершено!")


if __name__ == "__main__":
    main()
