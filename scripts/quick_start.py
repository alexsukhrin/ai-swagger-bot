#!/usr/bin/env python3
"""
Quick Start скрипт для AI Swagger Bot.
Демонструє основну функціональність агента.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Завантажуємо змінні середовища
load_dotenv()

# Додаємо шлях до src та кореневої директорії
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

def check_environment():
    """Перевіряє налаштування середовища."""
    print("🔍 Перевірка середовища...")
    
    # Перевіряємо Python версію
    if sys.version_info < (3, 8):
        print("❌ Потрібен Python 3.8 або новіше")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Перевіряємо OpenAI API ключ
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Не знайдено OPENAI_API_KEY")
        print("💡 Додайте API ключ в .env файл або змінні середовища")
        return False
    print("✅ OpenAI API ключ знайдено")
    
    # Перевіряємо Swagger файл
    swagger_file = "examples/swagger_specs/shop_api.json"
    if not os.path.exists(swagger_file):
        print(f"❌ Swagger файл не знайдено: {swagger_file}")
        return False
    print(f"✅ Swagger файл знайдено: {swagger_file}")
    
    return True


def demo_simple_agent():
    """Демонструє простий агент."""
    print("\n🤖 Демонстрація простого агента (без LangChain)")
    print("=" * 60)
    
    try:
        from interactive_api_agent import InteractiveSwaggerAgent as SimpleSwaggerAgent
        
        # Ініціалізуємо агента
        agent = SimpleSwaggerAgent(
            "examples/swagger_specs/shop_api.json",
            enable_api_calls=False
        )
        
        # Тестові запити
        test_queries = [
            "Додай товар: синя сукня, розмір 22, кількість 10",
            "Покажи всі товари",
            "Отримай товар з ID 123"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Тест {i}: {query}")
            print("-" * 40)
            
            try:
                response = agent.process_interactive_query(query)
                print(f"🤖 Відповідь: {response['response']}")
                print(f"📊 Статус: {response['status']}")
            except Exception as e:
                print(f"❌ Помилка: {e}")
        
        # Інформація про агента
        if hasattr(agent, 'get_agent_info'):
            info = agent.get_agent_info()
            print(f"\n📊 Інформація про агента:")
            print(f"   Базовий URL: {info.get('base_url')}")
            print(f"   Endpoints: {info.get('endpoints_count')}")
        
    except Exception as e:
        print(f"❌ Помилка демонстрації простого агента: {e}")


def demo_api_agent():
    """Демонструє API агент."""
    print("\n🤖 Демонстрація API агента (з LangChain)")
    print("=" * 60)
    
    try:
        from interactive_api_agent import InteractiveSwaggerAgent as SwaggerAgent
        
        # Ініціалізуємо агента
        agent = SwaggerAgent(
            "examples/swagger_specs/shop_api.json",
            enable_api_calls=False
        )
        
        # Тестові запити
        test_queries = [
            "Створи новий товар - червона сукня, розмір 44, 5 штук",
            "Онови товар 456 - зміни ціну на 2000 грн",
            "Видали товар 789"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Тест {i}: {query}")
            print("-" * 40)
            
            try:
                response = agent.process_interactive_query(query)
                print(f"🤖 Відповідь: {response['response']}")
                print(f"📊 Статус: {response['status']}")
            except Exception as e:
                print(f"❌ Помилка: {e}")
        
    except Exception as e:
        print(f"❌ Помилка демонстрації API агента: {e}")


def demo_endpoints():
    """Демонструє перегляд endpoints."""
    print("\n🔍 Демонстрація перегляду endpoints")
    print("=" * 60)
    
    try:
        from interactive_api_agent import InteractiveSwaggerAgent as SwaggerAgent
        
        agent = SwaggerAgent("examples/swagger_specs/shop_api.json")
        endpoints = agent.get_available_endpoints()
        
        print(f"📊 Знайдено {len(endpoints)} endpoints:\n")
        
        for i, endpoint in enumerate(endpoints[:5], 1):  # Показуємо перші 5
            metadata = endpoint['metadata']
            method = metadata.get('method', 'GET')
            path = metadata.get('path', '')
            summary = metadata.get('summary', 'Без опису')
            
            # Кольори для методів
            method_colors = {
                'GET': '🟢',
                'POST': '🔵',
                'PUT': '🟡',
                'DELETE': '🔴',
                'PATCH': '🟠'
            }
            
            method_icon = method_colors.get(method, '⚪')
            print(f"{i}. {method_icon} {method:6} {path}")
            print(f"   {summary}")
            print()
        
        if len(endpoints) > 5:
            print(f"... та ще {len(endpoints) - 5} endpoints")
        
    except Exception as e:
        print(f"❌ Помилка демонстрації endpoints: {e}")


def show_usage_examples():
    """Показує приклади використання."""
    print("\n📚 Приклади використання")
    print("=" * 60)
    
    examples = {
        "CLI інтерфейс": [
            "python cli.py --swagger examples/swagger_specs/shop_api.json",
            "python cli.py --swagger examples/swagger_specs/shop_api.json --query 'Додай товар: тест'",
            "python cli.py --swagger examples/swagger_specs/shop_api.json --list-endpoints"
        ],
        "Streamlit інтерфейс": [
            "streamlit run enhanced_chat_app.py"
        ],
        "Python код": [
            "from src.interactive_api_agent import InteractiveSwaggerAgent",
            "agent = InteractiveSwaggerAgent('examples/swagger_specs/shop_api.json')",
            "response = agent.process_interactive_query('Додай товар: тест')"
        ],
        "Make команди": [
            "make install    # Встановлення",
            "make test      # Тести",
            "make run       # Запуск Streamlit",
            "make clean     # Очищення"
        ]
    }
    
    for category, commands in examples.items():
        print(f"\n{category}:")
        for command in commands:
            print(f"  {command}")


def main():
    """Основний функція демонстрації."""
    print("🚀 AI Swagger Bot - Quick Start")
    print("=" * 60)
    
    # Перевіряємо середовище
    if not check_environment():
        print("\n❌ Перевірка середовища не пройшла")
        print("💡 Перевірте налаштування та спробуйте ще раз")
        return
    
    print("\n✅ Середовище готове до роботи!")
    
    # Демонстрації
    demo_simple_agent()
    demo_api_agent()
    demo_endpoints()
    show_usage_examples()
    
    print("\n🎉 Демонстрація завершена!")
    print("\n💡 Для повної функціональності:")
    print("1. Додайте ваші Swagger файли в examples/swagger_specs/")
    print("2. Налаштуйте API виклики в .env файлі")
    print("3. Використовуйте CLI або Streamlit інтерфейс")
    print("\n📚 Детальна документація: README.md")


if __name__ == "__main__":
    main()
