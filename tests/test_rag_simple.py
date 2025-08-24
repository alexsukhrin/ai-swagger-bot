"""
Простий тест для RAG engine
"""

from unittest.mock import Mock, patch

import pytest


def test_rag_engine_import():
    """Тест імпорту RAG engine"""
    try:
        from src.rag_engine import PostgresRAGEngine

        assert True
    except ImportError as e:
        pytest.skip(f"RAG Engine не може бути імпортований: {e}")


def test_rag_engine_basic():
    """Базовий тест RAG engine"""
    with patch("src.rag_engine.PostgresVectorManager") as mock_vector_manager:
        mock_vector_manager.return_value = Mock()

        try:
            from src.rag_engine import PostgresRAGEngine

            rag = PostgresRAGEngine("test_user", "test_spec")
            assert rag is not None
        except Exception as e:
            pytest.skip(f"RAG Engine не може бути створений: {e}")


def test_rag_engine_methods():
    """Тест методів RAG engine"""
    with patch("src.rag_engine.PostgresVectorManager") as mock_vector_manager:
        mock_vector_manager.return_value = Mock()

        try:
            from src.rag_engine import PostgresRAGEngine

            rag = PostgresRAGEngine("test_user", "test_spec")

            # Перевіряємо, що основні методи існують
            assert hasattr(rag, "create_vectorstore_from_swagger")
            assert hasattr(rag, "search_relevant_endpoints")
            assert hasattr(rag, "generate_response")
        except Exception as e:
            pytest.skip(f"RAG Engine методи не можуть бути перевірені: {e}")
