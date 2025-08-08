"""
Менеджер YAML промптів для AI Swagger Bot
Завантажує базові промпти з YAML файлу та дозволяє додавати кастомні промпти через API
"""

import json
import os
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import yaml


class PromptCategory(str, Enum):
    """Категорії промптів."""

    SYSTEM = "system"
    INTENT_ANALYSIS = "intent_analysis"
    ERROR_HANDLING = "error_handling"
    RESPONSE_FORMATTING = "response_formatting"
    DATA_CREATION = "data_creation"
    DATA_RETRIEVAL = "data_retrieval"
    VALIDATION = "validation"
    DEBUGGING = "debugging"
    OPTIMIZATION = "optimization"
    USER_DEFINED = "user_defined"


@dataclass
class PromptTemplate:
    """Клас для представлення промпт-шаблону."""

    id: str
    name: str
    description: str
    template: str
    category: str
    tags: List[str]
    is_active: bool = True
    is_public: bool = True
    priority: int = 1
    created_at: str = ""
    updated_at: str = ""
    usage_count: int = 0
    success_rate: float = 0.0
    user_id: Optional[str] = None
    source: str = "yaml"  # "yaml", "api", "database"

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class PromptCategoryInfo:
    """Інформація про категорію промптів."""

    name: str
    description: str
    tags: List[str]
    prompt_count: int = 0


