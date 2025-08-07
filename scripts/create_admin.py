#!/usr/bin/env python3
"""
Скрипт для створення адміністратора AI Swagger Bot
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid

from api.auth import get_password_hash
from api.database import SessionLocal
from api.models import User


def create_admin_user(email: str, username: str, password: str):
    """Створення адміністратора"""
    db = SessionLocal()

    try:
        # Перевіряємо чи існує користувач
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"❌ Користувач з email {email} вже існує!")
            return False

        # Створюємо адміністратора
        admin_user = User(
            id=str(uuid.uuid4()),
            email=email,
            username=username,
            hashed_password=get_password_hash(password),
            is_active=True,
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print(f"✅ Адміністратор створений успішно!")
        print(f"   Email: {email}")
        print(f"   Username: {username}")
        print(f"   ID: {admin_user.id}")

        return True

    except Exception as e:
        print(f"❌ Помилка створення адміністратора: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def main():
    """Головна функція"""
    print("🤖 AI Swagger Bot - Створення Адміністратора")
    print("=" * 50)

    # Отримуємо дані від користувача
    email = input("Введіть email адміністратора: ").strip()
    username = input("Введіть username адміністратора: ").strip()
    password = input("Введіть пароль адміністратора: ").strip()

    if not email or not username or not password:
        print("❌ Всі поля повинні бути заповнені!")
        return

    # Створюємо адміністратора
    success = create_admin_user(email, username, password)

    if success:
        print("\n🎉 Адміністратор створений!")
        print("Тепер ви можете:")
        print("1. Запустити API: make run-api")
        print("2. Відкрити адмінку: http://localhost:8000/admin")
        print("3. Відкрити API docs: http://localhost:8000/docs")
    else:
        print("\n❌ Не вдалося створити адміністратора!")


if __name__ == "__main__":
    main()
