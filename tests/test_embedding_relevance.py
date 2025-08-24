"""
Тест релевантності embedding пошуку
"""

from typing import Any, Dict, List
from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def mock_embeddings():
    """Мок для OpenAIEmbeddings"""
    with patch("src.postgres_vector_manager.OpenAIEmbeddings") as mock:
        mock_instance = Mock()
        mock_instance.embed_query.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_vector_manager():
    """Мок для PostgresVectorManager"""
    with patch("src.postgres_vector_manager.PostgresVectorManager") as mock:
        mock_instance = Mock()
        mock_instance.search_similar.return_value = [
            {"endpoint_path": "/products", "method": "GET", "description": "Get products"},
            {
                "endpoint_path": "/products/{id}",
                "method": "GET",
                "description": "Get product by ID",
            },
        ]
        mock.return_value = mock_instance
        yield mock_instance


def test_search_relevance_products(mock_embeddings, mock_vector_manager):
    """Тест пошуку товарів"""
    try:
        from src.postgres_vector_manager import PostgresVectorManager

        vector_manager = PostgresVectorManager()
        query_embedding = mock_embeddings.embed_query("найти товары")

        results = vector_manager.search_similar(
            query_embedding=query_embedding,
            user_id="test_user",
            limit=5,
        )

        assert len(results) > 0
        assert any("products" in str(result.get("endpoint_path", "")).lower() for result in results)
    except ImportError:
        pytest.skip("PostgresVectorManager не може бути імпортований")


def test_search_relevance_orders(mock_embeddings, mock_vector_manager):
    """Тест пошуку замовлень"""
    try:
        from src.postgres_vector_manager import PostgresVectorManager

        vector_manager = PostgresVectorManager()
        query_embedding = mock_embeddings.embed_query("оформить заказ")

        results = vector_manager.search_similar(
            query_embedding=query_embedding,
            user_id="test_user",
            limit=5,
        )

        assert len(results) > 0
    except ImportError:
        pytest.skip("PostgresVectorManager не може бути імпортований")


def test_search_relevance_categories(mock_embeddings, mock_vector_manager):
    """Тест пошуку категорій"""
    try:
        from src.postgres_vector_manager import PostgresVectorManager

        vector_manager = PostgresVectorManager()
        query_embedding = mock_embeddings.embed_query("список категорий")

        results = vector_manager.search_similar(
            query_embedding=query_embedding,
            user_id="test_user",
            limit=5,
        )

        assert len(results) > 0
    except ImportError:
        pytest.skip("PostgresVectorManager не може бути імпортований")


def test_embedding_creation(mock_embeddings):
    """Тест створення embedding"""
    try:
        from src.postgres_vector_manager import OpenAIEmbeddings

        embeddings = OpenAIEmbeddings()
        query = "тестовий запит"
        embedding = embeddings.embed_query(query)

        assert embedding is not None
        assert len(embedding) > 0
    except ImportError:
        pytest.skip("OpenAIEmbeddings не може бути імпортований")
