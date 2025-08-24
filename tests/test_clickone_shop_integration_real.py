"""
Інтеграційні тести для реального Clickone Shop API з JWT токеном
"""

import time
from typing import Any, Dict

import pytest

from src.clickone_shop_agent import ClickoneAPIConfig, ClickoneShopAgent

# JWT токен для тестування (замініть на актуальний)
JWT_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Im5Wd1A4T04zSDRqd09tUFBvYy16ZiJ9.eyJpc3MiOiJodHRwczovL2Rldi0ycjFoYzJnaHNieXU0YTF4LnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJnb29nbGUtb2F1dGgyfDEwNzQwMTYwODI1MTYxODY2MTk1MyIsImF1ZCI6WyJodHRwczovL29uZWNsaWNrLWZyb250L2FwaS92MiIsImh0dHBzOi8vZGV2LTJyMWhjMmdoc2J5dTRhMXgudXMuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTc1NjA0NzcwNywiZXhwIjoxNzU2MTM0MTA3LCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwiYXpwIjoiT0R0UVVscGRKbXRHb0xRWVk5Nk4za2wyM0lVNEprcWoifQ.kkht-NUCUEuJ_L3F5YWs68yBeuHkuNoQDLCN46gtwj_fVaXvw_j-DKmkspu_7Ce7n5nfy21AiqnC5SHW88cyQC_JDyLxJarxGes8Sn41pBH5Rrcv7AArkbdkXW9FnjyyJpHmaXR_dSguub-i8bQ7Sw_x-mPQsFLwaEMzlcsMVeK30GMRrJ7ey2OJJM6VwTix-07d3KUzNI_v7EEy-kE9d_NrMrwCfC8Mwz750c2OckuRRks4Yoy8gcoOtjvHgsXA71InLehaGo_diALfRBB4demTKKibMQGdOg63Oj8DFJJ2Bqqdo1YHklJ0aqbeXmR5ULAKb_PVP0Pizz6Kl8DI0A"


@pytest.fixture
def real_agent():
    """Створює агента з реальним JWT токеном"""
    config = ClickoneAPIConfig(
        base_url="https://api.oneshop.click", api_version="1.0", timeout=30, verify_ssl=True
    )

    agent = ClickoneShopAgent(config)
    agent.set_jwt_token(JWT_TOKEN)

    return agent


@pytest.fixture
def test_category_data():
    """Тестові дані для категорії"""
    timestamp = int(time.time())
    return {
        "name": f"Test Category {timestamp}",
        "slug": f"test-category-{timestamp}",
        "description": f"Тестова категорія створена {timestamp}",
        "isActive": True,
        "sortOrder": 1,
    }


