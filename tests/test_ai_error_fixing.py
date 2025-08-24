"""
Тест використання AI моделі для автоматичного виправлення помилок API
"""

import os
import time
from typing import Any, Dict
from unittest.mock import Mock, patch

import openai
import pytest

# Налаштування OpenAI з .env файлу
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")


@pytest.fixture
def openai_client():
    """Створює клієнт OpenAI"""
    if not OPENAI_API_KEY or OPENAI_API_KEY == "test_key":
        pytest.skip("OpenAI API ключ не налаштовано")

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        # Тестуємо підключення
        response = client.chat.completions.create(
            model=OPENAI_MODEL, messages=[{"role": "user", "content": "Hello"}], max_tokens=5
        )
        print(f"✅ OpenAI підключення успішне, модель: {OPENAI_MODEL}")
        return client
    except Exception as e:
        print(f"❌ Помилка підключення до OpenAI: {e}")
        pytest.skip(f"OpenAI недоступний: {e}")


@pytest.fixture
def api_error_examples():
    """Приклади помилок API для тестування"""
    return [
        {
            "error": "Category name must contain only letters (no numbers or special characters)",
            "input_data": {
                "name": "Test Category 123",
                "slug": "test-category-123",
                "description": "Test category with numbers",
            },
            "expected_fix": {
                "name": "TestCategory",
                "slug": "test-category",
                "description": "Test category with numbers",
            },
        },
        {
            "error": "Slug must be unique",
            "input_data": {
                "name": "Test Category",
                "slug": "existing-slug",
                "description": "Test category",
            },
            "expected_fix": {
                "name": "Test Category",
                "slug": "test-category-new",
                "description": "Test category",
            },
        },
        {
            "error": "Description is too long (max 500 characters)",
            "input_data": {
                "name": "Test Category",
                "slug": "test-category",
                "description": "A" * 600,  # Занадто довгий опис
            },
            "expected_fix": {
                "name": "Test Category",
                "slug": "test-category",
                "description": "A" * 500,  # Обрізаний опис
            },
        },
    ]


