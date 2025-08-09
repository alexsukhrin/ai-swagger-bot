#!/usr/bin/env python3
"""
CLI інтерфейс для тестування AI Swagger Bot API
Дозволяє виконувати команди без авторизації для тестування
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional

import requests

from src.postgres_prompt_manager import PostgresPromptManager, PromptTemplate


class APITester:
    """CLI тестер для AI Swagger Bot API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.current_user = None
        self.current_token = None

    def print_response(self, response: requests.Response, show_headers: bool = False) -> None:
        """Виводить відповідь API в зручному форматі"""
        print(f"\n{'='*60}")
        print(f"📡 {response.request.method} {response.request.url}")
        print(f"📊 Статус: {response.status_code} {response.reason}")

        if show_headers:
            print(f"📋 Заголовки відповіді:")
            for key, value in response.headers.items():
                print(f"   {key}: {value}")

        try:
            data = response.json()
            print(f"📦 Дані відповіді:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print(f"📄 Текст відповіді:")
            print(response.text)

        print(f"{'='*60}\n")

    def health_check(self) -> None:
        """Перевірка стану сервісу"""
        print("🏥 Перевірка стану сервісу...")
        response = self.session.get(f"{self.base_url}/health")
        self.print_response(response)

    def create_demo_user(self) -> None:
        """Створення демо користувача"""
        print("👤 Створення демо користувача...")
        response = self.session.post(f"{self.base_url}/demo/create-user")
        self.print_response(response)

        if response.status_code == 200:
            data = response.json()
            # Створюємо об'єкт користувача з даних API
            self.current_user = {
                "id": data.get("user_id"),
                "email": f"{data.get('user_id')}@demo.com",
                "username": data.get("user_id"),
            }
            self.current_token = data.get("token")
            print(f"✅ Демо користувач створений!")
            print(f"   ID: {self.current_user.get('id')}")
            print(f"   Email: {self.current_user.get('email')}")
            print(f"   Token: {self.current_token[:20]}...")

    def upload_swagger(self, file_path: str) -> None:
        """Завантаження Swagger файлу"""
        if not self.current_token:
            print("❌ Спочатку створіть демо користувача!")
            return

        print(f"📁 Завантаження Swagger файлу: {file_path}")

        try:
            with open(file_path, "rb") as f:
                files = {"file": f}
                headers = {"Authorization": f"Bearer {self.current_token}"}
                response = self.session.post(
                    f"{self.base_url}/upload-swagger", files=files, headers=headers
                )
                self.print_response(response)
        except FileNotFoundError:
            print(f"❌ Файл не знайдено: {file_path}")
        except Exception as e:
            print(f"❌ Помилка завантаження: {e}")

    def chat(self, message: str) -> None:
        """Чат з AI агентом"""
        if not self.current_token:
            print("❌ Спочатку створіть демо користувача!")
            return

        print(f"💬 Чат: {message}")

        data = {"message": message}
        headers = {
            "Authorization": f"Bearer {self.current_token}",
            "Content-Type": "application/json",
        }

        response = self.session.post(f"{self.base_url}/chat", json=data, headers=headers)
        self.print_response(response)

    def get_chat_history(self) -> None:
        """Отримання історії чату"""
        if not self.current_token:
            print("❌ Спочатку створіть демо користувача!")
            return

        print("📜 Отримання історії чату...")

        headers = {"Authorization": f"Bearer {self.current_token}"}
        response = self.session.get(f"{self.base_url}/chat-history", headers=headers)
        self.print_response(response)

    def get_prompts(self, category: Optional[str] = None, search: Optional[str] = None) -> None:
        """Отримання промптів"""
        if not self.current_token:
            print("❌ Спочатку створіть демо користувача!")
            return

        print("📝 Отримання промптів...")

        params = {}
        if category:
            params["category"] = category
        if search:
            params["search"] = search

        headers = {"Authorization": f"Bearer {self.current_token}"}
        response = self.session.get(f"{self.base_url}/prompts/", params=params, headers=headers)
        self.print_response(response)

    def get_prompt_categories(self) -> None:
        """Отримання категорій промптів"""
        if not self.current_token:
            print("❌ Спочатку створіть демо користувача!")
            return

        print("📂 Отримання категорій промптів...")

        headers = {"Authorization": f"Bearer {self.current_token}"}
        response = self.session.get(f"{self.base_url}/prompts/categories", headers=headers)
        self.print_response(response)

    def get_prompt_statistics(self) -> None:
        """Отримання статистики промптів"""
        if not self.current_token:
            print("❌ Спочатку створіть демо користувача!")
            return

        print("📊 Отримання статистики промптів...")

        headers = {"Authorization": f"Bearer {self.current_token}"}
        response = self.session.get(f"{self.base_url}/prompts/statistics", headers=headers)
        self.print_response(response)

    def get_swagger_specs(self) -> None:
        """Отримання списку Swagger специфікацій"""
        if not self.current_token:
            print("❌ Спочатку створіть демо користувача!")
            return

        print("📋 Отримання списку Swagger специфікацій...")

        headers = {"Authorization": f"Bearer {self.current_token}"}
        response = self.session.get(f"{self.base_url}/swagger-specs", headers=headers)
        self.print_response(response)

    def get_user_info(self) -> None:
        """Отримання інформації про користувача"""
        if not self.current_token:
            print("❌ Спочатку створіть демо користувача!")
            return

        print("👤 Отримання інформації про користувача...")

        headers = {"Authorization": f"Bearer {self.current_token}"}
        response = self.session.get(f"{self.base_url}/users/me", headers=headers)
        self.print_response(response)

    def create_custom_prompt(
        self, name: str, description: str, template: str, category: str
    ) -> None:
        """Створення кастомного промпту"""
        if not self.current_token:
            print("❌ Спочатку створіть демо користувача!")
            return

        print(f"✨ Створення кастомного промпту: {name}")

        data = {
            "name": name,
            "description": description,
            "template": template,
            "category": category,
            "is_public": False,
        }

        headers = {
            "Authorization": f"Bearer {self.current_token}",
            "Content-Type": "application/json",
        }

        response = self.session.post(f"{self.base_url}/prompts/", json=data, headers=headers)
        self.print_response(response)

    def search_prompts(self, query: str, category: Optional[str] = None) -> None:
        """Пошук промптів"""
        if not self.current_token:
            print("❌ Спочатку створіть демо користувача!")
            return

        print(f"🔍 Пошук промптів: {query}")

        params = {"query": query}
        if category:
            params["category"] = category

        headers = {"Authorization": f"Bearer {self.current_token}"}
        response = self.session.get(
            f"{self.base_url}/prompts/search", params=params, headers=headers
        )
        self.print_response(response)

    def get_prompt_suggestions(self, query: str, context: str = "") -> None:
        """Отримання пропозицій промптів"""
        if not self.current_token:
            print("❌ Спочатку створіть демо користувача!")
            return

        print(f"💡 Отримання пропозицій для: {query}")

        params = {"query": query}
        if context:
            params["context"] = context

        headers = {"Authorization": f"Bearer {self.current_token}"}
        response = self.session.get(
            f"{self.base_url}/prompts/suggestions", params=params, headers=headers
        )
        self.print_response(response)

    def format_prompt(self, prompt_id: str, **parameters) -> None:
        """Форматування промпту з параметрами"""
        if not self.current_token:
            print("❌ Спочатку створіть демо користувача!")
            return

        print(f"🔧 Форматування промпту: {prompt_id}")

        data = {"prompt_id": prompt_id, "parameters": parameters}

        headers = {
            "Authorization": f"Bearer {self.current_token}",
            "Content-Type": "application/json",
        }

        response = self.session.post(f"{self.base_url}/prompts/format", json=data, headers=headers)
        self.print_response(response)

    def export_prompts(self, include_custom: bool = True) -> None:
        """Експорт промптів"""
        if not self.current_token:
            print("❌ Спочатку створіть демо користувача!")
            return

        print("📤 Експорт промптів...")

        params = {"include_custom": include_custom}
        headers = {"Authorization": f"Bearer {self.current_token}"}
        response = self.session.post(
            f"{self.base_url}/prompts/export", params=params, headers=headers
        )
        self.print_response(response)

    def reload_prompts(self) -> None:
        """Перезавантаження базових промптів"""
        if not self.current_token:
            print("❌ Спочатку створіть демо користувача!")
            return

        print("🔄 Перезавантаження базових промптів...")

        headers = {"Authorization": f"Bearer {self.current_token}"}
        response = self.session.post(f"{self.base_url}/prompts/reload", headers=headers)
        self.print_response(response)

    def show_status(self) -> None:
        """Показати поточний статус"""
        print("📊 Поточний статус:")
        print(f"   Base URL: {self.base_url}")
        if self.current_user:
            print(f"   Користувач: {self.current_user.get('email', 'Невідомий')}")
        else:
            print(f"   Користувач: Не створений")
        print(f"   Token: {'Так' if self.current_token else 'Ні'}")
        print(f"   Час: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def generate_prompts_from_swagger(self, swagger_file: str, api_key: str = None) -> None:
        """Генерує промпти через GPT на основі Swagger файлу."""
        try:
            # Читаємо Swagger файл
            with open(swagger_file, "r", encoding="utf-8") as f:
                swagger_data = json.load(f)

            print(f"📁 Завантажено Swagger файл: {swagger_file}")
            print(f"🔍 Аналізую {len(swagger_data.get('paths', {}))} endpoints...")

            # Генеруємо промпти
            response = self.session.post(
                f"{self.base_url}/prompts/generate-from-swagger",
                json={"swagger_data": swagger_data, "api_key": api_key},
            )

            if response.status_code == 200:
                data = response.json()
                print(f"✅ {data['message']}")
                print(f"📊 Згенеровано: {data['generated_count']} промптів")
                print(f"💾 Збережено: {data['saved_count']} промптів")

                if data.get("prompts"):
                    print("\n📋 Деталі згенерованих промптів:")
                    for prompt in data["prompts"]:
                        print(f"  • {prompt['name']} ({prompt['category']})")
                        print(f"    Ресурс: {prompt['resource_type']}")
                        print(f"    Endpoint: {prompt['http_method']} {prompt['endpoint_path']}")
                        print()
            else:
                print(f"❌ Помилка генерації промптів: {response.status_code}")
                print(f"Відповідь: {response.text}")

        except FileNotFoundError:
            print(f"❌ Файл не знайдено: {swagger_file}")
        except json.JSONDecodeError:
            print(f"❌ Помилка парсингу JSON файлу: {swagger_file}")
        except Exception as e:
            print(f"❌ Помилка: {e}")

    def generate_smart_suggestions(self, swagger_file: str, api_key: str = None) -> None:
        """Генерує розумні підказки через GPT на основі Swagger файлу."""
        try:
            # Читаємо Swagger файл
            with open(swagger_file, "r", encoding="utf-8") as f:
                swagger_data = json.load(f)

            print(f"📁 Завантажено Swagger файл: {swagger_file}")
            print(f"🎯 Генерую розумні підказки...")

            # Генеруємо підказки
            response = self.session.post(
                f"{self.base_url}/prompts/generate-suggestions",
                json={"swagger_data": swagger_data, "api_key": api_key},
            )

            if response.status_code == 200:
                data = response.json()
                print(f"✅ {data['message']}")
                print(f"💡 Згенеровано: {data['suggestions_count']} підказок")

                if data.get("suggestions"):
                    print("\n📋 Згенеровані підказки:")
                    for i, suggestion in enumerate(data["suggestions"], 1):
                        print(f"  {i}. {suggestion.get('title', 'Підказка')}")
                        print(f"     Категорія: {suggestion.get('category', 'Інші')}")
                        print(f"     Складність: {suggestion.get('difficulty', 'medium')}")
                        if suggestion.get("description"):
                            print(f"     Опис: {suggestion['description']}")
                        if suggestion.get("example_query"):
                            print(f"     Приклад: {suggestion['example_query']}")
                        print()
            else:
                print(f"❌ Помилка генерації підказок: {response.status_code}")
                print(f"Відповідь: {response.text}")

        except FileNotFoundError:
            print(f"❌ Файл не знайдено: {swagger_file}")
        except json.JSONDecodeError:
            print(f"❌ Помилка парсингу JSON файлу: {swagger_file}")
        except Exception as e:
            print(f"❌ Помилка: {e}")

    def auto_generate_prompts_for_user(self, swagger_spec_id: str, api_key: str = None) -> None:
        """Автоматично генерує промпти для користувача."""
        print("🤖 Автоматична генерація промптів для користувача...")

        data = {"swagger_spec_id": swagger_spec_id}

        if api_key:
            data["api_key"] = api_key

        response = requests.post(f"{self.base_url}/prompts/auto-generate-for-user", json=data)
        self.print_response(response)

    def test_postgres_prompts(self) -> None:
        """Тестування PostgreSQL промптів."""
        print("🧪 Тестування PostgreSQL промптів...")

        try:
            from src.postgres_prompt_manager import PostgresPromptManager, PromptTemplate

            manager = PostgresPromptManager()

            # Додаємо тестовий промпт
            test_prompt = PromptTemplate(
                name="Тестовий промпт PostgreSQL",
                description="Промпт для тестування PostgreSQL",
                template="Це тестовий промпт з PostgreSQL",
                category="test",
                tags=["test", "demo", "postgresql"],
            )

            prompt_id = manager.add_prompt(test_prompt)
            print(f"✅ Додано тестовий промпт з ID: {prompt_id}")

            # Отримуємо промпт
            retrieved_prompt = manager.get_prompt(prompt_id)
            if retrieved_prompt:
                print(f"✅ Отримано промпт: {retrieved_prompt.name}")

            # Шукаємо промпти
            search_results = manager.search_prompts("тест")
            print(f"✅ Знайдено {len(search_results)} промптів при пошуку")

            # Статистика
            stats = manager.get_statistics()
            print(f"📊 Статистика: {stats['total_prompts']} промптів")

        except Exception as e:
            print(f"❌ Помилка тестування PostgreSQL промптів: {e}")

    def migrate_prompts(self) -> None:
        """Міграція промптів з SQLite в PostgreSQL."""
        print("🔄 Міграція промптів з SQLite в PostgreSQL...")

        try:
            from src.postgres_prompt_manager import PostgresPromptManager

            manager = PostgresPromptManager()
            manager.migrate_from_sqlite("prompts.db")
            print("✅ Міграція завершена успішно!")

        except Exception as e:
            print(f"❌ Помилка міграції: {e}")

    def list_postgres_prompts(self) -> None:
        """Показує всі промпти в PostgreSQL."""
        print("📋 Список промптів в PostgreSQL...")

        try:
            from sqlalchemy import text

            from src.postgres_prompt_manager import PostgresPromptManager

            manager = PostgresPromptManager()

            # Отримуємо всі промпти
            with manager.get_db_session() as session:
                result = session.execute(
                    text(
                        """
                    SELECT id, name, description, category, is_active, created_at
                    FROM prompt_templates
                    ORDER BY created_at DESC
                """
                    )
                )

                prompts = result.fetchall()

                if not prompts:
                    print("📭 Промпти не знайдено")
                    return

                print(f"📊 Знайдено {len(prompts)} промптів:")
                print("-" * 80)

                for i, prompt in enumerate(prompts, 1):
                    status = "✅" if prompt[4] else "❌"
                    print(f"{i:2d}. {status} {prompt[1]}")
                    print(f"     ID: {prompt[0]}")
                    print(f"     Категорія: {prompt[3]}")
                    print(f"     Створено: {prompt[5]}")
                    if prompt[2]:
                        print(f"     Опис: {prompt[2][:50]}...")
                    print()

        except Exception as e:
            print(f"❌ Помилка отримання промптів: {e}")

    def remove_sqlite_files(self) -> None:
        """Видаляє SQLite файли."""
        print("🗑️ Видалення SQLite файлів...")
        try:
            import os

            sqlite_files = ["prompts.db", "prompts.db-shm", "prompts.db-wal"]
            for file in sqlite_files:
                if os.path.exists(file):
                    os.remove(file)
                    print(f"✅ Видалено: {file}")
                else:
                    print(f"❌ Файл не знайдено: {file}")
            print("✅ Видалення SQLite файлів завершено!")
        except Exception as e:
            print(f"❌ Помилка видалення SQLite файлів: {e}")


def main():
    """Головна функція CLI"""
    parser = argparse.ArgumentParser(
        description="CLI тестер для AI Swagger Bot API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Приклади використання:
  python cli_tester.py health
  python cli_tester.py demo-user
  python cli_tester.py upload-swagger examples/swagger_specs/shop_api.json
  python cli_tester.py chat "Покажи всі доступні endpoints"
  python cli_tester.py prompts
  python cli_tester.py prompts --category system
  python cli_tester.py create-prompt "Мій промпт" "Опис" "Ти експерт {user_query}" user_defined
        """,
    )

    parser.add_argument("command", help="Команда для виконання")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL API")
    parser.add_argument("--file", help="Шлях до файлу (для upload-swagger)")
    parser.add_argument("--message", help="Повідомлення для чату")
    parser.add_argument("--category", help="Категорія промптів")
    parser.add_argument("--search", help="Пошуковий запит")
    parser.add_argument("--query", help="Запит для пошуку")
    parser.add_argument("--context", help="Контекст для пропозицій")
    parser.add_argument("--name", help="Назва промпту")
    parser.add_argument("--description", help="Опис промпту")
    parser.add_argument("--template", help="Шаблон промпту")
    parser.add_argument("--prompt-id", help="ID промпту")
    parser.add_argument("--parameters", help="Параметри для форматування (JSON)")
    parser.add_argument("--include-custom", action="store_true", help="Включити кастомні промпти")
    parser.add_argument("--api-key", help="OpenAI API ключ")
    parser.add_argument("--swagger-spec-id", help="ID Swagger специфікації")

    args = parser.parse_args()

    tester = APITester(args.url)

    try:
        if args.command == "health":
            tester.health_check()

        elif args.command == "demo-user":
            tester.create_demo_user()

        elif args.command == "upload-swagger":
            if not args.file:
                print("❌ Вкажіть шлях до файлу: --file path/to/file.json")
                sys.exit(1)
            tester.upload_swagger(args.file)

        elif args.command == "chat":
            if not args.message:
                print("❌ Вкажіть повідомлення: --message 'Ваше повідомлення'")
                sys.exit(1)
            tester.chat(args.message)

        elif args.command == "chat-history":
            tester.get_chat_history()

        elif args.command == "prompts":
            tester.get_prompts(category=args.category, search=args.search)

        elif args.command == "prompt-categories":
            tester.get_prompt_categories()

        elif args.command == "prompt-statistics":
            tester.get_prompt_statistics()

        elif args.command == "swagger-specs":
            tester.get_swagger_specs()

        elif args.command == "user-info":
            tester.get_user_info()

        elif args.command == "create-prompt":
            if not all([args.name, args.description, args.template]):
                print("❌ Вкажіть назву, опис та шаблон промпту")
                sys.exit(1)
            tester.create_custom_prompt(
                args.name, args.description, args.template, args.category or "user_defined"
            )

        elif args.command == "search-prompts":
            if not args.query:
                print("❌ Вкажіть запит для пошуку: --query 'пошуковий запит'")
                sys.exit(1)
            tester.search_prompts(args.query, args.category)

        elif args.command == "prompt-suggestions":
            if not args.query:
                print("❌ Вкажіть запит для пропозицій: --query 'запит'")
                sys.exit(1)
            tester.get_prompt_suggestions(args.query, args.context or "")

        elif args.command == "format-prompt":
            if not args.prompt_id:
                print("❌ Вкажіть ID промпту: --prompt-id 'prompt_id'")
                sys.exit(1)
            parameters = {}
            if args.parameters:
                try:
                    parameters = json.loads(args.parameters)
                except json.JSONDecodeError:
                    print("❌ Неправильний формат JSON для параметрів")
                    sys.exit(1)
            tester.format_prompt(args.prompt_id, **parameters)

        elif args.command == "export-prompts":
            tester.export_prompts(args.include_custom)

        elif args.command == "reload-prompts":
            tester.reload_prompts()

        elif args.command == "generate-prompts":
            if not args.file:
                print("❌ Вкажіть Swagger файл: --file path/to/swagger.json")
                sys.exit(1)
            tester.generate_prompts_from_swagger(args.file, args.api_key)

        elif args.command == "generate-suggestions":
            if not args.file:
                print("❌ Вкажіть Swagger файл: --file path/to/swagger.json")
                sys.exit(1)
            tester.generate_smart_suggestions(args.file, args.api_key)

        elif args.command == "auto-generate":
            if not args.swagger_spec_id:
                print("❌ Вкажіть ID Swagger специфікації: --swagger-spec-id 'id'")
                sys.exit(1)
            tester.auto_generate_prompts_for_user(args.swagger_spec_id, args.api_key)

        elif args.command == "test-postgres-prompts":
            tester.test_postgres_prompts()

        elif args.command == "migrate-prompts":
            tester.migrate_prompts()

        elif args.command == "list-postgres-prompts":
            tester.list_postgres_prompts()

        elif args.command == "remove-sqlite":
            tester.remove_sqlite_files()

        elif args.command == "status":
            tester.show_status()

        else:
            print(f"❌ Невідома команда: {args.command}")
            print("Доступні команди:")
            print("  health, demo-user, upload-swagger, chat, chat-history")
            print("  prompts, prompt-categories, prompt-statistics, swagger-specs")
            print("  user-info, create-prompt, search-prompts, prompt-suggestions")
            print("  format-prompt, export-prompts, reload-prompts")
            print("  generate-prompts, generate-suggestions, auto-generate")
            print("  test-postgres-prompts, migrate-prompts, list-postgres-prompts, status")
            sys.exit(1)

    except requests.exceptions.ConnectionError:
        print(f"❌ Не вдалося підключитися до {args.url}")
        print("Перевірте, чи запущений API сервер")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Помилка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
