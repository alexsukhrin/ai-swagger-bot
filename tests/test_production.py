#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки AI Swagger Agent з продакшн сервером
"""

import os
import sys
from dotenv import load_dotenv

# Завантажуємо змінні середовища з .env файлу
load_dotenv()

# Додаємо шлях до src
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from interactive_api_agent import InteractiveSwaggerAgent as SwaggerAgent

def test_production_api():
    """Тестуємо API з продакшн сервером"""
    
    print("🚀 Тестування AI Swagger Agent з продакшн сервером")
    print("=" * 60)
    
    # Завантажуємо змінні середовища
    
    # Ініціалізуємо агента з продакшн Swagger файлом
    swagger_file = "examples/swagger_specs/shop_api_prod.json"
    
    try:
        agent = SwaggerAgent(
            swagger_spec_path=swagger_file,
            enable_api_calls=True
        )
        
        print(f"✅ Агент ініціалізовано успішно")
        print(f"📁 Swagger файл: {swagger_file}")
        print(f"🌐 Базовий URL: {agent.base_url}")
        print()
        
        # Тестуємо різні запити
        test_queries = [
            "Покажи всі категорії",
            "Створи категорію: Електроніка, опис: Електронні пристрої та гаджети",
            "Створи категорію: Одяг, опис: Модний одяг для всіх сезонів",
            "Покажи всі бренди",
            "Створи бренд: Apple, опис: Американська компанія з виробництва електроніки",
            "Покажи всі продукти",
            "Створи продукт: iPhone 15 Pro, ціна: 999.99, опис: Новий iPhone з передовими функціями"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"🔍 Тест {i}: {query}")
            print("-" * 40)
            
            try:
                response = agent.process_interactive_query(query)
                print(f"✅ Відповідь: {response['response']}")
                print(f"📊 Статус: {response['status']}")
            except Exception as e:
                print(f"❌ Помилка: {e}")
            
            print()
        
        print("🎉 Тестування завершено!")
        
    except Exception as e:
        print(f"❌ Помилка ініціалізації агента: {e}")

if __name__ == "__main__":
    test_production_api()