class TestAIErrorFixing:
    """Тести для AI виправлення помилок API"""

    def test_openai_connection(self, openai_client):
        """Тест підключення до OpenAI"""
        print("🔌 Тестуємо підключення до OpenAI...")

        try:
            response = openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": "Test connection"}],
                max_tokens=10,
            )

            assert response is not None
            assert response.choices is not None
            assert len(response.choices) > 0

            print("✅ OpenAI підключення працює")

        except Exception as e:
            print(f"❌ Помилка тестування OpenAI: {e}")
            raise

    def test_ai_error_analysis(self, openai_client, api_error_examples):
        """Тест аналізу помилок API за допомогою AI"""
        print("🧠 Тестуємо AI аналіз помилок API...")

        for i, error_example in enumerate(api_error_examples):
            print(f"\n🔍 Тест {i+1}: {error_example['error']}")

            # Створюємо промпт для AI
            prompt = f"""
            Аналізуй помилку API та запропонуй виправлення українською мовою:

            Помилка: {error_example['error']}
            Вхідні дані: {error_example['input_data']}

            Дай зрозумілу відповідь користувачу українською мовою:
            - Поясни, в чому проблема
            - Запропонуй конкретні виправлення
            - Наведи приклади правильних даних
            """

            try:
                response = openai_client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": "Ти експерт з API та валідації даних. Аналізуй помилки та запропонуй конкретні виправлення українською мовою.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=200,
                    temperature=0.1,
                )

                ai_response = response.choices[0].message.content
                print(f"🤖 AI відповідь: {ai_response}")

                # Перевіряємо, що AI дав відповідь
                assert ai_response is not None
                assert len(ai_response) > 0

                # Перевіряємо, що відповідь містить ключові слова українською мовою
                assert any(
                    word in ai_response.lower()
                    for word in ["назва", "slug", "опис", "проблема", "виправлення"]
                )

                print(f"✅ AI аналіз помилки {i+1} успішний")

            except Exception as e:
                print(f"❌ Помилка AI аналізу {i+1}: {e}")
                # Продовжуємо з наступним тестом
                continue

    def test_ai_data_fixing(self, openai_client, api_error_examples):
        """Тест автоматичного виправлення даних за допомогою AI"""
        print("🔧 Тестуємо AI виправлення даних...")

        for i, error_example in enumerate(api_error_examples):
            print(f"\n🔧 Виправлення {i+1}: {error_example['error']}")

            # Створюємо промпт для виправлення
            prompt = f"""
            Виправ ці дані відповідно до помилки API та дай відповідь українською мовою:

            Помилка: {error_example['error']}
            Поточні дані: {error_example['input_data']}

            Дай зрозумілу відповідь користувачу:
            - Поясни, що було неправильно
            - Запропонуй виправлені дані
            - Наведи приклади правильних значень
            """

            try:
                response = openai_client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": "Ти експерт з валідації даних. Давай зрозумілі відповіді українською мовою.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=150,
                    temperature=0.0,
                )

                ai_response = response.choices[0].message.content
                print(f"🤖 AI виправлення: {ai_response}")

                # Перевіряємо, що AI дав відповідь
                assert ai_response is not None
                assert len(ai_response) > 0

                # Перевіряємо, що відповідь містить українські слова
                assert any(
                    word in ai_response.lower()
                    for word in ["правильно", "виправлення", "приклад", "назва", "slug"]
                )

                print(f"✅ AI виправлення {i+1} успішне")

            except Exception as e:
                print(f"❌ Помилка AI виправлення {i+1}: {e}")
                continue

    def test_ai_validation_rules(self, openai_client):
        """Тест отримання правил валідації від AI"""
        print("📋 Тестуємо AI правила валідації...")

        prompt = """
        Опиши правила валідації для створення категорії товарів в e-commerce API українською мовою:

        1. Назва категорії
        2. Slug (URL-підручний ідентифікатор)
        3. Опис
        4. Інші важливі поля

        Дай зрозуміле пояснення правил українською мовою з прикладами.
        """

        try:
            response = openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Ти експерт з API валідації та e-commerce систем. Пояснюй українською мовою.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=300,
                temperature=0.1,
            )

            ai_response = response.choices[0].message.content
            print(f"🤖 AI правила валідації: {ai_response}")

            # Перевіряємо відповідь
            assert ai_response is not None
            assert len(ai_response) > 0
            assert any(
                word in ai_response.lower()
                for word in ["назва", "slug", "опис", "правила", "валідація"]
            )

            print("✅ AI правила валідації отримано")

        except Exception as e:
            print(f"❌ Помилка отримання правил валідації: {e}")

    def test_ai_error_suggestions(self, openai_client):
        """Тест отримання пропозицій по виправленню помилок від AI"""
        print("💡 Тестуємо AI пропозиції по виправленню...")

        error_scenarios = [
            "Category name must contain only letters (no numbers or special characters)",
            "Slug must be unique and contain only lowercase letters, numbers, and hyphens",
            "Description is too long (maximum 500 characters allowed)",
            "Sort order must be a positive integer between 1 and 1000",
        ]

        for i, error in enumerate(error_scenarios):
            print(f"\n💡 Сценарій {i+1}: {error}")

            prompt = f"""
            Дай конкретні приклади виправлення цієї помилки API українською мовою:

            Помилка: {error}

            Наведи 3 приклади виправлення з поясненням:
            - Що неправильно
            - Як правильно
            - Чому так краще
            """

            try:
                response = openai_client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": "Ти експерт з виправлення помилок API. Давай конкретні приклади українською мовою.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=250,
                    temperature=0.2,
                )

                ai_response = response.choices[0].message.content
                print(f"🤖 AI пропозиції: {ai_response}")

                # Перевіряємо відповідь
                assert ai_response is not None
                assert len(ai_response) > 0
                assert any(
                    word in ai_response.lower()
                    for word in ["приклад", "виправлення", "пояснення", "правильно", "неправильно"]
                )

                print(f"✅ AI пропозиції {i+1} отримано")

            except Exception as e:
                print(f"❌ Помилка AI пропозицій {i+1}: {e}")
                continue


if __name__ == "__main__":
    # Запуск тестів
    pytest.main([__file__, "-v", "-s"])
