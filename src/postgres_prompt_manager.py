"""
Менеджер промптів з використанням PostgreSQL бази даних
"""

import json
import os
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.config import Config


@dataclass
class PromptTemplate:
    """Клас для представлення промпт-шаблону."""

    id: Optional[str] = None
    user_id: Optional[str] = None
    name: str = ""
    description: str = ""
    template: str = ""
    category: str = ""
    tags: List[str] = None
    is_public: bool = False
    is_active: bool = True
    created_at: str = ""
    updated_at: str = ""
    usage_count: int = 0
    success_rate: float = 0.0

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()


class PostgresPromptManager:
    """Менеджер для динамічного управління промптами з PostgreSQL."""

    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv(
            "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ai_swagger_bot"
        )
        self.engine = None
        self.SessionLocal = None
        self.init_database()

    def init_database(self):
        """Ініціалізує з'єднання з PostgreSQL базою даних."""
        try:
            if self.database_url.startswith("sqlite"):
                # SQLite налаштування (для тестування)
                self.engine = create_engine(
                    self.database_url,
                    connect_args={"check_same_thread": False},
                    poolclass=StaticPool,
                    echo=False,
                )
            else:
                # PostgreSQL налаштування
                self.engine = create_engine(
                    self.database_url,
                    pool_pre_ping=True,
                    pool_recycle=300,
                    echo=False,
                )

            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            print(f"✅ Підключено до бази даних: {self.database_url}")
        except Exception as e:
            print(f"❌ Помилка підключення до бази даних: {e}")
            raise

    def get_db_session(self):
        """Отримує сесію бази даних."""
        if not self.SessionLocal:
            self.init_database()
        return self.SessionLocal()

    def add_prompt(self, prompt: PromptTemplate) -> str:
        """Додає новий промпт в базу даних."""
        with self.get_db_session() as session:
            try:
                # Перевіряємо чи існує таблиця
                result = session.execute(
                    text(
                        """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'prompt_templates'
                    );
                """
                    )
                )

                if not result.scalar():
                    # Створюємо таблиці якщо не існують
                    self._create_tables(session)

                # Додаємо промпт
                session.execute(
                    text(
                        """
                    INSERT INTO prompt_templates
                    (id, user_id, name, description, template, category, is_public, is_active, created_at, updated_at)
                    VALUES (:id, :user_id, :name, :description, :template, :category, :is_public, :is_active, :created_at, :updated_at)
                """
                    ),
                    {
                        "id": prompt.id,
                        "user_id": prompt.user_id
                        or "system",  # Використовуємо 'system' якщо user_id не вказано
                        "name": prompt.name,
                        "description": prompt.description,
                        "template": prompt.template,
                        "category": prompt.category,
                        "is_public": prompt.is_public,
                        "is_active": prompt.is_active,
                        "created_at": prompt.created_at,
                        "updated_at": prompt.updated_at,
                    },
                )

                session.commit()
                print(f"✅ Додано промпт: {prompt.name}")
                return prompt.id
            except Exception as e:
                session.rollback()
                print(f"❌ Помилка додавання промпту: {e}")
                raise

    def get_prompt(self, prompt_id: str) -> Optional[PromptTemplate]:
        """Отримує промпт за ID."""
        with self.get_db_session() as session:
            try:
                result = session.execute(
                    text(
                        """
                    SELECT id, user_id, name, description, template, category, is_public, is_active,
                           created_at, updated_at
                    FROM prompt_templates WHERE id = :prompt_id
                """
                    ),
                    {"prompt_id": prompt_id},
                )

                row = result.fetchone()
                if row:
                    return self._row_to_prompt(row)
                return None
            except Exception as e:
                print(f"❌ Помилка отримання промпту: {e}")
                return None

    def get_prompts_by_category(self, category: str) -> List[PromptTemplate]:
        """Отримує всі промпти за категорією."""
        with self.get_db_session() as session:
            try:
                result = session.execute(
                    text(
                        """
                    SELECT id, user_id, name, description, template, category, is_public, is_active,
                           created_at, updated_at
                    FROM prompt_templates
                    WHERE category = :category AND is_active = true
                    ORDER BY created_at DESC
                """
                    ),
                    {"category": category},
                )

                return [self._row_to_prompt(row) for row in result.fetchall()]
            except Exception as e:
                print(f"❌ Помилка отримання промптів за категорією: {e}")
                return []

    def search_prompts(self, query: str, category: str = None) -> List[PromptTemplate]:
        """Шукає промпти за запитом."""
        with self.get_db_session() as session:
            try:
                if category:
                    result = session.execute(
                        text(
                            """
                        SELECT id, user_id, name, description, template, category, is_public, is_active,
                               created_at, updated_at
                        FROM prompt_templates
                        WHERE (name ILIKE :query OR description ILIKE :query OR template ILIKE :query)
                        AND category = :category AND is_active = true
                        ORDER BY created_at DESC
                    """
                        ),
                        {"query": f"%{query}%", "category": category},
                    )
                else:
                    result = session.execute(
                        text(
                            """
                        SELECT id, user_id, name, description, template, category, is_public, is_active,
                               created_at, updated_at
                        FROM prompt_templates
                        WHERE (name ILIKE :query OR description ILIKE :query OR template ILIKE :query)
                        AND is_active = true
                        ORDER BY created_at DESC
                    """
                        ),
                        {"query": f"%{query}%"},
                    )

                return [self._row_to_prompt(row) for row in result.fetchall()]
            except Exception as e:
                print(f"❌ Помилка пошуку промптів: {e}")
                return []

    def update_prompt(self, prompt_id: str, **kwargs) -> bool:
        """Оновлює промпт."""
        with self.get_db_session() as session:
            try:
                update_fields = []
                params = {"prompt_id": prompt_id}

                for key, value in kwargs.items():
                    if key in [
                        "name",
                        "description",
                        "template",
                        "category",
                        "is_public",
                        "is_active",
                    ]:
                        update_fields.append(f"{key} = :{key}")
                        params[key] = value

                if update_fields:
                    update_fields.append("updated_at = :updated_at")
                    params["updated_at"] = datetime.now().isoformat()

                    session.execute(
                        text(
                            f"""
                        UPDATE prompt_templates
                        SET {', '.join(update_fields)}
                        WHERE id = :prompt_id
                    """
                        ),
                        params,
                    )

                    session.commit()
                    print(f"✅ Оновлено промпт: {prompt_id}")
                    return True
                return False
            except Exception as e:
                session.rollback()
                print(f"❌ Помилка оновлення промпту: {e}")
                return False

    def delete_prompt(self, prompt_id: str) -> bool:
        """Видаляє промпт."""
        with self.get_db_session() as session:
            try:
                session.execute(
                    text(
                        """
                    DELETE FROM prompt_templates WHERE id = :prompt_id
                """
                    ),
                    {"prompt_id": prompt_id},
                )

                session.commit()
                print(f"✅ Видалено промпт: {prompt_id}")
                return True
            except Exception as e:
                session.rollback()
                print(f"❌ Помилка видалення промпту: {e}")
                return False

    def record_usage(
        self,
        prompt_id: str,
        user_query: str = None,
        context: str = None,
        result: str = None,
        success: bool = True,
    ) -> bool:
        """Записує використання промпту."""
        with self.get_db_session() as session:
            try:
                # Додаємо запис про використання
                session.execute(
                    text(
                        """
                    INSERT INTO prompt_usage_history
                    (id, prompt_template_id, user_query, context, result, success, created_at)
                    VALUES (:id, :prompt_template_id, :user_query, :context, :result, :success, :created_at)
                """
                    ),
                    {
                        "id": str(uuid.uuid4()),
                        "prompt_template_id": prompt_id,
                        "user_query": user_query,
                        "context": context,
                        "result": result,
                        "success": success,
                        "created_at": datetime.now().isoformat(),
                    },
                )

                # Оновлюємо статистику промпту
                session.execute(
                    text(
                        """
                    UPDATE prompt_templates
                    SET usage_count = usage_count + 1,
                        success_rate = (
                            SELECT AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END)
                            FROM prompt_usage_history
                            WHERE prompt_template_id = :prompt_id
                        ),
                        updated_at = :updated_at
                    WHERE id = :prompt_id
                """
                    ),
                    {"prompt_id": prompt_id, "updated_at": datetime.now().isoformat()},
                )

                session.commit()
                return True
            except Exception as e:
                session.rollback()
                print(f"❌ Помилка запису використання: {e}")
                return False

    def get_best_prompt_for_query(
        self, user_query: str, category: str = None
    ) -> Optional[PromptTemplate]:
        """Знаходить найкращий промпт для запиту користувача."""
        if category:
            prompts = self.get_prompts_by_category(category)
        else:
            with self.get_db_session() as session:
                try:
                    result = session.execute(
                        text(
                            """
                        SELECT id, user_id, name, description, template, category, is_public, is_active,
                               created_at, updated_at
                        FROM prompt_templates
                        WHERE is_active = true
                        ORDER BY usage_count DESC, success_rate DESC
                    """
                        )
                    )
                    prompts = [self._row_to_prompt(row) for row in result.fetchall()]
                except Exception as e:
                    print(f"❌ Помилка отримання промптів: {e}")
                    return None

        if not prompts:
            return None

        # Простий алгоритм вибору найкращого промпту
        return prompts[0]

    def get_statistics(self) -> Dict[str, Any]:
        """Отримує статистику по промптах."""
        with self.get_db_session() as session:
            try:
                # Загальна статистика
                result = session.execute(
                    text(
                        """
                    SELECT
                        COUNT(*) as total_prompts,
                        COUNT(CASE WHEN is_active = true THEN 1 END) as active_prompts
                    FROM prompt_templates
                """
                    )
                )

                stats = result.fetchone()

                # Статистика по категоріях
                result = session.execute(
                    text(
                        """
                    SELECT category, COUNT(*) as count
                    FROM prompt_templates
                    WHERE is_active = true
                    GROUP BY category
                """
                    )
                )

                categories = [
                    {"category": row[0], "count": row[1], "avg_success": 0.0}
                    for row in result.fetchall()
                ]

                return {
                    "total_prompts": stats[0] or 0,
                    "active_prompts": stats[1] or 0,
                    "avg_success_rate": 0.0,  # Поки не реалізовано
                    "total_usage": 0,  # Поки не реалізовано
                    "categories": categories,
                }
            except Exception as e:
                print(f"❌ Помилка отримання статистики: {e}")
                return {
                    "total_prompts": 0,
                    "active_prompts": 0,
                    "avg_success_rate": 0.0,
                    "total_usage": 0,
                    "categories": [],
                }

    def _create_tables(self, session):
        """Створює таблиці якщо не існують."""
        try:
            # Імпортуємо моделі для створення таблиць
            from api.database import engine
            from api.models import Base

            # Створюємо всі таблиці через SQLAlchemy
            Base.metadata.create_all(bind=engine)

            # Створюємо системного користувача якщо не існує
            session.execute(
                text(
                    """
                INSERT INTO users (id, email, username, hashed_password, is_active)
                VALUES ('system', 'system@ai-swagger-bot.com', 'system', 'system_hash', true)
                ON CONFLICT (id) DO NOTHING
            """
                )
            )

            session.commit()
            print("✅ Створено таблиці для промптів")
        except Exception as e:
            session.rollback()
            print(f"❌ Помилка створення таблиць: {e}")
            raise

    def _row_to_prompt(self, row) -> PromptTemplate:
        """Конвертує рядок з БД в об'єкт PromptTemplate."""
        return PromptTemplate(
            id=row[0],
            user_id=row[1],
            name=row[2],
            description=row[3],
            template=row[4],
            category=row[5],
            is_public=row[6],
            is_active=row[7],
            created_at=row[8].isoformat() if row[8] else "",
            updated_at=row[9].isoformat() if row[9] else "",
        )

    def migrate_from_sqlite(self, sqlite_db_path: str = "prompts.db"):
        """Мігрує дані з SQLite в PostgreSQL."""
        import sqlite3

        try:
            # Підключаємося до SQLite
            sqlite_conn = sqlite3.connect(sqlite_db_path)
            sqlite_cursor = sqlite_conn.cursor()

            # Отримуємо всі промпти з SQLite
            sqlite_cursor.execute(
                """
                SELECT name, description, prompt_text, category, tags, is_active, created_at, updated_at, usage_count, success_rate
                FROM prompt_templates
            """
            )

            sqlite_prompts = sqlite_cursor.fetchall()

            print(f"📦 Знайдено {len(sqlite_prompts)} промптів для міграції")

            # Мігруємо кожен промпт
            for i, row in enumerate(sqlite_prompts, 1):
                prompt = PromptTemplate(
                    name=row[0],
                    description=row[1],
                    template=row[2],
                    category=row[3],
                    tags=json.loads(row[4]) if row[4] else [],
                    is_active=bool(row[5]),
                    created_at=row[6],
                    updated_at=row[7],
                    usage_count=row[8],
                    success_rate=row[9],
                )

                self.add_prompt(prompt)
                print(f"✅ Мігровано промпт {i}/{len(sqlite_prompts)}: {prompt.name}")

            sqlite_conn.close()
            print("🎉 Міграція завершена успішно!")

        except Exception as e:
            print(f"❌ Помилка міграції: {e}")
            raise
