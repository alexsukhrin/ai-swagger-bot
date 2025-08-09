"""
Тести для YAML менеджера промптів
"""

import os
import tempfile
from datetime import datetime

import pytest
import yaml

from src.yaml_prompt_manager import PromptCategory, PromptTemplate, YAMLPromptManager


class TestYAMLPromptManager:
    """Тести для YAMLPromptManager."""

    @pytest.fixture
    def temp_yaml_file(self):
        """Створює тимчасовий YAML файл для тестів."""
        test_data = {
            "version": "1.0",
            "description": "Тестові промпти",
            "settings": {"default_language": "uk", "default_emoji": True},
            "categories": {
                "system": {
                    "name": "Системні промпти",
                    "description": "Базові промпти для системи",
                    "tags": ["core", "system"],
                },
                "test": {
                    "name": "Тестові промпти",
                    "description": "Промпти для тестування",
                    "tags": ["test", "debug"],
                },
            },
            "prompts": {
                "test_system": {
                    "name": "Тестовий системний промпт",
                    "description": "Тестовий промпт для системи",
                    "template": "Ти - експерт з API. {user_query}",
                    "category": "system",
                    "tags": ["test", "system"],
                    "is_active": True,
                    "is_public": True,
                    "priority": 1,
                },
                "test_creation": {
                    "name": "Тестовий промпт створення",
                    "description": "Тестовий промпт для створення об'єктів",
                    "template": "Створи об'єкт: {user_query}",
                    "category": "data_creation",
                    "tags": ["test", "creation"],
                    "is_active": True,
                    "is_public": True,
                    "priority": 2,
                },
            },
            "emoji_constants": {"SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f, default_flow_style=False, allow_unicode=True)
            yield f.name

        # Видаляємо тимчасовий файл
        os.unlink(f.name)

    @pytest.fixture
    def manager(self, temp_yaml_file):
        """Створює менеджер з тестовими даними."""
        return YAMLPromptManager(temp_yaml_file)

    def test_load_base_prompts(self, manager):
        """Тест завантаження базових промптів."""
        assert len(manager.prompts) == 2
        assert "test_system" in manager.prompts
        assert "test_creation" in manager.prompts

        # Перевіряємо налаштування
        assert manager.settings["default_language"] == "uk"
        assert manager.settings["default_emoji"] is True

        # Перевіряємо категорії
        assert len(manager.categories) == 2
        assert "system" in manager.categories
        assert "test" in manager.categories

        # Перевіряємо константи емодзі
        assert manager.emoji_constants["SUCCESS"] == "✅"
        assert manager.emoji_constants["ERROR"] == "❌"

    def test_get_prompt(self, manager):
        """Тест отримання промпту за ID."""
        prompt = manager.get_prompt("test_system")
        assert prompt is not None
        assert prompt.name == "Тестовий системний промпт"
        assert prompt.category == "system"
        assert prompt.is_active is True

        # Тест неіснуючого промпту
        prompt = manager.get_prompt("non_existent")
        assert prompt is None

    def test_get_prompts_by_category(self, manager):
        """Тест отримання промптів за категорією."""
        system_prompts = manager.get_prompts_by_category("system")
        assert len(system_prompts) == 1
        assert system_prompts[0].name == "Тестовий системний промпт"

        creation_prompts = manager.get_prompts_by_category("data_creation")
        assert len(creation_prompts) == 1
        assert creation_prompts[0].name == "Тестовий промпт створення"

    def test_get_active_prompts(self, manager):
        """Тест отримання активних промптів."""
        active_prompts = manager.get_active_prompts()
        assert len(active_prompts) == 2

        # Додаємо неактивний промпт
        inactive_prompt = PromptTemplate(
            id="inactive_test",
            name="Неактивний промпт",
            description="Тестовий неактивний промпт",
            template="Тест",
            category="system",
            tags=["test"],
            is_active=False,
        )
        manager.prompts["inactive_test"] = inactive_prompt

        active_prompts = manager.get_active_prompts()
        assert len(active_prompts) == 2  # Неактивний не включається

    def test_add_custom_prompt(self, manager):
        """Тест додавання кастомного промпту."""
        prompt_data = {
            "name": "Мій кастомний промпт",
            "description": "Опис кастомного промпту",
            "template": "Кастомний шаблон: {user_query}",
            "category": "user_defined",
            "tags": ["custom", "test"],
            "is_active": True,
            "is_public": False,
            "priority": 100,
        }

        prompt_id = manager.add_custom_prompt(prompt_data, user_id="test_user")
        assert prompt_id is not None

        # Перевіряємо що промпт додано
        prompt = manager.get_prompt(prompt_id)
        assert prompt is not None
        assert prompt.name == "Мій кастомний промпт"
        assert prompt.user_id == "test_user"
        assert prompt.source == "api"

    def test_update_prompt(self, manager):
        """Тест оновлення промпту."""
        # Додаємо кастомний промпт
        prompt_data = {
            "name": "Промпт для оновлення",
            "description": "Оригінальний опис",
            "template": "Оригінальний шаблон",
            "category": "user_defined",
            "tags": ["test"],
        }
        prompt_id = manager.add_custom_prompt(prompt_data, user_id="test_user")

        # Оновлюємо промпт
        update_data = {
            "name": "Оновлена назва",
            "description": "Оновлений опис",
            "template": "Оновлений шаблон",
            "category": "system",
        }

        success = manager.update_prompt(prompt_id, update_data)
        assert success is True

        # Перевіряємо оновлення
        updated_prompt = manager.get_prompt(prompt_id)
        assert updated_prompt.name == "Оновлена назва"
        assert updated_prompt.description == "Оновлений опис"
        assert updated_prompt.template == "Оновлений шаблон"
        assert updated_prompt.category == "system"

    def test_delete_prompt(self, manager):
        """Тест видалення промпту."""
        # Додаємо кастомний промпт
        prompt_data = {
            "name": "Промпт для видалення",
            "description": "Опис",
            "template": "Шаблон",
            "category": "user_defined",
            "tags": ["test"],
        }
        prompt_id = manager.add_custom_prompt(prompt_data, user_id="test_user")

        # Перевіряємо що промпт існує
        assert manager.get_prompt(prompt_id) is not None

        # Видаляємо промпт
        success = manager.delete_prompt(prompt_id)
        assert success is True

        # Перевіряємо що промпт видалено
        assert manager.get_prompt(prompt_id) is None

    def test_search_prompts(self, manager):
        """Тест пошуку промптів."""
        # Пошук за назвою
        results = manager.search_prompts("системний")
        assert len(results) == 1
        assert results[0].name == "Тестовий системний промпт"

        # Пошук за категорією
        results = manager.search_prompts("створення", category="data_creation")
        assert len(results) == 1
        assert results[0].name == "Тестовий промпт створення"

        # Пошук за тегами
        results = manager.search_prompts("test")
        assert len(results) == 2

        # Пошук неіснуючого
        results = manager.search_prompts("неіснуючий")
        assert len(results) == 0

    def test_get_prompt_suggestions(self, manager):
        """Тест отримання пропозицій промптів."""
        # Пропозиції для створення
        suggestions = manager.get_prompt_suggestions("Створи нову категорію")
        assert len(suggestions) > 0

        # Пропозиції для системних операцій
        suggestions = manager.get_prompt_suggestions("Покажи всі категорії")
        assert len(suggestions) > 0

    def test_format_prompt(self, manager):
        """Тест форматування промпту."""
        formatted = manager.format_prompt("test_system", user_query="Покажи категорії")
        assert "Ти - експерт з API" in formatted
        assert "Покажи категорії" in formatted

        # Тест з неіснуючим параметром
        formatted = manager.format_prompt("test_system", user_query="Тест", non_existent="value")
        assert "Ти - експерт з API" in formatted

    def test_get_statistics(self, manager):
        """Тест отримання статистики."""
        stats = manager.get_statistics()

        assert "total_prompts" in stats
        assert "active_prompts" in stats
        assert "public_prompts" in stats
        assert "categories" in stats
        assert "sources" in stats

        assert stats["total_prompts"] == 2
        assert stats["active_prompts"] == 2
        assert stats["public_prompts"] == 2
        assert "system" in stats["categories"]
        assert "data_creation" in stats["categories"]

    def test_export_import_prompts(self, manager, temp_yaml_file):
        """Тест експорту та імпорту промптів."""
        # Додаємо кастомний промпт
        prompt_data = {
            "name": "Промпт для експорту",
            "description": "Опис",
            "template": "Шаблон",
            "category": "user_defined",
            "tags": ["export"],
        }
        manager.add_custom_prompt(prompt_data, user_id="test_user")

        # Експортуємо промпти
        export_file = temp_yaml_file.replace(".yaml", "_export.yaml")
        manager.export_prompts_to_yaml(export_file, include_custom=True)

        # Створюємо новий менеджер
        new_manager = YAMLPromptManager()

        # Імпортуємо промпти
        new_manager.import_prompts_from_yaml(export_file, overwrite=True)

        # Перевіряємо що промпти імпортовано
        assert len(new_manager.prompts) > 0

        # Видаляємо тимчасовий файл
        os.unlink(export_file)

    def test_reload_base_prompts(self, manager):
        """Тест перезавантаження базових промптів."""
        # Додаємо кастомний промпт
        prompt_data = {
            "name": "Кастомний промпт",
            "description": "Опис",
            "template": "Шаблон",
            "category": "user_defined",
            "tags": ["custom"],
        }
        custom_prompt_id = manager.add_custom_prompt(prompt_data, user_id="test_user")

        # Перезавантажуємо базові промпти
        manager.reload_base_prompts()

        # Перевіряємо що базові промпти завантажено
        assert "test_system" in manager.prompts
        assert "test_creation" in manager.prompts

        # Перевіряємо що кастомний промпт зберігся
        assert custom_prompt_id in manager.prompts

    def test_prompt_template_creation(self):
        """Тест створення PromptTemplate."""
        prompt = PromptTemplate(
            id="test_id",
            name="Тестовий промпт",
            description="Опис",
            template="Шаблон",
            category="system",
            tags=["test"],
            is_active=True,
            is_public=True,
            priority=1,
        )

        assert prompt.id == "test_id"
        assert prompt.name == "Тестовий промпт"
        assert prompt.category == "system"
        assert prompt.is_active is True
        assert prompt.is_public is True
        assert prompt.priority == 1
        assert prompt.source == "yaml"

    def test_prompt_category_enum(self):
        """Тест enum категорій промптів."""
        assert PromptCategory.SYSTEM.value == "system"
        assert PromptCategory.USER_DEFINED.value == "user_defined"
        assert PromptCategory.DATA_CREATION.value == "data_creation"

        # Перевіряємо всі категорії
        categories = [cat.value for cat in PromptCategory]
        expected_categories = [
            "system",
            "intent_analysis",
            "error_handling",
            "response_formatting",
            "data_creation",
            "data_retrieval",
            "validation",
            "debugging",
            "optimization",
            "user_defined",
        ]
        assert set(categories) == set(expected_categories)


if __name__ == "__main__":
    pytest.main([__file__])
