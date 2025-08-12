#!/usr/bin/env python3
"""
Приклад використання AI Swagger Bot як серверлес сервіса
"""

import json
import os
import sys
from pathlib import Path

# Додаємо кореневу директорію проекту до Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def example_health_check():
    """Приклад health check запиту."""
    print("🔍 Приклад health check запиту:")
    
    # Створюємо тестовий event
    event = {
        "version": "2.0",
        "routeKey": "GET /health",
        "rawPath": "/health",
        "rawQueryString": "",
        "headers": {
            "accept": "application/json",
            "content-type": "application/json",
            "host": "api.example.com"
        },
        "requestContext": {
            "accountId": "123456789012",
            "apiId": "api-id",
            "domainName": "api.example.com",
            "http": {
                "method": "GET",
                "path": "/health",
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1"
            },
            "requestId": "request-id",
            "routeKey": "GET /health",
            "stage": "$default"
        },
        "isBase64Encoded": False,
        "body": ""
    }
    
    print(f"📤 Event: {json.dumps(event, indent=2)}")
    
    try:
        from lambda_handler import handler
        
        # Викликаємо Lambda handler
        response = handler(event, {})
        
        print(f"📥 Response: {json.dumps(response, indent=2)}")
        return response
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return None

def example_chat_request():
    """Приклад chat запиту."""
    print("\n💬 Приклад chat запиту:")
    
    chat_data = {
        "message": "Покажи мені всі доступні API endpoints",
        "user_id": "user-123"
    }
    
    event = {
        "version": "2.0",
        "routeKey": "POST /chat",
        "rawPath": "/chat",
        "rawQueryString": "",
        "headers": {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "host": "api.example.com"
        },
        "requestContext": {
            "accountId": "123456789012",
            "apiId": "api-id",
            "domainName": "api.example.com",
            "http": {
                "method": "POST",
                "path": "/chat",
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1"
            },
            "requestId": "request-id",
            "routeKey": "POST /chat",
            "stage": "$default"
        },
        "isBase64Encoded": False,
        "body": json.dumps(chat_data)
    }
    
    print(f"📤 Event: {json.dumps(event, indent=2)}")
    
    try:
        from lambda_handler import handler
        
        # Викликаємо Lambda handler
        response = handler(event, {})
        
        print(f"📥 Response: {json.dumps(response, indent=2)}")
        return response
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return None

def example_upload_swagger():
    """Приклад завантаження Swagger специфікації."""
    print("\n📄 Приклад завантаження Swagger специфікації:")
    
    # Тестова Swagger специфікація
    swagger_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "E-commerce API",
            "version": "1.0.0",
            "description": "API для e-commerce платформи"
        },
        "paths": {
            "/products": {
                "get": {
                    "summary": "Отримати список товарів",
                    "responses": {
                        "200": {
                            "description": "Успішно"
                        }
                    }
                },
                "post": {
                    "summary": "Створити новий товар",
                    "responses": {
                        "201": {
                            "description": "Товар створено"
                        }
                    }
                }
            },
            "/orders": {
                "get": {
                    "summary": "Отримати список замовлень",
                    "responses": {
                        "200": {
                            "description": "Успішно"
                        }
                    }
                }
            }
        }
    }
    
    # Симулюємо multipart form data
    import base64
    swagger_content = json.dumps(swagger_spec)
    encoded_content = base64.b64encode(swagger_content.encode()).decode()
    
    event = {
        "version": "2.0",
        "routeKey": "POST /upload-swagger",
        "rawPath": "/upload-swagger",
        "rawQueryString": "",
        "headers": {
            "accept": "application/json",
            "content-type": "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
            "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "host": "api.example.com"
        },
        "requestContext": {
            "accountId": "123456789012",
            "apiId": "api-id",
            "domainName": "api.example.com",
            "http": {
                "method": "POST",
                "path": "/upload-swagger",
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1"
            },
            "requestId": "request-id",
            "routeKey": "POST /upload-swagger",
            "stage": "$default"
        },
        "isBase64Encoded": True,
        "body": encoded_content
    }
    
    print(f"📤 Event: {json.dumps(event, indent=2)}")
    
    try:
        from lambda_handler import handler
        
        # Викликаємо Lambda handler
        response = handler(event, {})
        
        print(f"📥 Response: {json.dumps(response, indent=2)}")
        return response
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return None

