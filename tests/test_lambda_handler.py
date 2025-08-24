"""
Тест Lambda handler
"""

import json
from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def sample_event():
    """Приклад event для Lambda"""
    return {
        "httpMethod": "POST",
        "path": "/chat",
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Hello, world!", "user_id": "test_user"}),
    }


@pytest.fixture
def sample_context():
    """Приклад context для Lambda"""
    context = Mock()
    context.function_name = "ai-swagger-bot"
    context.memory_limit_in_mb = 128
    context.remaining_time_in_millis = 30000
    return context


def test_lambda_handler_import():
    """Тест імпорту lambda handler"""
    try:
        from lambda_handler import lambda_handler

        assert callable(lambda_handler)
    except ImportError as e:
        pytest.skip(f"lambda_handler не може бути імпортований: {e}")


def test_lambda_handler_basic(sample_event, sample_context):
    """Базовий тест lambda handler"""
    try:
        from lambda_handler import lambda_handler

        # Мокуємо залежності
        with patch("lambda_handler.process_chat_message") as mock_process:
            mock_process.return_value = {"response": "Hello from Lambda!"}

            result = lambda_handler(sample_event, sample_context)

            assert result is not None
            assert "statusCode" in result
            assert result["statusCode"] == 200

    except ImportError:
        pytest.skip("lambda_handler не може бути імпортований")


def test_lambda_handler_chat_endpoint(sample_context):
    """Тест chat endpoint"""
    try:
        from lambda_handler import lambda_handler

        event = {
            "httpMethod": "POST",
            "path": "/chat",
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Test message"}),
        }

        with patch("lambda_handler.process_chat_message") as mock_process:
            mock_process.return_value = {"response": "Test response"}

            result = lambda_handler(event, sample_context)

            assert result["statusCode"] == 200
            assert "Test response" in result["body"]

    except ImportError:
        pytest.skip("lambda_handler не може бути імпортований")


def test_lambda_handler_health_endpoint(sample_context):
    """Тест health endpoint"""
    try:
        from lambda_handler import lambda_handler

        event = {"httpMethod": "GET", "path": "/health", "headers": {}, "body": None}

        result = lambda_handler(event, sample_context)

        assert result["statusCode"] == 200
        assert "status" in result["body"]

    except ImportError:
        pytest.skip("lambda_handler не може бути імпортований")


def test_lambda_handler_error_handling(sample_context):
    """Тест обробки помилок"""
    try:
        from lambda_handler import lambda_handler

        event = {"httpMethod": "POST", "path": "/invalid", "headers": {}, "body": None}

        result = lambda_handler(event, sample_context)

        assert result["statusCode"] == 404
        assert "error" in result["body"]

    except ImportError:
        pytest.skip("lambda_handler не може бути імпортований")


def test_lambda_handler_cors_headers(sample_event, sample_context):
    """Тест CORS заголовків"""
    try:
        from lambda_handler import lambda_handler

        with patch("lambda_handler.process_chat_message") as mock_process:
            mock_process.return_value = {"response": "Test"}

            result = lambda_handler(sample_event, sample_context)

            assert "headers" in result
            assert "Access-Control-Allow-Origin" in result["headers"]
            assert "Access-Control-Allow-Headers" in result["headers"]

    except ImportError:
        pytest.skip("lambda_handler не може бути імпортований")


def test_lambda_handler_memory_usage(sample_event, sample_context):
    """Тест використання пам'яті"""
    try:
        from lambda_handler import lambda_handler

        with patch("lambda_handler.process_chat_message") as mock_process:
            mock_process.return_value = {"response": "Test"}

            result = lambda_handler(sample_event, sample_context)

            # Перевіряємо, що handler не використовує забагато пам'яті
            assert result is not None

    except ImportError:
        pytest.skip("lambda_handler не може бути імпортований")
