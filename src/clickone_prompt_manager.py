"""
Спеціалізований менеджер промптів для Clickone Shop API
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class ClickonePrompt:
    """Структура промпту для Clickone Shop API"""

    name: str
    description: str
    template: str
    tags: List[str]
    priority: int
    category: str


class ClickonePromptManager:
    """Менеджер промптів для Clickone Shop API"""

    def __init__(self, prompts_file: str = "prompts/clickone_shop_api_prompts.yaml"):
        self.prompts_file = prompts_file
        self.prompts: Dict[str, ClickonePrompt] = {}
        self.categories: Dict[str, Dict[str, Any]] = {}
        self.settings: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
        self.load_prompts()

    def load_prompts(self) -> None:
        """Завантажує промпти з YAML файлу"""
        try:
            prompts_path = Path(__file__).parent.parent / self.prompts_file

            if not prompts_path.exists():
                raise FileNotFoundError(f"Файл промптів не знайдено: {prompts_path}")

            with open(prompts_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            # Завантажуємо налаштування
            self.settings = data.get("settings", {})
            self.categories = data.get("categories", {})
            self.metadata = data.get("metadata", {})

            # Завантажуємо промпти
            prompts_data = data.get("prompts", {})
            for prompt_id, prompt_data in prompts_data.items():
                prompt = ClickonePrompt(
                    name=prompt_data.get("name", ""),
                    description=prompt_data.get("description", ""),
                    template=prompt_data.get("template", ""),
                    tags=prompt_data.get("tags", []),
                    priority=prompt_data.get("priority", 5),
                    category=prompt_data.get("category", "clickone_core"),
                )
                self.prompts[prompt_id] = prompt

            print(f"✅ Завантажено {len(self.prompts)} промптів для Clickone Shop API")

        except Exception as e:
            print(f"❌ Помилка завантаження промптів: {e}")
            self._create_default_prompts()

    def _create_default_prompts(self) -> None:
        """Створює базові промпти за замовчуванням"""
        print("🔄 Створення базових промптів за замовчуванням...")

        # Базовий системний промпт
        system_prompt = ClickonePrompt(
            name="Базовий системний промпт Clickone Shop API",
            description="Основний промпт для роботи з Clickone Shop Backend API",
            template="Ти - експерт з Clickone Shop Backend API v1.0. Допоможи користувачу взаємодіяти з e-commerce платформою.",
            tags=["clickone", "system", "base"],
            priority=1,
            category="clickone_core",
        )

        self.prompts["clickone_system_base"] = system_prompt
        print("✅ Створено базовий системний промпт")

    def get_prompt(self, prompt_id: str) -> Optional[ClickonePrompt]:
        """Отримує промпт за ID"""
        return self.prompts.get(prompt_id)

    def get_prompts_by_category(self, category: str) -> List[ClickonePrompt]:
        """Отримує всі промпти за категорією"""
        return [prompt for prompt in self.prompts.values() if prompt.category == category]

    def get_prompts_by_tag(self, tag: str) -> List[ClickonePrompt]:
        """Отримує всі промпти за тегом"""
        return [prompt for prompt in self.prompts.values() if tag in prompt.tags]

    def get_prompts_by_priority(self, priority: int) -> List[ClickonePrompt]:
        """Отримує всі промпти за пріоритетом"""
        return [prompt for prompt in self.prompts.values() if prompt.priority == priority]

    def search_prompts(self, query: str) -> List[ClickonePrompt]:
        """Шукає промпти за запитом"""
        query_lower = query.lower()
        results = []

        for prompt in self.prompts.values():
            if (
                query_lower in prompt.name.lower()
                or query_lower in prompt.description.lower()
                or any(query_lower in tag.lower() for tag in prompt.tags)
            ):
                results.append(prompt)

        return results

    def get_system_prompt(self) -> str:
        """Отримує системний промпт"""
        system_prompt = self.get_prompt("clickone_system_base")
        if system_prompt:
            return system_prompt.template
        return "Ти - експерт з Clickone Shop Backend API. Допоможи користувачу."

    def get_intent_analysis_prompt(self) -> str:
        """Отримує промпт для аналізу наміру"""
        intent_prompt = self.get_prompt("clickone_intent_analysis")
        if intent_prompt:
            return intent_prompt.template
        return "Проаналізуй запит користувача для Clickone Shop API."

    def get_category_creation_prompt(self) -> str:
        """Отримує промпт для створення категорії"""
        create_prompt = self.get_prompt("clickone_create_category")
        if create_prompt:
            return create_prompt.template
        return "Допоможи створити категорію в Clickone Shop API."

    def get_category_retrieval_prompt(self) -> str:
        """Отримує промпт для отримання категорій"""
        get_prompt = self.get_prompt("clickone_get_categories")
        if get_prompt:
            return get_prompt.template
        return "Допоможи отримати категорії з Clickone Shop API."

    def get_category_update_prompt(self) -> str:
        """Отримує промпт для оновлення категорії"""
        update_prompt = self.get_prompt("clickone_update_category")
        if update_prompt:
            return update_prompt.template
        return "Допоможи оновити категорію в Clickone Shop API."

    def get_category_deletion_prompt(self) -> str:
        """Отримує промпт для видалення категорії"""
        delete_prompt = self.get_prompt("clickone_delete_category")
        if delete_prompt:
            return delete_prompt.template
        return "Допоможи видалити категорію з Clickone Shop API."

    def get_search_filter_prompt(self) -> str:
        """Отримує промпт для пошуку та фільтрації"""
        search_prompt = self.get_prompt("clickone_search_filter")
        if search_prompt:
            return search_prompt.template
        return "Допоможи знайти інформацію в Clickone Shop API."

    def get_error_handling_prompt(self) -> str:
        """Отримує промпт для обробки помилок"""
        error_prompt = self.get_prompt("clickone_error_handling")
        if error_prompt:
            return error_prompt.template
        return "Допоможи зрозуміти та виправити помилку API."

    def get_jwt_auth_prompt(self) -> str:
        """Отримує промпт для JWT автентифікації"""
        jwt_prompt = self.get_prompt("clickone_jwt_auth")
        if jwt_prompt:
            return jwt_prompt.template
        return "Допоможи налаштувати JWT автентифікацію."

    def get_user_help_prompt(self) -> str:
        """Отримує промпт для допомоги користувачу"""
        help_prompt = self.get_prompt("clickone_user_help")
        if help_prompt:
            return help_prompt.template
        return "Надай допомогу користувачу Clickone Shop API."

    def format_prompt(self, prompt_id: str, **kwargs) -> str:
        """Форматує промпт з параметрами"""
        prompt = self.get_prompt(prompt_id)
        if not prompt:
            return f"Промпт {prompt_id} не знайдено"

        try:
            return prompt.template.format(**kwargs)
        except KeyError as e:
            return f"Помилка форматування промпту: відсутній параметр {e}"

    def get_api_info(self) -> Dict[str, Any]:
        """Отримує інформацію про API"""
        return {
            "title": self.metadata.get("api_title", "Clickone Shop Backend API"),
            "version": self.metadata.get("api_version", "1.0"),
            "base_url": self.metadata.get("base_url", "https://api.oneshop.click"),
            "endpoints_count": self.metadata.get("endpoints_count", 5),
            "schemas_count": self.metadata.get("schemas_count", 37),
            "security_scheme": self.metadata.get("security_scheme", "JWT Bearer"),
            "documentation_url": self.metadata.get("documentation_url", ""),
            "openapi_spec_url": self.metadata.get("openapi_spec_url", ""),
        }

    def get_categories_info(self) -> Dict[str, Any]:
        """Отримує інформацію про категорії промптів"""
        return {
            "total_categories": len(self.categories),
            "total_prompts": len(self.prompts),
            "categories": self.categories,
            "prompts_by_category": {
                category: len(self.get_prompts_by_category(category))
                for category in self.categories.keys()
            },
        }

    def validate_prompts(self) -> List[str]:
        """Валідує промпти та повертає список помилок"""
        errors = []

        for prompt_id, prompt in self.prompts.items():
            # Перевіряємо обов'язкові поля
            if not prompt.name:
                errors.append(f"Промпт {prompt_id}: відсутня назва")
            if not prompt.template:
                errors.append(f"Промпт {prompt_id}: відсутній шаблон")
            if not prompt.tags:
                errors.append(f"Промпт {prompt_id}: відсутні теги")

            # Перевіряємо категорію
            if prompt.category not in self.categories:
                errors.append(f"Промпт {prompt_id}: невідома категорія {prompt.category}")

        return errors

    def export_prompts(self, output_file: str = "clickone_prompts_export.yaml") -> bool:
        """Експортує промпти в YAML файл"""
        try:
            export_data = {
                "version": "2.0",
                "exported_at": "2025-01-27T00:00:00Z",
                "description": "Експорт промптів Clickone Shop API",
                "settings": self.settings,
                "categories": self.categories,
                "metadata": self.metadata,
                "prompts": {},
            }

            for prompt_id, prompt in self.prompts.items():
                export_data["prompts"][prompt_id] = {
                    "name": prompt.name,
                    "description": prompt.description,
                    "template": prompt.template,
                    "tags": prompt.tags,
                    "priority": prompt.priority,
                    "category": prompt.category,
                }

            output_path = Path(__file__).parent.parent / output_file
            with open(output_path, "w", encoding="utf-8") as f:
                yaml.dump(export_data, f, default_flow_style=False, allow_unicode=True)

            print(f"✅ Промпти експортовано в {output_file}")
            return True

        except Exception as e:
            print(f"❌ Помилка експорту промптів: {e}")
            return False


# Глобальний екземпляр менеджера промптів
clickone_prompt_manager = ClickonePromptManager()


def get_clickone_prompt_manager() -> ClickonePromptManager:
    """Отримує глобальний екземпляр менеджера промптів"""
    return clickone_prompt_manager
