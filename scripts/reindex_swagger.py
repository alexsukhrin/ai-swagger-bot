#!/usr/bin/env python3
"""
Скрипт для переіндексації Swagger файлів.
Використовується після очищення бази даних.
"""

import os
import sys
from pathlib import Path

# Додаємо кореневу директорію до шляху
sys.path.append(str(Path(__file__).parent.parent))

from src.enhanced_swagger_parser import EnhancedSwaggerParser
from src.rag_engine import RAGEngine


def reindex_swagger_files():
    """Переіндексує всі Swagger файли."""
    print("🔄 Переіндексація Swagger файлів")
    print("=" * 50)

    # Шлях до Swagger файлів
    swagger_dir = Path("examples/swagger_specs")

    if not swagger_dir.exists():
        print(f"❌ Директорія не знайдена: {swagger_dir}")
        return

    # Знаходимо всі JSON файли
    swagger_files = list(swagger_dir.glob("*.json"))

    if not swagger_files:
        print(f"❌ Swagger файли не знайдено в {swagger_dir}")
        return

    print(f"📁 Знайдено {len(swagger_files)} Swagger файлів:")
    for file in swagger_files:
        print(f"   • {file.name}")

    # Індексуємо кожен файл
    for swagger_file in swagger_files:
        print(f"\n🔄 Індексація: {swagger_file.name}")

        try:
            # Створюємо парсер для конкретного файлу
            parser = EnhancedSwaggerParser(str(swagger_file))

            # Створюємо RAG двигун для конкретного файлу
            rag_engine = RAGEngine(str(swagger_file))

            # Парсимо Swagger файл та створюємо chunks
            chunks = parser.create_enhanced_endpoint_chunks()

            if chunks:
                # Створюємо векторну базу з chunks
                rag_engine.create_vectorstore(chunks)
                print(f"✅ Успішно індексовано: {swagger_file.name} ({len(chunks)} endpoints)")
            else:
                print(f"❌ Не знайдено endpoints в: {swagger_file.name}")

        except Exception as e:
            print(f"❌ Помилка індексації {swagger_file.name}: {e}")

    print("\n✅ Переіндексація завершена!")
    print("💡 Тепер можна запускати чат-інтерфейс")


def main():
    """Основний функція переіндексації."""
    print("🔄 ПЕРЕІНДЕКСАЦІЯ SWAGGER ФАЙЛІВ")
    print("=" * 50)

    reindex_swagger_files()


if __name__ == "__main__":
    main()
