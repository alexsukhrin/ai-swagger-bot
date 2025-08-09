"""
Приклад використання розширеного AI-асистента
Демонструє нові функції для e-commerce та веб-сайтів
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.enhanced_ai_assistant import EnhancedAIAssistant
from src.enhanced_prompt_manager import EnhancedPromptManager
from src.rag_engine import PostgresRAGEngine


def demo_enhanced_ai_assistant():
    """
    Демонстрація роботи розширеного AI-асистента
    """
    print("🤖 Демонстрація розширеного AI-асистента")
    print("=" * 50)

    # Ініціалізація компонентів
    prompt_manager = EnhancedPromptManager()
    rag_engine = PostgresRAGEngine(user_id="example_user", swagger_spec_id="example_spec")
    assistant = EnhancedAIAssistant(prompt_manager, rag_engine)

    # Додавання тестових даних
    setup_test_data(assistant)

    # Демонстрація різних функцій
    demo_queries = [
        # Пошук товарів
        "Знайди теплу куртку для зими",
        "Потрібен подарунок для дівчини",
        "Шукаю телефон в діапазоні 5000-15000 грн",
        # Допомога з замовленнями
        "Відстежи моє замовлення #12345",
        "Як оформити замовлення?",
        "Хочу скасувати замовлення",
        # Створення контенту
        "Створи опис для товару Смартфон Samsung Galaxy",
        "Напиши опис для куртки зимової",
        "Створи опис для подарункового набору",
        # Підтримка клієнтів
        "Проблема з оплатою замовлення",
        "Коли прибуде моє замовлення?",
        "Як повернути товар?",
        # Рекомендації
        "Що порекомендуєш для подарунка?",
        "Покажи рекомендації на основі моїх покупок",
        "Що популярне зараз?",
        # Аналітика
        "Покажи статистику продажів",
        "Які товари найпопулярніші?",
        "Звіт по користувачах",
        # Сповіщення
        "Створи сповіщення про акцію",
        "Надішли повідомлення про статус замовлення",
        "Оголоси про новинки",
    ]

    for i, query in enumerate(demo_queries, 1):
        print(f"\n📝 Запит {i}: {query}")
        print("-" * 40)

        try:
            response = assistant.process_user_query("demo_user", query)
            print(f"🤖 Відповідь: {response}")
        except Exception as e:
            print(f"❌ Помилка: {e}")

        print()


def setup_test_data(assistant):
    """
    Налаштування тестових даних для демонстрації
    """
    print("📊 Налаштування тестових даних...")

    # Профіль користувача
    assistant.update_user_profile(
        "demo_user",
        {
            "name": "Демо Користувач",
            "email": "demo@example.com",
            "preferences": {
                "categories": ["Електроніка", "Одяг", "Подарунки"],
                "price_range": {"min": 100, "max": 5000},
                "notification_preferences": {"email": True, "sms": False, "push": True},
            },
            "purchase_history": [
                {"product": "Смартфон", "category": "Електроніка", "price": 8000},
                {"product": "Куртка", "category": "Одяг", "price": 2500},
                {"product": "Книга", "category": "Подарунки", "price": 300},
            ],
            "viewed_products": [
                {"product": "Навушники", "category": "Електроніка"},
                {"product": "Сумка", "category": "Аксесуари"},
                {"product": "Годинник", "category": "Аксесуари"},
            ],
            "cart_items": [
                {"product": "Чохол для телефону", "price": 200},
                {"product": "Зарядний кабель", "price": 150},
            ],
        },
    )

    # Товари в базі даних
    products = [
        {
            "id": 1,
            "name": "Смартфон Samsung Galaxy S23",
            "category": "Електроніка",
            "price": 25000,
            "description": "Сучасний смартфон з потужною камерою",
            "features": ["5G", "128GB", "Android 13"],
            "in_stock": True,
        },
        {
            "id": 2,
            "name": "Зимова куртка Columbia",
            "category": "Одяг",
            "price": 3500,
            "description": "Тепла зимова куртка для активного відпочинку",
            "features": ["Водонепроникома", "Утеплена", "Вітрозахисна"],
            "in_stock": True,
        },
        {
            "id": 3,
            "name": "Подарунковий набір косметики",
            "category": "Подарунки",
            "price": 800,
            "description": "Елегантний подарунковий набір для жінок",
            "features": ["Натуральні компоненти", "Елегантна упаковка"],
            "in_stock": True,
        },
        {
            "id": 4,
            "name": "Бездротові навушники AirPods",
            "category": "Електроніка",
            "price": 4500,
            "description": "Преміум бездротові навушники",
            "features": ["Bluetooth 5.0", "Шумопоглинання", "20 годин автономності"],
            "in_stock": True,
        },
        {
            "id": 5,
            "name": "Смарт-годинник Apple Watch",
            "category": "Електроніка",
            "price": 12000,
            "description": "Розумний годинник з моніторингом здоров'я",
            "features": ["GPS", "Пульсометр", "Водонепроникомий"],
            "in_stock": False,
        },
    ]

    for product in products:
        assistant.add_product_to_database(product)

    # Замовлення користувача
    orders = [
        {
            "id": "12345",
            "status": "active",
            "items": [{"product": "Смартфон Samsung Galaxy S23", "price": 25000, "quantity": 1}],
            "total": 25000,
            "shipping_address": "м. Київ, вул. Хрещатик, 1",
            "created_at": "2025-01-15T10:30:00Z",
            "estimated_delivery": "2025-01-20T14:00:00Z",
        },
        {
            "id": "12346",
            "status": "completed",
            "items": [{"product": "Зимова куртка Columbia", "price": 3500, "quantity": 1}],
            "total": 3500,
            "shipping_address": "м. Львів, вул. Свободи, 15",
            "created_at": "2025-01-10T09:15:00Z",
            "delivered_at": "2025-01-12T16:30:00Z",
        },
    ]

    for order in orders:
        assistant.add_order_to_database("demo_user", order)

    print("✅ Тестові дані налаштовані!")


def demo_specific_features():
    """
    Демонстрація конкретних функцій
    """
    print("\n🎯 Демонстрація конкретних функцій")
    print("=" * 50)

    prompt_manager = EnhancedPromptManager()
    rag_engine = PostgresRAGEngine(user_id="example_user", swagger_spec_id="example_spec")
    assistant = EnhancedAIAssistant(prompt_manager, rag_engine)

    # Демонстрація створення опису товару
    print("\n📝 Демонстрація створення опису товару:")
    product_description_query = "Створи опис для товару Смартфон iPhone 15 Pro з ціною 45000 грн"
    response = assistant.process_user_query("demo_user", product_description_query)
    print(f"Запит: {product_description_query}")
    print(f"Відповідь: {response}")

    # Демонстрація розумного пошуку
    print("\n🔍 Демонстрація розумного пошуку:")
    search_query = "Потрібен подарунок для чоловіка 30 років"
    response = assistant.process_user_query("demo_user", search_query)
    print(f"Запит: {search_query}")
    print(f"Відповідь: {response}")

    # Демонстрація допомоги з замовленнями
    print("\n📦 Демонстрація допомоги з замовленнями:")
    order_query = "Відстежи замовлення #12345"
    response = assistant.process_user_query("demo_user", order_query)
    print(f"Запит: {order_query}")
    print(f"Відповідь: {response}")

    # Демонстрація рекомендацій
    print("\n🎯 Демонстрація рекомендацій:")
    recommendation_query = "Що порекомендуєш на основі моїх покупок?"
    response = assistant.process_user_query("demo_user", recommendation_query)
    print(f"Запит: {recommendation_query}")
    print(f"Відповідь: {response}")


def demo_conversation_history():
    """
    Демонстрація роботи з історією розмови
    """
    print("\n💬 Демонстрація історії розмови")
    print("=" * 50)

    prompt_manager = EnhancedPromptManager()
    rag_engine = PostgresRAGEngine(user_id="example_user", swagger_spec_id="example_spec")
    assistant = EnhancedAIAssistant(prompt_manager, rag_engine)

    user_id = "test_user"

    # Серія повідомлень
    conversations = [
        "Привіт! Я шукаю подарунок для дівчини",
        "А що є в діапазоні 1000-3000 грн?",
        "Добре, покажи найпопулярніші",
        "А які аксесуари підійдуть до телефону?",
        "Дякую за допомогу!",
    ]

    for i, message in enumerate(conversations, 1):
        print(f"\n👤 Повідомлення {i}: {message}")
        response = assistant.process_user_query(user_id, message)
        print(f"🤖 Відповідь: {response}")

    # Показ історії
    print(f"\n📋 Історія розмови для користувача {user_id}:")
    history = assistant.get_conversation_history(user_id)
    for i, entry in enumerate(history, 1):
        print(f"{i}. [{entry['timestamp']}] {entry['category']}: {entry['query']}")


if __name__ == "__main__":
    print("🚀 Запуск демонстрації розширеного AI-асистента")
    print("=" * 60)

    try:
        # Основна демонстрація
        demo_enhanced_ai_assistant()

        # Демонстрація конкретних функцій
        demo_specific_features()

        # Демонстрація історії розмови
        demo_conversation_history()

        print("\n✅ Демонстрація завершена успішно!")

    except Exception as e:
        print(f"❌ Помилка під час демонстрації: {e}")
        import traceback

        traceback.print_exc()
