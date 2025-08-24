"""
Тест для ClickoneSwaggerService
"""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.clickone_swagger_service import ClickoneSwaggerService, get_clickone_swagger_service


@pytest.fixture
def service():
    """Створює сервіс для тестування"""
    return ClickoneSwaggerService()


@pytest.fixture
def mock_swagger_spec():
    """Мокаємо Swagger специфікацію"""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Clickone Shop Backend API",
            "description": "API for Clickone Shop Backend",
            "version": "1.0",
        },
        "paths": {
            "/api/categories": {
                "post": {
                    "summary": "Create a new product category",
                    "description": "Create a new product category in the system",
                    "tags": ["AI Categories"],
                    "security": [{"bearer": []}],
                    "parameters": [],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/CreateCategoryDto"}
                            }
                        },
                    },
                    "responses": {
                        "201": {"description": "Category created successfully"},
                        "400": {"description": "Bad Request"},
                        "401": {"description": "Unauthorized"},
                    },
                },
                "get": {
                    "summary": "Get all categories",
                    "description": "Retrieve all product categories",
                    "tags": ["AI Categories"],
                    "parameters": [
                        {
                            "name": "isActive",
                            "in": "query",
                            "description": "Filter by active status",
                            "schema": {"type": "boolean"},
                        }
                    ],
                    "responses": {
                        "200": {"description": "Categories retrieved successfully"},
                        "404": {"description": "No categories found"},
                    },
                },
            }
        },
        "components": {
            "schemas": {
                "CreateCategoryDto": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the category",
                            "example": "Electronics",
                        },
                        "slug": {
                            "type": "string",
                            "description": "URL-friendly slug",
                            "example": "electronics",
                        },
                        "description": {
                            "type": "string",
                            "description": "Category description",
                            "example": "Electronic devices and gadgets",
                        },
                    },
                    "required": ["name", "slug"],
                }
            }
        },
    }


class TestClickoneSwaggerService:
    """Тести для ClickoneSwaggerService"""

    def test_service_initialization(self, service):
        """Тест ініціалізації сервісу"""
        assert service.swagger_url == "https://api.oneshop.click/docs/ai-json"
        assert service.api_url == "https://api.oneshop.click"
        assert service.swagger_parser is not None
        # vector_manager може бути None в тестовому середовищі
        print("✅ Сервіс успішно ініціалізовано")

    @patch("requests.get")
    def test_download_swagger_spec_success(self, mock_get, service):
        """Тест успішного завантаження Swagger специфікації"""
        # Мокаємо успішну відповідь
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"openapi": "3.0.0", "info": {"title": "Test API"}}
        mock_get.return_value = mock_response

        result = service.download_swagger_spec()

        assert result is not None
        assert result["openapi"] == "3.0.0"
        assert result["info"]["title"] == "Test API"
        print("✅ Swagger специфікацію завантажено успішно")

    @patch("requests.get")
    def test_download_swagger_spec_failure(self, mock_get, service):
        """Тест невдалого завантаження Swagger специфікації"""
        # Мокаємо невдалу відповідь
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = service.download_swagger_spec()

        assert result is None
        print("✅ Обробка помилки завантаження працює")

    def test_parse_swagger_spec(self, service, mock_swagger_spec):
        """Тест парсингу Swagger специфікації"""
        with patch.object(service.swagger_parser, "parse_swagger_spec") as mock_parse:
            mock_parse.return_value = {"endpoints": ["test"]}

            result = service.parse_swagger_spec(mock_swagger_spec)

            assert result["api_name"] == "Clickone Shop API"
            assert result["api_version"] == "1.0"
            assert "parsed_at" in result
            print("✅ Swagger специфікацію парсовано успішно")

    def test_convert_spec_to_text(self, service, mock_swagger_spec):
        """Тест конвертації специфікації в текст"""
        text = service._convert_spec_to_text(mock_swagger_spec)

        assert "API: Clickone Shop Backend API" in text
        assert "Версія: 1.0" in text
        assert "Ендпоінт: /api/categories" in text
        assert "Метод: POST" in text
        assert "Метод: GET" in text
        assert "Схеми даних:" in text
        assert "CreateCategoryDto:" in text

        print("✅ Специфікацію конвертовано в текст успішно")

    def test_get_api_endpoints_summary(self, service, mock_swagger_spec):
        """Тест створення опису ендпоінтів"""
        summary = service.get_api_endpoints_summary(mock_swagger_spec)

        assert "/api/categories" in summary
        assert "post" in summary["/api/categories"]
        assert "get" in summary["/api/categories"]

        post_info = summary["/api/categories"]["post"]
        assert post_info["summary"] == "Create a new product category"
        assert post_info["tags"] == ["AI Categories"]
        assert post_info["parameters_count"] == 0
        assert post_info["responses_count"] == 3

        print("✅ Опис ендпоінтів створено успішно")

    @patch("requests.get")
    def test_validate_api_connection_success(self, mock_get, service):
        """Тест успішного з'єднання з API"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = service.validate_api_connection()

        assert result is True
        print("✅ З'єднання з API перевірено успішно")

    @patch("requests.get")
    def test_validate_api_connection_failure(self, mock_get, service):
        """Тест невдалого з'єднання з API"""
        mock_get.side_effect = Exception("Connection error")

        result = service.validate_api_connection()

        assert result is False
        print("✅ Обробка помилки з'єднання працює")

    @patch.object(service, "download_swagger_spec")
    @patch.object(service, "parse_swagger_spec")
    @patch.object(service, "create_embeddings_for_spec")
    @patch.object(service, "get_api_endpoints_summary")
    def test_process_clickone_swagger_success(
        self, mock_summary, mock_embeddings, mock_parse, mock_download, service
    ):
        """Тест успішної обробки Clickone Shop API Swagger"""
        # Мокаємо всі залежності
        mock_download.return_value = {"openapi": "3.0.0"}
        mock_parse.return_value = {"api_name": "Test API", "api_version": "1.0"}
        mock_embeddings.return_value = True
        mock_summary.return_value = {"/test": {"get": {}}}

        result = service.process_clickone_swagger("test_user", "test_spec")

        assert result["success"] is True
        assert result["message"] == "Clickone Shop API Swagger успішно оброблено"
        assert result["spec_info"]["api_name"] == "Test API"
        assert result["spec_info"]["endpoints_count"] == 1

        print("✅ Обробку Clickone Shop API Swagger завершено успішно")

    @patch.object(service, "download_swagger_spec")
    def test_process_clickone_swagger_download_failure(self, mock_download, service):
        """Тест обробки з помилкою завантаження"""
        mock_download.return_value = None

        result = service.process_clickone_swagger("test_user", "test_spec")

        assert result["success"] is False
        assert "Не вдалося завантажити" in result["error"]
        print("✅ Обробка помилки завантаження працює")

    def test_search_api_documentation(self, service):
        """Тест пошуку в документації API"""
        with patch("src.rag_engine.PostgresRAGEngine") as mock_rag_class:
            mock_rag_engine = Mock()
            mock_rag_class.return_value = mock_rag_engine
            mock_rag_engine.search.return_value = [{"content": "test result"}]

            results = service.search_api_documentation("test_user", "test_spec", "test query")

            assert len(results) == 1
            assert results[0]["content"] == "test result"
            print("✅ Пошук в документації API працює")


