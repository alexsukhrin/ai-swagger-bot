#!/usr/bin/env python3
"""
CLI тестер зі збереженням стану сесії
Дозволяє виконувати команди з збереженням токена між викликами
"""

import json
import os
import sys

import requests
from cli_tester import APITester


class SessionCLI:
    """CLI тестер зі збереженням стану"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_file = ".cli_session.json"
        self.tester = APITester(base_url)
        self.load_session()

    def load_session(self):
        """Завантажує сесію з файлу"""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, "r") as f:
                    session_data = json.load(f)
                    self.tester.current_user = session_data.get("user")
                    self.tester.current_token = session_data.get("token")
                    print(
                        f"📂 Завантажено сесію для користувача: {self.tester.current_user.get('email') if self.tester.current_user else 'Невідомий'}"
                    )
            except Exception as e:
                print(f"⚠️ Помилка завантаження сесії: {e}")

    def save_session(self):
        """Зберігає сесію в файл"""
        session_data = {"user": self.tester.current_user, "token": self.tester.current_token}
        try:
            with open(self.session_file, "w") as f:
                json.dump(session_data, f)
        except Exception as e:
            print(f"⚠️ Помилка збереження сесії: {e}")

    def create_demo_user(self):
        """Створює демо користувача та зберігає сесію"""
        self.tester.create_demo_user()
        if self.tester.current_token:
            self.save_session()

    def run_command(self, command, *args, **kwargs):
        """Виконує команду та зберігає стан"""
        if hasattr(self.tester, command):
            method = getattr(self.tester, command)
            if callable(method):
                result = method(*args, **kwargs)
                # Зберігаємо сесію після команд, які можуть змінити стан
                if command in ["create_demo_user", "upload_swagger", "create_custom_prompt"]:
                    self.save_session()
                return result
            else:
                print(f"❌ {command} не є методом")
        else:
            print(f"❌ Невідома команда: {command}")

    def show_status(self):
        """Показує статус з інформацією про сесію"""
        print("📊 Статус CLI тестера:")
        print(f"   Base URL: {self.base_url}")
        if self.tester.current_user:
            print(f"   Користувач: {self.tester.current_user.get('email', 'Невідомий')}")
        else:
            print(f"   Користувач: Не створений")
        print(f"   Token: {'Так' if self.tester.current_token else 'Ні'}")
        print(f"   Сесія: {'Збережена' if os.path.exists(self.session_file) else 'Не збережена'}")

        # Перевіряємо чи файл сесії існує
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, "r") as f:
                    session_data = json.load(f)
                    print(f"   Файл сесії: {self.session_file}")
                    print(f"   Розмір файлу: {os.path.getsize(self.session_file)} байт")
            except Exception as e:
                print(f"   Помилка читання сесії: {e}")

    def clear_session(self):
        """Очищає сесію"""
        if os.path.exists(self.session_file):
            os.remove(self.session_file)
            print("🗑️ Сесія очищена")
        self.tester.current_user = None
        self.tester.current_token = None

    def health_check(self):
        """Health check"""
        return self.run_command("health_check")

    def upload_swagger(self, file_path):
        """Завантаження Swagger"""
        return self.run_command("upload_swagger", file_path)

    def chat(self, message):
        """Чат з AI"""
        return self.run_command("chat", message)

    def get_chat_history(self):
        """Історія чату"""
        return self.run_command("get_chat_history")

    def get_prompts(self, category=None, search=None):
        """Промпти"""
        return self.run_command("get_prompts", category, search)

    def get_prompt_categories(self):
        """Категорії промптів"""
        return self.run_command("get_prompt_categories")

    def get_prompt_statistics(self):
        """Статистика промптів"""
        return self.run_command("get_prompt_statistics")

    def get_swagger_specs(self):
        """Swagger специфікації"""
        return self.run_command("get_swagger_specs")

    def get_user_info(self):
        """Інформація про користувача"""
        return self.run_command("get_user_info")

    def create_custom_prompt(self, name, description, template, category):
        """Створення кастомного промпту"""
        return self.run_command("create_custom_prompt", name, description, template, category)

    def search_prompts(self, query, category=None):
        """Пошук промптів"""
        return self.run_command("search_prompts", query, category)

    def get_prompt_suggestions(self, query, context=""):
        """Пропозиції промптів"""
        return self.run_command("get_prompt_suggestions", query, context)

    def format_prompt(self, prompt_id, **parameters):
        """Форматування промпту"""
        return self.run_command("format_prompt", prompt_id, **parameters)

    def export_prompts(self, include_custom=True):
        """Експорт промптів"""
        return self.run_command("export_prompts", include_custom)

    def reload_prompts(self):
        """Перезавантаження промптів"""
        return self.run_command("reload_prompts")


def main():
    """Головна функція"""
    import argparse

    parser = argparse.ArgumentParser(
        description="CLI тестер зі збереженням стану для AI Swagger Bot API"
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
    parser.add_argument("--clear-session", action="store_true", help="Очистити сесію")

    args = parser.parse_args()

    cli = SessionCLI(args.url)

    try:
        if args.clear_session:
            cli.clear_session()
            return

        if args.command == "status":
            cli.show_status()

        elif args.command == "health":
            cli.health_check()

        elif args.command == "demo-user":
            cli.create_demo_user()

        elif args.command == "upload-swagger":
            if not args.file:
                print("❌ Вкажіть шлях до файлу: --file path/to/file.json")
                sys.exit(1)
            cli.upload_swagger(args.file)

        elif args.command == "chat":
            if not args.message:
                print("❌ Вкажіть повідомлення: --message 'Ваше повідомлення'")
                sys.exit(1)
            cli.chat(args.message)

        elif args.command == "chat-history":
            cli.get_chat_history()

        elif args.command == "prompts":
            cli.get_prompts(category=args.category, search=args.search)

        elif args.command == "prompt-categories":
            cli.get_prompt_categories()

        elif args.command == "prompt-statistics":
            cli.get_prompt_statistics()

        elif args.command == "swagger-specs":
            cli.get_swagger_specs()

        elif args.command == "user-info":
            cli.get_user_info()

        elif args.command == "create-prompt":
            if not all([args.name, args.description, args.template]):
                print("❌ Вкажіть назву, опис та шаблон промпту")
                sys.exit(1)
            cli.create_custom_prompt(
                args.name, args.description, args.template, args.category or "user_defined"
            )

        elif args.command == "search-prompts":
            if not args.query:
                print("❌ Вкажіть запит для пошуку: --query 'пошуковий запит'")
                sys.exit(1)
            cli.search_prompts(args.query, args.category)

        elif args.command == "prompt-suggestions":
            if not args.query:
                print("❌ Вкажіть запит для пропозицій: --query 'запит'")
                sys.exit(1)
            cli.get_prompt_suggestions(args.query, args.context or "")

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
            cli.format_prompt(args.prompt_id, **parameters)

        elif args.command == "export-prompts":
            cli.export_prompts(args.include_custom)

        elif args.command == "reload-prompts":
            cli.reload_prompts()

        else:
            print(f"❌ Невідома команда: {args.command}")
            print("Доступні команди:")
            print("  health, demo-user, upload-swagger, chat, chat-history")
            print("  prompts, prompt-categories, prompt-statistics, swagger-specs")
            print("  user-info, create-prompt, search-prompts, prompt-suggestions")
            print("  format-prompt, export-prompts, reload-prompts, status")
            print("  --clear-session - очистити сесію")
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
