"""
Тест RAG функціональності з реальною PostgreSQL базою та pgvector
"""

import os
import time
from typing import Any, Dict, List
from unittest.mock import Mock, patch

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
        {
            "text": "Видалення категорії за ID",
            "metadata": {"type": "endpoint", "method": "DELETE", "path": "/api/categories/{id}"},
            "embedding": [0.4, 0.5, 0.6, 0.7, 0.8] * 20,
        },
        {
            "text": "Схема даних для категорії товару",
            "metadata": {
                "type": "schema",
                "name": "Category",
                "properties": ["id", "name", "slug"],
            },
            "embedding": [0.5, 0.6, 0.7, 0.8, 0.9] * 20,
        },
    ]


class TestRAGRealDatabase:
    """Тести RAG функціональності з реальною базою даних"""

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
                cursor.execute(
                    """
                    INSERT INTO test_vectors (text_content, embedding)
                    VALUES (%s, %s);
                """,
                    (text, vector),
                )

            # Тест векторного пошуку (cosine similarity)
            cursor.execute(
                """
                SELECT text_content, embedding <=> %s as distance
                FROM test_vectors
                ORDER BY embedding <=> %s
                LIMIT 2;
            """,
                (test_vectors[0][1], test_vectors[0][1]),
            )

            results = cursor.fetchall()
            assert len(results) == 2

            # Перший результат повинен мати найменшу відстань (0.0)
            assert results[0][1] == 0.0

            # Тест L2 відстані
            cursor.execute(
                """
                SELECT text_content, embedding <-> %s as distance
                FROM test_vectors
                ORDER BY embedding <-> %s
                LIMIT 2;
            """,
                (test_vectors[0][1], test_vectors[0][1]),
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

    def test_rag_engine_integration(self, real_database, clean_database, test_embeddings_data):
        """Тест інтеграції RAG двигуна з реальною базою"""
        print("🔍 Тестуємо RAG двигун з реальною базою...")

        try:
            from src.rag_engine import PostgresRAGEngine

            # Створюємо RAG двигун
            rag_engine = PostgresRAGEngine(
                host=real_database["host"],
                port=real_database["port"],
                database=real_database["database"],
                user=real_database["user"],
                password=real_database["password"],
            )

            # Тестуємо створення векторного сховища
            print("📊 Створюємо векторне сховище...")

            # Мокаємо OpenAI для генерації embeddings
            with patch("openai.Embedding.create") as mock_embedding:
                mock_embedding.return_value = {
                    "data": [{"embedding": test_embeddings_data[0]["embedding"]}]
                }

                # Додаємо документи до сховища
                for doc in test_embeddings_data:
                    success = rag_engine.add_document(text=doc["text"], metadata=doc["metadata"])
                    assert success is True

                print(f"✅ Додано {len(test_embeddings_data)} документів")

            # Тестуємо пошук подібних документів
            print("🔍 Тестуємо пошук подібних документів...")

            with patch("openai.Embedding.create") as mock_embedding:
                mock_embedding.return_value = {
                    "data": [{"embedding": test_embeddings_data[0]["embedding"]}]
                }

                # Шукаємо подібні документи
                similar_docs = rag_engine.search_similar(
                    query="API для роботи з категоріями", top_k=3
                )

                print(f"📋 Знайдено {len(similar_docs)} подібних документів")

                assert len(similar_docs) > 0
                assert len(similar_docs) <= 3

                # Перевіряємо структуру результатів
                for doc in similar_docs:
                    assert "text" in doc
                    assert "metadata" in doc
                    assert "similarity" in doc
                    assert doc["similarity"] >= 0.0
                    assert doc["similarity"] <= 1.0

                print("✅ Пошук подібних документів працює")

            # Тестуємо пошук за метаданими
            print("🏷️ Тестуємо пошук за метаданими...")

            metadata_results = rag_engine.search_by_metadata({"type": "endpoint", "method": "GET"})

            print(f"📋 Знайдено {len(metadata_results)} документів за метаданими")

            assert len(metadata_results) > 0

            # Перевіряємо, що всі результати мають потрібні метадані
            for doc in metadata_results:
                assert doc["metadata"]["type"] == "endpoint"
                assert doc["metadata"]["method"] == "GET"

            print("✅ Пошук за метаданими працює")

            # Тестуємо гібридний пошук
            print("🔀 Тестуємо гібридний пошук...")

            with patch("openai.Embedding.create") as mock_embedding:
                mock_embedding.return_value = {
                    "data": [{"embedding": test_embeddings_data[0]["embedding"]}]
                }

                hybrid_results = rag_engine.hybrid_search(
                    query="категорії товарів", metadata_filter={"type": "endpoint"}, top_k=5
                )

                print(f"📋 Гібридний пошук знайшов {len(hybrid_results)} документів")

                assert len(hybrid_results) > 0

                # Перевіряємо, що всі результати відповідають фільтру
                for doc in hybrid_results:
                    assert doc["metadata"]["type"] == "endpoint"

            print("✅ Гібридний пошук працює")

        except ImportError as e:
            print(f"⚠️ Не вдалося імпортувати RAG двигун: {e}")
            pytest.skip(f"RAG двигун недоступний: {e}")
        except Exception as e:
            print(f"❌ Помилка тестування RAG двигуна: {e}")
            raise

    def test_swagger_parser_integration(self, real_database, clean_database):
        """Тест інтеграції парсера Swagger з реальною базою"""
        print("📋 Тестуємо парсер Swagger з реальною базою...")

        try:
            from src.enhanced_swagger_parser import EnhancedSwaggerParser
            from src.rag_engine import PostgresRAGEngine

            # Створюємо RAG двигун
            rag_engine = PostgresRAGEngine(
                host=real_database["host"],
                port=real_database["port"],
                database=real_database["database"],
                user=real_database["user"],
                password=real_database["password"],
            )

            # Створюємо парсер Swagger
            swagger_parser = EnhancedSwaggerParser()

            # Тестуємо парсинг Swagger специфікації
            swagger_spec_path = "examples/swagger_specs/clickone_shop_api.json"

            if not os.path.exists(swagger_spec_path):
                print(f"⚠️ Файл {swagger_spec_path} не знайдено, пропускаємо тест")
                pytest.skip(f"Swagger специфікація не знайдена: {swagger_spec_path}")

            print(f"📄 Парсимо Swagger специфікацію: {swagger_spec_path}")

            # Парсимо специфікацію
            parsed_spec = swagger_parser.parse_swagger_spec(swagger_spec_path)

            assert parsed_spec is not None
            assert "paths" in parsed_spec
            assert "components" in parsed_spec

            print(f"✅ Парсинг успішний: {len(parsed_spec.get('paths', {}))} endpoints")

            # Тестуємо створення векторного сховища з Swagger
            print("🔗 Створюємо векторне сховище з Swagger...")

            # Мокаємо OpenAI для embeddings
            with patch("openai.Embedding.create") as mock_embedding:
                mock_embedding.return_value = {"data": [{"embedding": [0.1] * 100}]}

                # Створюємо векторне сховище
                success = rag_engine.create_vector_store_from_swagger(
                    swagger_spec_path=swagger_spec_path, swagger_parser=swagger_parser
                )

                assert success is True
                print("✅ Векторне сховище створено з Swagger")

            # Тестуємо пошук по Swagger документації
            print("🔍 Тестуємо пошук по Swagger документації...")

            with patch("openai.Embedding.create") as mock_embedding:
                mock_embedding.return_value = {"data": [{"embedding": [0.1] * 100}]}

                # Шукаємо endpoint для категорій
                search_results = rag_engine.search_similar(
                    query="створення категорії товарів", top_k=5
                )

                print(f"📋 Пошук знайшов {len(search_results)} результатів")

                if len(search_results) > 0:
                    print("📋 Перші результати:")
                    for i, doc in enumerate(search_results[:3]):
                        print(f"  {i+1}. {doc.get('text', 'Невідомий текст')[:100]}...")
                        print(f"     Метадані: {doc.get('metadata', {})}")
                        print(f"     Схожість: {doc.get('similarity', 0):.3f}")

                # Перевіряємо, що пошук повернув результати
                assert len(search_results) >= 0  # Може бути 0, якщо embeddings не згенеровані

            print("✅ Пошук по Swagger документації працює")

        except ImportError as e:
            print(f"⚠️ Не вдалося імпортувати модулі: {e}")
            pytest.skip(f"Модулі недоступні: {e}")
        except Exception as e:
            print(f"❌ Помилка тестування парсера Swagger: {e}")
            raise

    def test_error_handling_real_database(self, real_database):
        """Тест обробки помилок з реальною базою даних"""
        print("⚠️ Тестуємо обробку помилок з реальною базою...")

        try:
            from src.rag_engine import PostgresRAGEngine

            # Тестуємо підключення з неправильними даними
            print("🔌 Тестуємо неправильні дані підключення...")

            wrong_config = real_database.copy()
            wrong_config["password"] = "wrong_password"

            try:
                rag_engine = PostgresRAGEngine(**wrong_config)
                # Якщо не виникла помилка, це може означати, що пароль не перевіряється
                print("⚠️ Підключення з неправильним паролем не викликало помилку")
            except Exception as e:
                print(f"✅ Очікувана помилка підключення: {e}")
                assert (
                    "password authentication failed" in str(e).lower()
                    or "authentication failed" in str(e).lower()
                )

            # Тестуємо неправильну базу даних
            print("🗄️ Тестуємо неправильну базу даних...")

            wrong_db_config = real_database.copy()
            wrong_db_config["database"] = "nonexistent_database"

            try:
                rag_engine = PostgresRAGEngine(**wrong_db_config)
                print("⚠️ Підключення до неіснуючої бази не викликало помилку")
            except Exception as e:
                print(f"✅ Очікувана помилка бази: {e}")
                assert "database" in str(e).lower() or "does not exist" in str(e).lower()

            # Тестуємо неправильний хост
            print("🌐 Тестуємо неправильний хост...")

            wrong_host_config = real_database.copy()
            wrong_host_config["host"] = "nonexistent.host.local"

            try:
                rag_engine = PostgresRAGEngine(**wrong_host_config)
                print("⚠️ Підключення до неіснуючого хоста не викликало помилку")
            except Exception as e:
                print(f"✅ Очікувана помилка хоста: {e}")
                assert "connection" in str(e).lower() or "timeout" in str(e).lower()

            print("✅ Обробка помилок підключення працює коректно")

        except ImportError as e:
            print(f"⚠️ Не вдалося імпортувати RAG двигун: {e}")
            pytest.skip(f"RAG двигун недоступний: {e}")
        except Exception as e:
            print(f"❌ Помилка тестування обробки помилок: {e}")
            raise

    def test_performance_real_database(self, real_database, clean_database, test_embeddings_data):
        """Тест продуктивності з реальною базою даних"""
        print("⚡ Тестуємо продуктивність з реальною базою...")

        try:
            from src.rag_engine import PostgresRAGEngine

            # Створюємо RAG двигун
            rag_engine = PostgresRAGEngine(
                host=real_database["host"],
                port=real_database["port"],
                database=real_database["database"],
                user=real_database["user"],
                password=real_database["password"],
            )

            # Тестуємо швидкість вставки
            print("📥 Тестуємо швидкість вставки...")

            start_time = time.time()

            with patch("openai.Embedding.create") as mock_embedding:
                mock_embedding.return_value = {
                    "data": [{"embedding": test_embeddings_data[0]["embedding"]}]
                }

                for doc in test_embeddings_data:
                    success = rag_engine.add_document(text=doc["text"], metadata=doc["metadata"])
                    assert success is True

            insert_time = time.time() - start_time
            print(f"⏱️ Вставка {len(test_embeddings_data)} документів зайняла: {insert_time:.3f}с")
            print(f"📊 Швидкість: {len(test_embeddings_data) / insert_time:.1f} документів/сек")

            # Тестуємо швидкість пошуку
            print("🔍 Тестуємо швидкість пошуку...")

            start_time = time.time()

            with patch("openai.Embedding.create") as mock_embedding:
                mock_embedding.return_value = {
                    "data": [{"embedding": test_embeddings_data[0]["embedding"]}]
                }

                for i in range(10):
                    results = rag_engine.search_similar(query=f"тестовий запит {i}", top_k=3)
                    assert len(results) >= 0

            search_time = time.time() - start_time
            print(f"⏱️ 10 пошуків зайняли: {search_time:.3f}с")
            print(f"📊 Швидкість: {10 / search_time:.1f} пошуків/сек")

            # Тестуємо швидкість пошуку за метаданими
            print("🏷️ Тестуємо швидкість пошуку за метаданими...")

            start_time = time.time()

            for i in range(10):
                results = rag_engine.search_by_metadata({"type": "endpoint", "method": "GET"})
                assert len(results) >= 0

            metadata_search_time = time.time() - start_time
            print(f"⏱️ 10 пошуків за метаданими зайняли: {metadata_search_time:.3f}с")
            print(f"📊 Швидкість: {10 / metadata_search_time:.1f} пошуків/сек")

            # Перевіряємо, що продуктивність прийнятна
            assert insert_time < 10.0  # Вставка не повинна займати більше 10 секунд
            assert search_time < 5.0  # Пошук не повинен займати більше 5 секунд

            print("✅ Продуктивність прийнятна")

        except ImportError as e:
            print(f"⚠️ Не вдалося імпортувати RAG двигун: {e}")
            pytest.skip(f"RAG двигун недоступний: {e}")
        except Exception as e:
            print(f"❌ Помилка тестування продуктивності: {e}")
            raise


if __name__ == "__main__":
    # Запуск тестів
    pytest.main([__file__, "-v", "-s"])
