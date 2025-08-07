"""
Промпти для обробки помилок коли Swagger специфікація не відповідає реальному API
"""

import json
from typing import Dict, Any, List, Optional

class SwaggerErrorHandler:
    """Клас для обробки помилок коли Swagger специфікація не відповідає реальному API."""
    
    @staticmethod
    def get_swagger_mismatch_detection_prompt(user_query: str, swagger_endpoints: List[Dict[str, Any]], 
                                            api_error: Dict[str, Any] = None) -> str:
        """Промпт для виявлення невідповідності між Swagger специфікацією та реальним API."""
        return f"""
Ти - експерт з API. Вияви та оброби невідповідність між Swagger специфікацією та реальним API.

ЗАПИТ КОРИСТУВАЧА: {user_query}

ENDPOINTS З SWAGGER СПЕЦИФІКАЦІЇ:
{json.dumps(swagger_endpoints, ensure_ascii=False, indent=2)}

ПОМИЛКА API (якщо є):
{json.dumps(api_error, ensure_ascii=False, indent=2) if api_error else "Немає помилки"}

ТИПОВІ ПРОБЛЕМИ SWAGGER СПЕЦИФІКАЦІЇ:
1. Endpoint має параметр {{id}} замість бути без параметрів
2. Неправильна назва ресурсу (category замість categories)
3. Відсутній endpoint для отримання всіх записів
4. Неправильний HTTP метод
5. Endpoint очікує UUID але отримує строку

АНАЛІЗ ЗАПИТУ КОРИСТУВАЧА:
- "Покажи всі категорії" = GET без параметрів
- "Покажи категорію з ID" = GET з параметром
- "Створи категорію" = POST
- "Онови категорію" = PUT/PATCH
- "Видали категорію" = DELETE

ЗАВДАННЯ:
1. Проаналізуй що хоче користувач
2. Знайди відповідний endpoint в Swagger
3. Вияви невідповідність між Swagger та реальним API
4. Запропонуй правильний endpoint
5. Поясни проблему користувачу

ПРАВИЛА ВИПРАВЛЕННЯ:
- Для "всі записи" використовуй GET /api/{{resource}} (без параметрів)
- Для "конкретний запис" використовуй GET /api/{{resource}}/{{id}}
- Для "створення" використовуй POST /api/{{resource}}
- Для "оновлення" використовуй PUT /api/{{resource}}/{{id}}
- Для "видалення" використовуй DELETE /api/{{resource}}/{{id}}

ВІДПОВІДЬ У ФОРМАТІ:
{{
    "user_intent": "що хоче користувач",
    "swagger_issue": "проблема в Swagger специфікації",
    "correct_endpoint": "правильний endpoint",
    "alternative_endpoints": ["альтернативні endpoints"],
    "explanation": "пояснення проблеми",
    "user_message": "повідомлення для користувача",
    "suggestion": "пропозиція для виправлення"
}}
"""

    @staticmethod
    def get_endpoint_correction_prompt(user_query: str, incorrect_endpoint: Dict[str, Any], 
                                     api_error: Dict[str, Any]) -> str:
        """Промпт для виправлення неправильного endpoint на основі помилки API."""
        return f"""
Ти - експерт з API. Виправ неправильний endpoint на основі помилки сервера.

ЗАПИТ КОРИСТУВАЧА: {user_query}

НЕПРАВИЛЬНИЙ ENDPOINT:
{json.dumps(incorrect_endpoint, ensure_ascii=False, indent=2)}

ПОМИЛКА СЕРВЕРА:
{json.dumps(api_error, ensure_ascii=False, indent=2)}

АНАЛІЗ ПОМИЛКИ:
- Помилка: "invalid input syntax for type uuid: \"{{id}}\""
- Це означає що endpoint очікує UUID параметр, але отримує "{{id}}"
- Можливо це endpoint для отримання конкретної категорії, а не всіх

ТИПОВІ ПОМИЛКИ ТА ЇХ ВИПРАВЛЕННЯ:
1. "invalid input syntax for type uuid" → endpoint потребує реальний ID, не placeholder
2. "404 Not Found" → endpoint не існує або неправильний URL
3. "400 Bad Request" → неправильні параметри або дані
4. "405 Method Not Allowed" → неправильний HTTP метод

ЗАВДАННЯ:
1. Визначи правильний endpoint для запиту
2. Якщо потрібно отримати всі категорії - знайди endpoint без параметрів
3. Якщо потрібно отримати одну категорію - виправ параметр
4. Поясни користувачу що відбувається

ВІДПОВІДЬ У ФОРМАТІ:
{{
    "correct_endpoint": "правильний endpoint",
    "explanation": "пояснення проблеми",
    "user_message": "повідомлення для користувача",
    "retry_suggestion": "пропозиція для повторної спроби"
}}
"""

    @staticmethod
    def get_swagger_retry_prompt(user_query: str, original_endpoint: Dict[str, Any], 
                                corrected_endpoint: Dict[str, Any]) -> str:
        """Промпт для повторної спроби з виправленим endpoint."""
        return f"""
Ти - експерт з API. Виконай повторну спробу з виправленим endpoint.

ЗАПИТ КОРИСТУВАЧА: {user_query}

ОРИГІНАЛЬНИЙ ENDPOINT (неправильний):
{json.dumps(original_endpoint, ensure_ascii=False, indent=2)}

ВИПРАВЛЕНИЙ ENDPOINT:
{json.dumps(corrected_endpoint, ensure_ascii=False, indent=2)}

ЗАВДАННЯ:
1. Виконай запит з виправленим endpoint
2. Якщо потрібно - зміни HTTP метод
3. Якщо потрібно - додай або видали параметри
4. Поверни результат користувачу

ПРАВИЛА ВИПРАВЛЕННЯ:
- Для "всі категорії" використовуй GET без параметрів
- Для "конкретна категорія" використовуй GET з ID
- Для "створення" використовуй POST
- Для "оновлення" використовуй PUT/PATCH
- Для "видалення" використовуй DELETE

ВІДПОВІДЬ У ФОРМАТІ:
{{
    "corrected_request": "виправлений запит",
    "expected_response": "очікувана відповідь",
    "user_message": "повідомлення для користувача"
}}
"""

    @staticmethod
    def get_endpoint_discovery_prompt(user_query: str, available_endpoints: List[Dict[str, Any]]) -> str:
        """Промпт для пошуку правильного endpoint коли Swagger специфікація неправильна."""
        return f"""
Ти - експерт з API. Знайди правильний endpoint коли Swagger специфікація не відповідає реальному API.

ЗАПИТ КОРИСТУВАЧА: {user_query}

ДОСТУПНІ ENDPOINTS:
{json.dumps(available_endpoints, ensure_ascii=False, indent=2)}

ЗАВДАННЯ:
1. Проаналізуй запит користувача
2. Визначи тип операції (GET, POST, PUT, DELETE)
3. Визначи ресурс (категорії, товари, користувачі, тощо)
4. Знайди найбільш підходящий endpoint
5. Якщо точного endpoint немає - запропонуй альтернативу

ПРАВИЛА ПОШУКУ:
- "всі категорії" → шукай GET без параметрів
- "категорія з ID" → шукай GET з параметром
- "створи категорію" → шукай POST
- "онови категорію" → шукай PUT/PATCH
- "видали категорію" → шукай DELETE

АЛЬТЕРНАТИВНІ НАЗВИ РЕСУРСІВ:
- category/categories
- product/products
- user/users
- order/orders
- item/items

ВІДПОВІДЬ У ФОРМАТІ:
{{
    "user_intent": "що хоче користувач",
    "operation_type": "GET|POST|PUT|DELETE",
    "resource": "назва ресурсу",
    "best_match": "найкращий endpoint",
    "alternatives": ["альтернативні endpoints"],
    "confidence": "відсоток впевненості",
    "reasoning": "пояснення вибору"
}}
"""

    @staticmethod
    def get_user_friendly_error_message(error_type: str, user_query: str, 
                                      swagger_issue: str, suggestion: str) -> str:
        """Генерує дружелюбне повідомлення про помилку для користувача."""
        
        error_messages = {
            "swagger_mismatch": f"""
⚠️ **Проблема з Swagger специфікацією**

🔍 **Ваш запит:** {user_query}

❌ **Проблема:** {swagger_issue}

💡 **Рішення:** {suggestion}

🔄 **Що робимо:** Виправляємо endpoint та повторюємо запит автоматично.
""",
            
            "invalid_parameter": f"""
⚠️ **Неправильний параметр**

🔍 **Ваш запит:** {user_query}

❌ **Проблема:** {swagger_issue}

💡 **Рішення:** {suggestion}

🔄 **Що робимо:** Використовуємо правильний endpoint без параметрів.
""",
            
            "missing_endpoint": f"""
⚠️ **Відсутній endpoint**

🔍 **Ваш запит:** {user_query}

❌ **Проблема:** {swagger_issue}

💡 **Рішення:** {suggestion}

🔄 **Що робимо:** Шукаємо альтернативний endpoint.
""",
            
            "wrong_method": f"""
⚠️ **Неправильний HTTP метод**

🔍 **Ваш запит:** {user_query}

❌ **Проблема:** {swagger_issue}

💡 **Рішення:** {suggestion}

🔄 **Що робимо:** Використовуємо правильний HTTP метод.
"""
        }
        
        return error_messages.get(error_type, f"""
⚠️ **Помилка API**

🔍 **Ваш запит:** {user_query}

❌ **Проблема:** {swagger_issue}

💡 **Рішення:** {suggestion}

🔄 **Що робимо:** Виправляємо проблему та повторюємо запит.
""")

    @staticmethod
    def get_common_endpoint_patterns() -> Dict[str, Dict[str, str]]:
        """Повертає загальні патерни endpoints для різних операцій."""
        return {
            "get_all": {
                "pattern": "GET /api/{resource}",
                "example": "GET /api/categories",
                "description": "Отримання всіх записів",
                "swagger_issue": "Endpoint має параметр {id} замість бути без параметрів"
            },
            "get_by_id": {
                "pattern": "GET /api/{resource}/{id}",
                "example": "GET /api/categories/123",
                "description": "Отримання запису за ID",
                "swagger_issue": "Endpoint очікує реальний ID, не placeholder"
            },
            "create": {
                "pattern": "POST /api/{resource}",
                "example": "POST /api/categories",
                "description": "Створення нового запису",
                "swagger_issue": "Неправильний HTTP метод або URL"
            },
            "update": {
                "pattern": "PUT /api/{resource}/{id}",
                "example": "PUT /api/categories/123",
                "description": "Оновлення запису",
                "swagger_issue": "Неправильний HTTP метод або відсутній ID"
            },
            "delete": {
                "pattern": "DELETE /api/{resource}/{id}",
                "example": "DELETE /api/categories/123",
                "description": "Видалення запису",
                "swagger_issue": "Неправильний HTTP метод або відсутній ID"
            }
        }

# Приклади використання
if __name__ == "__main__":
    # Приклад проблемної ситуації
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
    
    print("🔍 Промпт для виявлення невідповідності Swagger:")
    print(detection_prompt)
    print()
    
    # Генеруємо дружелюбне повідомлення про помилку
    error_message = SwaggerErrorHandler.get_user_friendly_error_message(
        "swagger_mismatch",
        user_query,
        "Swagger специфікація містить endpoint з параметром {id} замість endpoint для отримання всіх категорій",
        "Використовуємо endpoint без параметрів для отримання всіх категорій"
    )
    
    print("💬 Дружелюбне повідомлення про помилку:")
    print(error_message)
    print()
    
    print("✅ Промпти для обробки помилок Swagger готові!")
