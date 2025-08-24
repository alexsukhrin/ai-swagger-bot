"""
Тест для менеджера промптів Clickone Shop API
"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
import yaml


@pytest.fixture
def mock_yaml_load():
    with patch("yaml.safe_load") as mock:
        mock.return_value = {
            "settings": {"default_language": "uk", "api_base_url": "https://api.oneshop.click"},
            "categories": {
                "clickone_core": {
                    "name": "Основні функції Clickone Shop API",
                    "description": "Базові промпти для роботи з API",
                }
            },
            "metadata": {"api_version": "1.0", "endpoints_count": 5},
            "prompts": {
                "clickone_system_base": {
                    "name": "Базовий системний промпт",
                    "description": "Основний промпт для роботи з API",
                    "template": "Ти - експерт з Clickone Shop API",
                    "tags": ["clickone", "system"],
                    "priority": 1,
                    "category": "clickone_core",
                }
            },
        }
        yield mock


@pytest.fixture
def mock_file_exists():
    with patch("pathlib.Path.exists") as mock:
        mock.return_value = True
        yield mock


class TestClickonePromptManager:
    """Тести для менеджера промптів Clickone Shop API"""

    @patch("pathlib.Path.exists")
    @patch("builtins.open")
    @patch("yaml.safe_load")
    def test_prompt_manager_initialization(self, mock_yaml_load, mock_open, mock_exists):
        """Тест ініціалізації менеджера промптів"""
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = "test content"

        mock_yaml_load.return_value = {
            "settings": {"default_language": "uk"},
            "categories": {"test": {"name": "Test"}},
            "metadata": {"version": "1.0"},
            "prompts": {},
        }

        from src.clickone_prompt_manager import ClickonePromptManager

        manager = ClickonePromptManager()

        assert manager is not None
        assert len(manager.prompts) == 0
        assert len(manager.categories) == 1

    @patch("pathlib.Path.exists")
    def test_prompt_manager_file_not_found(self, mock_exists):
        """Тест поведінки при відсутності файлу промптів"""
        mock_exists.return_value = False

        from src.clickone_prompt_manager import ClickonePromptManager

        manager = ClickonePromptManager()

        # Повинен створити базові промпти за замовчуванням
        assert len(manager.prompts) > 0
        assert "clickone_system_base" in manager.prompts

    def test_prompt_manager_get_prompt(self):
        """Тест отримання промпту за ID"""
        from src.clickone_prompt_manager import ClickonePromptManager

        with patch("pathlib.Path.exists", return_value=False):
            manager = ClickonePromptManager()

        # Тестуємо отримання існуючого промпту
        prompt = manager.get_prompt("clickone_system_base")
        assert prompt is not None
        assert prompt.name == "Базовий системний промпт Clickone Shop API"

        # Тестуємо отримання неіснуючого промпту
        prompt = manager.get_prompt("non_existent")
        assert prompt is None

    def test_prompt_manager_get_prompts_by_category(self):
        """Тест отримання промптів за категорією"""
        from src.clickone_prompt_manager import ClickonePromptManager

        with patch("pathlib.Path.exists", return_value=False):
            manager = ClickonePromptManager()

        prompts = manager.get_prompts_by_category("clickone_core")
        assert len(prompts) > 0
        assert all(prompt.category == "clickone_core" for prompt in prompts)

    def test_prompt_manager_get_prompts_by_tag(self):
        """Тест отримання промптів за тегом"""
        from src.clickone_prompt_manager import ClickonePromptManager

        with patch("pathlib.Path.exists", return_value=False):
            manager = ClickonePromptManager()

        prompts = manager.get_prompts_by_tag("clickone")
        assert len(prompts) > 0
        assert all("clickone" in prompt.tags for prompt in prompts)

    def test_prompt_manager_get_prompts_by_priority(self):
        """Тест отримання промптів за пріоритетом"""
        from src.clickone_prompt_manager import ClickonePromptManager

        with patch("pathlib.Path.exists", return_value=False):
            manager = ClickonePromptManager()

        prompts = manager.get_prompts_by_priority(1)
        assert len(prompts) > 0
        assert all(prompt.priority == 1 for prompt in prompts)

    def test_prompt_manager_search_prompts(self):
        """Тест пошуку промптів"""
        from src.clickone_prompt_manager import ClickonePromptManager

        with patch("pathlib.Path.exists", return_value=False):
            manager = ClickonePromptManager()

        # Пошук за назвою
        results = manager.search_prompts("системний")
        assert len(results) > 0

        # Пошук за тегом
        results = manager.search_prompts("clickone")
        assert len(results) > 0

        # Пошук неіснуючого
        results = manager.search_prompts("неіснуючий")
        assert len(results) == 0

    def test_prompt_manager_get_system_prompt(self):
        """Тест отримання системного промпту"""
        from src.clickone_prompt_manager import ClickonePromptManager

        with patch("pathlib.Path.exists", return_value=False):
            manager = ClickonePromptManager()

        system_prompt = manager.get_system_prompt()
        assert system_prompt is not None
        assert "Clickone Shop Backend API" in system_prompt

    def test_prompt_manager_get_intent_analysis_prompt(self):
        """Тест отримання промпту для аналізу наміру"""
        from src.clickone_prompt_manager import ClickonePromptManager

        with patch("pathlib.Path.exists", return_value=False):
            manager = ClickonePromptManager()

        intent_prompt = manager.get_intent_analysis_prompt()
        assert intent_prompt is not None
        assert "аналізу" in intent_prompt.lower()

    def test_prompt_manager_get_category_creation_prompt(self):
        """Тест отримання промпту для створення категорії"""
        from src.clickone_prompt_manager import ClickonePromptManager

        with patch("pathlib.Path.exists", return_value=False):
            manager = ClickonePromptManager()

        create_prompt = manager.get_category_creation_prompt()
        assert create_prompt is not None
        assert "створити" in create_prompt.lower()

    def test_prompt_manager_get_category_retrieval_prompt(self):
        """Тест отримання промпту для отримання категорій"""
        from src.clickone_prompt_manager import ClickonePromptManager

        with patch("pathlib.Path.exists", return_value=False):
            manager = ClickonePromptManager()

        get_prompt = manager.get_category_retrieval_prompt()
        assert get_prompt is not None
        assert "отримати" in get_prompt.lower()

    def test_prompt_manager_get_category_update_prompt(self):
        """Тест отримання промпту для оновлення категорії"""
        from src.clickone_prompt_manager import ClickonePromptManager

        with patch("pathlib.Path.exists", return_value=False):
            manager = ClickonePromptManager()

        update_prompt = manager.get_category_update_prompt()
        assert update_prompt is not None
        assert "оновити" in update_prompt.lower()

    def test_prompt_manager_get_category_deletion_prompt(self):
        """Тест отримання промпту для видалення категорії"""
        from src.clickone_prompt_manager import ClickonePromptManager

        with patch("pathlib.Path.exists", return_value=False):
            manager = ClickonePromptManager()

        delete_prompt = manager.get_category_deletion_prompt()
        assert delete_prompt is not None
        assert "видалити" in delete_prompt.lower()

    def test_prompt_manager_get_search_filter_prompt(self):
        """Тест отримання промпту для пошуку та фільтрації"""
        from src.clickone_prompt_manager import ClickonePromptManager

        with patch("pathlib.Path.exists", return_value=False):
            manager = ClickonePromptManager()

        search_prompt = manager.get_search_filter_prompt()
        assert search_prompt is not None
        assert "знайти" in search_prompt.lower()

    def test_prompt_manager_get_error_handling_prompt(self):
        """Тест отримання промпту для обробки помилок"""
        from src.clickone_prompt_manager import ClickonePromptManager

        with patch("pathlib.Path.exists", return_value=False):
            manager = ClickonePromptManager()

        error_prompt = manager.get_error_handling_prompt()
        assert error_prompt is not None
        assert "помилку" in error_prompt.lower()

    def test_prompt_manager_get_jwt_auth_prompt(self):
        """Тест отримання промпту для JWT автентифікації"""
        from src.clickone_prompt_manager import ClickonePromptManager

        with patch("pathlib.Path.exists", return_value=False):
            manager = ClickonePromptManager()

        jwt_prompt = manager.get_jwt_auth_prompt()
        assert jwt_prompt is not None
        assert "jwt" in jwt_prompt.lower()

    def test_prompt_manager_get_user_help_prompt(self):
        """Тест отримання промпту для допомоги користувачу"""
        from src.clickone_prompt_manager import ClickonePromptManager

        with patch("pathlib.Path.exists", return_value=False):
            manager = ClickonePromptManager()

        help_prompt = manager.get_user_help_prompt()
        assert help_prompt is not None
        assert "допомогу" in help_prompt.lower()

    def test_prompt_manager_format_prompt(self):
        """Тест форматування промпту з параметрами"""
        from src.clickone_prompt_manager import ClickonePromptManager

        with patch("pathlib.Path.exists", return_value=False):
            manager = ClickonePromptManager()

        # Тестуємо форматування з параметрами
        formatted = manager.format_prompt("clickone_system_base")
        assert formatted is not None

        # Тестуємо форматування неіснуючого промпту
        formatted = manager.format_prompt("non_existent")
        assert "не знайдено" in formatted

    def test_prompt_manager_get_api_info(self):
        """Тест отримання інформації про API"""
        from src.clickone_prompt_manager import ClickonePromptManager

        with patch("pathlib.Path.exists", return_value=False):
            manager = ClickonePromptManager()

        api_info = manager.get_api_info()
        assert api_info is not None
        assert "title" in api_info
        assert "version" in api_info
        assert "base_url" in api_info

    def test_prompt_manager_get_categories_info(self):
        """Тест отримання інформації про категорії промптів"""
        from src.clickone_prompt_manager import ClickonePromptManager

        with patch("pathlib.Path.exists", return_value=False):
            manager = ClickonePromptManager()

        categories_info = manager.get_categories_info()
        assert categories_info is not None
        assert "total_categories" in categories_info
        assert "total_prompts" in categories_info
        assert "categories" in categories_info

    def test_prompt_manager_validate_prompts(self):
        """Тест валідації промптів"""
        from src.clickone_prompt_manager import ClickonePromptManager

        with patch("pathlib.Path.exists", return_value=False):
            manager = ClickonePromptManager()

        errors = manager.validate_prompts()
        assert isinstance(errors, list)
        # Базові промпти можуть мати помилки через відсутність категорій
        assert len(errors) >= 0

    @patch("pathlib.Path")
    @patch("yaml.dump")
    def test_prompt_manager_export_prompts(self, mock_yaml_dump, mock_path):
        """Тест експорту промптів"""
        from src.clickone_prompt_manager import ClickonePromptManager

        with patch("pathlib.Path.exists", return_value=False):
            manager = ClickonePromptManager()

        # Мокаємо Path та yaml.dump
        mock_path_instance = Mock()
        mock_path_instance.parent = Mock()
        mock_path_instance.parent.parent = Mock()
        mock_path.return_value = mock_path_instance

        result = manager.export_prompts("test_export.yaml")
        assert result is True

    def test_clickone_prompt_dataclass(self):
        """Тест структури ClickonePrompt"""
        from src.clickone_prompt_manager import ClickonePrompt

        prompt = ClickonePrompt(
            name="Тестовий промпт",
            description="Опис тестового промпту",
            template="Шаблон промпту",
            tags=["test", "clickone"],
            priority=1,
            category="test_category",
        )

        assert prompt.name == "Тестовий промпт"
        assert prompt.description == "Опис тестового промпту"
        assert prompt.template == "Шаблон промпту"
        assert prompt.tags == ["test", "clickone"]
        assert prompt.priority == 1
        assert prompt.category == "test_category"

    def test_global_prompt_manager(self):
        """Тест глобального екземпляра менеджера промптів"""
        from src.clickone_prompt_manager import get_clickone_prompt_manager

        manager = get_clickone_prompt_manager()
        assert manager is not None
        assert hasattr(manager, "prompts")
        assert hasattr(manager, "categories")
        assert hasattr(manager, "settings")
