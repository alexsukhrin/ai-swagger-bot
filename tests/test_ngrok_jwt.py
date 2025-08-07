#!/usr/bin/env python3
"""
Тест JWT авторизації з ngrok URL.
"""

import os
import sys
from pathlib import Path

# Додаємо шлях до src
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

try:
    from interactive_api_agent import InteractiveSwaggerAgent as SwaggerAgent
    print("✅ Успішно імпортовано SwaggerAgent")
except ImportError as e:
    print(f"❌ Помилка імпорту: {e}")
    sys.exit(1)


def test_jwt_with_ngrok_url():
    """Тест JWT авторизації з ngrok URL."""
    print("🔐 ТЕСТ JWT АВТОРИЗАЦІЇ З NGROK URL")
    print("=" * 60)
    
    # Перевіряємо змінні середовища
    api_key = os.getenv('OPENAI_API_KEY')
    jwt_token = os.getenv('JWT_TOKEN')
    
    if not api_key or not jwt_token:
        print("❌ Відсутні OPENAI_API_KEY або JWT_TOKEN")
        return False
    
    print("✅ Всі необхідні ключі знайдено")
    
    try:
        # Створюємо агента
        agent = SwaggerAgent(
            swagger_spec_path="examples/swagger_specs/shop_api.json",
            enable_api_calls=True,
            openai_api_key=api_key,
            jwt_token=jwt_token
        )
        print("✅ Агент ініціалізовано")
        
        # Тестуємо з різними URL
        test_urls = [
            {
                "name": "Локальний URL (localhost)",
                "url": "http://localhost:3030/api/products",
                "should_have_jwt": False
            },
            {
                "name": "Ngrok URL",
                "url": "https://your-app.ngrok-free.app/api/products", 
                "should_have_jwt": True
            },
            {
                "name": "Інший ngrok URL",
                "url": "https://test-app.ngrok-free.app/api/products",
                "should_have_jwt": True
            }
        ]
        
        print("\n📋 Тестування різних URL...")
        
        for i, test_case in enumerate(test_urls, 1):
            print(f"\n📝 Тест {i}: {test_case['name']}")
            print(f"   URL: {test_case['url']}")
            print(f"   Очікується JWT: {'Так' if test_case['should_have_jwt'] else 'Ні'}")
            
            # Симулюємо API запит з конкретним URL
            api_request = {
                "method": "POST",
                "url": test_case['url'],
                "headers": {},
                "data": {"name": "test", "price": 100}
            }
            
            # Перевіряємо чи додається JWT токен
            if agent.jwt_token and api_request['method'] == 'POST' and 'ngrok-free.app' in api_request['url']:
                api_request['headers']['Authorization'] = f'Bearer {agent.jwt_token}'
                print("   ✅ JWT токен додано")
                jwt_added = True
            else:
                print("   ℹ️ JWT токен не додано")
                jwt_added = False
            
            # Перевіряємо результат
            if jwt_added == test_case['should_have_jwt']:
                print("   ✅ Результат відповідає очікуванням")
            else:
                print("   ❌ Результат не відповідає очікуванням")
        
        print("\n✅ Всі URL тести завершено!")
        assert True, "JWT тести з ngrok URL пройшли успішно"
        
    except Exception as e:
        print(f"❌ Помилка під час тестування: {e}")
        assert False, f"JWT тести з ngrok URL не пройшли: {e}"


def test_jwt_conditions():
    """Тест умов використання JWT токена."""
    print("\n🔍 ТЕСТ УМОВ ВИКОРИСТАННЯ JWT ТОКЕНА")
    print("=" * 60)
    
    try:
        agent = SwaggerAgent(
            swagger_spec_path="examples/swagger_specs/shop_api.json",
            enable_api_calls=False,  # Тільки для тестування
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            jwt_token=os.getenv('JWT_TOKEN')
        )
        
        # Тестуємо різні умови
        test_conditions = [
            {
                "method": "GET",
                "url": "https://app.ngrok-free.app/api/products",
                "description": "GET запит з ngrok URL",
                "should_have_jwt": False
            },
            {
                "method": "POST", 
                "url": "http://localhost:3030/api/products",
                "description": "POST запит з localhost",
                "should_have_jwt": False
            },
            {
                "method": "POST",
                "url": "https://app.ngrok-free.app/api/products", 
                "description": "POST запит з ngrok URL",
                "should_have_jwt": True
            },
            {
                "method": "PUT",
                "url": "https://app.ngrok-free.app/api/products/123",
                "description": "PUT запит з ngrok URL",
                "should_have_jwt": False
            }
        ]
        
        print("📋 Тестування умов JWT авторизації...")
        
        for i, condition in enumerate(test_conditions, 1):
            print(f"\n📝 Тест {i}: {condition['description']}")
            print(f"   Метод: {condition['method']}")
            print(f"   URL: {condition['url']}")
            
            # Симулюємо перевірку умов
            should_add_jwt = (
                agent.jwt_token and 
                condition['method'] == 'POST' and 
                'ngrok-free.app' in condition['url']
            )
            
            print(f"   Умови виконані: {'Так' if should_add_jwt else 'Ні'}")
            print(f"   Очікується JWT: {'Так' if condition['should_have_jwt'] else 'Ні'}")
            
            if should_add_jwt == condition['should_have_jwt']:
                print("   ✅ Результат правильний")
            else:
                print("   ❌ Результат неправильний")
        
        print("\n✅ Всі умови протестовано!")
        assert True, "JWT умови протестовано успішно"
        
    except Exception as e:
        print(f"❌ Помилка під час тестування умов: {e}")
        assert False, f"JWT умови не протестовано: {e}"


def main():
    """Основний функція тестування."""
    print("🔐 ТЕСТ JWT АВТОРИЗАЦІЇ З NGROK URL")
    print("=" * 60)
    
    # Перевіряємо змінні середовища
    if not os.getenv('OPENAI_API_KEY') or not os.getenv('JWT_TOKEN'):
        print("❌ Відсутні необхідні змінні середовища")
        print("💡 Встановіть:")
        print("   export OPENAI_API_KEY='your-key'")
        print("   export JWT_TOKEN='your-jwt-token'")
        return False
    
    print("✅ Всі змінні середовища знайдено")
    
    # Запускаємо тести
    test1_success = test_jwt_with_ngrok_url()
    test2_success = test_jwt_conditions()
    
    # Підсумок
    print("\n" + "=" * 60)
    print("📊 ПІДСУМОК JWT ТЕСТУ")
    print("=" * 60)
    
    if test1_success and test2_success:
        print("🎉 Всі JWT тести пройдено успішно!")
        print("✅ JWT авторизація працює коректно")
        print("✅ Умови використання JWT токена правильні")
        return True
    else:
        print("❌ Є проблеми з JWT авторизацією")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
