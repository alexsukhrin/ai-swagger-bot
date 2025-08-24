"""
Тест для перевірки роботи AI Swagger Bot з Clickone Shop API
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest


# Мокаємо OpenAI та інші зовнішні залежності
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


class TestClickoneShopAPI:
    """Тести для роботи з Clickone Shop API"""

    def test_swagger_spec_loading(self, clickone_swagger_spec):
        """Тест завантаження Swagger специфікації"""
        assert clickone_swagger_spec is not None
        assert "openapi" in clickone_swagger_spec
        assert clickone_swagger_spec["openapi"] == "3.0.0"
        assert "paths" in clickone_swagger_spec
        assert "info" in clickone_swagger_spec

        # Перевіряємо основну інформацію
        info = clickone_swagger_spec["info"]
        assert info["title"] == "Clickone Shop Backend API"
        assert info["version"] == "1.0"

        # Перевіряємо наявність основних endpoints
        paths = clickone_swagger_spec["paths"]
        assert "/api/categories" in paths
        assert "/api/categories/{id}" in paths

    def test_categories_endpoints(self, clickone_swagger_spec):
        """Тест endpoints для категорій"""
        categories_path = clickone_swagger_spec["paths"]["/api/categories"]

        # GET endpoint
        assert "get" in categories_path
        get_op = categories_path["get"]
        assert get_op["summary"] == "Get all categories (Public)"
        assert get_op["tags"] == ["AI Categories"]
        assert get_op["operationId"] == "CategoryAIController_findAll"

        # POST endpoint
        assert "post" in categories_path
        post_op = categories_path["post"]
        assert post_op["summary"] == "Create a new category (Admin only)"
        assert post_op["tags"] == ["AI Categories"]
        assert post_op["operationId"] == "CategoryAIController_create"

    def test_products_endpoints(self, clickone_swagger_spec):
        """Тест endpoints для продуктів"""
        # Перевіряємо наявність продуктів в схемах
        schemas = clickone_swagger_spec["components"]["schemas"]
        assert "CreateProductDto" in schemas
        assert "UpdateProductDto" in schemas

        # Перевіряємо структуру CreateProductDto
        create_product = schemas["CreateProductDto"]
        assert "properties" in create_product
        assert "name" in create_product["properties"]
        assert "price" in create_product["properties"]
        assert "sku" in create_product["properties"]
        assert "categoryId" in create_product["properties"]

        # Перевіряємо required поля
        assert "name" in create_product["required"]
        assert "price" in create_product["required"]
        assert "sku" in create_product["required"]
        assert "categoryId" in create_product["required"]

    def test_security_schemes(self, clickone_swagger_spec):
        """Тест схем безпеки"""
        security_schemes = clickone_swagger_spec["components"]["securitySchemes"]
        assert "bearer" in security_schemes

        bearer_scheme = security_schemes["bearer"]
        assert bearer_scheme["type"] == "http"
        assert bearer_scheme["scheme"] == "bearer"
        assert bearer_scheme["bearerFormat"] == "JWT"

    def test_orders_endpoints(self, clickone_swagger_spec):
        """Тест endpoints для замовлень"""
        schemas = clickone_swagger_spec["components"]["schemas"]

        # Перевіряємо схеми замовлень
        assert "CreateOrderDto" in schemas
        assert "UpdateOrderDto" in schemas
        assert "OrderItemDto" in schemas

        # Перевіряємо структуру CreateOrderDto
        create_order = schemas["CreateOrderDto"]
        assert "properties" in create_order
        assert "orderNumber" in create_order["properties"]
        assert "customerId" in create_order["properties"]
        assert "status" in create_order["properties"]
        assert "items" in create_order["properties"]

        # Перевіряємо enum значення для статусу
        status_prop = create_order["properties"]["status"]
        assert "enum" in status_prop
        expected_statuses = [
            "pending",
            "confirmed",
            "processing",
            "shipped",
            "delivered",
            "cancelled",
            "returned",
        ]
        assert status_prop["enum"] == expected_statuses

    def test_brands_endpoints(self, clickone_swagger_spec):
        """Тест endpoints для брендів"""
        schemas = clickone_swagger_spec["components"]["schemas"]

        assert "CreateBrandDto" in schemas
        assert "UpdateBrandDto" in schemas

        # Перевіряємо структуру CreateBrandDto
        create_brand = schemas["CreateBrandDto"]
        assert "properties" in create_brand
        assert "name" in create_brand["properties"]
        assert "slug" in create_brand["properties"]
        assert "status" in create_brand["properties"]

        # Перевіряємо enum значення для статусу бренду
        status_prop = create_brand["properties"]["status"]
        assert "enum" in status_prop
        assert status_prop["enum"] == ["active", "inactive"]

    def test_collections_endpoints(self, clickone_swagger_spec):
        """Тест endpoints для колекцій"""
        schemas = clickone_swagger_spec["components"]["schemas"]

        assert "CollectionsDto" in schemas
        assert "AddProductsToCollectionDto" in schemas
        assert "RemoveProductsFromCollectionDto" in schemas

        # Перевіряємо структуру CollectionsDto
        collections = schemas["CollectionsDto"]
        assert "properties" in collections
        assert "name" in collections["properties"]
        assert "slug" in collections["properties"]
        assert "type" in collections["properties"]
        assert "status" in collections["properties"]

        # Перевіряємо enum значення
        type_prop = collections["properties"]["type"]
        assert "enum" in type_prop
        assert type_prop["enum"] == ["manual", "automatic", "seasonal"]

        status_prop = collections["properties"]["status"]
        assert "enum" in status_prop
        assert status_prop["enum"] == ["active", "inactive", "scheduled"]

    def test_customers_endpoints(self, clickone_swagger_spec):
        """Тест endpoints для клієнтів"""
        schemas = clickone_swagger_spec["components"]["schemas"]

        assert "CreateCustomerDto" in schemas
        assert "UpdateCustomerProfileDto" in schemas
        assert "CustomerEntity" in schemas

        # Перевіряємо структуру UpdateCustomerProfileDto
        update_customer = schemas["UpdateCustomerProfileDto"]
        assert "properties" in update_customer
        assert "firstName" in update_customer["properties"]
        assert "lastName" in update_customer["properties"]
        assert "phone" in update_customer["properties"]
        assert "gender" in update_customer["properties"]

        # Перевіряємо enum значення для гендеру
        gender_prop = update_customer["properties"]["gender"]
        assert "enum" in gender_prop
        assert gender_prop["enum"] == ["male", "female", "other"]

    def test_warehouse_operations(self, clickone_swagger_spec):
        """Тест warehouse operations"""
        schemas = clickone_swagger_spec["components"]["schemas"]

        assert "CreateWarehouseOperationDto" in schemas

        # Перевіряємо структуру
        warehouse_op = schemas["CreateWarehouseOperationDto"]
        assert "properties" in warehouse_op
        assert "warehouseId" in warehouse_op["properties"]
        assert "type" in warehouse_op["properties"]
        assert "performedBy" in warehouse_op["properties"]

        # Перевіряємо enum значення для типу операції
        type_prop = warehouse_op["properties"]["type"]
        assert "enum" in type_prop
        assert type_prop["enum"] == ["addition", "writeOff", "lowStockChange"]

    def test_swagger_spec_completeness(self, clickone_swagger_spec):
        """Тест повноти Swagger специфікації"""
        # Перевіряємо загальну структуру
        required_top_level = ["openapi", "info", "paths", "components"]
        for field in required_top_level:
            assert field in clickone_swagger_spec

        # Перевіряємо компоненти
        components = clickone_swagger_spec["components"]
        required_components = ["securitySchemes", "schemas"]
        for component in required_components:
            assert component in components

        # Перевіряємо кількість endpoints
        paths = clickone_swagger_spec["paths"]
        assert len(paths) > 0

        # Перевіряємо кількість схем
        schemas = components["schemas"]
        assert len(schemas) > 0

        # Перевіряємо наявність основних DTOs
        required_dtos = [
            "CreateProductDto",
            "UpdateProductDto",
            "CreateCategoryDto",
            "UpdateCategoryDto",
            "CreateOrderDto",
            "UpdateOrderDto",
            "CreateBrandDto",
            "UpdateBrandDto",
        ]
        for dto in required_dtos:
            assert dto in schemas, f"Missing DTO: {dto}"