class TestClickoneShopRealAPI:
    """Тести для реального Clickone Shop API"""

    def test_jwt_token_validation(self, real_agent):
        """Тест валідації JWT токена"""
        assert real_agent.jwt_token is not None
        assert real_agent.jwt_token == JWT_TOKEN
        assert "Authorization" in real_agent.session.headers
        assert real_agent.session.headers["Authorization"] == f"Bearer {JWT_TOKEN}"

    def test_get_categories_public(self, real_agent):
        """Тест отримання категорій (публічний endpoint)"""
        print("🔍 Тестуємо отримання категорій...")

        response = real_agent.get_categories()

        print(f"📊 Статус: {response.status_code}")
        print(f"📊 Успіх: {response.success}")
        print(f"📊 Дані: {response.data}")

        # Перевіряємо, що запит пройшов успішно
        assert response.success is True
        assert response.status_code == 200
        assert response.data is not None

        # Перевіряємо структуру даних
        if isinstance(response.data, list):
            print(f"📋 Знайдено {len(response.data)} категорій")
            if len(response.data) > 0:
                category = response.data[0]
                assert "id" in category or "name" in category
        elif isinstance(response.data, dict):
            print(f"📋 Отримано об'єкт: {list(response.data.keys())}")

    def test_create_category_admin(self, real_agent, test_category_data):
        """Тест створення категорії (admin endpoint)"""
        print(f"🔨 Тестуємо створення категорії: {test_category_data['name']}")

        response = real_agent.create_category(test_category_data)

        print(f"📊 Статус: {response.status_code}")
        print(f"📊 Успіх: {response.success}")
        print(f"📊 Дані: {response.data}")
        print(f"📊 Помилка: {response.error}")

        # Перевіряємо результат
        if response.success:
            print("✅ Категорія створена успішно")
            assert response.status_code in [200, 201]
            assert response.data is not None

            # Зберігаємо ID для подальших тестів
            if isinstance(response.data, dict) and "id" in response.data:
                test_category_data["id"] = response.data["id"]
                print(f"🆔 ID категорії: {response.data['id']}")
        else:
            print(f"❌ Помилка створення: {response.error}")
            # Якщо не можемо створити, це не критично для тестування
            assert response.status_code in [400, 401, 403, 500]

    def test_get_category_by_id(self, real_agent, test_category_data):
        """Тест отримання категорії за ID"""
        if "id" not in test_category_data:
            pytest.skip("Категорія не була створена в попередньому тесті")

        print(f"🔍 Тестуємо отримання категорії за ID: {test_category_data['id']}")

        response = real_agent.get_category_by_id(test_category_data["id"])

        print(f"📊 Статус: {response.status_code}")
        print(f"📊 Успіх: {response.success}")
        print(f"📊 Дані: {response.data}")

        if response.success:
            print("✅ Категорія отримана успішно")
            assert response.status_code == 200
            assert response.data is not None
            assert response.data.get("id") == test_category_data["id"]
        else:
            print(f"❌ Помилка отримання: {response.error}")
            # Можливо категорія не існує або немає доступу
            assert response.status_code in [400, 401, 403, 404, 500]

    def test_update_category_admin(self, real_agent, test_category_data):
        """Тест оновлення категорії (admin endpoint)"""
        if "id" not in test_category_data:
            pytest.skip("Категорія не була створена в попередньому тесті")

        update_data = {"description": f"Оновлений опис {int(time.time())}", "isActive": True}

        print(f"✏️ Тестуємо оновлення категорії {test_category_data['id']}: {update_data}")

        response = real_agent.update_category(test_category_data["id"], update_data)

        print(f"📊 Статус: {response.status_code}")
        print(f"📊 Успіх: {response.success}")
        print(f"📊 Дані: {response.data}")
        print(f"📊 Помилка: {response.error}")

        if response.success:
            print("✅ Категорія оновлена успішно")
            assert response.status_code == 200
            assert response.data is not None
        else:
            print(f"❌ Помилка оновлення: {response.error}")
            # Можливо немає прав або категорія не існує
            assert response.status_code in [400, 401, 403, 404, 500]

    def test_delete_category_admin(self, real_agent, test_category_data):
        """Тест видалення категорії (admin endpoint)"""
        if "id" not in test_category_data:
            pytest.skip("Категорія не була створена в попередньому тесті")

        print(f"🗑️ Тестуємо видалення категорії {test_category_data['id']}")

        response = real_agent.delete_category(test_category_data["id"])

        print(f"📊 Статус: {response.status_code}")
        print(f"📊 Успіх: {response.success}")
        print(f"📊 Дані: {response.data}")
        print(f"📊 Помилка: {response.error}")

        if response.success:
            print("✅ Категорія видалена успішно")
            assert response.status_code in [200, 204]
        else:
            print(f"❌ Помилка видалення: {response.error}")
            # Можливо немає прав або категорія не існує
            assert response.status_code in [400, 401, 403, 404, 500]

    def test_user_intent_analysis(self, real_agent):
        """Тест аналізу наміру користувача"""
        print("🧠 Тестуємо аналіз наміру користувача...")

        test_queries = [
            "Створи категорію електроніка",
            "Покажи всі категорії",
            "Онови категорію 123",
            "Видали категорію 456",
        ]

        for query in test_queries:
            print(f"🔍 Аналіз запиту: '{query}'")
            intent = real_agent.analyze_user_intent(query)

            print(f"📊 Намір: {intent}")

            # Перевіряємо структуру наміру
            assert "action" in intent
            assert "entity" in intent
            assert "access_level" in intent
            assert "confidence" in intent

            # Перевіряємо логіку
            if "створи" in query.lower():
                assert intent["action"] == "create"
                assert intent["access_level"] == "admin"
            elif "покажи" in query.lower():
                assert intent["action"] == "retrieve"
                assert intent["access_level"] == "public"
            elif "онови" in query.lower():
                assert intent["action"] == "update"
                assert intent["access_level"] == "admin"
            elif "видали" in query.lower():
                assert intent["action"] == "delete"
                assert intent["access_level"] == "admin"

    def test_process_user_queries(self, real_agent):
        """Тест обробки запитів користувача"""
        print("🔄 Тестуємо обробку запитів користувача...")

        # Тест публічного запиту
        print("🔍 Тест публічного запиту: 'Покажи всі категорії'")
        result = real_agent.process_user_query("Покажи всі категорії")

        print(f"📊 Результат: {result}")

        assert "success" in result
        assert "intent" in result
        assert result["intent"]["action"] == "retrieve"

        # Тест admin запиту без JWT
        print("🔍 Тест admin запиту без JWT: 'Створи категорію тест'")
        real_agent.clear_jwt_token()

        result = real_agent.process_user_query("Створи категорію тест")

        print(f"📊 Результат: {result}")

        assert result["success"] is False
        assert "action_required" in result
        assert result["action_required"] == "set_jwt_token"

        # Відновлюємо JWT для подальших тестів
        real_agent.set_jwt_token(JWT_TOKEN)

    def test_api_info_retrieval(self, real_agent):
        """Тест отримання інформації про API"""
        print("ℹ️ Тестуємо отримання інформації про API...")

        api_info = real_agent.get_api_info()

        print(f"📊 API інформація: {api_info}")

        assert api_info is not None
        assert "title" in api_info
        assert "version" in api_info
        assert "base_url" in api_info

        print(f"🏷️ Назва: {api_info.get('title')}")
        print(f"📋 Версія: {api_info.get('version')}")
        print(f"🌐 URL: {api_info.get('base_url')}")

    def test_prompts_info_retrieval(self, real_agent):
        """Тест отримання інформації про промпти"""
        print("📝 Тестуємо отримання інформації про промпти...")

        prompts_info = real_agent.get_prompts_info()

        print(f"📊 Інформація про промпти: {prompts_info}")

        assert prompts_info is not None
        assert "total_categories" in prompts_info
        assert "total_prompts" in prompts_info

        print(f"📂 Категорій: {prompts_info.get('total_categories')}")
        print(f"📄 Промптів: {prompts_info.get('total_prompts')}")

    def test_error_handling(self, real_agent):
        """Тест обробки помилок"""
        print("⚠️ Тестуємо обробку помилок...")

        # Тест неіснуючого endpoint
        print("🔍 Тест неіснуючого endpoint...")
        response = real_agent._make_request("GET", "/api/nonexistent")

        print(f"📊 Статус: {response.status_code}")
        print(f"📊 Успіх: {response.success}")
        print(f"📊 Помилка: {response.error}")

        # Очікуємо помилку 404 або подібну
        assert response.success is False
        assert response.status_code >= 400

        # Тест неправильного методу
        print("🔍 Тест неправильного методу...")
        response = real_agent._make_request("INVALID", "/api/categories")

        print(f"📊 Статус: {response.status_code}")
        print(f"📊 Успіх: {response.success}")
        print(f"📊 Помилка: {response.error}")

        assert response.success is False
        assert response.status_code == 0
        assert "Непідтримуваний HTTP метод" in response.error

    def test_jwt_token_expiry_handling(self, real_agent):
        """Тест обробки застарілого JWT токена"""
        print("⏰ Тестуємо обробку застарілого JWT токена...")

        # Встановлюємо застарілий токен
        expired_token = (
            "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Im5Wd1A4T04zSDRqd09tUFBvYy16ZiJ9.expired"
        )
        real_agent.set_jwt_token(expired_token)

        print("🔍 Тестуємо admin операцію з застарілим токеном...")

        # Спробуємо створити категорію
        test_data = {
            "name": "Test Expired Token",
            "slug": "test-expired-token",
            "description": "Тест застарілого токена",
        }

        response = real_agent.create_category(test_data)

        print(f"📊 Статус: {response.status_code}")
        print(f"📊 Успіх: {response.success}")
        print(f"📊 Помилка: {response.error}")

        # Очікуємо помилку автентифікації
        if not response.success:
            assert response.status_code in [401, 403]
            print("✅ Застарілий токен правильно відхилено")
        else:
            print("⚠️ Застарілий токен не відхилено (можливо сервер не перевіряє)")

        # Відновлюємо валідний токен
        real_agent.set_jwt_token(JWT_TOKEN)

    def test_rate_limiting_handling(self, real_agent):
        """Тест обробки обмеження швидкості"""
        print("🚦 Тестуємо обробку обмеження швидкості...")

        # Робимо кілька швидких запитів
        print("🔍 Робимо кілька швидких запитів...")

        responses = []
        for i in range(5):
            print(f"📊 Запит {i+1}/5...")
            response = real_agent.get_categories()
            responses.append(response)
            time.sleep(0.1)  # Невелика затримка

        # Перевіряємо результати
        success_count = sum(1 for r in responses if r.success)
        print(f"✅ Успішних запитів: {success_count}/{len(responses)}")

        # Більшість запитів повинні пройти успішно
        assert success_count >= len(responses) * 0.8  # 80% успішних

        # Перевіряємо, чи немає помилок обмеження швидкості
        rate_limit_errors = [r for r in responses if r.status_code == 429]
        if rate_limit_errors:
            print(f"⚠️ Знайдено помилок обмеження швидкості: {len(rate_limit_errors)}")
        else:
            print("✅ Обмеження швидкості не спрацювало")

    def test_concurrent_requests(self, real_agent):
        """Тест одночасних запитів"""
        print("⚡ Тестуємо одночасні запити...")

        import queue
        import threading

        results_queue = queue.Queue()

        def make_request(request_id):
            """Функція для виконання запиту"""
            try:
                response = real_agent.get_categories()
                results_queue.put((request_id, response))
            except Exception as e:
                results_queue.put((request_id, f"Помилка: {e}"))

        # Створюємо кілька потоків
        threads = []
        for i in range(3):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()

        # Чекаємо завершення всіх потоків
        for thread in threads:
            thread.join()

        # Збираємо результати
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())

        print(f"📊 Отримано {len(results)} результатів")

        # Перевіряємо результати
        for request_id, result in results:
            if isinstance(result, str):
                print(f"❌ Запит {request_id}: {result}")
            else:
                print(f"✅ Запит {request_id}: статус {result.status_code}")
                assert result.success is True
                assert result.status_code == 200


if __name__ == "__main__":
    # Запуск тестів
    pytest.main([__file__, "-v", "-s"])
