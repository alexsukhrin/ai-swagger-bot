#!/usr/bin/env python3
"""
Скрипт для міграції з ChromaDB на pgvector
"""

import logging
import os
import sys
from typing import Any, Dict, List

# Додаємо корінь проекту до шляху
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Встановлюємо правильний DATABASE_URL для локального тестування
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@127.0.0.1:5432/ai_swagger_bot"

from src.config import Config
from src.postgres_vector_manager import PostgresVectorManager
from src.rag_engine import RAGEngine

# Налаштовуємо логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_chromadb_to_pgvector():
    """Мігрує дані з ChromaDB в pgvector."""
    print("🔄 Міграція з ChromaDB на pgvector...")

    try:
        # Створюємо PostgreSQL менеджер
        pg_manager = PostgresVectorManager()

        # Створюємо ChromaDB RAG Engine для читання даних
        chroma_rag = RAGEngine(
            swagger_spec_path=Config.SWAGGER_SPEC_PATH, persist_directory=Config.CHROMA_DB_PATH
        )

        # Отримуємо всі дані з ChromaDB
        print("📖 Читаємо дані з ChromaDB...")

        # Створюємо новий RAG Engine з ChromaDB для експорту
        from src.rag_engine import RAGEngine as ChromaRAGEngine

        # Тимчасово вимикаємо pgvector
        original_use_pgvector = Config.USE_PGVECTOR
        Config.USE_PGVECTOR = False

        chroma_engine = ChromaRAGEngine(
            swagger_spec_path=Config.SWAGGER_SPEC_PATH, persist_directory=Config.CHROMA_DB_PATH
        )

        # Отримуємо всі endpoints
        all_endpoints = chroma_engine.vectorstore.get()

        if not all_endpoints["ids"]:
            print("⚠️ ChromaDB порожня, немає що мігрувати")
            return True

        print(f"📦 Знайдено {len(all_endpoints['ids'])} векторів для міграції")

        # Мігруємо кожен вектор
        migrated_count = 0
        for i, doc_id in enumerate(all_endpoints["ids"]):
            try:
                # Отримуємо дані
                embedding = all_endpoints["embeddings"][i]
                metadata = all_endpoints["metadatas"][i]
                document = all_endpoints["documents"][i]

                # Парсимо метадані
                method = metadata.get("method", "GET")
                path = metadata.get("path", "")
                description = metadata.get("description", document)

                # Додаємо в PostgreSQL
                pg_manager.add_embedding(
                    endpoint_path=path,
                    method=method,
                    description=description,
                    embedding=embedding,
                    metadata=metadata,
                )

                migrated_count += 1
                if migrated_count % 10 == 0:
                    print(f"✅ Мігровано {migrated_count}/{len(all_endpoints['ids'])} векторів")

            except Exception as e:
                print(f"⚠️ Помилка міграції вектора {i}: {e}")
                continue

        # Відновлюємо налаштування
        Config.USE_PGVECTOR = original_use_pgvector

        print(f"✅ Успішно мігровано {migrated_count} векторів")

        # Перевіряємо результат
        info = pg_manager.get_embeddings_info()
        print(f"📊 PostgreSQL база: {info.get('total_embeddings', 0)} векторів")

        return True

    except Exception as e:
        print(f"❌ Помилка міграції: {e}")
        return False


def cleanup_chromadb():
    """Видаляє ChromaDB файли."""
    print("🗑️ Видалення ChromaDB файлів...")

    try:
        chroma_path = Config.CHROMA_DB_PATH

        if os.path.exists(chroma_path):
            import shutil

            shutil.rmtree(chroma_path)
            print(f"✅ Видалено директорію: {chroma_path}")
        else:
            print(f"ℹ️ Директорія не існує: {chroma_path}")

        return True

    except Exception as e:
        print(f"❌ Помилка видалення ChromaDB: {e}")
        return False


def update_dependencies():
    """Оновлює залежності проекту."""
    print("📦 Оновлення залежностей...")

    try:
        # Видаляємо ChromaDB з requirements.txt
        requirements_file = "requirements.txt"

        if os.path.exists(requirements_file):
            with open(requirements_file, "r") as f:
                lines = f.readlines()

            # Фільтруємо ChromaDB залежності
            filtered_lines = []
            for line in lines:
                if not any(chroma_dep in line.lower() for chroma_dep in ["chromadb", "chroma"]):
                    filtered_lines.append(line)

            # Записуємо оновлений файл
            with open(requirements_file, "w") as f:
                f.writelines(filtered_lines)

            print("✅ Оновлено requirements.txt")

        return True

    except Exception as e:
        print(f"❌ Помилка оновлення залежностей: {e}")
        return False


def main():
    """Основний процес міграції."""
    print("🚀 Міграція з ChromaDB на pgvector")
    print("=" * 50)

    # Етап 1: Міграція даних
    print("\n📋 Етап 1: Міграція даних")
    if not migrate_chromadb_to_pgvector():
        print("❌ Міграція невдала")
        return False

    # Етап 2: Видалення ChromaDB
    print("\n📋 Етап 2: Видалення ChromaDB")
    if not cleanup_chromadb():
        print("⚠️ Помилка видалення ChromaDB")

    # Етап 3: Оновлення залежностей
    print("\n📋 Етап 3: Оновлення залежностей")
    if not update_dependencies():
        print("⚠️ Помилка оновлення залежностей")

    print("\n" + "=" * 50)
    print("✅ Міграція завершена успішно!")
    print("\n🎯 Наступні кроки:")
    print("1. Перезапустіть додаток")
    print("2. Протестуйте функціональність")
    print("3. Видаліть тестові файли ChromaDB")

    return True


if __name__ == "__main__":
    main()
