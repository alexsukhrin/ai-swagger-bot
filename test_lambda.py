#!/usr/bin/env python3
"""
Тестування Lambda функції AI Swagger Bot локально
"""

import json
import os
import sys
from pathlib import Path

# Додаємо кореневу директорію проекту до Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def create_test_event(path="/health", method="GET", body=None, headers=None):
    """Створює тестовий event для Lambda функції."""
    
    if headers is None:
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "host": "localhost:3000",
            "user-agent": "test-lambda/1.0"
        }
    
    event = {
        "version": "2.0",
        "routeKey": f"{method} {path}",
        "rawPath": path,
        "rawQueryString": "",
        "headers": headers,
        "requestContext": {
            "accountId": "123456789012",
            "apiId": "test-api-id",
            "domainName": "localhost:3000",
            "domainPrefix": "localhost",
            "http": {
                "method": method,
                "path": path,
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1",
                "userAgent": "test-lambda/1.0"
            },
            "requestId": "test-request-id",
            "routeKey": f"{method} {path}",
            "stage": "$default",
            "time": "12/Mar/2024:19:03:58 +0000",
            "timeEpoch": 1710267838000
        },
        "isBase64Encoded": False,
        "body": body or ""
    }
    
    return event

def test_health_endpoint():
    """Тестує health endpoint."""
    print("🧪 Тестування health endpoint...")
    
    try:
        from lambda_handler import handler
        
        event = create_test_event("/health", "GET")
        response = handler(event, {})
        
        print(f"✅ Status Code: {response.get('statusCode', 'N/A')}")
        print(f"📝 Response: {response.get('body', 'N/A')}")
        
        return response
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return None

def test_chat_endpoint():
    """Тестує chat endpoint."""
    print("\n🧪 Тестування chat endpoint...")
    
    try:
        from lambda_handler import handler
        
        chat_data = {
            "message": "Привіт! Як справи?",
            "user_id": "test-user-123"
        }
        
        event = create_test_event(
            "/chat", 
            "POST", 
            body=json.dumps(chat_data),
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": "Bearer test-token"
            }
        )
        
        response = handler(event, {})
        
        print(f"✅ Status Code: {response.get('statusCode', 'N/A')}")
        print(f"📝 Response: {response.get('body', 'N/A')}")
        
        return response
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return None

def test_upload_swagger_endpoint():
    """Тестує upload-swagger endpoint."""
    print("\n🧪 Тестування upload-swagger endpoint...")
    
    try:
        from lambda_handler import handler
        
        # Створюємо тестовий Swagger файл
        test_swagger = {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            },
            "paths": {
                "/test": {
                    "get": {
                        "summary": "Test endpoint",
                        "responses": {
                            "200": {
                                "description": "OK"
                            }
                        }
                    }
                }
            }
        }
        
        # Симулюємо multipart form data
        import base64
        swagger_content = json.dumps(test_swagger)
        encoded_content = base64.b64encode(swagger_content.encode()).decode()
        
        event = create_test_event(
            "/upload-swagger",
            "POST",
            body=encoded_content,
            headers={
                "accept": "application/json",
                "content-type": "multipart/form-data; boundary=test-boundary",
                "authorization": "Bearer test-token"
            }
        )
        
        response = handler(event, {})
        
        print(f"✅ Status Code: {response.get('statusCode', 'N/A')}")
        print(f"📝 Response: {response.get('body', 'N/A')}")
        
        return response
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return None

def test_custom_event(event_data):
    """Тестує з кастомним event."""
    print(f"\n🧪 Тестування з кастомним event: {event_data.get('routeKey', 'N/A')}")
    
    try:
        from lambda_handler import handler
        
        response = handler(event_data, {})
        
        print(f"✅ Status Code: {response.get('statusCode', 'N/A')}")
        print(f"📝 Response: {response.get('body', 'N/A')}")
        
        return response
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return None

def run_all_tests():
    """Запускає всі тести."""
    print("🚀 Запуск тестів Lambda функції...")
    print("=" * 50)
    
    results = []
    
    # Тест health endpoint
    health_result = test_health_endpoint()
    results.append(("Health Endpoint", health_result))
    
    # Тест chat endpoint
    chat_result = test_chat_endpoint()
    results.append(("Chat Endpoint", chat_result))
    
    # Тест upload-swagger endpoint
    upload_result = test_upload_swagger_endpoint()
    results.append(("Upload Swagger Endpoint", upload_result))
    
    # Підсумок
    print("\n" + "=" * 50)
    print("📊 Підсумок тестів:")
    
    success_count = 0
    total_count = len(results)
    
    for test_name, result in results:
        if result and result.get('statusCode') == 200:
            print(f"✅ {test_name}: УСПІШНО")
            success_count += 1
        else:
            print(f"❌ {test_name}: НЕУСПІШНО")
    
    print(f"\n🎯 Результат: {success_count}/{total_count} тестів пройшли успішно")
    
    if success_count == total_count:
        print("🎉 Всі тести пройшли успішно!")
    else:
        print("⚠️ Деякі тести не пройшли. Перевірте логи для деталей.")
    
    return results

def test_with_file(event_file):
    """Тестує з event файлу."""
    print(f"📁 Тестування з файлу: {event_file}")
    
    try:
        with open(event_file, 'r') as f:
            event_data = json.load(f)
        
        return test_custom_event(event_data)
        
    except FileNotFoundError:
        print(f"❌ Файл {event_file} не знайдено")
        return None
    except json.JSONDecodeError:
        print(f"❌ Помилка парсингу JSON в файлі {event_file}")
        return None

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Тестування Lambda функції AI Swagger Bot")
    parser.add_argument("--event-file", help="Файл з event для тестування")
    parser.add_argument("--all", action="store_true", help="Запустити всі тести")
    parser.add_argument("--health", action="store_true", help="Тестувати тільки health endpoint")
    parser.add_argument("--chat", action="store_true", help="Тестувати тільки chat endpoint")
    parser.add_argument("--upload", action="store_true", help="Тестувати тільки upload endpoint")
    
    args = parser.parse_args()
    
    if args.event_file:
        test_with_file(args.event_file)
    elif args.health:
        test_health_endpoint()
    elif args.chat:
        test_chat_endpoint()
    elif args.upload:
        test_upload_swagger_endpoint()
    elif args.all:
        run_all_tests()
    else:
        print("🔍 Виберіть опцію тестування:")
        print("  --all          - Запустити всі тести")
        print("  --health       - Тестувати health endpoint")
        print("  --chat         - Тестувати chat endpoint")
        print("  --upload       - Тестувати upload endpoint")
        print("  --event-file   - Тестувати з event файлу")
        print("\n💡 Приклад: python test_lambda.py --all") 