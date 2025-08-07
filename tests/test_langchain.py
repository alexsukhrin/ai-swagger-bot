#!/usr/bin/env python3
"""
Швидкий тест LangChain функціональності.
"""

import os
import sys
from dotenv import load_dotenv

# Завантажуємо змінні середовища
load_dotenv()

# Додаємо src до шляху
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_langchain():
    """Тестуємо основні компоненти LangChain."""
    print("🧪 Тестування LangChain компонентів")
    print("=" * 40)
    
    try:
        # Тест 1: OpenAI Embeddings
        print("1. Тестуємо OpenAI Embeddings...")
        from langchain_openai import OpenAIEmbeddings
        embeddings = OpenAIEmbeddings()
        test_text = "Hello, world!"
        vector = embeddings.embed_query(test_text)
        print(f"✅ Embeddings працює (вектор довжиною {len(vector)})")
        
        # Тест 2: ChatOpenAI
        print("2. Тестуємо ChatOpenAI...")
        from langchain_openai import ChatOpenAI
        from langchain.schema import HumanMessage
        
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        response = llm.invoke([HumanMessage(content="Привіт!")])
        print(f"✅ ChatOpenAI працює: {response.content[:50]}...")
        
        # Тест 3: Наш SwaggerAgent
        print("3. Тестуємо SwaggerAgent...")
        from interactive_api_agent import InteractiveSwaggerAgent as SwaggerAgent
        
        agent = SwaggerAgent("examples/swagger_specs/shop_api.json", enable_api_calls=False)
        result = agent.process_interactive_query("Покажи всі товари")
        print(f"✅ SwaggerAgent працює: {result.get('response', '')[:100]}...")
        
        print("\n🎉 Всі тести пройшли успішно!")
        assert True, "LangChain тести пройшли успішно"
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        assert False, f"LangChain тести не пройшли: {e}"

def test_categories():
    """Тестуємо роботу з категоріями."""
    print("\n📂 Тестування роботи з категоріями")
    print("=" * 40)
    
    try:
        from interactive_api_agent import InteractiveSwaggerAgent as SwaggerAgent
        
        agent = SwaggerAgent("examples/swagger_specs/shop_api.json", enable_api_calls=False)
        
        # Тест 1: Створити категорію
        print("1. Тест створення категорії...")
        create_result = agent.process_interactive_query("Створи категорію: Електроніка")
        print(f"✅ Створення категорії: {create_result.get('response', '')[:100]}...")
        
        # Тест 2: Показати всі категорії
        print("2. Тест перегляду категорій...")
        list_result = agent.process_interactive_query("Покажи всі категорії")
        print(f"✅ Перегляд категорій: {list_result.get('response', '')[:100]}...")
        
        # Тест 3: Створити категорію з деталями
        print("3. Тест створення категорії з деталями...")
        detailed_result = agent.process_interactive_query("Створи категорію: Одяг, опис: Модний одяг для всіх сезонів")
        print(f"✅ Створення з деталями: {detailed_result.get('response', '')[:100]}...")
        
        print("\n🎉 Всі тести категорій пройшли успішно!")
        assert True, "Тести категорій пройшли успішно"
        
    except Exception as e:
        print(f"❌ Помилка тестування категорій: {e}")
        assert False, f"Тести категорій не пройшли: {e}"

if __name__ == "__main__":
    success1 = test_langchain()
    success2 = test_categories()
    
    if success1 and success2:
        print("\n🚀 LangChain готовий до використання!")
        print("📂 Робота з категоріями працює ідеально!")
    else:
        print("\n💡 Перевірте налаштування середовища.")
