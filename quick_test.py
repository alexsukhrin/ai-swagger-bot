#!/usr/bin/env python3
"""
Швидкий тестовий скрипт для демонстрації CLI функціоналу
"""

import time

from cli_tester import APITester


def run_quick_test():
    """Запуск швидкого тесту"""
    print("🚀 ШВИДКИЙ ТЕСТ CLI ТЕСТЕРА")
    print("=" * 50)

    tester = APITester()

    try:
        # 1. Health Check
        print("\n1️⃣ Перевірка стану сервісу...")
        tester.health_check()
        time.sleep(1)

        # 2. Створення демо користувача
        print("\n2️⃣ Створення демо користувача...")
        tester.create_demo_user()
        time.sleep(1)

        # 3. Перегляд промптів
        print("\n3️⃣ Перегляд промптів...")
        tester.get_prompts()
        time.sleep(1)

        # 4. Категорії промптів
        print("\n4️⃣ Категорії промптів...")
        tester.get_prompt_categories()
        time.sleep(1)

        # 5. Статистика промптів
        print("\n5️⃣ Статистика промптів...")
        tester.get_prompt_statistics()
        time.sleep(1)

        # 6. Інформація про користувача
        print("\n6️⃣ Інформація про користувача...")
        tester.get_user_info()
        time.sleep(1)

        # 7. Створення кастомного промпту
        print("\n7️⃣ Створення кастомного промпту...")
        tester.create_custom_prompt(
            "Тестовий промпт",
            "Промпт для тестування CLI",
            "Ти експерт з API. {user_query}",
            "user_defined",
        )
        time.sleep(1)

        # 8. Пошук промптів
        print("\n8️⃣ Пошук промптів...")
        tester.search_prompts("тестовий")
        time.sleep(1)

        # 9. Пропозиції промптів
        print("\n9️⃣ Пропозиції промптів...")
        tester.get_prompt_suggestions("Створи нову категорію")
        time.sleep(1)

        # 10. Статус
        print("\n🔟 Статус...")
        tester.show_status()

        print("\n✅ Швидкий тест завершено успішно!")
        print("💡 Тепер можете використовувати CLI тестер для повного тестування")

    except Exception as e:
        print(f"\n❌ Помилка під час тестування: {e}")
        print("💡 Перевірте, чи запущений API сервер")


if __name__ == "__main__":
    run_quick_test()
