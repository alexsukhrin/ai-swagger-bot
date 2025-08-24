"""
Простий тест RAG функціональності з реальною PostgreSQL базою та pgvector
Використовує тільки psycopg2 для прямого підключення
"""

import os
import time
from typing import Any, Dict, List

import psycopg2
import pytest
from psycopg2.extras import RealDictCursor

# Налаштування реальної бази даних
REAL_DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "database": os.getenv("POSTGRES_DB", "ai_swagger_bot_test"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "password"),
}


@pytest.fixture(scope="session")
def real_database():
    """Створює реальне з'єднання з базою даних"""
    print("🗄️ Підключення до реальної PostgreSQL бази...")

    try:
        # Тестуємо підключення
        conn = psycopg2.connect(**REAL_DB_CONFIG)
        cursor = conn.cursor()

        # Перевіряємо версію PostgreSQL
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Підключено до PostgreSQL: {version}")

        # Перевіряємо pgvector розширення
        cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
        vector_ext = cursor.fetchone()

        if vector_ext:
            print("✅ Розширення pgvector встановлено")
        else:
            print("⚠️ Розширення pgvector не знайдено")

        cursor.close()
        conn.close()

        return REAL_DB_CONFIG

    except Exception as e:
        print(f"❌ Помилка підключення до бази: {e}")
        pytest.skip(f"Не вдалося підключитися до бази: {e}")


@pytest.fixture
def clean_database(real_database):
    """Очищає базу даних перед кожним тестом"""
    print("🧹 Очищення бази даних...")

    conn = psycopg2.connect(**real_database)
    cursor = conn.cursor()

    try:
        # Видаляємо тестові дані
        cursor.execute(
            """
            DROP TABLE IF EXISTS test_embeddings CASCADE;
            DROP TABLE IF EXISTS test_documents CASCADE;
            DROP TABLE IF EXISTS test_swagger_specs CASCADE;
        """
        )

        conn.commit()
        print("✅ База очищена")

    except Exception as e:
        print(f"⚠️ Помилка очищення: {e}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()


@pytest.fixture
def test_embeddings_data():
    """Тестові дані для embeddings"""
    return [
        {
            "text": "API для створення категорій товарів",
            "metadata": {"type": "endpoint", "method": "POST", "path": "/api/categories"},
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5] * 20,  # 100-вимірний вектор
        },
        {
            "text": "Отримання списку всіх категорій",
            "metadata": {"type": "endpoint", "method": "GET", "path": "/api/categories"},
            "embedding": [0.2, 0.3, 0.4, 0.5, 0.6] * 20,
        },
        {
            "text": "Оновлення існуючої категорії",
            "metadata": {"type": "endpoint", "method": "PATCH", "path": "/api/categories/{id}"},
            "embedding": [0.3, 0.4, 0.5, 0.6, 0.7] * 20,
        },
    ]