def example_error_handling():
    """Приклад обробки помилок."""
    print("\n⚠️ Приклад обробки помилок:")
    
    # Event з неправильним шляхом
    event = {
        "version": "2.0",
        "routeKey": "GET /invalid-endpoint",
        "rawPath": "/invalid-endpoint",
        "rawQueryString": "",
        "headers": {
            "accept": "application/json",
            "content-type": "application/json",
            "host": "api.example.com"
        },
        "requestContext": {
            "accountId": "123456789012",
            "apiId": "api-id",
            "domainName": "api.example.com",
            "http": {
                "method": "GET",
                "path": "/invalid-endpoint",
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1"
            },
            "requestId": "request-id",
            "routeKey": "GET /invalid-endpoint",
            "stage": "$default"
        },
        "isBase64Encoded": False,
        "body": ""
    }
    
    print(f"📤 Event: {json.dumps(event, indent=2)}")
    
    try:
        from lambda_handler import handler
        
        # Викликаємо Lambda handler
        response = handler(event, {})
        
        print(f"📥 Response: {json.dumps(response, indent=2)}")
        return response
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return None

def run_all_examples():
    """Запускає всі приклади."""
    print("🚀 Запуск прикладів серверлес функціональності...")
    print("=" * 60)
    
    examples = [
        ("Health Check", example_health_check),
        ("Chat Request", example_chat_request),
        ("Upload Swagger", example_upload_swagger),
        ("Error Handling", example_error_handling)
    ]
    
    results = []
    
    for name, func in examples:
        print(f"\n{'='*20} {name} {'='*20}")
        try:
            result = func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Помилка в прикладі {name}: {e}")
            results.append((name, None))
    
    # Підсумок
    print("\n" + "=" * 60)
    print("📊 Підсумок прикладів:")
    
    success_count = 0
    total_count = len(results)
    
    for example_name, result in results:
        if result and result.get('statusCode') in [200, 201, 404]:
            print(f"✅ {example_name}: УСПІШНО")
            success_count += 1
        else:
            print(f"❌ {example_name}: НЕУСПІШНО")
    
    print(f"\n🎯 Результат: {success_count}/{total_count} прикладів виконано успішно")
    
    return results

def show_usage_instructions():
    """Показує інструкції по використанню."""
    print("📚 Інструкції по використанню:")
    print("=" * 50)
    
    print("\n1️⃣ Локальне тестування:")
    print("   python test_lambda.py --all")
    print("   python test_lambda.py --health")
    print("   python test_lambda.py --chat")
    
    print("\n2️⃣ Розгортання на AWS:")
    print("   make -f Makefile.lambda deploy")
    print("   make -f Makefile.lambda deploy-prod")
    
    print("\n3️⃣ Terraform розгортання:")
    print("   cd terraform")
    print("   make quick-deploy ENVIRONMENT=dev")
    
    print("\n4️⃣ Docker тестування:")
    print("   make -f Makefile.lambda test-docker")
    print("   docker-compose -f docker-compose.lambda.yml up")
    
    print("\n5️⃣ CI/CD:")
    print("   GitHub Actions: .github/workflows/deploy-lambda.yml")
    print("   GitLab CI: .gitlab-ci.yml")
    
    print("\n📖 Детальна документація:")
    print("   README_SERVERLESS.md")
    print("   terraform/README.md")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Приклади серверлес функціональності AI Swagger Bot")
    parser.add_argument("--all", action="store_true", help="Запустити всі приклади")
    parser.add_argument("--health", action="store_true", help="Приклад health check")
    parser.add_argument("--chat", action="store_true", help="Приклад chat запиту")
    parser.add_argument("--upload", action="store_true", help="Приклад завантаження Swagger")
    parser.add_argument("--error", action="store_true", help="Приклад обробки помилок")
    parser.add_argument("--usage", action="store_true", help="Показати інструкції")
    
    args = parser.parse_args()
    
    if args.usage:
        show_usage_instructions()
    elif args.health:
        example_health_check()
    elif args.chat:
        example_chat_request()
    elif args.upload:
        example_upload_swagger()
    elif args.error:
        example_error_handling()
    elif args.all:
        run_all_examples()
    else:
        print("🔍 Виберіть опцію:")
        print("  --all          - Запустити всі приклади")
        print("  --health       - Приклад health check")
        print("  --chat         - Приклад chat запиту")
        print("  --upload       - Приклад завантаження Swagger")
        print("  --error        - Приклад обробки помилок")
        print("  --usage        - Показати інструкції")
        print("\n💡 Приклад: python examples/serverless_example.py --all") 