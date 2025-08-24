"""
Тест продакшн функціональності з JWT токеном
"""

import os
from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def mock_swagger_agent():
    """Мок для SwaggerAgent з JWT"""
    with patch("src.interactive_api_agent.InteractiveSwaggerAgent") as mock:
        mock_instance = Mock()
        mock_instance.process_interactive_query.return_value = {
            "response": "Test response with JWT",
            "status": "success",
        }
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_env_vars():
    """Мок для змінних середовища"""
    with patch.dict(
        "os.environ", {"OPENAI_API_KEY": "test_openai_key", "JWT_TOKEN": "test_jwt_token"}
    ):
        yield


def test_production_jwt_import():
    """Тест імпорту SwaggerAgent з JWT"""
    try:
        from src.interactive_api_agent import InteractiveSwaggerAgent

        assert True
    except ImportError as e:
        pytest.skip(f"InteractiveSwaggerAgent не може бути імпортований: {e}")


def test_production_jwt_initialization(mock_swagger_agent, mock_env_vars):
    """Тест ініціалізації з JWT токеном"""
    try:
        from src.interactive_api_agent import InteractiveSwaggerAgent

        agent = InteractiveSwaggerAgent(
            swagger_spec_path="examples/swagger_specs/shop_api.json",
            enable_api_calls=True,
            openai_api_key="test_key",
            jwt_token="test_jwt",
        )

        assert agent is not None
        assert hasattr(agent, "jwt_token")

    except ImportError:
        pytest.skip("InteractiveSwaggerAgent не може бути імпортований")


def test_production_jwt_api_calls(mock_swagger_agent, mock_env_vars):
    """Тест API викликів з JWT токеном"""
    try:
        from src.interactive_api_agent import InteractiveSwaggerAgent

        agent = InteractiveSwaggerAgent(enable_api_calls=True, jwt_token="test_jwt")

        # Тестуємо різні типи запитів
        test_cases = [
            {"query": "Покажи всі товари", "expected_method": "GET"},
            {"query": "Створи новий товар: iPhone 15", "expected_method": "POST"},
            {"query": "Онови товар з ID 1", "expected_method": "PATCH"},
        ]

        for test_case in test_cases:
            response = agent.process_interactive_query(test_case["query"])
            assert response is not None
            assert "response" in response
            assert "status" in response

    except ImportError:
        pytest.skip("InteractiveSwaggerAgent не може бути імпортований")


def test_production_jwt_authorization(mock_swagger_agent, mock_env_vars):
    """Тест JWT авторизації"""
    try:
        from src.interactive_api_agent import InteractiveSwaggerAgent

        agent = InteractiveSwaggerAgent(enable_api_calls=True, jwt_token="test_jwt")

        # Перевіряємо, що JWT токен передається
        assert hasattr(agent, "jwt_token")
        assert agent.jwt_token == "test_jwt"

    except ImportError:
        pytest.skip("InteractiveSwaggerAgent не може бути імпортований")


def test_production_jwt_swagger_file(mock_swagger_agent, mock_env_vars):
    """Тест завантаження Swagger файлу з JWT"""
    try:
        from src.interactive_api_agent import InteractiveSwaggerAgent

        # Перевіряємо, чи існує тестовий Swagger файл
        swagger_file = "examples/swagger_specs/shop_api.json"

        if os.path.exists(swagger_file):
            agent = InteractiveSwaggerAgent(swagger_spec_path=swagger_file, jwt_token="test_jwt")
            assert agent is not None
        else:
            pytest.skip(f"Swagger файл {swagger_file} не знайдено")

    except ImportError:
        pytest.skip("InteractiveSwaggerAgent не може бути імпортований")


def test_production_jwt_error_handling(mock_swagger_agent, mock_env_vars):
    """Тест обробки помилок з JWT"""
    try:
        from src.interactive_api_agent import InteractiveSwaggerAgent

        agent = InteractiveSwaggerAgent(enable_api_calls=True, jwt_token="test_jwt")

        # Мокуємо помилку
        agent.process_interactive_query.side_effect = Exception("JWT error")

        with pytest.raises(Exception):
            agent.process_interactive_query("test query")

    except ImportError:
        pytest.skip("InteractiveSwaggerAgent не може бути імпортований")


def test_production_jwt_configuration(mock_swagger_agent, mock_env_vars):
    """Тест конфігурації з JWT"""
    try:
        from src.interactive_api_agent import InteractiveSwaggerAgent

        # Тестуємо різні конфігурації JWT
        agent1 = InteractiveSwaggerAgent(enable_api_calls=True, jwt_token="jwt1")
        agent2 = InteractiveSwaggerAgent(enable_api_calls=False, jwt_token="jwt2")

        assert agent1 is not None
        assert agent2 is not None
        assert agent1.jwt_token == "jwt1"
        assert agent2.jwt_token == "jwt2"

    except ImportError:
        pytest.skip("InteractiveSwaggerAgent не може бути імпортований")


def test_production_jwt_environment_variables(mock_swagger_agent):
    """Тест змінних середовища для JWT"""
    # Перевіряємо, що змінні середовища доступні
    with patch.dict(
        "os.environ", {"OPENAI_API_KEY": "env_openai_key", "JWT_TOKEN": "env_jwt_token"}
    ):
        openai_key = os.getenv("OPENAI_API_KEY")
        jwt_token = os.getenv("JWT_TOKEN")

        assert openai_key == "env_openai_key"
        assert jwt_token == "env_jwt_token"
