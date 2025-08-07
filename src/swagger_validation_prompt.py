"""
Промпт для валідації та виправлення Swagger специфікації
"""

import json
from typing import Any, Dict, List, Optional


class SwaggerValidationPrompt:
    """Клас для валідації та виправлення Swagger специфікації."""

    @staticmethod
    def get_swagger_validation_prompt(
        user_query: str, found_endpoints: List[Dict[str, Any]], api_response: Dict[str, Any] = None
    ) -> str:
        """Промпт для валідації Swagger специфікації."""
        return f"""
Ти - експерт з API та Swagger/OpenAPI специфікаціями. Проаналізуй ситуацію та виправ помилки.

ЗАПИТ КОРИСТУВАЧА: {user_query}

ЗНАЙДЕНІ ENDPOINTS:
{json.dumps(found_endpoints, ensure_ascii=False, indent=2)}

ВІДПОВІДЬ API (якщо є):
{json.dumps(api_response, ensure_ascii=False, indent=2) if api_response else "Немає відповіді"}

ПРОБЛЕМИ ЯКІ МОЖУ БУТИ:
1. Swagger специфікація не відповідає реальному API
2. Неправильні URL endpoints
3. Відсутні endpoints для певних операцій
4. Неправильні HTTP методи
5. Помилки в параметрах

ЗАВДАННЯ:
1. Проаналізуй запит користувача
2. Знайди відповідний endpoint
3. Якщо endpoint неправильний - запропонуй правильний
4. Якщо endpoint відсутній - запропонуй альтернативу
5. Поясни проблему користувачу

ВІДПОВІДЬ У ФОРМАТІ:
{{
    "analysis": "аналіз проблеми",
    "correct_endpoint": "правильний endpoint",
    "suggestion": "пропозиція для користувача",
    "swagger_issue": "проблема в Swagger специфікації",
    "user_message": "повідомлення для користувача"
}}
"""

    @staticmethod
    def get_endpoint_correction_prompt(
        user_query: str, incorrect_endpoint: Dict[str, Any], api_error: Dict[str, Any]
    ) -> str:
        """Промпт для виправлення неправильного endpoint."""
        return f"""
Ти - експерт з API. Виправ неправильний endpoint на основі помилки сервера.

ЗАПИТ КОРИСТУВАЧА: {user_query}

НЕПРАВИЛЬНИЙ ENDPOINT:
{json.dumps(incorrect_endpoint, ensure_ascii=False, indent=2)}

ПОМИЛКА СЕРВЕРА:
{json.dumps(api_error, ensure_ascii=False, indent=2)}

АНАЛІЗ ПОМИЛКИ:
- Помилка: "invalid input syntax for type uuid: "{id}""
- Це означає що endpoint очікує UUID параметр, але отримує "{id}"
- Можливо це endpoint для отримання конкретної категорії, а не всіх

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
    def get_swagger_mismatch_prompt(
        user_query: str, swagger_endpoints: List[Dict[str, Any]], api_error: Dict[str, Any] = None
    ) -> str:
        """Промпт для обробки ситуацій коли Swagger специфікація не відповідає реальному API."""
        return f"""
Ти - експерт з API. Оброби ситуацію коли Swagger специфікація не відповідає реальному API.

ЗАПИТ КОРИСТУВАЧА: {user_query}

ENDPOINTS З SWAGGER СПЕЦИФІКАЦІЇ:
{json.dumps(swagger_endpoints, ensure_ascii=False, indent=2)}

ПОМИЛКА API (якщо є):
{json.dumps(api_error, ensure_ascii=False, indent=2) if api_error else "Немає помилки"}

ТИПОВІ ПРОБЛЕМИ:
1. Endpoint має параметр {{id}} замість бути без параметрів
2. Неправильна назва ресурсу (category замість categories)
3. Відсутній endpoint для отримання всіх записів
4. Неправильний HTTP метод

АНАЛІЗ ЗАПИТУ:
- "Покажи всі категорії" = GET без параметрів
- "Покажи категорію з ID" = GET з параметром
- "Створи категорію" = POST
- "Онови категорію" = PUT/PATCH
- "Видали категорію" = DELETE

ЗАВДАННЯ:
1. Проаналізуй що хоче користувач
2. Знайди відповідний endpoint в Swagger
3. Якщо endpoint неправильний - запропонуй правильний
4. Якщо endpoint відсутній - створи альтернативу
5. Поясни проблему користувачу

