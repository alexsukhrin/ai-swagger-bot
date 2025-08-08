#!/usr/bin/env python3
"""
Скрипт для безпечного видалення SQLite файлів після міграції на PostgreSQL
"""

import os
import shutil
from pathlib import Path


def main():
    """Видаляє SQLite файли після міграції на PostgreSQL."""
    print("🗑️ Видалення SQLite файлів після міграції на PostgreSQL...")

    # Список файлів для видалення
    files_to_remove = ["prompts.db", "temp_chroma_db/chroma.sqlite3"]

    # Список директорій для видалення
    dirs_to_remove = ["temp_chroma_db"]

    total_freed_space = 0

    # Видаляємо файли
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                file_size = os.path.getsize(file_path)
                os.remove(file_path)
                total_freed_space += file_size
                print(f"✅ Видалено файл: {file_path} ({file_size / 1024:.1f} KB)")
            except Exception as e:
                print(f"❌ Помилка видалення {file_path}: {e}")
        else:
            print(f"⚠️ Файл не знайдено: {file_path}")

    # Видаляємо директорії
    for dir_path in dirs_to_remove:
        if os.path.exists(dir_path):
            try:
                # Підраховуємо розмір директорії
                dir_size = sum(
                    os.path.getsize(os.path.join(dirpath, filename))
                    for dirpath, dirnames, filenames in os.walk(dir_path)
                    for filename in filenames
                )

                shutil.rmtree(dir_path)
                total_freed_space += dir_size
                print(f"✅ Видалено директорію: {dir_path} ({dir_size / 1024:.1f} KB)")
            except Exception as e:
                print(f"❌ Помилка видалення {dir_path}: {e}")
        else:
            print(f"⚠️ Директорія не знайдена: {dir_path}")

    # Підсумок
    print(f"\n📊 Підсумок:")
    print(f"   Звільнено місця: {total_freed_space / 1024:.1f} KB")
    print(f"   Звільнено місця: {total_freed_space / (1024 * 1024):.2f} MB")

    print(f"\n✅ SQLite файли успішно видалено!")
    print(f"💡 Тепер система повністю використовує PostgreSQL та ChromaDB")


if __name__ == "__main__":
    main()
