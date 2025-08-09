#!/usr/bin/env python3
"""
Скрипт для міграції до нової структури БД з прив'язкою embeddings до користувачів.
"""

import json
import os
import sys
import uuid
from datetime import datetime

# Додаємо шлях до модуля
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import engine, get_db
from api.models import ApiEmbedding, Base, SwaggerSpec, User
from sqlalchemy import text


def create_new_tables():
    """Створює нові таблиці з правильною структурою."""
    print("🔧 Створення нових таблиць...")

    try:
        # Створюємо всі таблиці через SQLAlchemy
        Base.metadata.create_all(bind=engine)
        print("✅ Таблиці створено успішно!")

    except Exception as e:
        print(f"❌ Помилка створення таблиць: {e}")
        return False

    return True


def migrate_existing_embeddings():
    """Мігрує існуючі embeddings до нової структури."""
    print("🔄 Міграція існуючих embeddings...")

    try:
        with engine.connect() as conn:
            # Перевіряємо чи існує стара таблиця
            result = conn.execute(
                text(
                    """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'api_embeddings_old'
                )
            """
                )
            )

            if result.fetchone()[0]:
                print("📋 Знайдено стару таблицю api_embeddings_old")

                # Отримуємо дані з старої таблиці
                result = conn.execute(
                    text(
                        """
                    SELECT id, endpoint_path, method, description, embedding, metadata, created_at
                    FROM api_embeddings_old
                """
                    )
                )

                old_embeddings = result.fetchall()
                print(f"📊 Знайдено {len(old_embeddings)} старих embeddings")

                # Створюємо системного користувача якщо не існує
                system_user_id = "system"
                conn.execute(
                    text(
                        """
                    INSERT INTO users (id, email, username, hashed_password, is_active, created_at, updated_at)
                    VALUES (:id, 'system@ai-swagger-bot.com', 'system', 'system_hash', true, :created_at, :updated_at)
                    ON CONFLICT (id) DO NOTHING
                """
                    ),
                    {
                        "id": system_user_id,
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat(),
                    },
                )

                # Створюємо системну Swagger специфікацію
                system_swagger_id = "system-swagger"
                conn.execute(
                    text(
                        """
                    INSERT INTO swagger_specs (id, user_id, filename, original_data, parsed_data, endpoints_count, is_active, created_at, updated_at)
                    VALUES (:id, :user_id, 'system-swagger.json', '{}', '{}', 0, true, :created_at, :updated_at)
                    ON CONFLICT (id) DO NOTHING
                """
                    ),
                    {
                        "id": system_swagger_id,
                        "user_id": system_user_id,
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat(),
                    },
                )

                # Мігруємо embeddings
                migrated_count = 0
                for row in old_embeddings:
                    try:
                        # Конвертуємо embedding в JSON string якщо потрібно
                        embedding_data = row[4]
                        if isinstance(embedding_data, list):
                            embedding_json = json.dumps(embedding_data)
                        else:
                            embedding_json = embedding_data

                        # Додаємо в нову таблицю
                        conn.execute(
                            text(
                                """
                            INSERT INTO api_embeddings
                            (id, user_id, swagger_spec_id, endpoint_path, method, description, embedding, metadata, created_at)
                            VALUES (:id, :user_id, :swagger_spec_id, :endpoint_path, :method, :description, :embedding, :metadata, :created_at)
                        """
                            ),
                            {
                                "id": str(uuid.uuid4()),
                                "user_id": system_user_id,
                                "swagger_spec_id": system_swagger_id,
                                "endpoint_path": row[1],
                                "method": row[2],
                                "description": row[3],
                                "embedding": embedding_json,
                                "embedding_metadata": json.dumps(row[5]) if row[5] else None,
                                "created_at": (
                                    row[6].isoformat() if row[6] else datetime.now().isoformat()
                                ),
                            },
                        )

                        migrated_count += 1

                    except Exception as e:
                        print(f"⚠️ Помилка міграції embedding {row[0]}: {e}")
                        continue

                conn.commit()
                print(f"✅ Успішно мігровано {migrated_count}/{len(old_embeddings)} embeddings")

                # Видаляємо стару таблицю
                conn.execute(text("DROP TABLE IF EXISTS api_embeddings_old"))
                conn.commit()
                print("🗑️ Стара таблиця видалена")

            else:
                print("ℹ️ Стара таблиця не знайдена, пропускаємо міграцію")

    except Exception as e:
        print(f"❌ Помилка міграції: {e}")
        return False

    return True


def backup_old_table():
    """Створює резервну копію старої таблиці."""
    print("💾 Створення резервної копії...")

    try:
        with engine.connect() as conn:
            # Перевіряємо чи існує таблиця api_embeddings
            result = conn.execute(
                text(
                    """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'api_embeddings'
                )
            """
                )
            )

            if result.fetchone()[0]:
                # Перевіряємо чи є нові поля
                result = conn.execute(
                    text(
                        """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'api_embeddings' AND column_name = 'user_id'
                """
                    )
                )

                if not result.fetchone():
                    print("📋 Знайдено стару таблицю api_embeddings без user_id")

                    # Перейменовуємо стару таблицю
                    conn.execute(text("ALTER TABLE api_embeddings RENAME TO api_embeddings_old"))
                    conn.commit()
                    print("✅ Стара таблиця перейменована в api_embeddings_old")
                else:
                    print("ℹ️ Таблиця вже має нову структуру")
            else:
                print("ℹ️ Таблиця api_embeddings не існує")

    except Exception as e:
        print(f"❌ Помилка створення резервної копії: {e}")
        return False

    return True


def verify_migration():
    """Перевіряє успішність міграції."""
    print("🔍 Перевірка міграції...")

    try:
        with engine.connect() as conn:
            # Перевіряємо нову таблицю
            result = conn.execute(text("SELECT COUNT(*) FROM api_embeddings"))
            embeddings_count = result.fetchone()[0]

            # Перевіряємо користувачів
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            users_count = result.fetchone()[0]

            # Перевіряємо Swagger специфікації
            result = conn.execute(text("SELECT COUNT(*) FROM swagger_specs"))
            swagger_count = result.fetchone()[0]

            print(f"📊 Результати міграції:")
            print(f"   • Embeddings: {embeddings_count}")
            print(f"   • Користувачі: {users_count}")
            print(f"   • Swagger специфікації: {swagger_count}")

            if embeddings_count > 0 and users_count > 0:
                print("✅ Міграція пройшла успішно!")
                return True
            else:
                print("⚠️ Міграція може бути неповною")
                return False

    except Exception as e:
        print(f"❌ Помилка перевірки: {e}")
        return False


def main():
    """Основна функція міграції."""
    print("🚀 Початок міграції до нової структури БД...")

    try:
        # Крок 1: Створюємо резервну копію
        if not backup_old_table():
            print("❌ Помилка створення резервної копії")
            return False

        # Крок 2: Створюємо нові таблиці
        if not create_new_tables():
            print("❌ Помилка створення нових таблиць")
            return False

        # Крок 3: Мігруємо дані
        if not migrate_existing_embeddings():
            print("❌ Помилка міграції даних")
            return False

        # Крок 4: Перевіряємо результат
        if not verify_migration():
            print("❌ Помилка перевірки міграції")
            return False

        print("🎉 Міграція завершена успішно!")
        return True

    except Exception as e:
        print(f"❌ Критична помилка міграції: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
