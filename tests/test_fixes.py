#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки виправлень проблем з Streamlit.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Завантажуємо змінні середовища
load_dotenv()

# Додаємо src до шляху
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_swagger_agent():
    """Тестує SwaggerAgent."""
    print("🧪 Тестування SwaggerAgent...")
    
    try:
        from interactive_api_agent import InteractiveSwaggerAgent as SwaggerAgent
        
        # Ініціалізуємо агента
        swagger_path = "examples/swagger_specs/shop_api.json"
        agent = SwaggerAgent(swagger_path, enable_api_calls=False)
        
        print("✅ SwaggerAgent ініціалізовано успішно")
        print(f"📊 Базовий URL: {agent.base_url}")
        
        # Тестуємо отримання endpoints
        endpoints = agent.get_available_endpoints()
        print(f"📋 Знайдено {len(endpoints)} endpoints")
        
        # Перевіряємо структуру endpoints
        if endpoints:
            first_endpoint = endpoints[0]
            print(f"📝 Приклад endpoint: {type(first_endpoint)}")
            if isinstance(first_endpoint, dict):
                print(f"   - Має ключі: {list(first_endpoint.keys())}")
                if 'metadata' in first_endpoint:
                    print(f"   - Метадані: {first_endpoint['metadata']}")
        
        # Тестуємо доступ до parser
        parser = agent.parser
        print(f"✅ Parser доступний: {type(parser)}")
        
        # Тестуємо методи parser
        parser_endpoints = parser.get_endpoints()
        print(f"📊 Parser endpoints: {len(parser_endpoints)}")
        
        schemas = parser.get_schemas()
        print(f"📋 Parser схеми: {len(schemas)}")
        
        base_url = parser.get_base_url()
        print(f"🔗 Parser базовий URL: {base_url}")
        
        assert True, "SwaggerAgent працює коректно"
        
    except Exception as e:
        print(f"❌ Помилка тестування SwaggerAgent: {e}")
        assert False, f"SwaggerAgent не працює: {e}"

def test_rag_engine():
    """Тестує RAGEngine."""
    print("\n🧪 Тестування RAGEngine...")
    
    try:
        from rag_engine import RAGEngine
        
        # Ініціалізуємо RAG engine
        swagger_path = "examples/swagger_specs/shop_api.json"
        rag_engine = RAGEngine(swagger_path)
        
        print("✅ RAGEngine ініціалізовано успішно")
        
        # Тестуємо отримання всіх endpoints
        all_endpoints = rag_engine.get_all_endpoints()
        print(f"📋 Всі endpoints: {len(all_endpoints)}")
        
        # Перевіряємо структуру
        if all_endpoints:
            first_endpoint = all_endpoints[0]
            print(f"📝 Приклад endpoint: {type(first_endpoint)}")
            if isinstance(first_endpoint, dict):
                print(f"   - Має ключі: {list(first_endpoint.keys())}")
                if 'metadata' in first_endpoint:
                    print(f"   - Метадані: {first_endpoint['metadata']}")
        
        assert True, "RAGEngine працює коректно"
        
    except Exception as e:
        print(f"❌ Помилка тестування RAGEngine: {e}")
        assert False, f"RAGEngine не працює: {e}"

def main():
    """Головна функція тестування."""
    print("🚀 Тестування виправлень")
    print("=" * 50)
    
    # Перевіряємо наявність файлів
    swagger_file = "examples/swagger_specs/shop_api.json"
    if not os.path.exists(swagger_file):
        print(f"❌ Swagger файл не знайдено: {swagger_file}")
        return
    
    print(f"✅ Swagger файл знайдено: {swagger_file}")
    
    # Запускаємо тести
    test1_passed = test_swagger_agent()
    test2_passed = test_rag_engine()
    
    print("\n" + "=" * 50)
    print("📊 Результати тестування:")
    print(f"   SwaggerAgent: {'✅' if test1_passed else '❌'}")
    print(f"   RAGEngine: {'✅' if test2_passed else '❌'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 Всі тести пройшли успішно!")
        print("💡 Тепер можна запускати Streamlit додаток")
    else:
        print("\n⚠️ Є проблеми, які потрібно виправити")

if __name__ == "__main__":
    main()
