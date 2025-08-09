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

    def create_vectorstore_from_swagger(
        self, swagger_spec_path: str, enable_gpt_enhancement: bool = True
    ) -> bool:
        """
        Створює векторну базу з Swagger специфікації для конкретного користувача.
        Опціонально використовує GPT для покращення якості embeddings.

        Args:
            swagger_spec_path: Шлях до Swagger файлу
            enable_gpt_enhancement: Чи використовувати GPT для покращення

        Returns:
            True якщо успішно створено
        """
        try:
            logger.info("Парсинг Swagger специфікації...")
            # Парсимо Swagger файл
            parser = EnhancedSwaggerParser(swagger_spec_path)

            # Використовуємо новий метод для створення chunks
            chunks = parser.create_enhanced_endpoint_chunks()
            logger.info(f"Створено {len(chunks)} базових chunks")

            # GPT покращення (опціонально)
            if enable_gpt_enhancement:
                try:
                    # Перевіряємо чи є swagger_data у parser
                    if hasattr(parser, "swagger_data") and parser.swagger_data:
                        enhanced_chunks, gpt_prompts = self._enhance_chunks_with_gpt(
                            chunks, parser.swagger_data
                        )
                        if enhanced_chunks and gpt_prompts:
                            chunks = enhanced_chunks
                            logger.info(
                                f"✨ Покращено за допомогою GPT: {len(chunks)} chunks, {len(gpt_prompts)} промптів"
                            )

                            # Зберігаємо GPT-генеровані промпти
                            self._save_gpt_prompts(gpt_prompts)
                        else:
                            logger.warning(
                                "⚠️ GPT enhancement не дав результатів, використовуємо базові chunks"
                            )
                    else:
                        logger.warning("⚠️ Swagger data недоступна для GPT аналізу")
                except Exception as gpt_error:
                    logger.warning(
                        f"⚠️ GPT enhancement недоступний: {gpt_error}. Продовжуємо з базовими chunks"
                    )
                    # Продовжуємо з базовими chunks

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
                # Використовуємо full_url (base URL + path) замість тільки path
                endpoint_path = chunk["metadata"].get("full_url", chunk["metadata"].get("path", ""))
                self.vector_manager.add_embedding(
                    user_id=self.user_id,
                    swagger_spec_id=self.swagger_spec_id,
                    endpoint_path=endpoint_path,
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

    def _enhance_chunks_with_gpt(
        self, chunks: List[Dict[str, Any]], swagger_data: Dict[str, Any]
    ) -> tuple[List[Dict[str, Any]], List]:
        """
        Збагачує chunks за допомогою GPT-аналізу.

        Args:
            chunks: Базові chunks від parser
            swagger_data: Оригінальні дані Swagger

        Returns:
            Tuple: (покращені chunks, список GPT промптів)
        """
        try:
            from src.gpt_prompt_generator import GPTPromptGenerator

            # Ініціалізуємо GPT генератор
            gpt_generator = GPTPromptGenerator()

            # Генеруємо промпти для всіх endpoint'ів
            logger.debug(f"Передаємо swagger_data типу {type(swagger_data)} до GPT generator")
            gpt_prompts = gpt_generator.generate_prompts_from_swagger(swagger_data)

            if not gpt_prompts:
                logger.warning("GPT не згенерував промптів")
                return chunks, []

            enhanced_chunks = []

            for chunk in chunks:
                # Знаходимо відповідний GPT промпт
                matching_prompt = self._find_matching_gpt_prompt(chunk, gpt_prompts)

                if matching_prompt:
                    # Збагачуємо chunk GPT insights
                    enhanced_text = self._create_enhanced_chunk_text(chunk, matching_prompt)

                    chunk["text"] = enhanced_text
                    chunk["metadata"]["gpt_enhanced"] = True
                    chunk["metadata"]["gpt_prompt_id"] = matching_prompt.id
                    chunk["metadata"]["gpt_insights"] = True

                enhanced_chunks.append(chunk)

            logger.info(
                f"✨ GPT збагатив {len([c for c in enhanced_chunks if c['metadata'].get('gpt_enhanced')])} chunks"
            )
            return enhanced_chunks, gpt_prompts

        except Exception as e:
            logger.error(f"Помилка GPT покращення: {e}")
            import traceback

            logger.error(f"Traceback: {traceback.format_exc()}")
            return chunks, []

    def _find_matching_gpt_prompt(self, chunk: Dict[str, Any], gpt_prompts: List) -> any:
        """Знаходить відповідний GPT промпт для chunk."""
        try:
            chunk_path = chunk["metadata"].get("path", "")
            chunk_method = chunk["metadata"].get("method", "").upper()

            for prompt in gpt_prompts:
                if (
                    prompt.endpoint_path == chunk_path
                    and prompt.http_method.upper() == chunk_method
                ):
                    return prompt

            return None

        except Exception as e:
            logger.error(f"Помилка пошуку GPT промпту: {e}")
            return None

    def _create_enhanced_chunk_text(self, chunk: Dict[str, Any], gpt_prompt) -> str:
        """Створює збагачений текст chunk з GPT insights."""
        try:
            original_text = chunk["text"]

            # Додаємо GPT аналіз та контекст
            enhanced_parts = [
                original_text,
                "\n--- GPT Analysis ---",
                f"Smart Description: {gpt_prompt.description}",
                (
                    f"Use Cases: {gpt_prompt.template[:200]}..."
                    if len(gpt_prompt.template) > 200
                    else gpt_prompt.template
                ),
                f"Resource Type: {gpt_prompt.resource_type}",
                f"Category: {gpt_prompt.category}",
            ]

            if hasattr(gpt_prompt, "tags") and gpt_prompt.tags:
                enhanced_parts.append(f"Tags: {', '.join(gpt_prompt.tags)}")

            return "\n".join(enhanced_parts)

        except Exception as e:
            logger.error(f"Помилка створення збагаченого тексту: {e}")
            return chunk["text"]

    def _save_gpt_prompts(self, gpt_prompts: List) -> bool:
        """
        Зберігає GPT-генеровані промпти в базу даних.

        Args:
            gpt_prompts: Список GPT промптів

        Returns:
            True якщо успішно збережено
        """
        try:
            import uuid
            from datetime import datetime

            from api.database import get_db
            from api.models import PromptTemplate

            # Отримуємо сесію бази даних
            db = next(get_db())

            saved_count = 0

            for gpt_prompt in gpt_prompts:
                try:
                    # Створюємо новий промпт
                    db_prompt = PromptTemplate(
                        id=str(uuid.uuid4()),
                        user_id=self.user_id,
                        swagger_spec_id=self.swagger_spec_id,
                        name=gpt_prompt.name,
                        description=gpt_prompt.description,
                        template=gpt_prompt.template,
                        category=gpt_prompt.category,
                        endpoint_path=gpt_prompt.endpoint_path,
                        http_method=gpt_prompt.http_method,
                        resource_type=gpt_prompt.resource_type,
                        tags=gpt_prompt.tags if hasattr(gpt_prompt, "tags") else [],
                        source="gpt_generated",
                        priority=getattr(gpt_prompt, "priority", 1),
                        is_public=False,
                        is_active=True,
                        usage_count=0,
                        success_rate=0,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                    )

                    db.add(db_prompt)
                    saved_count += 1

                except Exception as e:
                    logger.warning(f"Не вдалося зберегти промпт {gpt_prompt.name}: {e}")
                    continue

            db.commit()
            db.close()

            logger.info(f"💾 Збережено {saved_count} GPT промптів для користувача {self.user_id}")
            return True

        except Exception as e:
            logger.error(f"Помилка збереження GPT промптів: {e}")
            return False
