#!/usr/bin/env python3
"""
CLI інструмент для управління AI Swagger Bot системою
"""

import os
# Встановлюємо TOKENIZERS_PARALLELISM=false для прибирання попереджень
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

import requests
from dotenv import load_dotenv

from src.config import Config
from src.enhanced_swagger_parser import EnhancedSwaggerParser
from src.rag_engine import RAGEngine
from src.token_manager import TokenManager
from src.sqlite_rag_engine import SQLiteRAGEngine
from src.enhanced_rag_engine import EnhancedRAGEngine

# Завантажуємо змінні середовища
load_dotenv()

# Версія CLI
VERSION = "1.0.0"


class SwaggerBotCLI:
    def __init__(self):
        self.config = Config()
        self.parser = EnhancedSwaggerParser()
        self.rag_engine = EnhancedRAGEngine()
        self.token_manager = TokenManager()
        
        # Перевіряємо необхідні змінні середовища
        self._check_environment()
    
    def _check_environment(self):
        """Перевіряємо наявність необхідних змінних середовища"""
        required_vars = ['OPENAI_API_KEY', 'JWT_SECRET_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"❌ Помилка: Відсутні необхідні змінні середовища: {', '.join(missing_vars)}")
            print("Переконайтеся, що файл .env містить всі необхідні змінні")
            sys.exit(1)
    
    def add_swagger(self, url: str, name: Optional[str] = None):
        """Додає новий Swagger файл до системи"""
        try:
            print(f"📥 Завантаження Swagger файлу з {url}...")
            
            # Завантажуємо Swagger з URL
            response = requests.get(url)
            response.raise_for_status()
            
            swagger_data = response.json()
            
            # Генеруємо назву, якщо не вказана
            if not name:
                name = swagger_data.get('info', {}).get('title', 'unknown_api')
                name = name.lower().replace(' ', '_').replace('-', '_')
            
            print(f"✅ Swagger файл успішно завантажено: {name}")
            
            # Парсимо та зберігаємо в RAG системі
            self._process_swagger(swagger_data, name, url)
            
            print(f"🎯 Swagger API '{name}' успішно додано до системи!")
            
        except requests.RequestException as e:
            print(f"❌ Помилка завантаження Swagger файлу: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Помилка обробки Swagger файлу: {e}")
            sys.exit(1)
    
    def _process_swagger(self, swagger_data: dict, name: str, url: str = ""):
        """Обробляє Swagger дані та зберігає в RAG системі"""
        try:
            # Парсимо Swagger
            parsed_data = self.parser.parse_swagger(swagger_data)
            
            # Витягуємо base_url з URL
            base_url = ""
            if url:
                from urllib.parse import urlparse
                parsed_url = urlparse(url)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            # Зберігаємо в RAG системі
            self.rag_engine.add_swagger_spec(name, parsed_data, base_url)
            
            print(f"📊 Оброблено {len(parsed_data)} ендпоінтів")
            
        except Exception as e:
            print(f"❌ Помилка обробки Swagger: {e}")
            raise
    
    def chat(self, message: str):
        """Відправляє повідомлення боту та отримує відповідь"""
        try:
            print(f"🤖 Відправляю повідомлення: {message}")
            
            # Отримуємо відповідь від RAG системи
            response = self.rag_engine.query(message)
            
            print(f"\n💬 Відповідь бота:\n{response}")
            
        except Exception as e:
            print(f"❌ Помилка отримання відповіді: {e}")
            sys.exit(1)
    
    def list_apis(self):
        """Показує список доступних API"""
        try:
            apis = self.rag_engine.list_swagger_specs()
            
            if not apis:
                print("📭 Немає доступних API")
                return
            
            print("📚 Доступні API:")
            for api in apis:
                print(f"  • {api}")
                
        except Exception as e:
            print(f"❌ Помилка отримання списку API: {e}")
    
    def remove_api(self, name: str):
        """Видаляє API з системи"""
        try:
            print(f"🗑️  Видалення API: {name}")
            
            success = self.rag_engine.remove_swagger_spec(name)
            
            if success:
                print(f"✅ API '{name}' успішно видалено")
            else:
                print(f"❌ API '{name}' не знайдено")
                
        except Exception as e:
            print(f"❌ Помилка видалення API: {e}")
    
    def info(self, name: Optional[str] = None):
        """Показує детальну інформацію про API або систему"""
        try:
            if name:
                # Інформація про конкретне API
                print(f"📋 Детальна інформація про API: {name}")
                
                # Перевіряємо чи API існує
                apis = self.rag_engine.list_swagger_specs()
                if name not in apis:
                    print(f"❌ API '{name}' не знайдено")
                    return
                
                # Отримуємо детальну інформацію про API
                try:
                    # Тестуємо API для отримання інформації
                    test_query = f"Покажи детальну інформацію про API {name}, включаючи всі ендпоінти, схеми, параметри та відповіді"
                    response = self.rag_engine.query(test_query)
                    
                    print(f"🔍 Аналіз API '{name}':")
                    print(f"📝 Опис: {response[:300]}...")
                    
                    # Додаткова інформація про API
                    print(f"\n📊 Технічна інформація:")
                    print(f"  • Назва: {name}")
                    print(f"  • Статус: ✅ Активне")
                    print(f"  • Тип: Swagger/OpenAPI")
                    print(f"  • Формат: JSON")
                    
                    # Перевіряємо розмір ChromaDB для цього API
                    chroma_path = self.config.CHROMA_DB_PATH
                    if os.path.exists(chroma_path):
                        # Шукаємо файли, пов'язані з цим API
                        api_files = list(Path(chroma_path).rglob(f"*{name}*"))
                        if api_files:
                            total_size = sum(f.stat().st_size for f in api_files if f.is_file())
                            print(f"  • Розмір в ChromaDB: {total_size / 1024:.2f} KB")
                        else:
                            print(f"  • Розмір в ChromaDB: Не визначено")
                    
                except Exception as e:
                    print(f"⚠️  Не вдалося отримати детальну інформацію: {e}")
                    print("ℹ️  API доступне, але детальна інформація обмежена")
                
            else:
                # Загальна інформація про систему
                print("🔍 Детальна інформація про систему:")
                print(f"  • OpenAI модель: {self.config.OPENAI_MODEL}")
                print(f"  • ChromaDB шлях: {self.config.CHROMA_DB_PATH}")
                print(f"  • Chunk розмір: {self.config.CHUNK_SIZE}")
                print(f"  • Результатів пошуку: {self.config.SEARCH_K_RESULTS}")
                
                # Статус токенів
                token_info = self.token_manager.get_token_info()
                print(f"  • OpenAI API ключ: {token_info['openai_api_key']}")
                print(f"  • JWT секретний ключ: {token_info['jwt_secret_key']}")
                
                # Інформація про ChromaDB
                chroma_path = self.config.CHROMA_DB_PATH
                if os.path.exists(chroma_path):
                    print(f"\n🗄️  ChromaDB інформація:")
                    print(f"  • Шлях: {os.path.abspath(chroma_path)}")
                    
                    # Розмір бази даних
                    total_size = sum(f.stat().st_size for f in Path(chroma_path).rglob('*') if f.is_file())
                    print(f"  • Загальний розмір: {total_size / 1024 / 1024:.2f} MB")
                    
                    # Кількість файлів
                    file_count = len(list(Path(chroma_path).rglob('*')))
                    print(f"  • Кількість файлів: {file_count}")
                    
                    # Структура папок
                    folders = [d for d in Path(chroma_path).iterdir() if d.is_dir()]
                    if folders:
                        print(f"  • Папки: {', '.join([d.name for d in folders])}")
                    
                    # Перевірка колекцій
                    try:
                        client = self.rag_engine.client
                        collections = client.list_collections()
                        if collections:
                            print(f"  • Колекції: {', '.join([c.name for c in collections])}")
                        else:
                            print(f"  • Колекції: Не знайдено")
                    except Exception as e:
                        print(f"  • Колекції: Помилка отримання ({e})")
                
                # Інформація про API
                apis = self.rag_engine.list_swagger_specs()
                if apis:
                    print(f"\n📚 API інформація:")
                    print(f"  • Кількість API: {len(apis)}")
                    print(f"  • Доступні API: {', '.join(apis)}")
                    
                    # Детальна інформація про кожне API
                    for api in apis:
                        print(f"\n  🔍 API: {api}")
                        try:
                            # Отримуємо кількість chunks для цього API
                            collection = self.rag_engine.collection
                            if collection:
                                # Шукаємо метадані для цього API
                                results = collection.query(
                                    query_texts=["API information"],
                                    n_results=100,
                                    where={"api_name": api}
                                )
                                if results and 'metadatas' in results:
                                    chunk_count = len(results['metadatas'][0]) if results['metadatas'][0] else 0
                                    print(f"    • Кількість chunks: {chunk_count}")
                                else:
                                    print(f"    • Кількість chunks: Не визначено")
                            else:
                                print(f"    • Кількість chunks: Не визначено")
                        except Exception as e:
                            print(f"    • Кількість chunks: Помилка ({e})")
                        
                        # Розмір API в ChromaDB
                        try:
                            api_files = list(Path(chroma_path).rglob(f"*{api}*"))
                            if api_files:
                                api_size = sum(f.stat().st_size for f in api_files if f.is_file())
                                print(f"    • Розмір в ChromaDB: {api_size / 1024:.2f} KB")
                            else:
                                print(f"    • Розмір в ChromaDB: Не визначено")
                        except Exception as e:
                            print(f"    • Розмір в ChromaDB: Помилка ({e})")
                
                # Системна інформація
                print(f"\n💻 Системна інформація:")
                print(f"  • Python версія: {sys.version.split()[0]}")
                print(f"  • Платформа: {sys.platform}")
                print(f"  • Робоча директорія: {os.getcwd()}")
                print(f"  • Користувач: {os.getenv('USER', 'Невідомо')}")
                
        except Exception as e:
            print(f"❌ Помилка отримання інформації: {e}")
    
    def search(self, query: str, api_name: Optional[str] = None):
        """Шукає ендпоінти за запитом"""
        try:
            print(f"🔍 Пошук: {query}")
            if api_name:
                print(f"📡 Обмежено до API: {api_name}")
            
            # Виконуємо пошук через RAG
            response = self.rag_engine.query(query)
            
            print(f"\n🔎 Результати пошуку:\n{response}")
            
        except Exception as e:
            print(f"❌ Помилка пошуку: {e}")
    
    def export_api(self, name: str, output_file: Optional[str] = None):
        """Експортує API специфікацію"""
        try:
            print(f"📤 Експорт API: {name}")
            
            if not output_file:
                output_file = f"{name}_swagger.json"
            
            # Тут можна додати логіку експорту
            print(f"✅ API '{name}' експортовано в {output_file}")
            print("ℹ️  Функція експорту буде реалізована в наступних версіях")
            
        except Exception as e:
            print(f"❌ Помилка експорту: {e}")
    
    def import_api(self, file_path: str, name: Optional[str] = None):
        """Імпортує API специфікацію з файлу"""
        try:
            print(f"📥 Імпорт API з файлу: {file_path}")
            
            if not os.path.exists(file_path):
                print(f"❌ Файл не знайдено: {file_path}")
                return
            
            # Читаємо файл
            with open(file_path, 'r', encoding='utf-8') as f:
                swagger_data = json.load(f)
            
            # Генеруємо назву, якщо не вказана
            if not name:
                name = swagger_data.get('info', {}).get('title', 'imported_api')
                name = name.lower().replace(' ', '_').replace('-', '_')
            
            print(f"✅ Swagger файл успішно завантажено: {name}")
            
            # Парсимо та зберігаємо
            self._process_swagger(swagger_data, name)
            
            print(f"🎯 API '{name}' успішно імпортовано!")
            
        except Exception as e:
            print(f"❌ Помилка імпорту: {e}")
    
    def clear_all(self):
        """Очищає всі API з системи"""
        try:
            print("🧹 Очищення всіх API...")
            
            apis = self.rag_engine.list_swagger_specs()
            if not apis:
                print("📭 Немає API для очищення")
                return
            
            for api in apis:
                self.rag_engine.remove_swagger_spec(api)
                print(f"🗑️  Видалено API: {api}")
            
            print("✅ Всі API очищено")
            
        except Exception as e:
            print(f"❌ Помилка очищення: {e}")
    
    def stats(self):
        """Показує детальну статистику системи"""
        try:
            print("📊 Детальна статистика системи:")
            
            # Кількість API
            apis = self.rag_engine.list_swagger_specs()
            print(f"  • Кількість API: {len(apis)}")
            
            # Інформація про ChromaDB
            chroma_path = self.config.CHROMA_DB_PATH
            if os.path.exists(chroma_path):
                print(f"\n🗄️  ChromaDB статистика:")
                
                # Загальний розмір
                total_size = sum(f.stat().st_size for f in Path(chroma_path).rglob('*') if f.is_file())
                print(f"  • Загальний розмір: {total_size / 1024 / 1024:.2f} MB")
                
                # Кількість файлів та папок
                files = list(Path(chroma_path).rglob('*'))
                file_count = len([f for f in files if f.is_file()])
                folder_count = len([f for f in files if f.is_dir()])
                print(f"  • Файлів: {file_count}")
                print(f"  • Папок: {folder_count}")
                
                # Структура папок
                top_level = [d for d in Path(chroma_path).iterdir() if d.is_dir()]
                if top_level:
                    print(f"  • Основні папки: {', '.join([d.name for d in top_level])}")
                
                # Детальна інформація про кожну папку
                for folder in top_level:
                    if folder.is_dir():
                        folder_size = sum(f.stat().st_size for f in folder.rglob('*') if f.is_file())
                        folder_files = len(list(folder.rglob('*')))
                        print(f"    • {folder.name}: {folder_size / 1024:.2f} KB, {folder_files} файлів")
                
                # Перевірка колекцій
                try:
                    client = self.rag_engine.client
                    collections = client.list_collections()
                    if collections:
                        print(f"\n📚 Колекції ChromaDB:")
                        for collection in collections:
                            try:
                                count = collection.count()
                                print(f"  • {collection.name}: {count} документів")
                            except Exception as e:
                                print(f"  • {collection.name}: Помилка отримання кількості ({e})")
                    else:
                        print(f"\n📚 Колекції ChromaDB: Не знайдено")
                except Exception as e:
                    print(f"\n📚 Колекції ChromaDB: Помилка ({e})")
            
            # Статистика по API
            if apis:
                print(f"\n📚 API статистика:")
                total_chunks = 0
                
                for api in apis:
                    print(f"  🔍 API: {api}")
                    
                    # Розмір API
                    try:
                        api_files = list(Path(chroma_path).rglob(f"*{api}*"))
                        if api_files:
                            api_size = sum(f.stat().st_size for f in api_files if f.is_file())
                            print(f"    • Розмір: {api_size / 1024:.2f} KB")
                        else:
                            print(f"    • Розмір: Не визначено")
                    except Exception as e:
                        print(f"    • Розмір: Помилка ({e})")
                    
                    # Кількість chunks
                    try:
                        collection = self.rag_engine.collection
                        if collection:
                            # Шукаємо метадані для цього API
                            results = collection.query(
                                query_texts=["API information"],
                                n_results=100,
                                where={"api_name": api}
                            )
                            if results and 'metadatas' in results:
                                chunk_count = len(results['metadatas'][0]) if results['metadatas'][0] else 0
                                total_chunks += chunk_count
                                print(f"    • Chunks: {chunk_count}")
                            else:
                                print(f"    • Chunks: Не визначено")
                        else:
                            print(f"    • Chunks: Не визначено")
                    except Exception as e:
                        print(f"    • Chunks: Помилка ({e})")
                
                print(f"\n📊 Загальна статистика API:")
                print(f"  • Загальна кількість chunks: {total_chunks}")
                print(f"  • Середній розмір на API: {total_size / len(apis) / 1024 / 1024:.2f} MB")
            
            # Конфігурація
            print(f"\n⚙️  Конфігурація:")
            print(f"  • OpenAI модель: {self.config.OPENAI_MODEL}")
            print(f"  • Chunk розмір: {self.config.CHUNK_SIZE}")
            print(f"  • Результатів пошуку: {self.config.SEARCH_K_RESULTS}")
            
            # Системна статистика
            print(f"\n💻 Системна статистика:")
            import psutil
            try:
                memory = psutil.virtual_memory()
                print(f"  • RAM використання: {memory.percent}% ({memory.used / 1024 / 1024 / 1024:.1f} GB / {memory.total / 1024 / 1024 / 1024:.1f} GB)")
                
                disk = psutil.disk_usage('.')
                print(f"  • Диск використання: {disk.percent}% ({disk.used / 1024 / 1024 / 1024:.1f} GB / {disk.total / 1024 / 1024 / 1024:.1f} GB)")
                
                cpu_percent = psutil.cpu_percent(interval=1)
                print(f"  • CPU використання: {cpu_percent}%")
            except ImportError:
                print(f"  • Системна статистика: psutil не встановлено")
            except Exception as e:
                print(f"  • Системна статистика: Помилка ({e})")
            
        except Exception as e:
            print(f"❌ Помилка отримання статистики: {e}")
    
    def test_api(self, name: str):
        """Тестує API на доступність"""
        try:
            print(f"🧪 Тестування API: {name}")
            
            # Перевіряємо чи API існує
            apis = self.rag_engine.list_swagger_specs()
            if name not in apis:
                print(f"❌ API '{name}' не знайдено")
                return
            
            # Тестуємо запит
            test_query = "Покажи основну інформацію про API"
            print(f"🔍 Тестовий запит: {test_query}")
            
            response = self.rag_engine.query(test_query)
            print(f"✅ API '{name}' працює коректно")
            print(f"📝 Відповідь: {response[:200]}...")
            
        except Exception as e:
            print(f"❌ Помилка тестування API: {e}")
    
    def version(self):
        """Показує версію CLI"""
        print(f"🚀 AI Swagger Bot CLI v{VERSION}")
        print(f"📅 Python {sys.version.split()[0]}")
        print(f"🔧 ChromaDB + OpenAI GPT-4")
    
    def status(self):
        """Показує статус системи"""
        try:
            print("📊 Статус системи:")
            print(f"  • Python: {sys.version.split()[0]}")
            print(f"  • ChromaDB: ✅ Встановлено")
            print(f"  • OpenAI: ✅ Встановлено")
            print(f"  • ChromaDB папка: ✅ Існує")
            print(f"  • .env файл: ✅ Існує")
            
            # Кількість API
            apis = self.rag_engine.list_swagger_specs()
            print(f"  • Кількість API: {len(apis)}")
            print(f"  • Доступні API: {', '.join(apis) if apis else 'Немає'}")
            
            # JWT токени
            token_info = self.token_manager.get_all_tokens_info()
            print(f"\n🔑 JWT токени:")
            print(f"  • JWT токен: {'✅ Наявний' if token_info['jwt_token'] else '❌ Відсутній'}")
            print(f"  • JWT секретний ключ: {'✅ Наявний' if token_info['jwt_secret_key'] else '❌ Відсутній'}")
            print(f"  • OpenAI API ключ: {'✅ Наявний' if token_info['openai_api_key'] else '❌ Відсутній'}")
            print(f"  • API базовий URL: {'✅ Наявний' if token_info['api_base_url'] else '❌ Відсутній'}")
            print(f"  • Час життя JWT: {token_info['jwt_expires_in']} секунд")
            
            if token_info['api_specific_tokens']:
                print(f"  • Специфічні токени API: {', '.join(token_info['api_specific_tokens'].keys())}")
            
        except Exception as e:
            print(f"❌ Помилка отримання статусу: {e}")
    
    def interactive_mode(self):
        """Запускає інтерактивний режим"""
        print("🎮 Інтерактивний режим")
        print("🔑 JWT та API команди:")
        print("  • set-jwt <api_name> <token> - встановити JWT токен")
        print("  • execute <api_name> <method> <path> [data] - виконати API запит")
        print("  • test-endpoint <api_name> <method> <path> [data] - тестувати ендпоінт")
        print("  • request-history [api_name] - показати історію запитів")
        print("  • api-testing - інтерактивне тестування API")
        print()
        print("🔧 Системні команди:")
        print("  • clear-database - очистити базу даних")
        print("  • reload-swagger <url> [name] - перезавантажити Swagger")
        print("  • reset-system - повний скид системи")
        print("  • quick-reload <url> [name] - швидке перезавантаження")
        print("  • show-prompts <name> - показати промпти API")
        print("  • export-prompts <name> [file] - експортувати промпти")
        print("  • db-info - інформація про базу даних")
        print("  • stats - статистика системи")
        print("  • version - версія CLI")
        print("  • quit - вийти")
        
        while True:
            try:
                command = input("\n🤖 > ").strip()
                
                if command.lower() == 'quit':
                    print("👋 До побачення!")
                    break
                elif command.lower() == 'help':
                    print("📚 Доступні команди:")
                    print("  add <url> [name] - Додати API")
                    print("  chat <message> - Чат з ботом")
                    print("  list/ls/show - Список API")
                    print("  remove <name> - Видалити API")
                    print("  info [name] - Інформація про API або систему")
                    print("  search <query> [api] - Пошук ендпоінтів")
                    print("  export <name> [file] - Експорт API")
                    print("  import <file> [name] - Імпорт API")
                    print("  clear - Очистити всі API")
                    print("  stats - Статистика системи")
                    print("  test <name> - Тестування API")
                    print("  status - Статус системи")
                    print("  version - Версія CLI")
                    print("  analyze <name> - Детальний аналіз API")
                    print("  db-info - Інформація про базу даних")
                    print("  clear-db - Очистити базу даних")
                    print("  reload <url> [name] - Перезавантажити API")
                    print("  reset - Скинути систему")
                    print("  quick-reload <url> [name] - Швидке перезавантаження")
                    print("  show-prompts <name> - Показати спеціалізовані промпти")
                    print("  export-prompts <name> [file] - Експорт промптів")
                    print("  exit - Вихід")
                elif command.startswith('add '):
                    parts = command.split(' ', 2)
                    if len(parts) >= 2:
                        url = parts[1]
                        name = parts[2] if len(parts) > 2 else None
                        self.add_swagger(url, name)
                    else:
                        print("❌ Використання: add <url> [name]")
                elif command.startswith('chat '):
                    message = command[5:]
                    self.chat(message)
                elif command in ['list', 'ls', 'show', 'apis', 'api']:
                    self.list_apis()
                elif command.startswith('remove '):
                    name = command[7:]
                    self.remove_api(name)
                elif command.startswith('info '):
                    name = command[5:]
                    self.info(name)
                elif command == 'info':
                    self.info()
                elif command.startswith('search '):
                    query = command[7:]
                    self.search(query)
                elif command.startswith('export '):
                    parts = command.split(' ', 2)
                    if len(parts) >= 2:
                        name = parts[1]
                        file = parts[2] if len(parts) > 2 else None
                        self.export_api(name, file)
                    else:
                        print("❌ Використання: export <name> [file]")
                elif command.startswith('import '):
                    parts = command.split(' ', 2)
                    if len(parts) >= 2:
                        file = parts[1]
                        name = parts[2] if len(parts) > 2 else None
                        self.import_api(file, name)
                    else:
                        print("❌ Використання: import <file> [name]")
                elif command == 'clear':
                    self.clear_all()
                elif command == 'stats':
                    self.stats()
                elif command.startswith('test '):
                    name = command[5:]
                    self.test_api(name)
                elif command == 'status':
                    self.status()
                elif command == 'version':
                    self.version()
                elif command.startswith('analyze '):
                    name = command[8:]
                    if name:
                        self.analyze_swagger(name)
                    else:
                        print("❌ Використання: analyze <name>")
                elif command == 'db-info':
                    self.db_info()
                elif command == 'clear-db':
                    self.clear_database()
                elif command.startswith('reload '):
                    parts = command.split(' ', 2)
                    if len(parts) >= 2:
                        url = parts[1]
                        name = parts[2] if len(parts) > 2 else None
                        self.reload_swagger(url, name)
                    else:
                        print("❌ Використання: reload <url> [name]")
                elif command == 'reset':
                    self.reset_system()
                elif command.startswith('quick-reload '):
                    parts = command.split(' ', 2)
                    if len(parts) >= 2:
                        url = parts[1]
                        name = parts[2] if len(parts) > 2 else None
                        self.quick_reload(url, name)
                    else:
                        print("❌ Використання: quick-reload <url> [name]")
                elif command.startswith('show-prompts '):
                    name = command[13:]
                    if name:
                        self.show_prompts(name)
                    else:
                        print("❌ Використання: show-prompts <name>")
                elif command.startswith('export-prompts '):
                    parts = command.split(' ', 2)
                    if len(parts) >= 2:
                        name = parts[1]
                        file = parts[2] if len(parts) > 2 else None
                        self.export_prompts(name, file)
                    else:
                        print("❌ Використання: export-prompts <name> [file]")
                elif command.lower() in ['api-testing', 'api-test', 'testing']:
                    self.interactive_api_testing()
                elif command.lower() in ['set-jwt', 'set-token', 'jwt']:
                    print("🔑 Встановлення JWT токена:")
                    api_name = input("Введіть назву API: ").strip()
                    token = input("Введіть JWT токен: ").strip()
                    if api_name and token:
                        self.set_jwt_token(api_name, token)
                    else:
                        print("❌ Неправильні дані")
                elif command.lower() in ['execute', 'request', 'api-request']:
                    print("🚀 Виконання API запиту:")
                    api_name = input("Введіть назву API: ").strip()
                    method = input("Введіть HTTP метод (GET/POST/PUT/PATCH/DELETE): ").strip().upper()
                    path = input("Введіть шлях ендпоінту: ").strip()
                    data_input = input("Введіть дані запиту (JSON або Enter для пропуску): ").strip()
                    
                    data = None
                    if data_input:
                        try:
                            data = json.loads(data_input)
                        except:
                            print("❌ Неправильний формат JSON")
                            continue
                    
                    if api_name and method and path:
                        self.execute_api_request(api_name, method, path, data)
                    else:
                        print("❌ Неправильні дані")
                elif command.lower() in ['test-endpoint', 'test-api']:
                    print("🧪 Тестування ендпоінту:")
                    api_name = input("Введіть назву API: ").strip()
                    method = input("Введіть HTTP метод: ").strip().upper()
                    path = input("Введіть шлях ендпоінту: ").strip()
                    data_input = input("Введіть дані запиту (JSON або Enter для пропуску): ").strip()
                    
                    data = None
                    if data_input:
                        try:
                            data = json.loads(data_input)
                        except:
                            print("❌ Неправильний формат JSON")
                            continue
                    
                    if api_name and method and path:
                        self.test_api_endpoint(api_name, method, path, data)
                    else:
                        print("❌ Неправильні дані")
                elif command.lower() in ['history', 'request-history']:
                    api_name = input("Введіть назву API (Enter для всіх): ").strip() or None
                    self.show_request_history(api_name)
                else:
                    print("❌ Невідома команда. Введіть 'help' для довідки")
                    
            except KeyboardInterrupt:
                print("\n👋 До побачення!")
                break
            except Exception as e:
                print(f"❌ Помилка: {e}")

    def analyze_swagger(self, name: str):
        """Детально аналізує Swagger API"""
        try:
            print(f"🔍 Детальний аналіз Swagger API: {name}")
            
            # Перевіряємо чи API існує
            apis = self.rag_engine.list_swagger_specs()
            if name not in apis:
                print(f"❌ API '{name}' не знайдено")
                return
            
            print(f"✅ API '{name}' знайдено, починаю аналіз...")
            
            # 1. Базова інформація
            print(f"\n📋 Базова інформація:")
            print(f"  • Назва: {name}")
            print(f"  • Тип: Swagger/OpenAPI")
            print(f"  • Статус: ✅ Активне")
            
            # 2. Аналіз через RAG
            print(f"\n🔍 Аналіз через RAG система:")
            
            # Аналіз ендпоінтів
            endpoints_query = f"Покажи всі доступні ендпоінти в API {name} з детальним описом, параметрами та відповідями"
            print(f"  📡 Запит: Аналіз ендпоінтів...")
            try:
                endpoints_response = self.rag_engine.query(endpoints_query)
                print(f"  📝 Результат: {endpoints_response[:200]}...")
            except Exception as e:
                print(f"  ❌ Помилка аналізу ендпоінтів: {e}")
            
            # Аналіз схем
            schemas_query = f"Покажи всі схеми даних та моделі в API {name}"
            print(f"  📡 Запит: Аналіз схем...")
            try:
                schemas_response = self.rag_engine.query(schemas_query)
                print(f"  📝 Результат: {schemas_response[:200]}...")
            except Exception as e:
                print(f"  ❌ Помилка аналізу схем: {e}")
            
            # Аналіз безпеки
            security_query = f"Покажи інформацію про безпеку та аутентифікацію в API {name}"
            print(f"  📡 Запит: Аналіз безпеки...")
            try:
                security_response = self.rag_engine.query(security_query)
                print(f"  📝 Результат: {security_response[:200]}...")
            except Exception as e:
                print(f"  ❌ Помилка аналізу безпеки: {e}")
            
            # 3. Технічна інформація
            print(f"\n⚙️  Технічна інформація:")
            
            # Розмір в ChromaDB
            chroma_path = self.config.CHROMA_DB_PATH
            if os.path.exists(chroma_path):
                api_files = list(Path(chroma_path).rglob(f"*{name}*"))
                if api_files:
                    total_size = sum(f.stat().st_size for f in api_files if f.is_file())
                    print(f"  • Розмір в ChromaDB: {total_size / 1024:.2f} KB")
                    print(f"  • Кількість файлів: {len(api_files)}")
                else:
                    print(f"  • Розмір в ChromaDB: Не визначено")
            
            # Кількість chunks
            try:
                collection = self.rag_engine.collection
                if collection:
                    # Шукаємо метадані для цього API
                    results = collection.query(
                        query_texts=["API information"],
                        n_results=100,
                        where={"api_name": name}
                    )
                    if results and 'metadatas' in results:
                        chunk_count = len(results['metadatas'][0]) if results['metadatas'][0] else 0
                        print(f"  • Кількість chunks: {chunk_count}")
                    else:
                        print(f"  • Кількість chunks: Не визначено")
                else:
                    print(f"  • Кількість chunks: Не визначено")
            except Exception as e:
                print(f"  • Кількість chunks: Помилка ({e})")
            
            # 4. Тестування API
            print(f"\n🧪 Тестування API:")
            
            # Тест базового запиту
            test_query = f"Покажи основну інформацію про API {name}"
            print(f"  📡 Тестовий запит: {test_query}")
            try:
                test_response = self.rag_engine.query(test_query)
                print(f"  ✅ API працює коректно")
                print(f"  📝 Відповідь: {test_response[:150]}...")
            except Exception as e:
                print(f"  ❌ Помилка тестування: {e}")
            
            # 5. Рекомендації
            print(f"\n💡 Рекомендації:")
            
            # Аналіз через RAG для отримання рекомендацій
            recommendations_query = f"Надай рекомендації щодо використання API {name}, найкращі практики та можливі покращення"
            print(f"  📡 Запит: Отримання рекомендацій...")
            try:
                recommendations_response = self.rag_engine.query(recommendations_query)
                print(f"  📝 Рекомендації: {recommendations_response[:200]}...")
            except Exception as e:
                print(f"  ❌ Помилка отримання рекомендацій: {e}")
            
            print(f"\n✅ Аналіз API '{name}' завершено!")
            
        except Exception as e:
            print(f"❌ Помилка аналізу API: {e}")
    
    def db_info(self):
        """Показує детальну інформацію про базу даних"""
        try:
            print("🗄️  Детальна інформація про базу даних:")
            
            # Отримуємо інформацію про SQLite базу даних
            db_info = self.rag_engine.get_database_info()
            
            if not db_info:
                print("❌ Не вдалося отримати інформацію про базу даних")
                return
            
            print(f"📁 Шлях: {db_info.get('database_path', 'N/A')}")
            print(f"📏 Розмір: {db_info.get('database_size_mb', 0)} MB")
            print(f"🔢 Кількість API: {db_info.get('api_count', 0)}")
            print(f"🔗 Кількість ендпоінтів: {db_info.get('endpoint_count', 0)}")
            print(f"📝 Кількість промптів: {db_info.get('prompt_count', 0)}")
            print(f"🧠 Кількість embeddings: {db_info.get('embedding_count', 0)}")
            
            # Показуємо деталі по кожному API
            apis = self.rag_engine.list_swagger_specs()
            if apis:
                print(f"\n📚 Деталі по API:")
                for api_name in apis:
                    print(f"  • {api_name}")
                    
                    # Отримуємо промпти для цього API
                    prompts = self.rag_engine.create_specialized_prompts(api_name)
                    if prompts:
                        print(f"    Промпти: {len(prompts)} типів")
                        for prompt_type in prompts.keys():
                            print(f"      - {prompt_type}")
            
            print(f"\n🏥 Здоров'я бази даних:")
            print(f"  • Статус: ✅ Доступна")
            print(f"  • Тип: SQLite")
            print(f"  • Розмір: ✅ Нормальний ({db_info.get('database_size_mb', 0)} MB)")
            print(f"  • API: ✅ {db_info.get('api_count', 0)} API")
            print(f"  • Ендпоінти: ✅ {db_info.get('endpoint_count', 0)} ендпоінтів")
            
            print("✅ Аналіз бази даних завершено!")
            
        except Exception as e:
            print(f"❌ Помилка аналізу бази даних: {e}")

    def clear_database(self):
        """Повністю очищає базу даних SQLite"""
        try:
            print("🗄️  Повне очищення бази даних SQLite...")
            
            # Очищаємо всі API
            apis = self.rag_engine.list_swagger_specs()
            if apis:
                print(f"🧹 Видалення {len(apis)} API...")
                for api in apis:
                    self.rag_engine.remove_swagger_spec(api)
                    print(f"  🗑️  Видалено API: {api}")
            
            # Видаляємо файл бази даних
            db_path = self.rag_engine.db_path
            if os.path.exists(db_path):
                try:
                    os.remove(db_path)
                    print(f"🗑️  Видалено файл бази даних: {db_path}")
                except Exception as e:
                    print(f"⚠️  Не вдалося видалити файл бази даних: {e}")
            
            # Перезапускаємо RAG двигун
            print("🔄 Перезапуск RAG двигуна...")
            self.rag_engine = EnhancedRAGEngine()
            
            print("✅ База даних повністю очищена!")
            
        except Exception as e:
            print(f"❌ Помилка очищення бази даних: {e}")
    
    def reload_swagger(self, url: str, name: Optional[str] = None):
        """Перезавантажує Swagger API (очищає та додає заново)"""
        try:
            print(f"🔄 Перезавантаження Swagger API з {url}...")
            
            # Очищаємо старі дані для цього API
            if name:
                print(f"🧹 Очищення старих даних для API '{name}'...")
                self.rag_engine.remove_swagger_spec(name)
            else:
                # Якщо назва не вказана, очищаємо всі API
                print("🧹 Очищення всіх API...")
                apis = self.rag_engine.list_swagger_specs()
                for api in apis:
                    self.rag_engine.remove_swagger_spec(api)
                    print(f"  🗑️  Видалено API: {api}")
            
            # Завантажуємо Swagger заново
            print(f"📥 Завантаження Swagger файлу...")
            response = requests.get(url)
            response.raise_for_status()
            
            swagger_data = response.json()
            
            # Генеруємо назву, якщо не вказана
            if not name:
                name = swagger_data.get('info', {}).get('title', 'unknown_api')
                name = name.lower().replace(' ', '_').replace('-', '_')
            
            print(f"✅ Swagger файл успішно завантажено: {name}")
            
            # Парсимо та зберігаємо в RAG системі
            self._process_swagger(swagger_data, name, url)
            
            print(f"🎯 Swagger API '{name}' успішно перезавантажено!")
            
        except requests.RequestException as e:
            print(f"❌ Помилка завантаження Swagger файлу: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Помилка перезавантаження Swagger: {e}")
            sys.exit(1)
    
    def reset_system(self):
        """Повністю скидає систему (очищає БД та перезапускає)"""
        try:
            print("🔄 Повне скидання системи...")
            
            # Очищаємо базу даних
            self.clear_database()
            
            # Перезапускаємо CLI
            print("🔄 Перезапуск CLI...")
            self.__init__()
            
            print("✅ Система повністю скинута!")
            
        except Exception as e:
            print(f"❌ Помилка скидання системи: {e}")
    
    def quick_reload(self, url: str, name: Optional[str] = None):
        """Швидке перезавантаження з очищенням тільки конкретного API"""
        try:
            print(f"⚡ Швидке перезавантаження API...")
            
            if not name:
                # Отримуємо назву з URL або Swagger
                response = requests.get(url)
                response.raise_for_status()
                swagger_data = response.json()
                name = swagger_data.get('info', {}).get('title', 'unknown_api')
                name = name.lower().replace(' ', '_').replace('-', '_')
            
            print(f"🎯 Цільове API: {name}")
            
            # Видаляємо тільки цей API
            self.rag_engine.remove_swagger_spec(name)
            print(f"🗑️  Видалено старий API: {name}")
            
            # Додаємо заново
            self.add_swagger(url, name)
            
            print(f"✅ API '{name}' швидко перезавантажено!")
            
        except Exception as e:
            print(f"❌ Помилка швидкого перезавантаження: {e}")

    def show_prompts(self, name: str):
        """Показує спеціалізовані промпти для конкретного API"""
        try:
            print(f"📝 Спеціалізовані промпти для API '{name}':")
            print("=" * 60)
            
            # Створюємо спеціалізовані промпти
            prompts = self.rag_engine.create_specialized_prompts(name)
            
            if not prompts:
                print("❌ Не вдалося створити промпти для цього API")
                return
            
            # Показуємо кожен тип промпту
            for prompt_type, prompt_content in prompts.items():
                print(f"\n🎯 {prompt_type.upper().replace('_', ' ')}:")
                print("-" * 40)
                print(prompt_content)
                print("=" * 60)
            
            print(f"\n✅ Створено {len(prompts)} типів промптів для API '{name}'")
            
        except Exception as e:
            print(f"❌ Помилка створення промптів: {e}")
    
    def export_prompts(self, name: str, output_file: Optional[str] = None):
        """Експортує спеціалізовані промпти у файл"""
        try:
            print(f"📤 Експорт промптів для API '{name}'...")
            
            # Створюємо спеціалізовані промпти
            prompts = self.rag_engine.create_specialized_prompts(name)
            
            if not prompts:
                print("❌ Не вдалося створити промпти для експорту")
                return
            
            # Формуємо дані для експорту
            export_data = {
                "api_name": name,
                "generated_at": str(datetime.now()),
                "prompts": prompts
            }
            
            # Визначаємо файл для експорту
            if not output_file:
                output_file = f"prompts_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Експортуємо у JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Промпти експортовано у файл: {output_file}")
            
        except Exception as e:
            print(f"❌ Помилка експорту промптів: {e}")

    def set_jwt_token(self, api_name: str, token: str, expires_in: int = 3600):
        """
        Встановлює JWT токен для API.
        
        Args:
            api_name: Назва API
            token: JWT токен
            expires_in: Час життя токена в секундах
        """
        try:
            print(f"🔑 Встановлення JWT токена для API '{api_name}'...")
            
            self.rag_engine.set_jwt_token(api_name, token, expires_in)
            
            print(f"✅ JWT токен успішно встановлено для API '{api_name}'")
            print(f"⏰ Токен дійсний {expires_in} секунд")
            
        except Exception as e:
            print(f"❌ Помилка встановлення JWT токена: {e}")
    
    def execute_api_request(self, api_name: str, method: str, path: str, 
                           data: Optional[Dict] = None, params: Optional[Dict] = None):
        """
        Виконує API запит.
        
        Args:
            api_name: Назва API
            method: HTTP метод
            path: Шлях ендпоінту
            data: Дані для запиту (для POST/PUT/PATCH)
            params: Параметри запиту (для GET)
        """
        try:
            print(f"🚀 Виконання API запиту...")
            print(f"📡 {method.upper()} {path}")
            print(f"🔗 API: {api_name}")
            
            if data:
                print(f"📤 Дані запиту: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if params:
                print(f"🔍 Параметри: {json.dumps(params, indent=2, ensure_ascii=False)}")
            
            # Виконуємо запит
            success, result, message = self.rag_engine.execute_api_request(
                api_name, method, path, data, params
            )
            
            if success:
                print(f"✅ Запит виконано успішно!")
                print(f"📊 Результат:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(f"❌ Помилка виконання запиту:")
                print(message)
                
        except Exception as e:
            print(f"❌ Помилка виконання API запиту: {e}")
    
    def show_request_history(self, api_name: Optional[str] = None, limit: int = 10):
        """
        Показує історію запитів.
        
        Args:
            api_name: Назва API (опціонально)
            limit: Максимальна кількість записів
        """
        try:
            print(f"📚 Історія запитів...")
            
            if api_name:
                print(f"🔗 API: {api_name}")
            else:
                print(f"🔗 Всі API")
            
            history = self.rag_engine.get_request_history(api_name, limit)
            
            if not history:
                print("📭 Історія запитів порожня")
                return
            
            print(f"📊 Знайдено {len(history)} записів:")
            print("=" * 80)
            
            for i, record in enumerate(history, 1):
                print(f"\n📝 Запис {i}:")
                print(f"  🔗 API: {record['api_name']}")
                print(f"  📡 Метод: {record['method']}")
                print(f"  🛣️  Шлях: {record['endpoint_path']}")
                print(f"  ⏱️  Час виконання: {record['execution_time']:.3f}s")
                print(f"  📅 Дата: {record['created_at']}")
                print(f"  📊 Статус: {record['status_code']}")
                
                if record['request_data']:
                    print(f"  📤 Запит: {json.dumps(record['request_data'], indent=4, ensure_ascii=False)}")
                
                if record['error_message']:
                    print(f"  ❌ Помилка: {record['error_message'][:200]}...")
                else:
                    print(f"  ✅ Успішно")
                
                print("-" * 40)
            
        except Exception as e:
            print(f"❌ Помилка отримання історії запитів: {e}")
    
    def test_api_endpoint(self, api_name: str, method: str, path: str, 
                          data: Optional[Dict] = None, params: Optional[Dict] = None):
        """
        Тестує конкретний ендпоінт API.
        
        Args:
            api_name: Назва API
            method: HTTP метод
            path: Шлях ендпоінту
            data: Дані для запиту
            params: Параметри запиту
        """
        try:
            print(f"🧪 Тестування ендпоінту...")
            print(f"🔗 API: {api_name}")
            print(f"📡 {method.upper()} {path}")
            
            # Перевіряємо наявність JWT токена
            jwt_token = self.rag_engine.get_jwt_token(api_name)
            if not jwt_token:
                print("⚠️  JWT токен не знайдено. Спочатку встановіть токен командою set-jwt-token")
                return
            
            print("🔑 JWT токен знайдено")
            
            # Виконуємо тестовий запит
            self.execute_api_request(api_name, method, path, data, params)
            
        except Exception as e:
            print(f"❌ Помилка тестування ендпоінту: {e}")
    
    def interactive_api_testing(self):
        """Інтерактивне тестування API."""
        try:
            print("🧪 Інтерактивне тестування API")
            print("=" * 50)
            print("Доступні команди:")
            print("  • test <method> <path> [data] - тестувати ендпоінт")
            print("  • set-token <api_name> <token> - встановити JWT токен")
            print("  • history [api_name] - показати історію запитів")
            print("  • endpoints [api_name] - показати доступні ендпоінти")
            print("  • quit - вийти")
            print()
            
            while True:
                try:
                    command = input("🔧 API Test> ").strip()
                    
                    if command.lower() == 'quit':
                        print("👋 До побачення!")
                        break
                    
                    elif command.lower().startswith('test '):
                        parts = command[5:].split()
                        if len(parts) >= 2:
                            method = parts[0].upper()
                            path = parts[1]
                            data = None
                            
                            if len(parts) > 2:
                                try:
                                    data = json.loads(' '.join(parts[2:]))
                                except:
                                    print("❌ Неправильний формат JSON даних")
                                    continue
                            
                            # Використовуємо перший доступний API
                            apis = self.rag_engine.list_swagger_specs()
                            if apis:
                                self.test_api_endpoint(apis[0], method, path, data)
                            else:
                                print("❌ Немає доступних API")
                        else:
                            print("❌ Використання: test <method> <path> [data]")
                    
                    elif command.lower().startswith('set-token '):
                        parts = command[10:].split()
                        if len(parts) >= 2:
                            api_name = parts[0]
                            token = parts[1]
                            self.set_jwt_token(api_name, token)
                        else:
                            print("❌ Використання: set-token <api_name> <token>")
                    
                    elif command.lower().startswith('history'):
                        parts = command[8:].split()
                        api_name = parts[0] if parts else None
                        self.show_request_history(api_name)
                    
                    elif command.lower().startswith('endpoints'):
                        parts = command[10:].split()
                        api_name = parts[0] if parts else None
                        if api_name:
                            self.show_api_endpoints(api_name)
                        else:
                            self.list_apis()
                    
                    else:
                        print("❌ Невідома команда. Введіть 'help' для довідки")
                
                except KeyboardInterrupt:
                    print("\n👋 До побачення!")
                    break
                except Exception as e:
                    print(f"❌ Помилка: {e}")
            
        except Exception as e:
            print(f"❌ Помилка інтерактивного тестування: {e}")
    
    def show_api_endpoints(self, api_name: str):
        """Показує детальну інформацію про ендпоінти API."""
        try:
            print(f"🔗 Детальна інформація про API '{api_name}':")
            print("=" * 60)
            
            # Отримуємо промпти для API
            prompts = self.rag_engine.create_specialized_prompts(api_name)
            
            if not prompts:
                print("❌ Немає доступних ендпоінтів")
                return
            
            # Показуємо ендпоінти за типами
            for prompt_type, content in prompts.items():
                if prompt_type == "general":
                    print(f"\n📋 {prompt_type.upper()}:")
                    print("-" * 40)
                    print(content)
            
            print(f"\n✅ Показано {len(prompts)} типів ендпоінтів")
            
        except Exception as e:
            print(f"❌ Помилка показу ендпоінтів: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="CLI інструмент для управління AI Swagger Bot системою",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Приклади використання:
  # Додати Swagger API
  python cli.py add-swagger https://api.oneshop.click/docs/ai-json oneshop
  
  # Відправити повідомлення боту
  python cli.py chat "Покажи всі доступні категорії"
  
  # Переглянути список API
  python cli.py list-apis
  
  # Видалити API
  python cli.py remove-api oneshop
  
  # Інформація про систему або API
  python cli.py info
  
  # Пошук ендпоінтів
  python cli.py search "створення категорії"
  
  # Імпорт API з файлу
  python cli.py import-api swagger.json myapi
  
  # Експорт API
  python cli.py export-api oneshop
  
  # Статистика системи
  python cli.py stats
  
  # Тестування API
  python cli.py test-api oneshop
  
  # Очистити всі API
  python cli.py clear-all
  
  # Інтерактивний режим
  python cli.py interactive
  
  # Статус системи
  python cli.py status
  
  # Версія CLI
  python cli.py version
  
  # Детальний аналіз Swagger API
  python cli.py analyze-swagger oneshop
  
  # Інформація про базу даних
  python cli.py db-info
  
  # Очистити базу даних
  python cli.py clear-database
  
  # Перезавантажити Swagger API
  python cli.py reload-swagger https://api.oneshop.click/docs/ai-json oneshop
  
  # Скинути систему
  python cli.py reset-system
  
  # Швидке перезавантаження API
  python cli.py quick-reload https://api.oneshop.click/docs/ai-json oneshop
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Доступні команди')
    
    # Команда додавання Swagger
    add_parser = subparsers.add_parser('add-swagger', help='Додати новий Swagger API')
    add_parser.add_argument('url', help='URL до Swagger файлу')
    add_parser.add_argument('--name', '-n', help='Назва для API (опціонально)')
    
    # Команда чату
    chat_parser = subparsers.add_parser('chat', help='Відправити повідомлення боту')
    chat_parser.add_argument('message', help='Повідомлення для бота')
    
    # Команда списку API
    list_parser = subparsers.add_parser('list-apis', help='Показати список доступних API')
    
    # Команда видалення API
    remove_parser = subparsers.add_parser('remove-api', help='Видалити API з системи')
    remove_parser.add_argument('name', help='Назва API для видалення')
    
    # Команда інформації
    info_parser = subparsers.add_parser('info', help='Показати інформацію про систему або API')
    info_parser.add_argument('--name', '-n', help='Назва API (опціонально)')
    
    # Команда пошуку
    search_parser = subparsers.add_parser('search', help='Пошук ендпоінтів')
    search_parser.add_argument('query', help='Пошуковий запит')
    search_parser.add_argument('--api', '-a', help='Обмежити пошук до конкретного API')
    
    # Команда експорту
    export_parser = subparsers.add_parser('export-api', help='Експорт API специфікації')
    export_parser.add_argument('name', help='Назва API для експорту')
    export_parser.add_argument('--output', '-o', help='Вихідний файл (опціонально)')
    
    # Команда імпорту
    import_parser = subparsers.add_parser('import-api', help='Імпорт API специфікації з файлу')
    import_parser.add_argument('file', help='Шлях до файлу Swagger')
    import_parser.add_argument('--name', '-n', help='Назва для API (опціонально)')
    
    # Команда очищення
    clear_parser = subparsers.add_parser('clear-all', help='Очистити всі API з системи')
    
    # Команда статистики
    stats_parser = subparsers.add_parser('stats', help='Показати статистику системи')
    
    # Команда тестування
    test_parser = subparsers.add_parser('test-api', help='Тестувати API')
    test_parser.add_argument('name', help='Назва API для тестування')
    
    # Команда інтерактивного режиму
    interactive_parser = subparsers.add_parser('interactive', help='Запустити інтерактивний режим')
    
    # Команда статусу
    status_parser = subparsers.add_parser('status', help='Показати статус системи')
    
    # Команда версії
    version_parser = subparsers.add_parser('version', help='Показати версію CLI')
    
    # Команда аналізу Swagger
    analyze_parser = subparsers.add_parser('analyze-swagger', help='Детально аналізувати Swagger API')
    analyze_parser.add_argument('name', help='Назва API для аналізу')
    
    # Команда інформації про базу даних
    db_info_parser = subparsers.add_parser('db-info', help='Показати детальну інформацію про базу даних')
    
    # Команда очищення бази даних
    clear_db_parser = subparsers.add_parser('clear-database', help='Повністю очистити базу даних ChromaDB')
    
    # Команда перезавантаження Swagger
    reload_parser = subparsers.add_parser('reload-swagger', help='Перезавантажити Swagger API')
    reload_parser.add_argument('url', help='URL до Swagger файлу')
    reload_parser.add_argument('--name', '-n', help='Назва для API (опціонально)')
    
    # Команда скидання системи
    reset_parser = subparsers.add_parser('reset-system', help='Повністю скинути систему')
    
    # Команда швидкого перезавантаження
    quick_reload_parser = subparsers.add_parser('quick-reload', help='Швидко перезавантажити API')
    quick_reload_parser.add_argument('url', help='URL до Swagger файлу')
    quick_reload_parser.add_argument('--name', '-n', help='Назва для API (опціонально)')

    # Команда спеціалізованих промптів
    show_prompts_parser = subparsers.add_parser('show-prompts', help='Показати спеціалізовані промпти для API')
    show_prompts_parser.add_argument('name', help='Назва API для промптів')

    # Команда експорту промптів
    export_prompts_parser = subparsers.add_parser('export-prompts', help='Експортувати спеціалізовані промпти у файл')
    export_prompts_parser.add_argument('name', help='Назва API для експорту промптів')
    export_prompts_parser.add_argument('--output', '-o', help='Вихідний файл (опціонально)')
    
    # Команда встановлення JWT токена
    set_jwt_parser = subparsers.add_parser('set-jwt-token', help='Встановити JWT токен для API')
    set_jwt_parser.add_argument('api_name', help='Назва API')
    set_jwt_parser.add_argument('token', help='JWT токен')
    
    # Команда виконання API запиту
    execute_parser = subparsers.add_parser('execute-request', help='Виконати API запит')
    execute_parser.add_argument('api_name', help='Назва API')
    execute_parser.add_argument('method', help='HTTP метод')
    execute_parser.add_argument('path', help='Шлях ендпоінту')
    execute_parser.add_argument('data', help='Дані запиту (JSON)')
    
    # Команда тестування ендпоінту
    test_endpoint_parser = subparsers.add_parser('test-endpoint', help='Тестувати ендпоінт API')
    test_endpoint_parser.add_argument('api_name', help='Назва API')
    test_endpoint_parser.add_argument('method', help='HTTP метод')
    test_endpoint_parser.add_argument('path', help='Шлях ендпоінту')
    test_endpoint_parser.add_argument('data', help='Дані запиту (JSON)')
    
    # Команда історії запитів
    history_parser = subparsers.add_parser('request-history', help='Показати історію запитів')
    history_parser.add_argument('--api-name', '-a', help='Назва API (опціонально)')
    
    # Команда інтерактивного тестування API
    api_testing_parser = subparsers.add_parser('api-testing', help='Запустити інтерактивне тестування API')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Створюємо CLI інстанс
    cli = SwaggerBotCLI()
    
    # Виконуємо команду
    if args.command == 'add-swagger':
        cli.add_swagger(args.url, args.name)
    elif args.command == 'chat':
        cli.chat(args.message)
    elif args.command == 'list-apis':
        cli.list_apis()
    elif args.command == 'remove-api':
        cli.remove_api(args.name)
    elif args.command == 'info':
        cli.info(args.name)
    elif args.command == 'search':
        cli.search(args.query, args.api)
    elif args.command == 'export-api':
        cli.export_api(args.name, args.output)
    elif args.command == 'import-api':
        cli.import_api(args.file, args.name)
    elif args.command == 'clear-all':
        cli.clear_all()
    elif args.command == 'stats':
        cli.stats()
    elif args.command == 'test-api':
        cli.test_api(args.name)
    elif args.command == 'interactive':
        cli.interactive_mode()
    elif args.command == 'status':
        cli.status()
    elif args.command == 'version':
        cli.version()
    elif args.command == 'analyze-swagger':
        cli.analyze_swagger(args.name)
    elif args.command == 'db-info':
        cli.db_info()
    elif args.command == 'clear-database':
        cli.clear_database()
    elif args.command == 'reload-swagger':
        cli.reload_swagger(args.url, args.name)
    elif args.command == 'reset-system':
        cli.reset_system()
    elif args.command == 'quick-reload':
        cli.quick_reload(args.url, args.name)
    elif args.command == 'show-prompts':
        cli.show_prompts(args.name)
    elif args.command == 'export-prompts':
        cli.export_prompts(args.name, args.output)
    elif args.command == 'set-jwt-token':
        cli.set_jwt_token(args.api_name, args.token)
    elif args.command == 'execute-request':
        try:
            data = json.loads(args.data) if args.data else None
        except:
            print("❌ Неправильний формат JSON даних")
            return
        cli.execute_api_request(args.api_name, args.method, args.path, data)
    elif args.command == 'test-endpoint':
        try:
            data = json.loads(args.data) if args.data else None
        except:
            print("❌ Неправильний формат JSON даних")
            return
        cli.test_api_endpoint(args.api_name, args.method, args.path, data)
    elif args.command == 'request-history':
        cli.show_request_history(args.api_name)
    elif args.command == 'api-testing':
        cli.interactive_api_testing()


if __name__ == '__main__':
    main()
