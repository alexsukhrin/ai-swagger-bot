#!/usr/bin/env python3
"""
Детальний аналіз Chroma бази даних.
Показує структуру, розміри та вміст векторної бази.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path


def analyze_chroma_database():
    """Аналізує Chroma базу даних."""
    print("🔍 Детальний аналіз Chroma бази даних")
    print("=" * 60)

    # Перевіряємо обидві можливі директорії
    chroma_dirs = [Path("./chroma_db"), Path("./temp_chroma_db")]
    sqlite_file = None
    chroma_dir = None

    for dir_path in chroma_dirs:
        if dir_path.exists():
            sqlite_file = dir_path / "chroma.sqlite3"
            if sqlite_file.exists():
                chroma_dir = dir_path
                break

    if not sqlite_file or not sqlite_file.exists():
        print("❌ SQLite файл не знайдено в ./chroma_db або ./temp_chroma_db")
        return

    if not sqlite_file.exists():
        print("❌ SQLite файл не знайдено")
        return

    try:
        conn = sqlite3.connect(sqlite_file)
        cursor = conn.cursor()

        # Отримуємо список таблиць
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"📋 Таблиці в базі: {[table[0] for table in tables]}")

        # Аналізуємо кожну таблицю
        for table in tables:
            table_name = table[0]
            print(f"\n📊 Таблиця: {table_name}")

            # Кількість рядків
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            print(f"   Рядків: {row_count}")

            # Структура таблиці
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"   Колонки:")
            for col in columns:
                print(f"     • {col[1]} ({col[2]})")

            # Приклади даних
            if row_count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                rows = cursor.fetchall()
                print(f"   Приклади даних:")
                for i, row in enumerate(rows):
                    print(f"     {i+1}. {str(row)[:100]}...")

        # Спеціальний аналіз embeddings таблиці
        if "embeddings" in [t[0] for t in tables]:
            print(f"\n🎯 Детальний аналіз embeddings:")

            # Кількість документів
            cursor.execute("SELECT COUNT(*) FROM embeddings")
            doc_count = cursor.fetchone()[0]
            print(f"   📄 Всього документів: {doc_count}")

            # Розмір embeddings (якщо колонка існує)
            try:
                cursor.execute("SELECT LENGTH(embedding) FROM embeddings LIMIT 1")
                embedding_size = cursor.fetchone()
                if embedding_size:
                    print(f"   📏 Розмір одного embedding: {embedding_size[0]} байт")
            except sqlite3.OperationalError:
                print("   📏 Розмір embedding: колонка не знайдена")

            # Перевіряємо чи існує колонка metadata
            cursor.execute("PRAGMA table_info(embeddings)")
            columns_info = cursor.fetchall()
            column_names = [col[1] for col in columns_info]

            if "metadata" in column_names:
                # Приклади метаданих
                try:
                    cursor.execute("SELECT metadata FROM embeddings LIMIT 5")
                    metadatas = cursor.fetchall()
                    print(f"   📋 Приклади метаданих:")
                    for i, metadata in enumerate(metadatas):
                        if metadata[0]:
                            try:
                                meta_dict = json.loads(metadata[0])
                                method = meta_dict.get("method", "N/A")
                                path = meta_dict.get("path", "N/A")
                                print(f"     {i+1}. {method} {path}")
                            except:
                                print(f"     {i+1}. {metadata[0][:50]}...")
                        else:
                            print(f"     {i+1}. <пусто>")
                except Exception as e:
                    print(f"   ❌ Помилка читання метаданих: {e}")
            else:
                print("   📋 Колонка metadata не знайдена в таблиці embeddings")

        conn.close()

    except Exception as e:
        print(f"❌ Помилка аналізу: {e}")


def analyze_binary_files():
    """Аналізує бінарні файли Chroma."""
    print(f"\n🔍 Аналіз бінарних файлів")
    print("=" * 60)

    # Перевіряємо обидві можливі директорії
    chroma_dirs = [Path("./chroma_db"), Path("./temp_chroma_db")]
    chroma_dir = None

    for dir_path in chroma_dirs:
        if dir_path.exists():
            chroma_dir = dir_path
            break

    if not chroma_dir:
        print("❌ Директорія Chroma не знайдена")
        return

    for item in chroma_dir.iterdir():
        if item.is_dir():
            print(f"📁 Директорія: {item.name}")

            total_size = 0
            for subitem in item.iterdir():
                if subitem.is_file():
                    size_bytes = subitem.stat().st_size
                    size_kb = size_bytes / 1024
                    size_mb = size_kb / 1024
                    total_size += size_bytes

                    print(f"   📄 {subitem.name}: {size_kb:.1f} KB ({size_mb:.2f} MB)")

            total_kb = total_size / 1024
            total_mb = total_kb / 1024
            print(f"   📊 Загальний розмір: {total_kb:.1f} KB ({total_mb:.2f} MB)")


def check_memory_usage():
    """Перевіряє використання пам'яті."""
    print(f"\n🧠 Аналіз використання пам'яті")
    print("=" * 60)

    try:
        import psutil

        process = psutil.Process()
        memory_info = process.memory_info()

        print(f"📊 Використання пам'яті поточним процесом:")
        print(f"   RSS (фізична пам'ять): {memory_info.rss / 1024 / 1024:.1f} MB")
        print(f"   VMS (віртуальна пам'ять): {memory_info.vms / 1024 / 1024:.1f} MB")

    except ImportError:
        print("⚠️ psutil не встановлено. Встановіть: pip install psutil")


def main():
    """Основний функція аналізу."""
    print("🔍 ДЕТАЛЬНИЙ АНАЛІЗ CHROMA БАЗИ ДАНИХ")
    print("=" * 60)
    print(f"⏰ Час аналізу: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    analyze_chroma_database()
    analyze_binary_files()
    check_memory_usage()

    print(f"\n✅ Аналіз завершено!")


if __name__ == "__main__":
    main()
