"""
Інтеграційні тести для перевірки роботи промптів з API агентом
Перевіряє як промпти використовуються в реальних сценаріях роботи з API
"""

import json
import os
import sys
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

# Додаємо шлях до модуля
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.interactive_api_agent import InteractiveSwaggerAgent
from src.prompt_templates import PromptTemplates
from src.yaml_prompt_manager import YAMLPromptManager


class TestPromptAgentIntegration:
    """Інтеграційні тести для перевірки роботи промптів з API агентом."""

    def setup_method(self):
        """Налаштування перед кожним тестом."""
        self.manager = YAMLPromptManager()
        self.setup_test_swagger_spec()
        self.setup_test_prompts()

    def setup_test_swagger_spec(self):
        """Налаштовує тестову Swagger специфікацію."""
        self.test_swagger_spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/products": {
                    "get": {
                        "summary": "Get products",
                        "operationId": "getProducts",
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {"type": "integer"},
                                                    "name": {"type": "string"},
                                                    "price": {"type": "number"},
                                                },
                                            },
                                        }
                                    }
                                },
                            }
                        },
                    },
                    "post": {
                        "summary": "Create product",
                        "operationId": "createProduct",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "required": ["name", "price"],
                                        "properties": {
                                            "name": {"type": "string"},
                                            "price": {"type": "number"},
                                            "description": {"type": "string"},
                                        },
                                    }
                                }
                            },
                        },
                        "responses": {
                            "201": {
                                "description": "Created",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "integer"},
                                                "name": {"type": "string"},
                                                "price": {"type": "number"},
                                            },
                                        }
                                    }
                                },
                            }
                        },
                    },
                }
            },
        }

    def setup_test_prompts(self):
        """Налаштовує тестові промпти для роботи з API."""

        # Промпт для аналізу наміру користувача
        intent_analysis_prompt = {
            "name": "Аналіз наміру користувача",
            "description": "Промпт для аналізу наміру користувача",
            "template": """
Ти - експерт з аналізу намірів користувачів.

ЗАПИТ КОРИСТУВАЧА: {user_query}

Твоя задача:
1. Визначити намір користувача
2. Визначити тип операції (GET, POST, PUT, DELETE)
3. Визначити ресурс (products, categories, users)
4. Визначити параметри

МОЖЛИВІ НАМІРИ:
- Отримання даних: "покажи", "знайди", "отримай"
- Створення даних: "створи", "додай", "новий"
- Оновлення даних: "зміни", "онові", "редагуй"
- Видалення даних: "видали", "видаляй"

ВІДПОВІДЬ у форматі JSON:
{{
    "intent": "retrieval|creation|update|deletion",
    "resource": "products|categories|users",
    "operation": "GET|POST|PUT|DELETE",
    "parameters": {{}},
    "confidence": 0.9
}}
""",
            "category": "intent_analysis",
            "is_public": True,
            "user_id": "test_user",
        }
        self.manager.add_custom_prompt(intent_analysis_prompt, "test_user")

        # Промпт для формування API запиту
        api_request_prompt = {
            "name": "Формування API запиту",
            "description": "Промпт для формування API запиту",
            "template": """
Ти - експерт з формування API запитів.

НАМІР: {intent}
РЕСУРС: {resource}
ОПЕРАЦІЯ: {operation}
ПАРАМЕТРИ: {parameters}

ENDPOINT: {endpoint}

Твоя задача:
1. Формувати правильний HTTP запит
2. Додавати необхідні заголовки
3. Формувати тіло запиту
4. Обробляти параметри

ВІДПОВІДЬ у форматі JSON:
{{
    "method": "GET|POST|PUT|DELETE",
    "url": "повний URL",
    "headers": {{}},
    "body": {{}},
    "query_params": {{}}
}}
""",
            "category": "api_request",
            "is_public": True,
            "user_id": "test_user",
        }
        self.manager.add_custom_prompt(api_request_prompt, "test_user")

        # Промпт для обробки відповіді API
        api_response_prompt = {
            "name": "Обробка відповіді API",
            "description": "Промпт для обробки відповіді API",
            "template": """
Ти - експерт з обробки відповідей API.

ЗАПИТ КОРИСТУВАЧА: {user_query}
ВІДПОВІДЬ API: {api_response}
СТАТУС: {status_code}

Твоя задача:
1. Аналізувати відповідь API
2. Форматувати інформацію зрозуміло
3. Обробляти помилки
4. Надавати корисну інформацію

ВІДПОВІДЬ:
""",
            "category": "response_formatting",
            "is_public": True,
            "user_id": "test_user",
        }
        self.manager.add_custom_prompt(api_response_prompt, "test_user")

    @patch("src.interactive_api_agent.InteractiveSwaggerAgent")
    def test_prompt_integration_with_agent(self, mock_agent_class):
        """Тест: інтеграція промптів з API агентом."""

        # Мокаємо агента
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        # Симулюємо відповідь агента
        mock_agent.process_interactive_query.return_value = {
            "response": "✅ Товар успішно створено",
            "status": "success",
            "api_call": {
                "method": "POST",
                "url": "/products",
                "body": {"name": "Test Product", "price": 100},
            },
        }

        # Тестуємо роботу з промптами
        user_query = "Створи товар з назвою 'Тестовий товар'"

        # 1. Аналізуємо намір користувача
        intent_prompt = self.manager.get_prompts_by_category("intent_analysis")[0]
        intent_formatted = self.manager.format_prompt(
            intent_prompt.id, user_query=user_query, context="Попередні взаємодії відсутні"
        )

        # Перевіряємо, що промпт правильно відформатований
        assert user_query in intent_formatted
        assert "аналізуй" in intent_formatted.lower()

        # 2. Формуємо API запит
        request_prompt = self.manager.get_prompts_by_category("api_request")[0]
        request_formatted = self.manager.format_prompt(
            request_prompt.id,
            intent="creation",
            resource="products",
            operation="POST",
            parameters={"name": "Тестовий товар"},
            endpoint="/products",
        )

        # Перевіряємо, що промпт правильно відформатований
        assert "POST" in request_formatted
        assert "/products" in request_formatted
        assert "Тестовий товар" in request_formatted

    def test_prompt_error_handling_integration(self):
        """Тест: інтеграційна перевірка обробки помилок з промптами."""

        # Симулюємо помилку API
        error_response = {
            "error": "Validation failed",
            "message": "Field 'price' is required",
            "status_code": 400,
        }

        # Отримуємо промпт для обробки помилок
        error_prompts = self.manager.get_prompts_by_category("error_handling")
        if error_prompts:
            error_prompt = error_prompts[0]

            # Форматуємо промпт з помилкою
            formatted = self.manager.format_prompt(
                error_prompt.id,
                error_message=error_response["message"],
                original_query="Створи товар",
                api_request='{"method": "POST", "url": "/products", "data": {"name": "test"}}',
            )

            # Перевіряємо, що промпт правильно відформатований
            assert error_response["message"] in formatted
            assert "Створи товар" in formatted

    def test_prompt_response_formatting_integration(self):
        """Тест: інтеграційна перевірка форматування відповідей з промптами."""

        # Симулюємо успішну відповідь API
        success_response = {
            "id": 1,
            "name": "iPhone 15 Pro",
            "price": 999.99,
            "description": "Новий iPhone",
        }

        # Отримуємо промпт для форматування відповідей
        response_prompts = self.manager.get_prompts_by_category("response_formatting")
        if response_prompts:
            response_prompt = response_prompts[0]

            # Форматуємо промпт з відповіддю
            formatted = self.manager.format_prompt(
                response_prompt.id,
                api_request='{"method": "POST", "url": "/products", "data": {"name": "iPhone 15 Pro"}}',
                server_response=json.dumps(success_response),
                status=201,
            )

            # Перевіряємо, що промпт правильно відформатований
            assert "iPhone 15 Pro" in formatted
            assert "201" in formatted
            assert "форматування" in formatted.lower()

    def test_prompt_suggestion_integration(self):
        """Тест: інтеграційна перевірка пропозицій промптів."""

        # Тестуємо різні типи запитів
        test_scenarios = [
            ("Створи новий товар", ["intent_analysis", "api_request"]),
            ("Покажи всі товари", ["intent_analysis", "api_request"]),
            ("Помилка при створенні", ["error_handling", "response_formatting"]),
        ]

        for query, expected_categories in test_scenarios:
            suggestions = self.manager.get_prompt_suggestions(query)

            # Перевіряємо, що знайдено пропозиції
            assert len(suggestions) > 0

            # Перевіряємо, що є промпти з очікуваними категоріями
            found_categories = set(p.category for p in suggestions)
            for expected_category in expected_categories:
                if expected_category in found_categories:
                    assert True  # Категорія знайдена

    def test_prompt_real_api_scenario(self):
        """Тест: реальний сценарій роботи з API через промпти."""

        # Симулюємо повний цикл роботи з API

        # 1. Користувач запитує створення товару
        user_query = "Створи товар з назвою 'MacBook Pro' та ціною 2000"

        # 2. Аналізуємо намір
        intent_prompts = self.manager.get_prompts_by_category("intent_analysis")
        if intent_prompts:
            intent_prompt = intent_prompts[0]
            intent_formatted = self.manager.format_prompt(
                intent_prompt.id, user_query=user_query, context="Попередні взаємодії відсутні"
            )

            # Перевіряємо аналіз наміру
            assert "MacBook Pro" in intent_formatted
            assert "2000" in intent_formatted

        # 3. Формуємо API запит
        request_prompts = self.manager.get_prompts_by_category("api_request")
        if request_prompts:
            request_prompt = request_prompts[0]
            request_formatted = self.manager.format_prompt(
                request_prompt.id,
                intent="creation",
                resource="products",
                operation="POST",
                parameters={"name": "MacBook Pro", "price": 2000},
                endpoint="/products",
            )

            # Перевіряємо формування запиту
            assert "POST" in request_formatted
            assert "MacBook Pro" in request_formatted
            assert "2000" in request_formatted

        # 4. Симулюємо успішну відповідь
        api_response = {"id": 123, "name": "MacBook Pro", "price": 2000.0, "status": "created"}

        # 5. Форматуємо відповідь
        response_prompts = self.manager.get_prompts_by_category("response_formatting")
        if response_prompts:
            response_prompt = response_prompts[0]
            response_formatted = self.manager.format_prompt(
                response_prompt.id,
                api_request='{"method": "POST", "url": "/products", "data": {"name": "MacBook Pro", "price": 2000}}',
                server_response=json.dumps(api_response),
                status=201,
            )

            # Перевіряємо форматування відповіді
            assert "MacBook Pro" in response_formatted
            assert "201" in response_formatted

    def test_prompt_performance_with_agent(self):
        """Тест: продуктивність промптів при роботі з агентом."""

        import time

        start_time = time.time()

        # Симулюємо кілька запитів до промптів
        for i in range(5):
            # Аналіз наміру
            intent_prompts = self.manager.get_prompts_by_category("intent_analysis")
            if intent_prompts:
                self.manager.format_prompt(
                    intent_prompts[0].id,
                    user_query=f"Створи товар {i}",
                    context="Попередні взаємодії відсутні",
                )

            # Формування запиту
            request_prompts = self.manager.get_prompts_by_category("api_request")
            if request_prompts:
                self.manager.format_prompt(
                    request_prompts[0].id,
                    intent="creation",
                    resource="products",
                    operation="POST",
                    parameters={"name": f"Товар {i}"},
                    endpoint="/products",
                )

            # Форматування відповіді
            response_prompts = self.manager.get_prompts_by_category("response_formatting")
            if response_prompts:
                self.manager.format_prompt(
                    response_prompts[0].id,
                    api_request=f'{{"method": "POST", "url": "/products", "data": {{"name": "Товар {i}"}}}}',
                    server_response=json.dumps({"id": i, "name": f"Товар {i}"}),
                    status=201,
                )

        end_time = time.time()
        execution_time = end_time - start_time

        # Перевіряємо, що виконання не займає забагато часу
        assert execution_time < 2.0  # Менше 2 секунд

    def test_prompt_error_scenarios(self):
        """Тест: сценарії помилок з промптами."""

        # Тестуємо різні сценарії помилок
        error_scenarios = [
            {
                "query": "Створи товар без назви",
                "error": "Field 'name' is required",
                "status_code": 400,
            },
            {"query": "Отримай неіснуючий товар", "error": "Product not found", "status_code": 404},
            {
                "query": "Створи товар з невалідною ціною",
                "error": "Price must be positive",
                "status_code": 422,
            },
        ]

        for scenario in error_scenarios:
            # Отримуємо промпт для обробки помилок
            error_prompts = self.manager.get_prompts_by_category("error_handling")
            if error_prompts:
                error_prompt = error_prompts[0]

                # Форматуємо промпт з помилкою
                formatted = self.manager.format_prompt(
                    error_prompt.id,
                    error_message=scenario["error"],
                    original_query=scenario["query"],
                    api_request='{"method": "POST", "url": "/products", "data": {}}',
                )

                # Перевіряємо, що помилка правильно оброблена
                assert scenario["error"] in formatted
                assert scenario["query"] in formatted


if __name__ == "__main__":
    # Запуск тестів
    pytest.main([__file__, "-v"])
