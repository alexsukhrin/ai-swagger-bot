"""
Менеджер векторів для PostgreSQL з pgvector.
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
from sqlalchemy import text
from sqlalchemy.engine import Engine

from src.config import Config


class PostgresVectorManager:
    """Менеджер векторів для PostgreSQL з pgvector."""

    def __init__(self, engine: Engine = None):
        """
        Ініціалізація менеджера векторів.

        Args:
            engine: SQLAlchemy engine для PostgreSQL
        """
        if engine:
            self.engine = engine
        else:
            from api.database import engine

            self.engine = engine

        # Перевіряємо чи встановлений pgvector
        self._check_pgvector_extension()

        # Створюємо таблицю якщо не існує
        self._create_embeddings_table()

    def _check_pgvector_extension(self):
        """Перевіряє чи встановлений pgvector extension."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM pg_extension WHERE extname = 'vector'"))
                if not result.fetchone():
                    print("⚠️  pgvector extension не встановлений. Встановлюємо...")
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                    conn.commit()
                    print("✅ pgvector extension встановлено")
        except Exception as e:
            print(f"❌ Помилка перевірки pgvector: {e}")
            raise

    def _create_embeddings_table(self):
        """Створює таблицю для embeddings якщо не існує."""
        try:
            with self.engine.connect() as conn:
                # Перевіряємо чи існує таблиця
                result = conn.execute(
                    text(
                        """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'api_embeddings'
                    )
                """
                    )
                )

                if not result.fetchone()[0]:
                    print("🔧 Створення таблиці api_embeddings...")

                    # Створюємо таблицю з новою структурою та констрейнтами
                    conn.execute(
                        text(
                            """
                        CREATE TABLE api_embeddings (
                            id VARCHAR(36) PRIMARY KEY,
                            user_id VARCHAR(36) NOT NULL,
                            swagger_spec_id VARCHAR(36) NOT NULL,
                            endpoint_path VARCHAR(500) NOT NULL,
                            method VARCHAR(10) NOT NULL,
                            description TEXT NOT NULL,
                            embedding TEXT NOT NULL,
                            embedding_metadata JSONB,
                            created_at TIMESTAMP DEFAULT NOW(),
                            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                            FOREIGN KEY (swagger_spec_id) REFERENCES swagger_specs(id) ON DELETE CASCADE,
                            UNIQUE(user_id, swagger_spec_id, endpoint_path, method)
                        )
                    """
                        )
                    )

                    # Створюємо індекси для швидкого пошуку
                    conn.execute(
                        text(
                            """
                        CREATE INDEX idx_api_embeddings_user_id ON api_embeddings(user_id)
                    """
                        )
                    )
                    conn.execute(
                        text(
                            """
                        CREATE INDEX idx_api_embeddings_swagger_spec_id ON api_embeddings(swagger_spec_id)
                    """
                        )
                    )
                    conn.execute(
                        text(
                            """
                        CREATE INDEX idx_api_embeddings_method_path ON api_embeddings(method, endpoint_path)
                    """
                        )
                    )
                    conn.execute(
                        text(
                            """
                        CREATE INDEX idx_api_embeddings_created ON api_embeddings(created_at)
                    """
                        )
                    )
                    conn.execute(
                        text(
                            """
                        CREATE INDEX idx_api_embeddings_user_swagger ON api_embeddings(user_id, swagger_spec_id)
                    """
                        )
                    )

                    conn.commit()
                    print("✅ Таблиця api_embeddings створена з констрейнтами та індексами")
                else:
                    print("✅ Таблиця api_embeddings вже існує")

        except Exception as e:
            print(f"❌ Помилка створення таблиці: {e}")
            raise

    def add_embedding(
        self,
        user_id: str,
        swagger_spec_id: str,
        endpoint_path: str,
        method: str,
        description: str,
        embedding: List[float],
        metadata: Dict[str, Any] = None,
    ) -> str:
        """
        Додає вектор в базу даних з обробкою дублювання.

        Args:
            user_id: ID користувача
            swagger_spec_id: ID Swagger специфікації
            endpoint_path: Шлях до endpoint
            method: HTTP метод
            description: Опис endpoint
            embedding: Вектор (список float)
            metadata: Додаткові метадані

        Returns:
            ID створеного або оновленого запису
        """
        try:
            embedding_json = json.dumps(embedding)

            with self.engine.connect() as conn:
                # Перевіряємо чи існує вже такий embedding
                result = conn.execute(
                    text(
                        """
                    SELECT id FROM api_embeddings
                    WHERE user_id = :user_id
                    AND swagger_spec_id = :swagger_spec_id
                    AND endpoint_path = :endpoint_path
                    AND method = :method
                """
                    ),
                    {
                        "user_id": user_id,
                        "swagger_spec_id": swagger_spec_id,
                        "endpoint_path": endpoint_path,
                        "method": method,
                    },
                )

                existing_record = result.fetchone()

                if existing_record:
                    # Оновлюємо існуючий запис
                    embedding_id = existing_record[0]
                    conn.execute(
                        text(
                            """
                        UPDATE api_embeddings
                        SET description = :description, embedding = :embedding,
                            embedding_metadata = :metadata, created_at = :created_at
                        WHERE id = :id
                    """
                        ),
                        {
                            "id": embedding_id,
                            "description": description,
                            "embedding": embedding_json,
                            "embedding_metadata": json.dumps(metadata) if metadata else None,
                            "created_at": datetime.now().isoformat(),
                        },
                    )
                    print(
                        f"🔄 Оновлено існуючий вектор: {method} {endpoint_path} для користувача {user_id}"
                    )
                else:
                    # Створюємо новий запис
                    embedding_id = str(uuid.uuid4())
                    conn.execute(
                        text(
                            """
                        INSERT INTO api_embeddings
                        (id, user_id, swagger_spec_id, endpoint_path, method, description,
                         embedding, embedding_metadata, created_at)
                        VALUES (:id, :user_id, :swagger_spec_id, :endpoint_path, :method,
                               :description, :embedding, :embedding_metadata, :created_at)
                    """
                        ),
                        {
                            "id": embedding_id,
                            "user_id": user_id,
                            "swagger_spec_id": swagger_spec_id,
                            "endpoint_path": endpoint_path,
                            "method": method,
                            "description": description,
                            "embedding": embedding_json,
                            "embedding_metadata": json.dumps(metadata) if metadata else None,
                            "created_at": datetime.now().isoformat(),
                        },
                    )
                    print(
                        f"✅ Додано новий вектор: {method} {endpoint_path} для користувача {user_id}"
                    )

                conn.commit()
                return embedding_id

        except Exception as e:
            print(f"❌ Помилка додавання вектора: {e}")
            raise

    def search_similar(
        self,
        query_embedding: List[float],
        user_id: str,
        swagger_spec_id: str = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Шукає подібні вектори для конкретного користувача.

        Args:
            query_embedding: Вектор запиту
            user_id: ID користувача
            swagger_spec_id: ID Swagger специфікації (опціонально)
            limit: Кількість результатів

        Returns:
            Список подібних embeddings з метаданими
        """
        try:
            query_embedding_json = json.dumps(query_embedding)

            # Запит з векторним пошуком за косинусною схожістю
            base_query = f"""
                SELECT id, endpoint_path, method, description, embedding, embedding_metadata, created_at,
                       1 - (embedding <=> '{query_embedding_json}'::vector) as similarity
                FROM api_embeddings
                WHERE user_id = :user_id
            """

            params = {"user_id": user_id}

            # Додаємо фільтр по Swagger специфікації якщо вказано
            if swagger_spec_id:
                base_query += " AND swagger_spec_id = :swagger_spec_id"
                params["swagger_spec_id"] = swagger_spec_id

            # Сортуємо по схожості (найбільш схожі спочатку)
            base_query += " ORDER BY similarity DESC LIMIT :limit"
            params["limit"] = limit

            with self.engine.connect() as conn:
                result = conn.execute(text(base_query), params)
                rows = result.fetchall()

                results = []
                for row in rows:
                    # Конвертуємо JSON string назад в список, або використовуємо як є, якщо вже dict/list
                    if row[4]:
                        if isinstance(row[4], str):
                            embedding = json.loads(row[4])
                        else:
                            embedding = row[4]  # Вже список або dict
                    else:
                        embedding = []

                    # Аналогічно для metadata
                    if row[5]:
                        if isinstance(row[5], str):
                            metadata = json.loads(row[5])
                        else:
                            metadata = row[5]  # Вже dict
                    else:
                        metadata = {}

                    results.append(
                        {
                            "id": row[0],
                            "endpoint_path": row[1],
                            "method": row[2],
                            "description": row[3],
                            "embedding": embedding,
                            "metadata": metadata,
                            "created_at": row[6],
                            "similarity": float(row[7]) if row[7] is not None else 0.0,
                        }
                    )

                return results

        except Exception as e:
            print(f"❌ Помилка пошуку подібних векторів: {e}")
            return []

    def get_embeddings_for_user(
        self, user_id: str, swagger_spec_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Отримує всі embeddings для конкретного користувача.

        Args:
            user_id: ID користувача
            swagger_spec_id: ID Swagger специфікації (опціонально)

        Returns:
            Список embeddings
        """
        try:
            base_query = """
                SELECT id, endpoint_path, method, description, embedding, embedding_metadata, created_at
                FROM api_embeddings
                WHERE user_id = :user_id
            """

            params = {"user_id": user_id}

            if swagger_spec_id:
                base_query += " AND swagger_spec_id = :swagger_spec_id"
                params["swagger_spec_id"] = swagger_spec_id

            base_query += " ORDER BY created_at DESC"

            with self.engine.connect() as conn:
                result = conn.execute(text(base_query), params)
                rows = result.fetchall()

                results = []
                for row in rows:
                    # Конвертуємо JSON string назад в список, або використовуємо як є, якщо вже dict/list
                    if row[4]:
                        if isinstance(row[4], str):
                            embedding = json.loads(row[4])
                        else:
                            embedding = row[4]  # Вже список або dict
                    else:
                        embedding = []

                    # Аналогічно для metadata
                    if row[5]:
                        if isinstance(row[5], str):
                            metadata = json.loads(row[5])
                        else:
                            metadata = row[5]  # Вже dict
                    else:
                        metadata = {}

                    results.append(
                        {
                            "id": row[0],
                            "endpoint_path": row[1],
                            "method": row[2],
                            "description": row[3],
                            "embedding": embedding,
                            "metadata": metadata,
                            "created_at": row[6],
                        }
                    )

                return results

        except Exception as e:
            print(f"❌ Помилка отримання embeddings: {e}")
            return []

    def delete_embeddings_for_user(self, user_id: str, swagger_spec_id: str = None) -> bool:
        """
        Видаляє embeddings для конкретного користувача.

        Args:
            user_id: ID користувача
            swagger_spec_id: ID Swagger специфікації (опціонально)

        Returns:
            True якщо успішно видалено
        """
        try:
            base_query = "DELETE FROM api_embeddings WHERE user_id = :user_id"
            params = {"user_id": user_id}

            if swagger_spec_id:
                base_query += " AND swagger_spec_id = :swagger_spec_id"
                params["swagger_spec_id"] = swagger_spec_id

            with self.engine.connect() as conn:
                result = conn.execute(text(base_query), params)
                conn.commit()

                deleted_count = result.rowcount
                print(f"✅ Видалено {deleted_count} embeddings для користувача {user_id}")
                return True

        except Exception as e:
            print(f"❌ Помилка видалення embeddings: {e}")
            return False

    def get_statistics(self, user_id: str = None) -> Dict[str, Any]:
        """
        Отримує статистику по embeddings.

        Args:
            user_id: ID користувача (опціонально)

        Returns:
            Словник зі статистикою
        """
        try:
            with self.engine.connect() as conn:
                if user_id:
                    # Статистика для конкретного користувача
                    result = conn.execute(
                        text(
                            """
                        SELECT
                            COUNT(*) as total_embeddings,
                            COUNT(DISTINCT swagger_spec_id) as swagger_specs_count,
                            COUNT(DISTINCT method) as methods_count,
                            COUNT(DISTINCT endpoint_path) as unique_endpoints
                        FROM api_embeddings
                        WHERE user_id = :user_id
                    """
                        ),
                        {"user_id": user_id},
                    )
                else:
                    # Загальна статистика
                    result = conn.execute(
                        text(
                            """
                        SELECT
                            COUNT(*) as total_embeddings,
                            COUNT(DISTINCT user_id) as users_count,
                            COUNT(DISTINCT swagger_spec_id) as swagger_specs_count,
                            COUNT(DISTINCT method) as methods_count,
                            COUNT(DISTINCT endpoint_path) as unique_endpoints
                        FROM api_embeddings
                    """
                        )
                    )

                row = result.fetchone()

                if user_id:
                    return {
                        "total_embeddings": row[0],
                        "swagger_specs_count": row[1],
                        "methods_count": row[2],
                        "unique_endpoints": row[3],
                    }
                else:
                    return {
                        "total_embeddings": row[0],
                        "users_count": row[1],
                        "swagger_specs_count": row[2],
                        "methods_count": row[3],
                        "unique_endpoints": row[4],
                    }

        except Exception as e:
            print(f"❌ Помилка отримання статистики: {e}")
            return {}

    def cleanup_duplicates(self) -> int:
        """
        Видаляє дублікати embeddings.

        Returns:
            Кількість видалених дублікатів
        """
        try:
            with self.engine.connect() as conn:
                # Знаходимо та видаляємо дублікати, залишаючи найновіший
                result = conn.execute(
                    text(
                        """
                    DELETE FROM api_embeddings
                    WHERE id IN (
                        SELECT id FROM (
                            SELECT id,
                                   ROW_NUMBER() OVER (
                                       PARTITION BY user_id, swagger_spec_id, endpoint_path, method
                                       ORDER BY created_at DESC
                                   ) as rn
                            FROM api_embeddings
                        ) t
                        WHERE t.rn > 1
                    )
                """
                    )
                )

                deleted_count = result.rowcount
                conn.commit()

                if deleted_count > 0:
                    print(f"🧹 Видалено {deleted_count} дублікатів embeddings")
                else:
                    print("✅ Дублікатів не знайдено")

                return deleted_count

        except Exception as e:
            print(f"❌ Помилка очищення дублікатів: {e}")
            return 0