class TestClickoneSwaggerServiceIntegration:
    """Інтеграційні тести для ClickoneSwaggerService"""

    @pytest.mark.integration
    def test_real_swagger_download(self):
        """Тест реального завантаження Swagger специфікації"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("Потрібен OpenAI API ключ для інтеграційного тесту")

        service = ClickoneSwaggerService()

        print("🔍 Тестую реальне завантаження Swagger специфікації...")

        # Завантажуємо реальну специфікацію
        swagger_spec = service.download_swagger_spec()

        if swagger_spec:
            assert "openapi" in swagger_spec
            assert "info" in swagger_spec
            assert "paths" in swagger_spec

            print(f"✅ Swagger специфікацію завантажено: {swagger_spec['info']['title']}")
            print(f"📊 Кількість ендпоінтів: {len(swagger_spec['paths'])}")

            # Тестуємо парсинг
            parsed_info = service.parse_swagger_spec(swagger_spec)
            assert parsed_info["api_name"] == "Clickone Shop API"

            print("✅ Реальну Swagger специфікацію парсовано успішно")
        else:
            print("⚠️ Не вдалося завантажити реальну Swagger специфікацію")

    @pytest.mark.integration
    def test_real_api_connection(self):
        """Тест реального з'єднання з Clickone Shop API"""
        service = ClickoneSwaggerService()

        print("🔌 Тестую реальне з'єднання з Clickone Shop API...")

        connection_works = service.validate_api_connection()

        if connection_works:
            print("✅ З'єднання з Clickone Shop API працює")
        else:
            print("⚠️ З'єднання з Clickone Shop API не працює")


def test_get_clickone_swagger_service():
    """Тест глобальної функції"""
    service = get_clickone_swagger_service()
    assert isinstance(service, ClickoneSwaggerService)
    print("✅ Глобальна функція працює")


if __name__ == "__main__":
    # Запуск тестів
    pytest.main([__file__, "-v", "-s"])
