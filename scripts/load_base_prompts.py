#!/usr/bin/env python3
"""
Скрипт для завантаження базових промптів для існуючих користувачів
"""

import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

import yaml

# Додаємо кореневу директорію до шляху
sys.path.append(str(Path(__file__).parent.parent))

from api.database import SessionLocal
from api.models import PromptTemplate, User


def load_base_prompts_from_yaml():
    """Завантажує базові промпти з YAML файлу"""
    yaml_path = Path("prompts/base_prompts.yaml")

    if not yaml_path.exists():
        print("❌ Файл prompts/base_prompts.yaml не знайдено")
        return []

    with open(yaml_path, "r", encoding="utf-8") as file:
        yaml_data = yaml.safe_load(file)

    # Обробляємо промпти з секції prompts
    prompts_data = yaml_data.get("prompts", {})
    base_prompts = []

    for prompt_id, prompt_data in prompts_data.items():
        prompt = {
            "name": prompt_data.get("name", ""),
            "description": prompt_data.get("description", ""),
            "template": prompt_data.get("template", ""),
            "category": prompt_data.get("category", "general"),
            "is_public": True,
            "is_active": True,
            "usage_count": 0,
            "success_rate": 0,
        }
        base_prompts.append(prompt)

    return base_prompts


def load_prompts_for_user(user_id: str, db: SessionLocal):
    """Завантажує базові промпти для конкретного користувача"""
    try:
        # Перевіряємо чи є вже промпти у користувача
        existing_prompts = (
            db.query(PromptTemplate).filter(PromptTemplate.user_id == user_id).count()
        )
        if existing_prompts > 0:
            print(f"⚠️ Користувач {user_id} вже має {existing_prompts} промптів")
            return False

        # Завантажуємо базові промпти
        base_prompts = load_base_prompts_from_yaml()

        if not base_prompts:
            print(f"❌ Не знайдено базових промптів для користувача {user_id}")
            return False

        print(f"📋 Завантажую {len(base_prompts)} базових промптів для користувача {user_id}")

        for i, prompt_data in enumerate(base_prompts):
            print(f"📝 Створюю промпт {i+1}/{len(base_prompts)}: {prompt_data['name']}")

            # Створюємо копію промпту для користувача
            user_prompt = PromptTemplate(
                id=str(uuid.uuid4()),
                user_id=user_id,
                name=prompt_data["name"],
                description=prompt_data["description"],
                template=prompt_data["template"],
                category=prompt_data["category"],
                is_public=False,  # Промпти користувача не публічні
                is_active=True,
                usage_count=0,
                success_rate=0,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            db.add(user_prompt)

        db.commit()
        print(f"✅ Успішно завантажено {len(base_prompts)} промптів для користувача {user_id}")
        return True

    except Exception as e:
        print(f"❌ Помилка завантаження промптів для користувача {user_id}: {e}")
        db.rollback()
        return False


def main():
    """Головна функція"""
    print("🔧 Завантаження базових промптів для користувачів...")

    db = SessionLocal()

    try:
        # Отримуємо всіх користувачів
        users = db.query(User).all()

        if not users:
            print("❌ Користувачів не знайдено")
            return

        print(f"👥 Знайдено {len(users)} користувачів")

        success_count = 0
        skip_count = 0

        for user in users:
            print(f"\n👤 Обробляю користувача: {user.username} ({user.email})")

            if load_prompts_for_user(user.id, db):
                success_count += 1
            else:
                skip_count += 1

        print(f"\n📊 Результат:")
        print(f"✅ Успішно завантажено: {success_count} користувачів")
        print(f"⏭️ Пропущено: {skip_count} користувачів")

    except Exception as e:
        print(f"❌ Помилка: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
