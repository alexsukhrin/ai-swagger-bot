#!/usr/bin/env python3
"""
Тестовий файл для демонстрації роботи промптів обробки помилок Swagger специфікації
"""

import json
import sys
import os

# Додаємо src до шляху для імпорту
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from swagger_error_handler import SwaggerErrorHandler

def test_swagger_mismatch_detection():
    """Тест виявлення невідповідності Swagger специфікації."""
    print("🔍 Тест виявлення невідповідності Swagger специфікації")
    print("=" * 60)
    
    user_query = "Покажи всі категорії"
    
    swagger_endpoints = [
        {
            "url": "https://db62d2b2c3a5.ngrok-free.app/api/category/{id}",
            "method": "GET",
            "description": "Get a category by ID (Public)"
        }
    ]
    
    api_error = {
        "message": "invalid input syntax for type uuid: \"{id}\"",
        "error": "Bad Request",
        "statusCode": 400
    }
    
    # Генеруємо промпт для виявлення невідповідності
    detection_prompt = SwaggerErrorHandler.get_swagger_mismatch_detection_prompt(
        user_query, swagger_endpoints, api_error
    )
    
    print("📝 Промпт для виявлення невідповідності:")
    print(detection_prompt)
    print()

def test_endpoint_correction():
    """Тест виправлення неправильного endpoint."""
    print("🔧 Тест виправлення неправильного endpoint")
    print("=" * 60)
    
    user_query = "Покажи всі категорії"
    
    incorrect_endpoint = {
        "url": "https://db62d2b2c3a5.ngrok-free.app/api/category/{id}",
        "method": "GET",
        "description": "Get a category by ID (Public)"
    }
    
    api_error = {
        "message": "invalid input syntax for type uuid: \"{id}\"",
        "error": "Bad Request",
        "statusCode": 400
    }
    
    # Генеруємо промпт для виправлення endpoint
    correction_prompt = SwaggerErrorHandler.get_endpoint_correction_prompt(
        user_query, incorrect_endpoint, api_error
    )
    
    print("📝 Промпт для виправлення endpoint:")
    print(correction_prompt)
    print()

def test_endpoint_discovery():
    """Тест пошуку правильного endpoint."""
    print("🔍 Тест пошуку правильного endpoint")
    print("=" * 60)
    
    user_query = "Покажи всі категорії"
    
    available_endpoints = [
        {
            "url": "https://db62d2b2c3a5.ngrok-free.app/api/category/{id}",
            "method": "GET",
            "description": "Get a category by ID (Public)"
        },
        {
            "url": "https://db62d2b2c3a5.ngrok-free.app/api/categories",
            "method": "GET",
            "description": "Get all categories (Public)"
        },
        {
            "url": "https://db62d2b2c3a5.ngrok-free.app/api/category",
            "method": "POST",
            "description": "Create a new category (Public)"
        }
    ]
    
    # Генеруємо промпт для пошуку endpoint
    discovery_prompt = SwaggerErrorHandler.get_endpoint_discovery_prompt(
        user_query, available_endpoints
    )
    
    print("📝 Промпт для пошуку endpoint:")
    print(discovery_prompt)
    print()

def test_user_friendly_error_messages():
    """Тест дружелюбних повідомлень про помилки."""
    print("💬 Тест дружелюбних повідомлень про помилки")
    print("=" * 60)
    
    user_query = "Покажи всі категорії"
    
    # Тестуємо різні типи помилок
    error_types = [
        "swagger_mismatch",
        "invalid_parameter", 
        "missing_endpoint",
        "wrong_method"
    ]
    
    for error_type in error_types:
        print(f"📋 Тип помилки: {error_type}")
        
        swagger_issue = "Swagger специфікація містить endpoint з параметром {id} замість endpoint для отримання всіх категорій"
        suggestion = "Використовуємо endpoint без параметрів для отримання всіх категорій"
        
        error_message = SwaggerErrorHandler.get_user_friendly_error_message(
            error_type, user_query, swagger_issue, suggestion
        )
        
        print(error_message)
        print("-" * 40)

def test_common_endpoint_patterns():
    """Тест загальних патернів endpoints."""
    print("📋 Тест загальних патернів endpoints")
    print("=" * 60)
    
    patterns = SwaggerErrorHandler.get_common_endpoint_patterns()
    
    for operation, pattern_info in patterns.items():
        print(f"🔗 {operation.upper()}:")
        print(f"   Патерн: {pattern_info['pattern']}")
        print(f"   Приклад: {pattern_info['example']}")
        print(f"   Опис: {pattern_info['description']}")
        print(f"   Типова проблема: {pattern_info['swagger_issue']}")
        print()

def simulate_swagger_mismatch_scenario():
    """Симуляція сценарію з невідповідністю Swagger специфікації."""
    print("🎭 Симуляція сценарію з невідповідністю Swagger специфікації")
    print("=" * 60)
    
    # Сценарій: користувач хоче побачити всі категорії
    user_query = "Покажи всі категорії"
    
    # Swagger специфікація містить тільки endpoint з параметром
    swagger_endpoints = [
        {
            "url": "https://api.example.com/api/category/{id}",
            "method": "GET",
            "description": "Get a category by ID"
        }
    ]
    
    # API повертає помилку
    api_error = {
        "message": "invalid input syntax for type uuid: \"{id}\"",
        "error": "Bad Request",
        "statusCode": 400
    }
    
    print("🔍 Аналіз ситуації:")
    print(f"   Запит користувача: {user_query}")
    print(f"   Endpoint в Swagger: {swagger_endpoints[0]['url']}")
    print(f"   Помилка API: {api_error['message']}")
    print()
    
    # Генеруємо промпт для виявлення проблеми
    detection_prompt = SwaggerErrorHandler.get_swagger_mismatch_detection_prompt(
        user_query, swagger_endpoints, api_error
    )
    
    print("📝 Промпт для виявлення проблеми:")
    print(detection_prompt)
    print()
    
    # Генеруємо дружелюбне повідомлення
    error_message = SwaggerErrorHandler.get_user_friendly_error_message(
        "swagger_mismatch",
        user_query,
        "Swagger специфікація містить endpoint з параметром {id} замість endpoint для отримання всіх категорій",
        "Використовуємо endpoint без параметрів для отримання всіх категорій"
    )
    
    print("💬 Повідомлення для користувача:")
    print(error_message)

def main():
    """Головна функція для запуску всіх тестів."""
    print("🧪 Тестування промптів обробки помилок Swagger специфікації")
    print("=" * 80)
    print()
    
    # Запускаємо всі тести
    test_swagger_mismatch_detection()
    test_endpoint_correction()
    test_endpoint_discovery()
    test_user_friendly_error_messages()
    test_common_endpoint_patterns()
    simulate_swagger_mismatch_scenario()
    
    print("✅ Всі тести завершено!")
    print("🎯 Промпти готові для інтеграції в InteractiveSwaggerAgent")

if __name__ == "__main__":
    main()