ПРАВИЛА ВИПРАВЛЕННЯ:
- Для "всі записи" використовуй GET /api/{resource} (без параметрів)
- Для "конкретний запис" використовуй GET /api/{resource}/{id}
- Для "створення" використовуй POST /api/{resource}
- Для "оновлення" використовуй PUT /api/{resource}/{id}
- Для "видалення" використовуй DELETE /api/{resource}/{id}

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
    def get_endpoint_discovery_prompt(
        user_query: str, available_endpoints: List[Dict[str, Any]]
    ) -> str:
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
    def get_swagger_retry_prompt(
        user_query: str, original_endpoint: Dict[str, Any], corrected_endpoint: Dict[str, Any]
    ) -> str:
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
    def get_common_endpoint_patterns() -> Dict[str, str]:
        """Повертає загальні патерни endpoints."""
        return {
            "get_all": {
                "pattern": "GET /api/{resource}",
                "example": "GET /api/categories",
                "description": "Отримання всіх записів",
            },
            "get_by_id": {
                "pattern": "GET /api/{resource}/{id}",
                "example": "GET /api/categories/123",
                "description": "Отримання запису за ID",
            },
            "create": {
                "pattern": "POST /api/{resource}",
                "example": "POST /api/categories",
                "description": "Створення нового запису",
            },
            "update": {
                "pattern": "PUT /api/{resource}/{id}",
                "example": "PUT /api/categories/123",
                "description": "Оновлення запису",
            },
            "delete": {
                "pattern": "DELETE /api/{resource}/{id}",
                "example": "DELETE /api/categories/123",
                "description": "Видалення запису",
            },
        }

    @staticmethod
    def get_swagger_issues_detection_prompt(swagger_spec: Dict[str, Any]) -> str:
        """Промпт для виявлення проблем у Swagger специфікації."""
        return f"""
Ти - експерт з API. Проаналізуй Swagger специфікацію та вияви проблеми.

SWAGGER СПЕЦИФІКАЦІЯ:
{json.dumps(swagger_spec, ensure_ascii=False, indent=2)}

ЗАВДАННЯ:
1. Знайди endpoints які не відповідають RESTful принципам
2. Вияви відсутні endpoints для базових операцій
3. Перевір правильність HTTP методів
4. Знайди проблеми з параметрами
5. Запропонуй виправлення

ТИПОВІ ПРОБЛЕМИ:
- Неправильні URL (наприклад, /api/category замість /api/categories)
- Відсутні endpoints для CRUD операцій
- Неправильні HTTP методи
- Проблеми з параметрами (наприклад, {id} замість реального ID)

ВІДПОВІДЬ У ФОРМАТІ:
{{
    "issues": [
        {{
            "type": "тип проблеми",
            "description": "опис проблеми",
            "endpoint": "проблемний endpoint",
            "suggestion": "пропозиція виправлення"
        }}
    ],
    "missing_endpoints": [
        {{
            "operation": "відсутня операція",
            "suggested_endpoint": "запропонований endpoint"
        }}
    ],
    "recommendations": "загальні рекомендації"
}}
"""


# Приклади використання
if __name__ == "__main__":
    # Приклад проблемної ситуації
    user_query = "Покажи всі категорії"

    found_endpoints = [
        {
            "url": "https://db62d2b2c3a5.ngrok-free.app/api/category/{id}",
            "method": "GET",
            "description": "Get a category by ID (Public)",
        }
    ]

    api_error = {
        "message": 'invalid input syntax for type uuid: "{id}"',
        "error": "Bad Request",
        "statusCode": 400,
    }

    # Генеруємо промпт для виправлення
    validation_prompt = SwaggerValidationPrompt.get_swagger_validation_prompt(
        user_query, found_endpoints, api_error
    )

    print("🔍 Промпт для валідації Swagger:")
    print(validation_prompt)
    print()

    # Генеруємо промпт для виправлення endpoint
    correction_prompt = SwaggerValidationPrompt.get_endpoint_correction_prompt(
        user_query, found_endpoints[0], api_error
    )

    print("🔧 Промпт для виправлення endpoint:")
    print(correction_prompt)
    print()

    # Генеруємо промпт для обробки невідповідності Swagger
    mismatch_prompt = SwaggerValidationPrompt.get_swagger_mismatch_prompt(
        user_query, found_endpoints, api_error
    )

    print("⚠️ Промпт для обробки невідповідності Swagger:")
    print(mismatch_prompt)
    print()

    print("✅ Промпти готові для використання в InteractiveSwaggerAgent!")
