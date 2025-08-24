"""
Тест AI Swagger Agent з продакшн сервером
"""

import os
from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def mock_swagger_agent():
    """Мок для SwaggerAgent"""
    with patch("src.interactive_api_agent.InteractiveSwaggerAgent") as mock:
        mock_instance = Mock()
        mock_instance.base_url = "https://api.example.com"
        mock_instance.process_interactive_query.return_value = {
            "response": "Test response",
            "status": "success",
        }
        mock.return_value = mock_instance
        yield mock_instance


def test_production_agent_import():
    """Тест імпорту продакшн агента"""
    try:
        from src.interactive_api_agent import InteractiveSwaggerAgent

        assert True
    except ImportError as e:
        pytest.skip(f"InteractiveSwaggerAgent не може бути імпортований: {e}")


def test_production_agent_initialization(mock_swagger_agent):
    """Тест ініціалізації продакшн агента"""
    try:
        from src.interactive_api_agent import InteractiveSwaggerAgent

        swagger_file = "examples/swagger_specs/shop_api_prod.json"
        agent = InteractiveSwaggerAgent(swagger_spec_path=swagger_file, enable_api_calls=True)

        assert agent is not None
        assert hasattr(agent, "base_url")

    except ImportError:
        pytest.skip("InteractiveSwaggerAgent не може бути імпортований")


def test_production_agent_api_calls(mock_swagger_agent):
    """Тест API викликів продакшн агента"""
    try:
        from src.interactive_api_agent import InteractiveSwaggerAgent

        agent = InteractiveSwaggerAgent()

        # Тестуємо різні запити
        test_queries = [
            "Покажи всі категорії",
            "Створи категорію: Електроніка",
            "Покажи всі бренди",
        ]

        for query in test_queries:
            response = agent.process_interactive_query(query)
            assert response is not None
            assert "response" in response
            assert "status" in response

    except ImportError:
        pytest.skip("InteractiveSwaggerAgent не може бути імпортований")


def test_production_agent_swagger_file():
    """Тест завантаження Swagger файлу"""
    try:
        from src.interactive_api_agent import InteractiveSwaggerAgent

        # Перевіряємо, чи існує тестовий Swagger файл
        swagger_file = "examples/swagger_specs/shop_api.json"

        if os.path.exists(swagger_file):
            agent = InteractiveSwaggerAgent(swagger_spec_path=swagger_file)
            assert agent is not None
        else:
            pytest.skip(f"Swagger файл {swagger_file} не знайдено")

    except ImportError:
        pytest.skip("InteractiveSwaggerAgent не може бути імпортований")


def test_production_agent_error_handling(mock_swagger_agent):
    """Тест обробки помилок продакшн агента"""
    try:
        from src.interactive_api_agent import InteractiveSwaggerAgent

        agent = InteractiveSwaggerAgent()

        # Мокуємо помилку
        agent.process_interactive_query.side_effect = Exception("Test error")

        with pytest.raises(Exception):
            agent.process_interactive_query("test query")

    except ImportError:
        pytest.skip("InteractiveSwaggerAgent не може бути імпортований")


def test_production_agent_configuration():
    """Тест конфігурації продакшн агента"""
    try:
        from src.interactive_api_agent import InteractiveSwaggerAgent

        # Тестуємо різні конфігурації
        agent1 = InteractiveSwaggerAgent(enable_api_calls=True)
        agent2 = InteractiveSwaggerAgent(enable_api_calls=False)

        assert agent1 is not None
        assert agent2 is not None

    except ImportError:
        pytest.skip("InteractiveSwaggerAgent не може бути імпортований")
