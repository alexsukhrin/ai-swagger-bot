#!/usr/bin/env python3
"""
Інтерактивний CLI інтерфейс для тестування AI Swagger Bot API
Зручне меню для тестування всіх функцій
"""

import json
import os
import sys
from typing import Optional

from cli_tester import APITester


class InteractiveCLI:
    """Інтерактивний CLI інтерфейс"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.tester = APITester(base_url)
        self.running = True

    def print_header(self):
        """Виводить заголовок"""
        print("\n" + "=" * 60)
        print("🤖 AI Swagger Bot - Інтерактивний CLI Тестер")
        print("=" * 60)
        print(f"📍 API URL: {self.tester.base_url}")
        print("💡 Використовуйте цифри для навігації по меню")
        if self.tester.current_user:
            print(f"👤 Користувач: {self.tester.current_user.get('email', 'Невідомий')}")
        else:
            print("👤 Користувач: Не створений")
        print("=" * 60)

    def print_menu(self):
        """Виводить головне меню"""
        print("\n📋 ГОЛОВНЕ МЕНЮ:")
        print("1.  🏥 Health Check")
        print("2.  👤 Створити демо користувача")
        print("3.  📁 Завантажити Swagger файл")
        print("4.  💬 Чат з AI")
        print("5.  📜 Історія чату")
        print("6.  📝 Промпти")
        print("7.  📂 Категорії промптів")
        print("8.  📊 Статистика промптів")
        print("9.  📋 Swagger специфікації")
        print("10. 👤 Інформація про користувача")
        print("11. ✨ Створити кастомний промпт")
        print("12. 🔍 Пошук промптів")
        print("13. 💡 Пропозиції промптів")
        print("14. 🔧 Форматування промпту")
        print("15. 📤 Експорт промптів")
        print("16. 🔄 Перезавантажити промпти")
        print("17. 📊 Статус")
        print("0.  🚪 Вихід")
        print("-" * 60)

    def get_input(self, prompt: str, default: str = "") -> str:
        """Отримує введення від користувача"""
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            return user_input if user_input else default
        return input(f"{prompt}: ").strip()

    def get_file_path(self, prompt: str) -> Optional[str]:
        """Отримує шлях до файлу з валідацією"""
        while True:
            file_path = self.get_input(prompt)
            if not file_path:
                return None

            if os.path.exists(file_path):
                return file_path
            else:
                print(f"❌ Файл не знайдено: {file_path}")
                retry = self.get_input("Спробувати ще раз? (y/n)", "y")
                if retry.lower() != "y":
                    return None

    def handle_health_check(self):
        """Обробка health check"""
        self.tester.health_check()
        input("\nНатисніть Enter для продовження...")

    def handle_demo_user(self):
        """Обробка створення демо користувача"""
        self.tester.create_demo_user()
        input("\nНатисніть Enter для продовження...")

    def handle_upload_swagger(self):
        """Обробка завантаження Swagger файлу"""
        print("\n📁 ЗАВАНТАЖЕННЯ SWAGGER ФАЙЛУ")
        print("Доступні приклади:")

        # Показуємо доступні файли
        examples_dir = "examples/swagger_specs"
        if os.path.exists(examples_dir):
            for file in os.listdir(examples_dir):
                if file.endswith(".json"):
                    print(f"  • {examples_dir}/{file}")

        file_path = self.get_file_path("Введіть шлях до Swagger файлу")
        if file_path:
            self.tester.upload_swagger(file_path)

        input("\nНатисніть Enter для продовження...")

    def handle_chat(self):
        """Обробка чату"""
        print("\n💬 ЧАТ З AI")
        print("Приклади запитів:")
        print("  • Покажи всі доступні endpoints")
        print("  • Створи товар з назвою Телефон")
        print("  • Покажи категорії товарів")
        print("  • Як створити нову категорію?")

        message = self.get_input("Введіть повідомлення для AI")
        if message:
            self.tester.chat(message)

        input("\nНатисніть Enter для продовження...")

    def handle_chat_history(self):
        """Обробка історії чату"""
        self.tester.get_chat_history()
        input("\nНатисніть Enter для продовження...")

    def handle_prompts(self):
        """Обробка промптів"""
        print("\n📝 ПРОМПТИ")
        print("1. Всі промпти")
        print("2. За категорією")
        print("3. Пошук")

        choice = self.get_input("Виберіть опцію", "1")

        if choice == "1":
            self.tester.get_prompts()
        elif choice == "2":
            category = self.get_input("Введіть категорію", "system")
            self.tester.get_prompts(category=category)
        elif choice == "3":
            search = self.get_input("Введіть пошуковий запит")
            self.tester.get_prompts(search=search)

        input("\nНатисніть Enter для продовження...")

    def handle_prompt_categories(self):
        """Обробка категорій промптів"""
        self.tester.get_prompt_categories()
        input("\nНатисніть Enter для продовження...")

    def handle_prompt_statistics(self):
        """Обробка статистики промптів"""
        self.tester.get_prompt_statistics()
        input("\nНатисніть Enter для продовження...")

    def handle_swagger_specs(self):
        """Обробка Swagger специфікацій"""
        self.tester.get_swagger_specs()
        input("\nНатисніть Enter для продовження...")

    def handle_user_info(self):
        """Обробка інформації про користувача"""
        self.tester.get_user_info()
        input("\nНатисніть Enter для продовження...")

    def handle_create_prompt(self):
        """Обробка створення кастомного промпту"""
        print("\n✨ СТВОРЕННЯ КАСТОМНОГО ПРОМПТУ")

        name = self.get_input("Назва промпту")
        if not name:
            return

        description = self.get_input("Опис промпту")
        template = self.get_input("Шаблон промпту (використовуйте {user_query} для запиту)")
        category = self.get_input("Категорія", "user_defined")

        if name and template:
            self.tester.create_custom_prompt(name, description, template, category)

        input("\nНатисніть Enter для продовження...")

    def handle_search_prompts(self):
        """Обробка пошуку промптів"""
        print("\n🔍 ПОШУК ПРОМПТІВ")

        query = self.get_input("Введіть пошуковий запит")
        if not query:
            return

        category = self.get_input("Категорія (необов'язково)")

        self.tester.search_prompts(query, category if category else None)
        input("\nНатисніть Enter для продовження...")

    def handle_prompt_suggestions(self):
        """Обробка пропозицій промптів"""
        print("\n💡 ПРОПОЗИЦІЇ ПРОМПТІВ")

        query = self.get_input("Введіть запит для пропозицій")
        if not query:
            return

        context = self.get_input("Контекст (необов'язково)")

        self.tester.get_prompt_suggestions(query, context)
        input("\nНатисніть Enter для продовження...")

    def handle_format_prompt(self):
        """Обробка форматування промпту"""
        print("\n🔧 ФОРМАТУВАННЯ ПРОМПТУ")

        prompt_id = self.get_input("ID промпту")
        if not prompt_id:
            return

        print('Параметри (JSON формат, наприклад: {"user_query": "тест"})')
        parameters_str = self.get_input("Параметри")

        parameters = {}
        if parameters_str:
            try:
                parameters = json.loads(parameters_str)
            except json.JSONDecodeError:
                print("❌ Неправильний формат JSON")
                input("\nНатисніть Enter для продовження...")
                return

        self.tester.format_prompt(prompt_id, **parameters)
        input("\nНатисніть Enter для продовження...")

    def handle_export_prompts(self):
        """Обробка експорту промптів"""
        print("\n📤 ЕКСПОРТ ПРОМПТІВ")

        include_custom = self.get_input("Включити кастомні промпти? (y/n)", "y")
        include_custom_bool = include_custom.lower() == "y"

        self.tester.export_prompts(include_custom_bool)
        input("\nНатисніть Enter для продовження...")

    def handle_reload_prompts(self):
        """Обробка перезавантаження промптів"""
        print("\n🔄 ПЕРЕЗАВАНТАЖЕННЯ ПРОМПТІВ")
        self.tester.reload_prompts()
        input("\nНатисніть Enter для продовження...")

    def handle_status(self):
        """Обробка статусу"""
        self.tester.show_status()
        input("\nНатисніть Enter для продовження...")

    def run(self):
        """Запуск інтерактивного CLI"""
        while self.running:
            try:
                self.print_header()
                self.print_menu()

                choice = self.get_input("Виберіть опцію", "0")

                if choice == "0":
                    print("👋 До побачення!")
                    self.running = False

                elif choice == "1":
                    self.handle_health_check()

                elif choice == "2":
                    self.handle_demo_user()

                elif choice == "3":
                    self.handle_upload_swagger()

                elif choice == "4":
                    self.handle_chat()

                elif choice == "5":
                    self.handle_chat_history()

                elif choice == "6":
                    self.handle_prompts()

                elif choice == "7":
                    self.handle_prompt_categories()

                elif choice == "8":
                    self.handle_prompt_statistics()

                elif choice == "9":
                    self.handle_swagger_specs()

                elif choice == "10":
                    self.handle_user_info()

                elif choice == "11":
                    self.handle_create_prompt()

                elif choice == "12":
                    self.handle_search_prompts()

                elif choice == "13":
                    self.handle_prompt_suggestions()

                elif choice == "14":
                    self.handle_format_prompt()

                elif choice == "15":
                    self.handle_export_prompts()

                elif choice == "16":
                    self.handle_reload_prompts()

                elif choice == "17":
                    self.handle_status()

                else:
                    print("❌ Невідома опція. Спробуйте ще раз.")
                    input("\nНатисніть Enter для продовження...")

            except KeyboardInterrupt:
                print("\n\n👋 До побачення!")
                self.running = False

            except Exception as e:
                print(f"\n❌ Помилка: {e}")
                input("\nНатисніть Enter для продовження...")


def main():
    """Головна функція"""
    import argparse

    parser = argparse.ArgumentParser(description="Інтерактивний CLI тестер для AI Swagger Bot API")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL API")

    args = parser.parse_args()

    try:
        cli = InteractiveCLI(args.url)
        cli.run()
    except KeyboardInterrupt:
        print("\n👋 До побачення!")
    except Exception as e:
        print(f"❌ Помилка: {e}")


if __name__ == "__main__":
    main()