class YAMLPromptManager:
    """Менеджер для роботи з YAML промптами."""

    def __init__(self, yaml_path: str = "prompts/base_prompts.yaml", db_manager=None):
        """
        Ініціалізація менеджера YAML промптів.

        Args:
            yaml_path: Шлях до YAML файлу з базовими промптами
            db_manager: Менеджер бази даних для збереження кастомних промптів
        """
        self.yaml_path = yaml_path
        self.db_manager = db_manager
        self.prompts: Dict[str, PromptTemplate] = {}
        self.categories: Dict[str, PromptCategoryInfo] = {}
        self.settings: Dict[str, Any] = {}
        self.emoji_constants: Dict[str, str] = {}

        # Завантажуємо базові промпти
        self.load_base_prompts()

    def load_base_prompts(self) -> None:
        """Завантажує базові промпти з YAML файлу."""
        if not os.path.exists(self.yaml_path):
            print(f"⚠️ YAML файл не знайдено: {self.yaml_path}")
            return

        try:
            with open(self.yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            # Завантажуємо налаштування
            if "settings" in data:
                self.settings = data["settings"]

            # Завантажуємо категорії
            if "categories" in data:
                for category_id, category_info in data["categories"].items():
                    self.categories[category_id] = PromptCategoryInfo(
                        name=category_info["name"],
                        description=category_info["description"],
                        tags=category_info.get("tags", []),
                    )

            # Завантажуємо промпти
            if "prompts" in data:
                for prompt_id, prompt_info in data["prompts"].items():
                    prompt = PromptTemplate(
                        id=prompt_id,
                        name=prompt_info["name"],
                        description=prompt_info["description"],
                        template=prompt_info["template"],
                        category=prompt_info["category"],
                        tags=prompt_info.get("tags", []),
                        is_active=prompt_info.get("is_active", True),
                        is_public=prompt_info.get("is_public", True),
                        priority=prompt_info.get("priority", 1),
                        source="yaml",
                    )
                    self.prompts[prompt_id] = prompt

            # Завантажуємо константи емодзі
            if "emoji_constants" in data:
                self.emoji_constants = data["emoji_constants"]

            print(f"✅ Завантажено {len(self.prompts)} базових промптів з {self.yaml_path}")

        except Exception as e:
            print(f"❌ Помилка завантаження YAML промптів: {e}")

    def get_prompt(self, prompt_id: str) -> Optional[PromptTemplate]:
        """Отримує промпт за ID."""
        return self.prompts.get(prompt_id)

    def get_prompts_by_category(self, category: str) -> List[PromptTemplate]:
        """Отримує всі промпти категорії."""
        return [p for p in self.prompts.values() if p.category == category]

    def get_active_prompts(self) -> List[PromptTemplate]:
        """Отримує всі активні промпти."""
        return [p for p in self.prompts.values() if p.is_active]

    def get_public_prompts(self) -> List[PromptTemplate]:
        """Отримує всі публічні промпти."""
        return [p for p in self.prompts.values() if p.is_public]

    def add_custom_prompt(self, prompt_data: Dict[str, Any], user_id: Optional[str] = None) -> str:
        """
        Додає кастомний промпт.

        Args:
            prompt_data: Дані промпту
            user_id: ID користувача (для кастомних промптів)

        Returns:
            ID створеного промпту
        """
        prompt_id = str(uuid.uuid4())

        prompt = PromptTemplate(
            id=prompt_id,
            name=prompt_data["name"],
            description=prompt_data.get("description", ""),
            template=prompt_data["template"],
            category=prompt_data.get("category", PromptCategory.USER_DEFINED.value),
            tags=prompt_data.get("tags", []),
            is_active=prompt_data.get("is_active", True),
            is_public=prompt_data.get("is_public", False),
            priority=prompt_data.get("priority", 100),  # Низький пріоритет для кастомних
            user_id=user_id,
            source="api",
        )

        self.prompts[prompt_id] = prompt

        # Зберігаємо в базу даних якщо є менеджер БД
        if self.db_manager:
            try:
                self.db_manager.add_prompt(prompt)
            except Exception as e:
                print(f"⚠️ Помилка збереження промпту в БД: {e}")

        print(f"✅ Додано кастомний промпт: {prompt.name}")
        return prompt_id

    def update_prompt(self, prompt_id: str, prompt_data: Dict[str, Any]) -> bool:
        """
        Оновлює промпт.

        Args:
            prompt_id: ID промпту
            prompt_data: Нові дані промпту

        Returns:
            True якщо успішно оновлено
        """
        if prompt_id not in self.prompts:
            return False

        prompt = self.prompts[prompt_id]

        # Оновлюємо поля
        for key, value in prompt_data.items():
            if hasattr(prompt, key):
                setattr(prompt, key, value)

        prompt.updated_at = datetime.now().isoformat()

        # Оновлюємо в базі даних
        if self.db_manager and prompt.source == "api":
            try:
                self.db_manager.update_prompt(prompt)
            except Exception as e:
                print(f"⚠️ Помилка оновлення промпту в БД: {e}")

        print(f"✅ Оновлено промпт: {prompt.name}")
        return True

    def delete_prompt(self, prompt_id: str) -> bool:
        """
        Видаляє промпт.

        Args:
            prompt_id: ID промпту

        Returns:
            True якщо успішно видалено
        """
        if prompt_id not in self.prompts:
            return False

        prompt = self.prompts[prompt_id]

        # Видаляємо з пам'яті
        del self.prompts[prompt_id]

        # Видаляємо з бази даних
        if self.db_manager and prompt.source == "api":
            try:
                self.db_manager.delete_prompt(prompt_id)
            except Exception as e:
                print(f"⚠️ Помилка видалення промпту з БД: {e}")

        print(f"✅ Видалено промпт: {prompt.name}")
        return True

    def search_prompts(self, query: str, category: Optional[str] = None) -> List[PromptTemplate]:
        """
        Шукає промпти за запитом.

        Args:
            query: Пошуковий запит
            category: Фільтр за категорією

        Returns:
            Список знайдених промптів
        """
        results = []
        query_lower = query.lower()

        for prompt in self.prompts.values():
            if not prompt.is_active:
                continue

            if category and prompt.category != category:
                continue

            # Пошук по назві, опису, тегам
            if (
                query_lower in prompt.name.lower()
                or query_lower in prompt.description.lower()
                or any(query_lower in tag.lower() for tag in prompt.tags)
            ):
                results.append(prompt)

        # Сортуємо за пріоритетом
        results.sort(key=lambda x: x.priority)
        return results

    def get_prompt_suggestions(self, user_query: str, context: str = "") -> List[PromptTemplate]:
        """
        Отримує пропозиції промптів для запиту користувача.

        Args:
            user_query: Запит користувача
            context: Контекст розмови

        Returns:
            Список рекомендованих промптів
        """
        suggestions = []
        query_lower = user_query.lower()

        # Аналізуємо запит для визначення типу операції
        is_creation = any(word in query_lower for word in ["створи", "додай", "create", "add"])
        is_retrieval = any(
            word in query_lower for word in ["покажи", "знайди", "get", "find", "show"]
        )
        is_update = any(word in query_lower for word in ["онов", "зміни", "update", "modify"])
        is_delete = any(word in query_lower for word in ["видали", "delete", "remove"])
        is_error = any(word in query_lower for word in ["помилка", "error", "проблема"])

        # Підбираємо промпти на основі типу операції
        for prompt in self.prompts.values():
            if not prompt.is_active:
                continue

            score = 0

            # Базовий скор за категорію
            if is_creation and prompt.category == PromptCategory.DATA_CREATION.value:
                score += 10
            elif is_retrieval and prompt.category == PromptCategory.DATA_RETRIEVAL.value:
                score += 10
            elif is_error and prompt.category == PromptCategory.ERROR_HANDLING.value:
                score += 10

            # Додатковий скор за теги
            for tag in prompt.tags:
                if tag.lower() in query_lower:
                    score += 5

            # Скор за пріоритет
            score += (100 - prompt.priority) / 10

            if score > 0:
                suggestions.append((prompt, score))

        # Сортуємо за скором
        suggestions.sort(key=lambda x: x[1], reverse=True)

        return [prompt for prompt, score in suggestions[:5]]  # Повертаємо топ-5

    def format_prompt(self, prompt_id: str, **kwargs) -> str:
        """
        Форматує промпт з параметрами.

        Args:
            prompt_id: ID промпту
            **kwargs: Параметри для форматування

        Returns:
            Відформатований промпт
        """
        prompt = self.get_prompt(prompt_id)
        if not prompt:
            return ""

        try:
            return prompt.template.format(**kwargs)
        except KeyError as e:
            print(f"⚠️ Помилка форматування промпту {prompt_id}: відсутній параметр {e}")
            return prompt.template

    def export_specific_prompts_to_yaml(
        self, file_path: str, specific_prompts: List[PromptTemplate]
    ) -> None:
        """
        Експортує конкретні промпти в YAML файл.

        Args:
            file_path: Шлях до файлу
            specific_prompts: Список промптів для експорту
        """
        export_data = {
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "description": f"Експорт {len(specific_prompts)} промптів з YAML менеджера",
            "settings": self.settings,
            "categories": {
                cat_id: asdict(cat_info) for cat_id, cat_info in self.categories.items()
            },
            "prompts": {},
        }

        for prompt in specific_prompts:
            export_data["prompts"][prompt.id] = asdict(prompt)

        # Створюємо директорію якщо не існує
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(export_data, f, default_flow_style=False, allow_unicode=True)
            print(f"✅ Експортовано {len(specific_prompts)} промптів в {file_path}")
        except Exception as e:
            print(f"❌ Помилка експорту: {e}")
            raise

    def export_prompts_to_yaml(self, file_path: str, include_custom: bool = True) -> None:
        """
        Експортує промпти в YAML файл.

        Args:
            file_path: Шлях до файлу
            include_custom: Чи включати кастомні промпти
        """
        export_data = {
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "description": "Експорт промптів з YAML менеджера",
            "settings": self.settings,
            "categories": {
                cat_id: asdict(cat_info) for cat_id, cat_info in self.categories.items()
            },
            "prompts": {},
        }

        for prompt_id, prompt in self.prompts.items():
            if not include_custom and prompt.source == "api":
                continue

            export_data["prompts"][prompt_id] = asdict(prompt)

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(export_data, f, default_flow_style=False, allow_unicode=True)
            print(f"✅ Промпти експортовано в {file_path}")
        except Exception as e:
            print(f"❌ Помилка експорту: {e}")

    def import_prompts_from_yaml(self, file_path: str, overwrite: bool = False) -> None:
        """
        Імпортує промпти з YAML файлу.

        Args:
            file_path: Шлях до файлу
            overwrite: Чи перезаписувати існуючі промпти
        """
        if not os.path.exists(file_path):
            print(f"❌ Файл не знайдено: {file_path}")
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            imported_count = 0

            if "prompts" in data:
                for prompt_id, prompt_info in data["prompts"].items():
                    if prompt_id in self.prompts and not overwrite:
                        continue

                    prompt = PromptTemplate(
                        id=prompt_id,
                        name=prompt_info["name"],
                        description=prompt_info["description"],
                        template=prompt_info["template"],
                        category=prompt_info["category"],
                        tags=prompt_info.get("tags", []),
                        is_active=prompt_info.get("is_active", True),
                        is_public=prompt_info.get("is_public", True),
                        priority=prompt_info.get("priority", 1),
                        source="imported",
                    )

                    self.prompts[prompt_id] = prompt
                    imported_count += 1

            print(f"✅ Імпортовано {imported_count} промптів з {file_path}")

        except Exception as e:
            print(f"❌ Помилка імпорту: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Отримує статистику промптів."""
        total_prompts = len(self.prompts)
        active_prompts = len(self.get_active_prompts())
        public_prompts = len(self.get_public_prompts())

        category_stats = {}
        for category in PromptCategory:
            category_prompts = self.get_prompts_by_category(category.value)
            category_stats[category.value] = len(category_prompts)

        source_stats = {}
        for prompt in self.prompts.values():
            source = prompt.source
            source_stats[source] = source_stats.get(source, 0) + 1

        return {
            "total_prompts": total_prompts,
            "active_prompts": active_prompts,
            "public_prompts": public_prompts,
            "categories": category_stats,
            "sources": source_stats,
            "categories_info": {
                cat_id: asdict(cat_info) for cat_id, cat_info in self.categories.items()
            },
        }

    def reload_base_prompts(self) -> None:
        """Перезавантажує базові промпти з YAML файлу."""
        # Зберігаємо кастомні промпти
        custom_prompts = {pid: p for pid, p in self.prompts.items() if p.source == "api"}

        # Очищаємо промпти
        self.prompts.clear()

        # Завантажуємо базові промпти
        self.load_base_prompts()

        # Відновлюємо кастомні промпти
        self.prompts.update(custom_prompts)

        print("✅ Базові промпти перезавантажено")


# Приклад використання
if __name__ == "__main__":
    # Створюємо менеджер
    manager = YAMLPromptManager()

    # Отримуємо статистику
    stats = manager.get_statistics()
    print("📊 Статистика промптів:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))

    # Шукаємо промпти
    search_results = manager.search_prompts("створення")
    print(f"\n🔍 Знайдено {len(search_results)} промптів для 'створення':")
    for prompt in search_results:
        print(f"  • {prompt.name} ({prompt.category})")

    # Отримуємо пропозиції
    suggestions = manager.get_prompt_suggestions("Створи нову категорію")
    print(f"\n💡 Пропозиції для 'Створи нову категорію':")
    for prompt in suggestions:
        print(f"  • {prompt.name} (пріоритет: {prompt.priority})")
