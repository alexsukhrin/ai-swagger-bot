#!/usr/bin/env python3
"""
Скрипт для створення таблиць бази даних
"""

import os
import sys

# Додаємо шлях до модуля
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import engine
from api.models import Base


def create_tables():
    """Створює всі таблиці в базі даних"""
    print("🔧 Створення таблиць бази даних...")

    try:
        # Створюємо всі таблиці
        Base.metadata.create_all(bind=engine)
        print("✅ Таблиці створено успішно!")

        print("\n📊 Створені таблиці:")
        print("   • users - користувачі")
        print("   • swagger_specs - Swagger специфікації")
        print("   • chat_sessions - сесії чату")
        print("   • chat_messages - повідомлення в чаті")
        print("   • prompt_templates - шаблони промптів")
        print("   • api_calls - виклики API")

    except Exception as e:
        print(f"❌ Помилка створення таблиць: {e}")
        return False

    return True


if __name__ == "__main__":
    create_tables()
