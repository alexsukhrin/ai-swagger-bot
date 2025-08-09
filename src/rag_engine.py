"""
RAG двигун для роботи з API endpoints.
"""

import logging
import os
from typing import Any, Dict, List, Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

from src.enhanced_swagger_parser import EnhancedSwaggerParser
from src.postgres_vector_manager import PostgresVectorManager

logger = logging.getLogger(__name__)


class PostgresRAGEngine:
    """RAG двигун з використанням PostgreSQL та pgvector."""

    def __init__(self, user_id: str, swagger_spec_id: str, config: Dict[str, Any] = None):
        """
        Ініціалізація PostgreSQL RAG двигуна.

        Args:
            user_id: ID користувача
            swagger_spec_id: ID Swagger специфікації
            config: Конфігурація RAG
        """
        from src.config import Config

        self.user_id = user_id
        self.swagger_spec_id = swagger_spec_id
        self.vector_manager = PostgresVectorManager()

        # Використовуємо конфігурацію або значення за замовчуванням
        if config:
            chunk_size = config.get("chunk_size", 1000)
            chunk_overlap = config.get("chunk_overlap", 200)
        else:
            chunk_size = 1000
            chunk_overlap = 200

        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap, separators=["\n\n", "\n", " ", ""]
        )

        logger.info(f"Ініціалізація PostgreSQL RAG Engine для користувача {user_id}")

    def create_vectorstore_from_swagger(self, swagger_spec_path: str) -> bool:
        """
        Створює векторну базу з Swagger специфікації для конкретного користувача.

        Args:
            swagger_spec_path: Шлях до Swagger файлу

        Returns:
            True якщо успішно створено
        """
        try:
            logger.info("Парсинг Swagger специфікації...")
            # Парсимо Swagger файл
            parser = EnhancedSwaggerParser(swagger_spec_path)

            # Використовуємо новий метод для створення chunks
            chunks = parser.create_enhanced_endpoint_chunks()
            logger.info(f"Створено {len(chunks)} chunks")

            # Створюємо векторну базу
            self.create_vectorstore(chunks)
            logger.info("Векторна база створена успішно")
            return True

        except Exception as e:
            logger.error(f"Помилка створення векторної бази: {e}")
            return False

    def create_vectorstore(self, chunks: List[Dict[str, Any]]) -> None:
        """
        Створює векторну базу даних з chunks для конкретного користувача.

        Args:
            chunks: Список chunks з метаданими
        """
        for chunk in chunks:
            try:
                # Створюємо ембедінг для тексту
                embedding = self.embeddings.embed_query(chunk["text"])

                # Додаємо в PostgreSQL з прив'язкою до користувача
                self.vector_manager.add_embedding(
                    user_id=self.user_id,
                    swagger_spec_id=self.swagger_spec_id,
                    endpoint_path=chunk["metadata"].get("path", ""),
                    method=chunk["metadata"].get("method", "GET"),
                    description=chunk["text"],
                    embedding=embedding,
                    metadata=chunk["metadata"],
                )
            except Exception as e:
                logger.error(f"Помилка створення вектора: {e}")
                continue

    def search_similar_endpoints(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Шукає подібні endpoints для конкретного користувача.

        Args:
            query: Пошуковий запит
            limit: Кількість результатів

        Returns:
            Список знайдених endpoints
        """
        try:
            # Створюємо ембедінг для запиту
            query_embedding = self.embeddings.embed_query(query)

            # Шукаємо подібні вектори
            results = self.vector_manager.search_similar(
                query_embedding=query_embedding,
                user_id=self.user_id,
                swagger_spec_id=self.swagger_spec_id,
                limit=limit,
            )

            logger.info(
                f"🔍 Знайдено {len(results)} подібних endpoints для користувача {self.user_id}"
            )
            return results

        except Exception as e:
            logger.error(f"Помилка пошуку endpoints: {e}")
            return []

    def get_all_endpoints(self) -> List[Dict[str, Any]]:
        """
        Отримує всі endpoints для конкретного користувача.

        Returns:
            Список всіх endpoints користувача
        """
        try:
            results = self.vector_manager.get_embeddings_for_user(
                user_id=self.user_id, swagger_spec_id=self.swagger_spec_id
            )

            logger.info(f"📋 Отримано {len(results)} endpoints для користувача {self.user_id}")
            return results

        except Exception as e:
            logger.error(f"Помилка отримання endpoints: {e}")
            return []

    def delete_user_embeddings(self) -> bool:
        """
        Видаляє всі embeddings для конкретного користувача.

        Returns:
            True якщо успішно видалено
        """
        try:
            success = self.vector_manager.delete_embeddings_for_user(
                user_id=self.user_id, swagger_spec_id=self.swagger_spec_id
            )

            if success:
                logger.info(f"✅ Видалено embeddings для користувача {self.user_id}")
            else:
                logger.error(f"❌ Помилка видалення embeddings для користувача {self.user_id}")

            return success

        except Exception as e:
            logger.error(f"Помилка видалення embeddings: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Отримує статистику по embeddings для користувача.

        Returns:
            Словник зі статистикою
        """
        try:
            stats = self.vector_manager.get_statistics(user_id=self.user_id)
            logger.info(f"📊 Статистика для користувача {self.user_id}: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Помилка отримання статистики: {e}")
            return {}
