"""
Тест інтеграції AI Error Handler з ClickoneShopAgent
"""

import os
from unittest.mock import Mock, patch

import pytest

from src.ai_error_handler import AIFixSuggestion, APIError
from src.clickone_shop_agent import ClickoneAPIConfig, ClickoneShopAgent


@pytest.fixture
def agent():
    """Створює агент для тестування"""
    # Використовуємо тестовий API ключ
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
        agent = ClickoneShopAgent()
        # Встановлюємо тестовий JWT токен
        agent.set_jwt_token("test_jwt_token")
        return agent


@pytest.fixture
def mock_ai_response():
    """Мокаємо відповідь від AI"""
    return {
        "fixed_data": {"name": "TestCategory", "slug": "test-category"},
        "explanation": "Назва категорії повинна містити тільки літери без чисел",
        "confidence": 0.9,
        "suggestions": [
            "Видаліть числа з назви категорії",
            "Використовуйте тільки літери та пробіли",
        ],
    }


class TestAIErrorHandlerIntegration:
    """Тести інтеграції AI Error Handler з ClickoneShopAgent"""

    def test_agent_initialization_with_ai_handler(self, agent):
        """Тест ініціалізації агента з AI Error Handler"""
        assert hasattr(agent, "ai_error_handler")
        assert agent.ai_error_handler is not None
        print("✅ AI Error Handler успішно ініціалізовано в агенті")

    def test_validation_rules_from_ai(self, agent):
        """Тест отримання правил валідації від AI"""
        # Мокаємо AI відповідь
        mock_rules = "Правила валідації для категорії:\n- Назва: тільки літери\n- Slug: унікальний"

        with patch.object(agent.ai_error_handler, "get_validation_rules", return_value=mock_rules):
            rules = agent.get_validation_rules("category")
            assert rules == mock_rules
            print("✅ Правила валідації отримано від AI")

    def test_ai_error_analysis(self, agent):
        """Тест аналізу помилки за допомогою AI"""
        error_message = "Category name must contain only letters"
        input_data = {"name": "Test123", "slug": "test-123"}

        # Мокаємо AI відповідь
        mock_ai_fix = AIFixSuggestion(
            fixed_data={"name": "Test", "slug": "test"},
            explanation="Назва містить числа, потрібно їх видалити",
            confidence=0.8,
            suggestions=["Видаліть числа з назви"],
        )

        with patch.object(agent.ai_error_handler, "analyze_api_error", return_value=mock_ai_fix):
            analysis = agent.get_ai_error_analysis(error_message, input_data)
            assert "🚨 **Помилка API**" in analysis
            assert "Назва містить числа" in analysis
            print("✅ AI аналіз помилки працює")

    def test_retry_with_ai_fix(self, agent):
        """Тест повторної спроби з виправленням від AI"""
        # Створюємо мок відповідь з помилкою та AI виправленням
        from src.clickone_shop_agent import ClickoneAPIResponse

        mock_error_response = ClickoneAPIResponse(
            success=False,
            status_code=400,
            error="create category error",  # Додаємо ключове слово "create"
            data={
                "ai_fix": {
                    "fixed_data": {"name": "TestCategory"},
                    "input_data": {"name": "Test123", "slug": "test-123"},
                }
            },
        )

        # Мокаємо створення категорії
        mock_success_response = ClickoneAPIResponse(
            success=True, status_code=201, data={"id": "test-id", "name": "TestCategory"}
        )

        with patch.object(agent, "create_category", return_value=mock_success_response):
            retry_response = agent.retry_with_ai_fix(mock_error_response)
            assert retry_response.success
            assert retry_response.status_code == 201
            print("✅ Повторна спроба з AI виправленням успішна")

    def test_error_handling_in_create_category(self, agent):
        """Тест обробки помилок при створенні категорії"""
        # Тестові дані з помилкою
        invalid_data = {"name": "Test Category 123", "slug": "test-category-123"}  # Містить числа

        # Мокаємо HTTP запит, щоб повернути помилку
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "message": "Category name must contain only letters (no numbers or special characters)"
        }
        mock_response.text = (
            "Category name must contain only letters (no numbers or special characters)"
        )
        mock_response.headers = {}

        with patch.object(agent.session, "post", return_value=mock_response):
            response = agent.create_category(invalid_data)

            assert not response.success
            assert response.status_code == 400
            assert "🚨 **Помилка API**" in response.error
            assert "ai_fix" in (response.data or {})
            print("✅ Помилка API оброблена з AI аналізом")

    def test_cache_functionality(self, agent):
        """Тест функціональності кешу помилок"""
        # Очищаємо кеш перед тестом
        agent.ai_error_handler.clear_cache()

        # Перевіряємо початковий стан кешу
        initial_stats = agent.ai_error_handler.get_cache_stats()
        assert initial_stats["total_errors"] == 0

        # Створюємо помилку
        api_error = APIError(
            error_message="Test error",
            status_code=400,
            endpoint="/api/test",
            method="POST",
            input_data={"test": "data"},
        )

        # Аналізуємо помилку
        agent.ai_error_handler.analyze_api_error(api_error)

        # Перевіряємо, що помилка додана в кеш
        updated_stats = agent.ai_error_handler.get_cache_stats()
        assert updated_stats["total_errors"] > 0

        # Очищаємо кеш
        agent.ai_error_handler.clear_cache()
        final_stats = agent.ai_error_handler.get_cache_stats()
        assert final_stats["total_errors"] == 0

        print("✅ Кеш помилок працює коректно")


