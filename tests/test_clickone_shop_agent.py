"""
Тест для агента Clickone Shop API
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests


@pytest.fixture
def mock_requests_session():
    with patch("requests.Session") as mock:
        mock_instance = Mock()
        mock_instance.headers = {}
        mock_instance.get.return_value = Mock(
            status_code=200,
            content=b'[{"name": "Test Category"}]',
            json=lambda: [{"name": "Test Category"}],
            headers={},
        )
        mock_instance.post.return_value = Mock(
            status_code=201,
            content=b'{"id": "123", "name": "Test Category"}',
            json=lambda: {"id": "123", "name": "Test Category"},
            headers={},
        )
        mock_instance.patch.return_value = Mock(
            status_code=200,
            content=b'{"id": "123", "name": "Updated Category"}',
            json=lambda: {"id": "123", "name": "Updated Category"},
            headers={},
        )
        mock_instance.delete.return_value = Mock(
            status_code=200,
            content=b'{"message": "Category deleted successfully"}',
            json=lambda: {"message": "Category deleted successfully"},
            headers={},
        )
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_prompt_manager():
    with patch("src.clickone_prompt_manager.get_clickone_prompt_manager") as mock:
        mock_instance = Mock()
        mock_instance.get_intent_analysis_prompt.return_value = "Аналізуй запит користувача"
        mock_instance.get_api_info.return_value = {
            "title": "Clickone Shop Backend API",
            "version": "1.0",
            "base_url": "https://api.oneshop.click",
        }
        mock.return_value = mock_instance
        yield mock_instance


class TestClickoneShopAgent:
    """Тести для агента Clickone Shop API"""

    @patch("src.clickone_prompt_manager.get_clickone_prompt_manager")
    def test_agent_initialization(self, mock_get_manager):
        """Тест ініціалізації агента"""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        from src.clickone_shop_agent import ClickoneAPIConfig, ClickoneShopAgent

        # Тест з конфігурацією за замовчуванням
        agent = ClickoneShopAgent()
        assert agent is not None
        assert agent.config.base_url == "https://api.oneshop.click"
        assert agent.config.api_version == "1.0"
        assert agent.jwt_token is None

        # Тест з кастомною конфігурацією
        config = ClickoneAPIConfig(base_url="https://test.api.com", api_version="2.0", timeout=60)
        agent = ClickoneShopAgent(config)
        assert agent.config.base_url == "https://test.api.com"
        assert agent.config.timeout == 60

    @patch("src.clickone_prompt_manager.get_clickone_prompt_manager")
    def test_jwt_token_management(self, mock_get_manager):
        """Тест управління JWT токенами"""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        from src.clickone_shop_agent import ClickoneShopAgent

        agent = ClickoneShopAgent()

        # Тест встановлення токена
        test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"
        agent.set_jwt_token(test_token)
        assert agent.jwt_token == test_token
        assert agent.session.headers["Authorization"] == f"Bearer {test_token}"

        # Тест очищення токена
        agent.clear_jwt_token()
        assert agent.jwt_token is None
        assert "Authorization" not in agent.session.headers

    @patch("src.clickone_prompt_manager.get_clickone_prompt_manager")
    @patch("requests.Session")
    def test_make_request_success(self, mock_session, mock_get_manager):
        """Тест успішного HTTP запиту"""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        mock_session_instance = Mock()
        mock_session_instance.headers = {}
        mock_session_instance.get.return_value = Mock(
            status_code=200,
            content=b'{"success": true}',
            json=lambda: {"success": True},
            headers={"Content-Type": "application/json"},
        )
        mock_session.return_value = mock_session_instance

        from src.clickone_shop_agent import ClickoneShopAgent

        agent = ClickoneShopAgent()

        # Тест GET запиту
        response = agent._make_request("GET", "/api/categories")
        assert response.success is True
        assert response.status_code == 200
        assert response.data == {"success": True}
        assert response.message == "Успішно"

    @patch("src.clickone_prompt_manager.get_clickone_prompt_manager")
    @patch("requests.Session")
    def test_make_request_error(self, mock_session, mock_get_manager):
        """Тест HTTP запиту з помилкою"""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        mock_session_instance = Mock()
        mock_session_instance.headers = {}
        mock_session_instance.post.return_value = Mock(
            status_code=400,
            content=b'{"message": "Bad Request"}',
            json=lambda: {"message": "Bad Request"},
            headers={},
        )
        mock_session.return_value = mock_session_instance

        from src.clickone_shop_agent import ClickoneShopAgent

        agent = ClickoneShopAgent()

        # Тест POST запиту з помилкою
        response = agent._make_request("POST", "/api/categories", data={"test": "data"})
        assert response.success is False
        assert response.status_code == 400
        assert "Bad Request" in response.error

    @patch("src.clickone_prompt_manager.get_clickone_prompt_manager")
    @patch("requests.Session")
    def test_make_request_network_error(self, mock_session, mock_get_manager):
        """Тест HTTP запиту з мережевою помилкою"""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        mock_session_instance = Mock()
        mock_session_instance.headers = {}
        mock_session_instance.get.side_effect = requests.exceptions.RequestException(
            "Network error"
        )
        mock_session.return_value = mock_session_instance

        from src.clickone_shop_agent import ClickoneShopAgent

        agent = ClickoneShopAgent()

        # Тест GET запиту з мережевою помилкою
        response = agent._make_request("GET", "/api/categories")
        assert response.success is False
        assert response.status_code == 0
        assert "Network error" in response.error

    @patch("src.clickone_prompt_manager.get_clickone_prompt_manager")
    @patch("requests.Session")
    def test_create_category_success(self, mock_session, mock_get_manager):
        """Тест успішного створення категорії"""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        mock_session_instance = Mock()
        mock_session_instance.headers = {}
        mock_session_instance.post.return_value = Mock(
            status_code=201,
            content=b'{"id": "123", "name": "Test Category"}',
            json=lambda: {"id": "123", "name": "Test Category"},
            headers={},
        )
        mock_session.return_value = mock_session_instance

        from src.clickone_shop_agent import ClickoneShopAgent

        agent = ClickoneShopAgent()
        agent.set_jwt_token("test_token")

        # Тест створення категорії
        category_data = {"name": "Test Category", "slug": "test-category"}
        response = agent.create_category(category_data)
        assert response.success is True
        assert response.status_code == 201
        assert response.data["name"] == "Test Category"

    @patch("src.clickone_prompt_manager.get_clickone_prompt_manager")
    def test_create_category_missing_fields(self, mock_get_manager):
        """Тест створення категорії з відсутніми полями"""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        from src.clickone_shop_agent import ClickoneShopAgent

        agent = ClickoneShopAgent()
        agent.set_jwt_token("test_token")

        # Тест з відсутніми обов'язковими полями
        category_data = {"name": "Test Category"}  # Відсутній slug
        response = agent.create_category(category_data)
        assert response.success is False
        assert response.status_code == 400
        assert "slug" in response.error

    @patch("src.clickone_prompt_manager.get_clickone_prompt_manager")
    def test_create_category_no_jwt(self, mock_get_manager):
        """Тест створення категорії без JWT токена"""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        from src.clickone_shop_agent import ClickoneShopAgent

        agent = ClickoneShopAgent()
        # JWT токен не встановлено

        # Тест створення категорії без автентифікації
        category_data = {"name": "Test Category", "slug": "test-category"}
        response = agent.create_category(category_data)
        assert response.success is False
        assert response.status_code == 401
        assert "JWT токен потрібен" in response.error

    @patch("src.clickone_prompt_manager.get_clickone_prompt_manager")
    @patch("requests.Session")
    def test_get_categories_success(self, mock_session, mock_get_manager):
        """Тест успішного отримання категорій"""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        mock_session_instance = Mock()
        mock_session_instance.headers = {}
        mock_session_instance.get.return_value = Mock(
            status_code=200,
            content=b'[{"name": "Category 1"}, {"name": "Category 2"}]',
            json=lambda: [{"name": "Category 1"}, {"name": "Category 2"}],
            headers={},
        )
        mock_session.return_value = mock_session_instance

        from src.clickone_shop_agent import ClickoneShopAgent

        agent = ClickoneShopAgent()

        # Тест отримання всіх категорій
        response = agent.get_categories()
        assert response.success is True
        assert response.status_code == 200
        assert len(response.data) == 2

        # Тест отримання з фільтрами
        response = agent.get_categories(is_active=True, parent_id="123")
        assert response.success is True

    @patch("src.clickone_prompt_manager.get_clickone_prompt_manager")
    @patch("requests.Session")
    def test_get_category_by_id_success(self, mock_session, mock_get_manager):
        """Тест успішного отримання категорії за ID"""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        mock_session_instance = Mock()
        mock_session_instance.headers = {}
        mock_session_instance.get.return_value = Mock(
            status_code=200,
            content=b'{"id": "123", "name": "Test Category"}',
            json=lambda: {"id": "123", "name": "Test Category"},
            headers={},
        )
        mock_session.return_value = mock_session_instance

        from src.clickone_shop_agent import ClickoneShopAgent

        agent = ClickoneShopAgent()

        # Тест отримання категорії за ID
        response = agent.get_category_by_id("123")
        assert response.success is True
        assert response.status_code == 200
        assert response.data["id"] == "123"

    @patch("src.clickone_prompt_manager.get_clickone_prompt_manager")
    @patch("requests.Session")
    def test_update_category_success(self, mock_session, mock_get_manager):
        """Тест успішного оновлення категорії"""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        mock_session_instance = Mock()
        mock_session_instance.headers = {}
        mock_session_instance.patch.return_value = Mock(
            status_code=200,
            content=b'{"id": "123", "name": "Updated Category"}',
            json=lambda: {"id": "123", "name": "Updated Category"},
            headers={},
        )
        mock_session.return_value = mock_session_instance

        from src.clickone_shop_agent import ClickoneShopAgent

        agent = ClickoneShopAgent()
        agent.set_jwt_token("test_token")

        # Тест оновлення категорії
        update_data = {"name": "Updated Category"}
        response = agent.update_category("123", update_data)
        assert response.success is True
        assert response.status_code == 200
        assert response.data["name"] == "Updated Category"

    @patch("src.clickone_prompt_manager.get_clickone_prompt_manager")
    def test_update_category_no_jwt(self, mock_get_manager):
        """Тест оновлення категорії без JWT токена"""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        from src.clickone_shop_agent import ClickoneShopAgent

        agent = ClickoneShopAgent()
        # JWT токен не встановлено

        # Тест оновлення категорії без автентифікації
        update_data = {"name": "Updated Category"}
        response = agent.update_category("123", update_data)
        assert response.success is False
        assert response.status_code == 401
        assert "JWT токен потрібен" in response.error

    @patch("src.clickone_prompt_manager.get_clickone_prompt_manager")
    @patch("requests.Session")
    def test_delete_category_success(self, mock_session, mock_get_manager):
        """Тест успішного видалення категорії"""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        mock_session_instance = Mock()
        mock_session_instance.headers = {}
        mock_session_instance.delete.return_value = Mock(
            status_code=200,
            content=b'{"message": "Category deleted successfully"}',
            json=lambda: {"message": "Category deleted successfully"},
            headers={},
        )
        mock_session.return_value = mock_session_instance

        from src.clickone_shop_agent import ClickoneShopAgent

        agent = ClickoneShopAgent()
        agent.set_jwt_token("test_token")

        # Тест видалення категорії
        response = agent.delete_category("123")
        assert response.success is True
        assert response.status_code == 200
        assert "deleted successfully" in response.data["message"]

    @patch("src.clickone_prompt_manager.get_clickone_prompt_manager")
    def test_delete_category_no_jwt(self, mock_get_manager):
        """Тест видалення категорії без JWT токена"""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        from src.clickone_shop_agent import ClickoneShopAgent

        agent = ClickoneShopAgent()
        # JWT токен не встановлено

        # Тест видалення категорії без автентифікації
        response = agent.delete_category("123")
        assert response.success is False
        assert response.status_code == 401
        assert "JWT токен потрібен" in response.error

    @patch("src.clickone_prompt_manager.get_clickone_prompt_manager")
    def test_analyze_user_intent(self, mock_get_manager):
        """Тест аналізу наміру користувача"""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        from src.clickone_shop_agent import ClickoneShopAgent

        agent = ClickoneShopAgent()

        # Тест створення категорії
        intent = agent.analyze_user_intent("Створи категорію електроніка")
        assert intent["action"] == "create"
        assert intent["entity"] == "categories"
        assert intent["access_level"] == "admin"
        assert intent["confidence"] > 0.5

        # Тест отримання категорій
        intent = agent.analyze_user_intent("Покажи всі категорії")
        assert intent["action"] == "retrieve"
        assert intent["entity"] == "categories"
        assert intent["access_level"] == "public"

        # Тест оновлення категорії
        intent = agent.analyze_user_intent("Онови категорію 123")
        assert intent["action"] == "update"
        assert intent["entity"] == "categories"
        assert intent["access_level"] == "admin"

        # Тест видалення категорії
        intent = agent.analyze_user_intent("Видали категорію 123")
        assert intent["action"] == "delete"
        assert intent["entity"] == "categories"
        assert intent["access_level"] == "admin"

    @patch("src.clickone_prompt_manager.get_clickone_prompt_manager")
    def test_process_user_query_create_category(self, mock_get_manager):
        """Тест обробки запиту на створення категорії"""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        from src.clickone_shop_agent import ClickoneShopAgent

        agent = ClickoneShopAgent()
        agent.set_jwt_token("test_token")

        # Мокаємо create_category
        with patch.object(agent, "create_category") as mock_create:
            mock_create.return_value = Mock(
                success=True,
                status_code=201,
                data={"id": "123", "name": "Електроніка"},
                message="Успішно створено",
            )

            result = agent.process_user_query("Створи категорію електроніка")
            assert result["success"] is True
            assert result["action_performed"] == "create_category"
            assert result["intent"]["action"] == "create"

    @patch("src.clickone_prompt_manager.get_clickone_prompt_manager")
    def test_process_user_query_get_categories(self, mock_get_manager):
        """Тест обробки запиту на отримання категорій"""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        from src.clickone_shop_agent import ClickoneShopAgent

        agent = ClickoneShopAgent()

        # Мокаємо get_categories
        with patch.object(agent, "get_categories") as mock_get:
            mock_get.return_value = Mock(
                success=True,
                status_code=200,
                data=[{"name": "Категорія 1"}, {"name": "Категорія 2"}],
                message="Успішно отримано",
            )

            result = agent.process_user_query("Покажи всі категорії")
            assert result["success"] is True
            assert result["action_performed"] == "get_categories"
            assert result["intent"]["action"] == "retrieve"

    @patch("src.clickone_prompt_manager.get_clickone_prompt_manager")
    def test_process_user_query_no_jwt_for_admin_action(self, mock_get_manager):
        """Тест обробки запиту без JWT для admin дії"""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        from src.clickone_shop_agent import ClickoneShopAgent

        agent = ClickoneShopAgent()
        # JWT токен не встановлено

        result = agent.process_user_query("Створи категорію електроніка")
        assert result["success"] is False
        assert result["action_required"] == "set_jwt_token"
        assert "JWT токен потрібен" in result["message"]

    def test_parse_category_data_from_query(self):
        """Тест парсингу даних категорії з запиту"""
        from src.clickone_shop_agent import ClickoneShopAgent

        agent = ClickoneShopAgent()

        # Тест з явною назвою
        data = agent._parse_category_data_from_query("Створи категорію назва Електроніка")
        assert data is not None
        assert data["name"] == "Електроніка"
        assert data["slug"] == "електроніка"

        # Тест з контекстною назвою
        data = agent._parse_category_data_from_query("Створи категорію електроніка")
        assert data is not None
        assert data["name"] == "Електроніка"
        assert data["slug"] == "електроніка"

        # Тест з невідомою назвою
        data = agent._parse_category_data_from_query("Створи категорію")
        assert data is None

    def test_parse_update_data_from_query(self):
        """Тест парсингу даних для оновлення з запиту"""
        from src.clickone_shop_agent import ClickoneShopAgent

        agent = ClickoneShopAgent()

        # Тест з назвою
        data = agent._parse_update_data_from_query("Онови назва Нова назва")
        assert "name" in data
        assert data["name"] == "Нова"

        # Тест з активністю
        data = agent._parse_update_data_from_query("Зроби категорію активна")
        assert "isActive" in data
        assert data["isActive"] is True

        # Тест з неактивністю
        data = agent._parse_update_data_from_query("Зроби категорію неактивна")
        assert "isActive" in data
        assert data["isActive"] is False

    def test_extract_category_id_from_query(self):
        """Тест витягування ID категорії з запиту"""
        from src.clickone_shop_agent import ClickoneShopAgent

        agent = ClickoneShopAgent()

        # Тест з числовим ID
        category_id = agent._extract_category_id_from_query("Онови категорію 123")
        assert category_id == "123"

        # Тест з UUID
        category_id = agent._extract_category_id_from_query(
            "Видали категорію 123e4567-e89b-12d3-a456-426614174000"
        )
        assert category_id == "123e4567-e89b-12d3-a456-426614174000"

        # Тест без ID
        category_id = agent._extract_category_id_from_query("Онови категорію")
        assert category_id is None

    @patch("src.clickone_shop_agent.ClickoneShopAgent.prompt_manager")
    def test_get_api_info(self, mock_prompt_manager):
        """Тест отримання інформації про API"""
        mock_prompt_manager.get_api_info.return_value = {
            "title": "Clickone Shop Backend API",
            "version": "1.0",
            "base_url": "https://api.oneshop.click",
        }

        from src.clickone_shop_agent import ClickoneShopAgent

        agent = ClickoneShopAgent()

        api_info = agent.get_api_info()
        assert api_info is not None
        assert "title" in api_info
        assert "version" in api_info
        assert "base_url" in api_info

    @patch("src.clickone_shop_agent.ClickoneShopAgent.prompt_manager")
    def test_get_prompts_info(self, mock_prompt_manager):
        """Тест отримання інформації про промпти"""
        mock_prompt_manager.get_categories_info.return_value = {
            "total_categories": 3,
            "total_prompts": 10,
            "categories": {"clickone_core": {}, "categories": {}, "products": {}},
            "prompts_by_category": {"clickone_core": 5, "categories": 3, "products": 2},
        }

        from src.clickone_shop_agent import ClickoneShopAgent

        agent = ClickoneShopAgent()

        prompts_info = agent.get_prompts_info()
        assert prompts_info is not None
        assert "total_categories" in prompts_info
        assert "total_prompts" in prompts_info

    @patch("src.clickone_shop_agent.ClickoneShopAgent.prompt_manager")
    def test_validate_prompts(self, mock_prompt_manager):
        """Тест валідації промптів"""
        mock_prompt_manager.validate_prompts.return_value = []

        from src.clickone_shop_agent import ClickoneShopAgent

        agent = ClickoneShopAgent()

        errors = agent.validate_prompts()
        assert isinstance(errors, list)

    @patch("src.clickone_shop_agent.ClickoneShopAgent.prompt_manager")
    def test_export_prompts(self, mock_prompt_manager):
        """Тест експорту промптів"""
        mock_prompt_manager.export_prompts.return_value = True

        from src.clickone_shop_agent import ClickoneShopAgent

        agent = ClickoneShopAgent()

        result = agent.export_prompts("test_export.yaml")
        assert isinstance(result, bool)

    def test_clickone_api_config_dataclass(self):
        """Тест структури ClickoneAPIConfig"""
        from src.clickone_shop_agent import ClickoneAPIConfig

        config = ClickoneAPIConfig(
            base_url="https://test.api.com", api_version="2.0", timeout=60, verify_ssl=False
        )

        assert config.base_url == "https://test.api.com"
        assert config.api_version == "2.0"
        assert config.timeout == 60
        assert config.verify_ssl is False

    def test_clickone_api_response_dataclass(self):
        """Тест структури ClickoneAPIResponse"""
        from src.clickone_shop_agent import ClickoneAPIResponse

        response = ClickoneAPIResponse(
            success=True,
            status_code=200,
            data={"test": "data"},
            message="Success",
            headers={"Content-Type": "application/json"},
        )

        assert response.success is True
        assert response.status_code == 200
        assert response.data == {"test": "data"}
        assert response.message == "Success"
        assert response.headers == {"Content-Type": "application/json"}

    def test_global_agent(self):
        """Тест глобального екземпляра агента"""
        from src.clickone_shop_agent import get_clickone_shop_agent

        agent = get_clickone_shop_agent()
        assert agent is not None
        assert hasattr(agent, "config")
        assert hasattr(agent, "prompt_manager")
        assert hasattr(agent, "jwt_token")
