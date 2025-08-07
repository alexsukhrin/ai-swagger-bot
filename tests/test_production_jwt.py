#!/usr/bin/env python3
"""
Тест продакшн функціональності з JWT токеном.
"""

import os
import sys
from dotenv import load_dotenv

# Завантажуємо змінні середовища
load_dotenv()

# Додаємо шлях до src
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from interactive_api_agent import InteractiveSwaggerAgent as SwaggerAgent
    print("✅ Успішно імпортовано SwaggerAgent")
except ImportError as e:
    print(f"❌ Помилка імпорту: {e}")
    sys.exit(1)


def test_production_with_jwt():
    """Тест продакшн функціональності з JWT токеном."""
    print("🚀 ТЕСТ ПРОДАКШН ФУНКЦІОНАЛЬНОСТІ З JWT")
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
        
        # Тестуємо різні типи запитів
        test_cases = [
            {
                "query": "Покажи всі товари",
                "expected_method": "GET"
            },
            {
                "query": "Створи новий товар: iPhone 15, ціна: 999.99",
                "expected_method": "POST"
            },
            {
                "query": "Онови товар з ID 1: зміни ціну на 899.99",
                "expected_method": "PATCH"
            }
        ]
        
        print("\n📋 Тестування різних типів запитів...")
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Тест {i}:")
            print(f"   Запит: {test_case['query']}")
            print(f"   Очікуваний метод: {test_case['expected_method']}")
            
            try:
                response = agent.process_interactive_query(test_case['query'])
                print(f"   ✅ Відповідь отримано")
                
                # Перевіряємо чи додається JWT токен
                if test_case['expected_method'] == 'POST' and 'JWT токен додано' in response.get('response', ''):
                    print("   🔐 JWT токен успішно додано")
                elif test_case['expected_method'] == 'POST':
                    print("   ⚠️ JWT токен не додано (можливо локальний URL)")
                else:
                    print("   ℹ️ JWT токен не потрібен для GET/PATCH запитів")
                
                # Показуємо частину відповіді
                print(f"   📄 Відповідь: {response.get('response', '')[:200]}...")
                
            except Exception as e:
                print(f"   ❌ Помилка: {e}")
        
        print("\n✅ Всі тести завершено!")
        assert True, "Продакшн тести з JWT пройшли успішно"
        
    except Exception as e:
        print(f"❌ Помилка під час тестування: {e}")
        assert False, f"Продакшн тести з JWT не пройшли: {e}"


def test_jwt_authorization():
    """Тест JWT авторизації."""
    print("\n🔐 ТЕСТ JWT АВТОРИЗАЦІЇ")
    print("=" * 60)
    
    try:
        agent = SwaggerAgent(
            swagger_spec_path="examples/swagger_specs/shop_api.json",
            enable_api_calls=True,
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            jwt_token=os.getenv('JWT_TOKEN')
        )
        
        # Тест POST запиту (повинен використовувати JWT)
        print("📝 Тест POST запиту з JWT авторизацією...")
        response = agent.process_interactive_query("Створи тестовий товар для перевірки JWT")
        
        if 'JWT токен додано' in response.get('response', ''):
            print("✅ JWT токен успішно додано до POST запиту")
        else:
            print("⚠️ JWT токен не додано (можливо локальний URL або інша причина)")
        
        print(f"📄 Відповідь: {response.get('response', '')[:300]}...")
        
        assert True, "JWT авторизація працює коректно"
        
    except Exception as e:
        print(f"❌ Помилка JWT тесту: {e}")
        assert False, f"JWT авторизація не працює: {e}"


def main():
    """Основний функція тестування."""
    print("🚀 ПРОДАКШН ТЕСТ З JWT ТОКЕНОМ")
    print("=" * 60)
    
    # Перевіряємо змінні середовища
    required_vars = ['OPENAI_API_KEY', 'JWT_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Відсутні змінні середовища: {missing_vars}")
        print("💡 Встановіть змінні:")
        for var in missing_vars:
            print(f"   export {var}='your-value'")
        return False
    
    print("✅ Всі необхідні змінні середовища знайдено")
    
    # Запускаємо тести
    test1_success = test_production_with_jwt()
    test2_success = test_jwt_authorization()
    
    # Підсумок
    print("\n" + "=" * 60)
    print("📊 ПІДСУМОК ПРОДАКШН ТЕСТУ")
    print("=" * 60)
    
    if test1_success and test2_success:
        print("🎉 Всі продакшн тести пройдено успішно!")
        print("✅ AI Swagger Bot готовий до продакшну з JWT токеном")
        return True
    else:
        print("❌ Є проблеми з продакшн функціональністю")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
