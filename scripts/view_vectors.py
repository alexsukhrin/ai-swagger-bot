#!/usr/bin/env python3
"""
Скрипт для перегляду векторів в ChromaDB.
"""

import os
import sys
import json
from dotenv import load_dotenv

# Завантажуємо змінні середовища
load_dotenv()

# Додаємо шлях до src та кореневої директорії
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config import Config
from rag_engine import RAGEngine

def view_chromadb_vectors():
    """Переглядає вектори в ChromaDB."""
    print("🔍 Перегляд векторів в ChromaDB")
    print("=" * 60)
    
    try:
        # Валідуємо конфігурацію
        if not Config.validate():
            return False
        
        # Ініціалізуємо RAG Engine
        print(f"📂 Директорія бази: {Config.CHROMA_DB_PATH}")
        
        if not os.path.exists(Config.CHROMA_DB_PATH):
            print("❌ База даних не знайдена. Спочатку запустіть reindex_swagger.py")
            return False
        
        # Створюємо RAG Engine для доступу до бази
        rag_config = Config.get_rag_config()
        rag_engine = RAGEngine(Config.SWAGGER_SPEC_PATH, config=rag_config)
        
        # Отримуємо всі endpoints
        print("\n📊 Отримання всіх векторів...")
        all_endpoints = rag_engine.get_all_endpoints()
        
        if not all_endpoints:
            print("❌ Вектори не знайдено")
            return False
        
        print(f"✅ Знайдено {len(all_endpoints)} векторів\n")
        
        # Показуємо детальну інформацію про кожен вектор
        for i, endpoint in enumerate(all_endpoints, 1):
            print(f"🔗 Вектор {i}:")
            print("-" * 40)
            
            # Контент
            content = endpoint.get('content', '')
            print(f"📝 Контент: {content[:200]}...")
            
            # Метадані
            metadata = endpoint.get('metadata', {})
            print(f"🏷️  Метадані:")
            for key, value in metadata.items():
                print(f"   {key}: {value}")
            
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
        return False

def search_vectors(query: str, k: int = 5):
    """Шукає вектори за запитом."""
    print(f"🔍 Пошук векторів для запиту: '{query}'")
    print("=" * 60)
    
    try:
        # Валідуємо конфігурацію
        if not Config.validate():
            return False
        
        # Створюємо RAG Engine
        rag_config = Config.get_rag_config()
        rag_engine = RAGEngine(Config.SWAGGER_SPEC_PATH, config=rag_config)
        
        # Шукаємо подібні вектори
        results = rag_engine.search_similar_endpoints(query, k=k)
        
        if not results:
            print("❌ Результати не знайдено")
            return False
        
        print(f"✅ Знайдено {len(results)} результатів\n")
        
        # Показуємо результати
        for i, result in enumerate(results, 1):
            print(f"🎯 Результат {i}:")
            print("-" * 40)
            
            # Контент
            content = result.get('content', '')
            print(f"📝 Контент: {content[:200]}...")
            
            # Метадані
            metadata = result.get('metadata', {})
            print(f"🏷️  Метадані:")
            for key, value in metadata.items():
                print(f"   {key}: {value}")
            
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_vector_statistics():
    """Аналізує статистику векторів."""
    print("📊 Аналіз статистики векторів")
    print("=" * 60)
    
    try:
        # Валідуємо конфігурацію
        if not Config.validate():
            return False
        
        # Створюємо RAG Engine
        rag_config = Config.get_rag_config()
        rag_engine = RAGEngine(Config.SWAGGER_SPEC_PATH, config=rag_config)
        
        # Отримуємо всі endpoints
        all_endpoints = rag_engine.get_all_endpoints()
        
        if not all_endpoints:
            print("❌ Вектори не знайдено")
            return False
        
        # Аналізуємо метадані
        methods = {}
        paths = {}
        tags = {}
        
        for endpoint in all_endpoints:
            metadata = endpoint.get('metadata', {})
            
            # Методи
            method = metadata.get('method', 'UNKNOWN')
            methods[method] = methods.get(method, 0) + 1
            
            # Шляхи
            path = metadata.get('path', 'UNKNOWN')
            paths[path] = paths.get(path, 0) + 1
            
            # Теги
            tag = metadata.get('tags', 'UNKNOWN')
            tags[tag] = tags.get(tag, 0) + 1
        
        print(f"📈 Загальна статистика:")
        print(f"   Всього векторів: {len(all_endpoints)}")
        print(f"   Унікальних методів: {len(methods)}")
        print(f"   Унікальних шляхів: {len(paths)}")
        print(f"   Унікальних тегів: {len(tags)}")
        
        print(f"\n🔧 Методи:")
        for method, count in methods.items():
            print(f"   {method}: {count}")
        
        print(f"\n🛣️  Шляхи:")
        for path, count in paths.items():
            print(f"   {path}: {count}")
        
        print(f"\n🏷️  Теги:")
        for tag, count in tags.items():
            print(f"   {tag}: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Головна функція."""
    print("🔍 Інструменти для перегляду векторів в ChromaDB")
    print("=" * 60)
    
    while True:
        print("\n📋 Виберіть опцію:")
        print("1. Переглянути всі вектори")
        print("2. Пошук векторів")
        print("3. Аналіз статистики")
        print("4. Вихід")
        
        choice = input("\n🎯 Ваш вибір (1-4): ").strip()
        
        if choice == "1":
            view_chromadb_vectors()
        elif choice == "2":
            query = input("🔍 Введіть запит для пошуку: ").strip()
            if query:
                search_vectors(query)
            else:
                print("❌ Запит не може бути порожнім")
        elif choice == "3":
            analyze_vector_statistics()
        elif choice == "4":
            print("👋 До побачення!")
            break
        else:
            print("❌ Невірний вибір. Спробуйте ще раз.")

if __name__ == "__main__":
    main()