class TestRealAPIErrorHandling:
    """Тести з реальним API для демонстрації AI обробки помилок"""

    @pytest.mark.integration
    def test_real_api_error_with_ai_fix(self):
        """Тест реальної помилки API з AI виправленням"""
        # Пропускаємо, якщо немає реального API ключа
        if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "test_key":
            pytest.skip("Потрібен реальний OpenAI API ключ")

        agent = ClickoneShopAgent()

        # Встановлюємо JWT токен з .env
        jwt_token = os.getenv("CLICKONE_JWT_TOKEN")
        if not jwt_token:
            pytest.skip("Потрібен JWT токен для Clickone API")

        agent.set_jwt_token(jwt_token)

        # Тестові дані з помилкою
        invalid_data = {
            "name": "Test Category 123",  # Містить числа
            "slug": "test-category-123",
            "description": "Test category with numbers",
        }

        print("🔍 Тестуємо реальну помилку API з AI виправленням...")

        # Спробуємо створити категорію з неправильними даними
        response = agent.create_category(invalid_data)

        if not response.success:
            print(f"❌ Очікувана помилка: {response.error}")

            # Перевіряємо, чи є AI виправлення
            if "ai_fix" in (response.data or {}):
                ai_fix = response.data["ai_fix"]
                print(f"🤖 AI виправлення: {ai_fix}")

                # Спробуємо знову з виправленими даними
                retry_response = agent.retry_with_ai_fix(response)
                print(f"🔄 Результат повторної спроби: {retry_response.success}")

                if retry_response.success:
                    print("✅ AI успішно виправив помилку!")
                else:
                    print("⚠️ AI виправлення не спрацювало")
            else:
                print("⚠️ AI виправлення не знайдено у відповіді")
        else:
            print("✅ Категорія створена успішно (неочікувано)")

    @pytest.mark.integration
    def test_validation_rules_from_real_ai(self):
        """Тест отримання правил валідації від реального AI"""
        if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "test_key":
            pytest.skip("Потрібен реальний OpenAI API ключ")

        agent = ClickoneShopAgent()

        print("📋 Отримую правила валідації від реального AI...")
        rules = agent.get_validation_rules("category")

        assert rules is not None
        assert len(rules) > 0
        print(f"✅ Правила валідації отримано: {rules[:100]}...")


if __name__ == "__main__":
    # Запуск тестів
    pytest.main([__file__, "-v", "-s"])
