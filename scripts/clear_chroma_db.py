#!/usr/bin/env python3
"""
Скрипт для очищення Chroma бази даних.
Видаляє всі дані та перестворює чисту базу.
"""

import shutil
from pathlib import Path
import sqlite3
import os
import sys


def clear_chroma_database():
    """Очищує Chroma базу даних."""
    print("🧹 Очищення Chroma бази даних")
    print("=" * 50)
    
    # Перевіряємо обидві можливі директорії
    chroma_dirs = [Path("./chroma_db"), Path("./temp_chroma_db")]
    
    for chroma_dir in chroma_dirs:
        if chroma_dir.exists():
            print(f"📁 Знайдено директорію: {chroma_dir}")
            
            # Видаляємо всю директорію
            try:
                shutil.rmtree(chroma_dir)
                print(f"✅ Видалено директорію: {chroma_dir}")
            except Exception as e:
                print(f"❌ Помилка видалення {chroma_dir}: {e}")
    
    # Перевіряємо чи є інші SQLite файли
    sqlite_files = list(Path(".").glob("*.sqlite*"))
    for sqlite_file in sqlite_files:
        try:
            os.remove(sqlite_file)
            print(f"✅ Видалено SQLite файл: {sqlite_file}")
        except Exception as e:
            print(f"❌ Помилка видалення {sqlite_file}: {e}")
    
    print("✅ Очищення завершено!")


def verify_clean_state():
    """Перевіряє чи база даних дійсно очищена."""
    print("\n🔍 Перевірка стану після очищення")
    print("=" * 50)
    
    chroma_dirs = [Path("./chroma_db"), Path("./temp_chroma_db")]
    
    for chroma_dir in chroma_dirs:
        if chroma_dir.exists():
            print(f"⚠️  Директорія все ще існує: {chroma_dir}")
        else:
            print(f"✅ Директорія видалена: {chroma_dir}")
    
    # Перевіряємо SQLite файли
    sqlite_files = list(Path(".").glob("*.sqlite*"))
    if sqlite_files:
        print(f"⚠️  Знайдено SQLite файли: {sqlite_files}")
    else:
        print("✅ SQLite файли видалені")


def main():
    """Основний функція очищення."""
    print("🧹 ОЧИЩЕННЯ CHROMA БАЗИ ДАНИХ")
    print("=" * 50)
    
    # Перевіряємо чи є флаг --auto
    auto_mode = "--auto" in sys.argv
    
    if not auto_mode:
        print("⚠️  Це видалить ВСІ дані з векторної бази!")
        print("⚠️  Після очищення потрібно буде переіндексувати Swagger файли")
        print("=" * 50)
        
        # Запитуємо підтвердження
        response = input("Продовжити очищення? (y/N): ")
        if response.lower() != 'y':
            print("❌ Очищення скасовано")
            return
    
    clear_chroma_database()
    verify_clean_state()
    
    print("\n✅ Очищення завершено!")
    if not auto_mode:
        print("💡 Тепер запустіть індексацію Swagger файлів заново")


if __name__ == "__main__":
    main()
