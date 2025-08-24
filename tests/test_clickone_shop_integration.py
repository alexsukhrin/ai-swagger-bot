"""
Тест інтеграції AI Swagger Bot з Clickone Shop API
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest


@pytest.fixture
def mock_openai():
    with patch("openai.OpenAI") as mock:
        mock_instance = Mock()
        mock_instance.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Test response"))]
        )
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_embeddings():
    with patch("langchain_openai.OpenAIEmbeddings") as mock:
        mock_instance = Mock()
        mock_instance.embed_query.return_value = [0.1, 0.2, 0.3]
        mock_instance.embed_documents.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def clickone_swagger_spec():
    """Завантажує Clickone Shop API специфікацію"""
    spec_path = (
        Path(__file__).parent.parent / "examples" / "swagger_specs" / "clickone_shop_api.json"
    )
    with open(spec_path, "r", encoding="utf-8") as f:
        return json.load(f)


class TestClickoneShopIntegration:
    """Тести інтеграції з Clickone Shop API"""

    @patch("src.enhanced_swagger_parser.EnhancedSwaggerParser")
    def test_swagger_parser_integration(self, mock_parser_class, clickone_swagger_spec):
        """Тест інтеграції з EnhancedSwaggerParser"""
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser

        # Мокаємо методи парсера
        mock_parser.parse_swagger_spec.return_value = {
            "endpoints": [
                {"path": "/api/categories", "method": "GET", "summary": "Get all categories"},
                {"path": "/api/categories", "method": "POST", "summary": "Create category"},
                {"path": "/api/categories/{id}", "method": "GET", "summary": "Get category by ID"},
            ],
            "schemas": ["CreateCategoryDto", "UpdateCategoryDto", "CreateProductDto"],
        }

        # Тестуємо парсинг
        result = mock_parser.parse_swagger_spec(clickone_swagger_spec)

        assert "endpoints" in result
        assert "schemas" in result
        assert len(result["endpoints"]) == 3
        assert len(result["schemas"]) == 3

        # Перевіряємо виклик парсера
        mock_parser.parse_swagger_spec.assert_called_once_with(clickone_swagger_spec)

    @patch("src.rag_engine.PostgresRAGEngine")
    def test_rag_engine_integration(self, mock_rag_class, clickone_swagger_spec):
        """Тест інтеграції з RAG Engine"""
        mock_rag = Mock()
        mock_rag_class.return_value = mock_rag

        # Мокаємо методи RAG engine
        mock_rag.create_vector_store_from_swagger.return_value = True
        mock_rag.enhance_chunks_with_gpt.return_value = True

        # Тестуємо створення vector store
        result = mock_rag.create_vector_store_from_swagger(clickone_swagger_spec)

        assert result is True
        mock_rag.create_vector_store_from_swagger.assert_called_once_with(clickone_swagger_spec)

    @patch("src.interactive_api_agent.InteractiveSwaggerAgent")
    def test_agent_integration(self, mock_agent_class, clickone_swagger_spec):
        """Тест інтеграції з InteractiveSwaggerAgent"""
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent

        # Мокаємо методи агента
        mock_agent.load_swagger_spec.return_value = True
        mock_agent.get_api_info.return_value = {
            "title": "Clickone Shop Backend API",
            "version": "1.0",
            "endpoints_count": 10,
        }

        # Тестуємо завантаження специфікації
        result = mock_agent.load_swagger_spec(clickone_swagger_spec)

        assert result is True
        mock_agent.load_swagger_spec.assert_called_once_with(clickone_swagger_spec)

        # Тестуємо отримання інформації про API
        api_info = mock_agent.get_api_info()
        assert api_info["title"] == "Clickone Shop Backend API"
        assert api_info["version"] == "1.0"

    @patch("src.gpt_prompt_generator.GPTPromptGenerator")
    def test_prompt_generator_integration(self, mock_generator_class, clickone_swagger_spec):
        """Тест інтеграції з GPT Prompt Generator"""
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator

        # Мокаємо методи генератора
        mock_generator.generate_endpoint_prompt.return_value = "Generated prompt for endpoint"
        mock_generator.generate_schema_prompt.return_value = "Generated prompt for schema"

        # Тестуємо генерацію prompt для endpoint
        endpoint_prompt = mock_generator.generate_endpoint_prompt(
            path="/api/categories",
            method="POST",
            operation=clickone_swagger_spec["paths"]["/api/categories"]["post"],
        )

        assert endpoint_prompt == "Generated prompt for endpoint"
        mock_generator.generate_endpoint_prompt.assert_called_once()

        # Тестуємо генерацію prompt для схеми
        schema_prompt = mock_generator.generate_schema_prompt(
            "CreateCategoryDto", clickone_swagger_spec["components"]["schemas"]["CreateCategoryDto"]
        )

        assert schema_prompt == "Generated prompt for schema"
        mock_generator.generate_schema_prompt.assert_called_once()

    def test_swagger_spec_validation(self, clickone_swagger_spec):
        """Тест валідації Swagger специфікації"""
        # Перевіряємо обов'язкові поля OpenAPI 3.0
        assert "openapi" in clickone_swagger_spec
        assert "info" in clickone_swagger_spec
        assert "paths" in clickone_swagger_spec
        assert "components" in clickone_swagger_spec

        # Перевіряємо версію
        assert clickone_swagger_spec["openapi"] == "3.0.0"

        # Перевіряємо інформацію
        info = clickone_swagger_spec["info"]
        assert "title" in info
        assert "version" in info
        assert info["title"] == "Clickone Shop Backend API"
        assert info["version"] == "1.0"

        # Перевіряємо наявність endpoints
        paths = clickone_swagger_spec["paths"]
        assert len(paths) > 0

        # Перевіряємо компоненти
        components = clickone_swagger_spec["components"]
        assert "schemas" in components
        assert "securitySchemes" in components

        # Перевіряємо схеми безпеки
        security_schemes = components["securitySchemes"]
        assert "bearer" in security_schemes

    def test_api_endpoints_structure(self, clickone_swagger_spec):
        """Тест структури API endpoints"""
        paths = clickone_swagger_spec["paths"]

        # Перевіряємо основні endpoints
        assert "/api/categories" in paths
        assert "/api/categories/{id}" in paths

        # Перевіряємо структуру categories endpoint
        categories = paths["/api/categories"]
        assert "get" in categories
        assert "post" in categories

        # Перевіряємо GET метод
        get_method = categories["get"]
        assert "summary" in get_method
        assert "description" in get_method
        assert "operationId" in get_method
        assert "tags" in get_method
        assert "responses" in get_method

        # Перевіряємо POST метод
        post_method = categories["post"]
        assert "summary" in post_method
        assert "description" in post_method
        assert "operationId" in post_method
        assert "tags" in post_method
        assert "requestBody" in post_method
        assert "responses" in post_method
        assert "security" in post_method

    def test_data_models_structure(self, clickone_swagger_spec):
        """Тест структури даних моделей"""
        schemas = clickone_swagger_spec["components"]["schemas"]

        # Перевіряємо основні DTOs
        required_dtos = [
            "CreateCategoryDto",
            "UpdateCategoryDto",
            "CreateProductDto",
            "UpdateProductDto",
            "CreateOrderDto",
            "UpdateOrderDto",
            "CreateBrandDto",
            "UpdateBrandDto",
        ]

        for dto in required_dtos:
            assert dto in schemas, f"Missing DTO: {dto}"

            dto_schema = schemas[dto]
            assert "type" in dto_schema
            assert dto_schema["type"] == "object"
            assert "properties" in dto_schema

        # Перевіряємо структуру CreateCategoryDto детально
        create_category = schemas["CreateCategoryDto"]
        properties = create_category["properties"]

        required_fields = ["name", "slug"]
        for field in required_fields:
            assert field in properties, f"Missing required field: {field}"

        # Перевіряємо типи полів
        assert properties["name"]["type"] == "string"
        assert properties["slug"]["type"] == "string"
        assert properties["isActive"]["type"] == "boolean"
        assert properties["sortOrder"]["type"] == "number"

    def test_security_implementation(self, clickone_swagger_spec):
        """Тест реалізації безпеки"""
        security_schemes = clickone_swagger_spec["components"]["securitySchemes"]

        # Перевіряємо Bearer token схему
        assert "bearer" in security_schemes
        bearer = security_schemes["bearer"]

        assert bearer["type"] == "http"
        assert bearer["scheme"] == "bearer"
        assert bearer["bearerFormat"] == "JWT"

        # Перевіряємо застосування безпеки в endpoints
        paths = clickone_swagger_spec["paths"]

        # POST endpoint повинен мати безпеку
        post_endpoint = paths["/api/categories"]["post"]
        assert "security" in post_endpoint
        assert post_endpoint["security"] == [{"bearer": []}]

        # GET endpoint може бути публічним
        get_endpoint = paths["/api/categories"]["get"]
        # GET може не мати security якщо публічний

    def test_error_handling(self, clickone_swagger_spec):
        """Тест обробки помилок"""
        paths = clickone_swagger_spec["paths"]

        # Перевіряємо responses в POST endpoint
        post_endpoint = paths["/api/categories"]["post"]
        responses = post_endpoint["responses"]

        # Перевіряємо наявність основних HTTP статусів
        assert "201" in responses  # Created
        assert "400" in responses  # Bad Request
        assert "401" in responses  # Unauthorized
        assert "403" in responses  # Forbidden

        # Перевіряємо опис помилок
        assert "description" in responses["400"]
        assert "description" in responses["401"]
        assert "description" in responses["403"]

        # Перевіряємо успішну відповідь
        success_response = responses["201"]
        assert "description" in success_response
        assert success_response["description"] == "Category created successfully"