class TestRAGRealDatabaseSimple:
    """Простий тест RAG функціональності з реальною базою даних"""

    def test_database_connection(self, real_database):
        """Тест підключення до бази даних"""
        print("🔌 Тестуємо підключення до бази...")

        conn = psycopg2.connect(**real_database)
        cursor = conn.cursor()

        try:
            # Тест базових операцій
            cursor.execute("SELECT 1;")
            result = cursor.fetchone()
            assert result[0] == 1

            # Тест створення таблиці
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS test_connection (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
            )

            # Тест вставки даних
            cursor.execute(
                """
                INSERT INTO test_connection (name) VALUES (%s) RETURNING id;
            """,
                ("Test Connection",),
            )

            inserted_id = cursor.fetchone()[0]
            assert inserted_id > 0

            # Тест читання даних
            cursor.execute("SELECT name FROM test_connection WHERE id = %s;", (inserted_id,))
            name = cursor.fetchone()[0]
            assert name == "Test Connection"

            # Тест видалення таблиці
            cursor.execute("DROP TABLE test_connection;")

            conn.commit()
            print("✅ Підключення до бази працює коректно")

        except Exception as e:
            print(f"❌ Помилка тестування бази: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def test_pgvector_extension(self, real_database):
        """Тест роботи pgvector розширення"""
        print("🔢 Тестуємо pgvector розширення...")

        conn = psycopg2.connect(**real_database)
        cursor = conn.cursor()

        try:
            # Перевіряємо, чи встановлено розширення
            cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
            vector_ext = cursor.fetchone()

            if not vector_ext:
                print("⚠️ pgvector не встановлено, пропускаємо тест")
                pytest.skip("pgvector розширення не встановлено")

            # Створюємо тестову таблицю з векторним полем
            cursor.execute(
                """
                CREATE TABLE test_vectors (
                    id SERIAL PRIMARY KEY,
                    text_content TEXT,
                    embedding vector(100)
                );
            """
            )

            # Вставляємо тестові вектори
            test_vectors = [
                ("API для категорій", [0.1, 0.2, 0.3, 0.4, 0.5] * 20),
                ("Отримання категорій", [0.2, 0.3, 0.4, 0.5, 0.6] * 20),
                ("Оновлення категорій", [0.3, 0.4, 0.5, 0.6, 0.7] * 20),
            ]

            for text, vector in test_vectors:
                # Конвертуємо список в vector тип PostgreSQL
                vector_str = f"[{','.join(map(str, vector))}]"
                cursor.execute(
                    """
                    INSERT INTO test_vectors (text_content, embedding)
                    VALUES (%s, %s::vector);
                """,
                    (text, vector_str),
                )

            # Тест векторного пошуку (cosine similarity)
            query_vector = test_vectors[0][1]
            query_vector_str = f"[{','.join(map(str, query_vector))}]"
            cursor.execute(
                """
                SELECT text_content, embedding <=> %s::vector as distance
                FROM test_vectors
                ORDER BY embedding <=> %s::vector
                LIMIT 2;
            """,
                (query_vector_str, query_vector_str),
            )

            results = cursor.fetchall()
            assert len(results) == 2

            # Перший результат повинен мати найменшу відстань (0.0)
            assert results[0][1] == 0.0

            # Тест L2 відстані
            cursor.execute(
                """
                SELECT text_content, embedding <-> %s::vector as distance
                FROM test_vectors
                ORDER BY embedding <-> %s::vector
                LIMIT 2;
            """,
                (query_vector_str, query_vector_str),
            )

            l2_results = cursor.fetchall()
            assert len(l2_results) == 2

            # Видаляємо тестову таблицю
            cursor.execute("DROP TABLE test_vectors;")

            conn.commit()
            print("✅ pgvector працює коректно")

        except Exception as e:
            print(f"❌ Помилка тестування pgvector: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def test_simple_rag_operations(self, real_database, clean_database, test_embeddings_data):
        """Простий тест RAG операцій"""
        print("🔍 Тестуємо прості RAG операції...")

        conn = psycopg2.connect(**real_database)
        cursor = conn.cursor()

        try:
            # Створюємо таблицю для embeddings
            cursor.execute(
                """
                CREATE TABLE test_embeddings (
                    id SERIAL PRIMARY KEY,
                    text_content TEXT NOT NULL,
                    metadata JSONB,
                    embedding vector(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
            )

            # Вставляємо тестові дані
            for doc in test_embeddings_data:
                vector_str = f"[{','.join(map(str, doc['embedding']))}]"
                cursor.execute(
                    """
                    INSERT INTO test_embeddings (text_content, metadata, embedding)
                    VALUES (%s, %s, %s::vector);
                """,
                    (doc["text"], psycopg2.extras.Json(doc["metadata"]), vector_str),
                )

            print(f"✅ Вставлено {len(test_embeddings_data)} документів")

            # Тестуємо пошук подібних документів
            query_embedding = test_embeddings_data[0]["embedding"]
            query_vector_str = f"[{','.join(map(str, query_embedding))}]"

            cursor.execute(
                """
                SELECT text_content, metadata, embedding <=> %s as similarity
                FROM test_embeddings
                ORDER BY embedding <=> %s
                LIMIT 3;
            """,
                (query_vector_str, query_vector_str),
            )

            results = cursor.fetchall()
            print(f"📋 Знайдено {len(results)} подібних документів")

            assert len(results) > 0
            assert len(results) <= 3

            # Перевіряємо структуру результатів
            for doc in results:
                assert len(doc) == 3  # text_content, metadata, similarity
                assert doc[2] >= 0.0  # similarity >= 0
                assert doc[2] <= 1.0  # similarity <= 1

            print("✅ Пошук подібних документів працює")

            # Тестуємо пошук за метаданими
            cursor.execute(
                """
                SELECT text_content, metadata
                FROM test_embeddings
                WHERE metadata->>'method' = 'GET';
            """
            )

            metadata_results = cursor.fetchall()
            print(f"📋 Знайдено {len(metadata_results)} документів за метаданими")

            assert len(metadata_results) > 0

            # Перевіряємо, що всі результати мають потрібні метадані
            for doc in metadata_results:
                assert doc[1]["method"] == "GET"

            print("✅ Пошук за метаданими працює")

            # Видаляємо тестову таблицю
            cursor.execute("DROP TABLE test_embeddings;")

            conn.commit()
            print("✅ Прості RAG операції працюють коректно")

        except Exception as e:
            print(f"❌ Помилка тестування RAG операцій: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def test_performance_simple(self, real_database, clean_database, test_embeddings_data):
        """Тест продуктивності простих операцій"""
        print("⚡ Тестуємо продуктивність простих операцій...")

        conn = psycopg2.connect(**real_database)
        cursor = conn.cursor()

        try:
            # Створюємо таблицю для embeddings
            cursor.execute(
                """
                CREATE TABLE test_embeddings (
                    id SERIAL PRIMARY KEY,
                    text_content TEXT NOT NULL,
                    metadata JSONB,
                    embedding vector(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
            )

            # Тестуємо швидкість вставки
            print("📥 Тестуємо швидкість вставки...")

            start_time = time.time()

            for doc in test_embeddings_data:
                vector_str = f"[{','.join(map(str, doc['embedding']))}]"
                cursor.execute(
                    """
                    INSERT INTO test_embeddings (text_content, metadata, embedding)
                    VALUES (%s, %s, %s::vector);
                """,
                    (doc["text"], psycopg2.extras.Json(doc["metadata"]), vector_str),
                )

            insert_time = time.time() - start_time
            print(f"⏱️ Вставка {len(test_embeddings_data)} документів зайняла: {insert_time:.3f}с")
            print(f"📊 Швидкість: {len(test_embeddings_data) / insert_time:.1f} документів/сек")

            # Тестуємо швидкість пошуку
            print("🔍 Тестуємо швидкість пошуку...")

            start_time = time.time()

            query_embedding = test_embeddings_data[0]["embedding"]
            query_vector_str = f"[{','.join(map(str, query_embedding))}]"

            for i in range(10):
                cursor.execute(
                    """
                    SELECT text_content, embedding <=> %s as similarity
                    FROM test_embeddings
                    ORDER BY embedding <=> %s
                    LIMIT 3;
                """,
                    (query_vector_str, query_vector_str),
                )
                results = cursor.fetchall()
                assert len(results) >= 0

            search_time = time.time() - start_time
            print(f"⏱️ 10 пошуків зайняли: {search_time:.3f}с")
            print(f"📊 Швидкість: {10 / search_time:.1f} пошуків/сек")

            # Перевіряємо, що продуктивність прийнятна
            assert insert_time < 10.0  # Вставка не повинна займати більше 10 секунд
            assert search_time < 5.0  # Пошук не повинен займати більше 5 секунд

            # Видаляємо тестову таблицю
            cursor.execute("DROP TABLE test_embeddings;")

            conn.commit()
            print("✅ Продуктивність прийнятна")

        except Exception as e:
            print(f"❌ Помилка тестування продуктивності: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()


if __name__ == "__main__":
    # Запуск тестів
    pytest.main([__file__, "-v", "-s"])
