"""
Готові промпт-шаблони для InteractiveSwaggerAgent
"""

import json
from typing import Any, Dict, List, Optional


class PromptTemplates:
    """Клас з готовими промпт-шаблонами для різних сценаріїв."""

    @staticmethod
    def get_system_prompt() -> str:
        """Загальний системний промпт для агента."""
        return """
Ти - експерт з API та Swagger/OpenAPI специфікаціями. Твоя задача - допомогти користувачам взаємодіяти з API через природну мову.

Ти маєш доступ до:
- Swagger/OpenAPI специфікації API
- Історії попередніх взаємодій з користувачем
- Можливості виконувати API виклики
- Аналізу помилок сервера

Твої основні функції:
1. Розуміти запити користувача природною мовою
2. Знаходити відповідні API endpoints
3. Формувати правильні API запити
4. Аналізувати помилки сервера
5. Запитувати додаткову інформацію при необхідності
6. Повторно виконувати запити з новою інформацією

Завжди відповідай українською мовою та будь корисним та дружелюбним.
Використовуй емодзі для кращого сприйняття та структуруй відповіді зрозуміло.
"""

    @staticmethod
    def get_intent_analysis_prompt(user_query: str, context: str = "") -> str:
        """Промпт для аналізу наміру користувача."""
        return f"""
Ти - експерт з API. Аналізуй запит користувача та визначай:
1. Тип операції (GET, POST, PUT, DELETE)
2. Ресурс або endpoint
3. Параметри та дані
4. Мета або ціль запиту

Контекст попередніх взаємодій:
{context}

Запит користувача: {user_query}

Відповідай у форматі JSON:
{{
    "operation": "GET|POST|PUT|DELETE",
    "resource": "назва ресурсу",
    "parameters": {{"param1": "value1"}},
    "data": {{"field1": "value1"}},
    "intent": "опис мети запиту"
}}
"""

    @staticmethod
    def get_error_analysis_prompt(
        error_message: str, original_query: str, api_request: Dict[str, Any]
    ) -> str:
        """Промпт для аналізу помилок сервера."""
        return f"""
Проаналізуй помилку сервера та згенеруй корисний запит на додаткову інформацію.

Помилка сервера: {error_message}
Оригінальний запит: {original_query}
API запит: {json.dumps(api_request, ensure_ascii=False, indent=2)}

Типи помилок:
- Валідація: потрібні додаткові поля
- Авторизація: проблеми з токеном
- Не знайдено: неправильний ID або шлях
- Конфлікт: запис вже існує

Створи зрозумілий запит українською мовою, який допоможе користувачу надати недостатню інформацію.

Відповідь має бути дружелюбною та конкретною, з емодзі для кращого сприйняття.
"""

    @staticmethod
    def get_response_formatting_prompt(
        api_request: Dict[str, Any],
        server_response: Optional[Dict[str, Any]] = None,
        status: str = "success",
    ) -> str:
        """Промпт для форматування відповіді користувачу."""
        return f"""
Відформатуй відповідь користувачу про API запит.

API запит: {json.dumps(api_request, ensure_ascii=False, indent=2)}
Відповідь сервера: {json.dumps(server_response, ensure_ascii=False, indent=2) if server_response else "Немає"}
Статус: {status}

Правила форматування:
- Використовуй емодзі для кращої читабельності
- Покажи URL, метод, параметри
- Якщо є помилка - поясни її зрозуміло
- Якщо успіх - покажи результат
- Будь дружелюбним та корисним
- Використовуй структурований формат

Відповідай українською мовою.
"""

    @staticmethod
    def get_api_response_processing_prompt(
        user_query: str, api_response: Dict[str, Any], available_fields: List[str] = None
    ) -> str:
        """Промпт для обробки відповіді API сервера в дружелюбний текст."""

        # Аналізуємо запит користувача для визначення потрібних полів
        query_lower = user_query.lower()

        # Визначаємо що хоче користувач
        wants_names = any(word in query_lower for word in ["назв", "ім'я", "title", "name"])
        wants_ids = any(word in query_lower for word in ["id", "айді", "номер"])
        wants_categories = any(word in query_lower for word in ["категорі", "category"])
        wants_prices = any(word in query_lower for word in ["цін", "price", "вартість"])
        wants_only = any(word in query_lower for word in ["тільки", "лише", "only"])
        wants_list = any(word in query_lower for word in ["список", "list", "всі", "all"])

        # Визначаємо тип обробки
        if wants_only and (wants_names or wants_ids or wants_categories):
            processing_type = "filtered"
        elif wants_list:
            processing_type = "list"
        else:
            processing_type = "full"

        return f"""
Ти - експерт з обробки даних. Твоя задача - перетворити JSON відповідь від API сервера в дружелюбний текст для користувача.

ЗАПИТ КОРИСТУВАЧА: {user_query}
ТИП ОБРОБКИ: {processing_type}

JSON ВІДПОВІДЬ API:
{json.dumps(api_response, ensure_ascii=False, indent=2)}

ДОСТУПНІ ПОЛЯ: {available_fields if available_fields else "Всі поля з JSON"}

ПРАВИЛА ОБРОБКИ:

1. **Аналіз запиту користувача:**
   - Якщо користувач просить "тільки назви" - покажи тільки назви
   - Якщо просить "ID та назву" - покажи ID та назву
   - Якщо просить "категорії" - покажи категорії
   - Якщо просить "ціни" - покажи ціни

2. **Форматування відповіді:**
   - Використовуй емодзі для кращого сприйняття
   - Структуруй інформацію зрозуміло
   - Якщо список - використовуй маркери
   - Якщо таблиця - використовуй структурований формат

3. **Адаптація до контексту:**
   - Якщо один елемент - покажи детально
   - Якщо багато елементів - покажи список
   - Якщо порожній результат - поясни це

4. **Спеціальні випадки:**
   - Якщо користувач просить "тільки назви" - покажи тільки назви без додаткової інформації
   - Якщо просить "ID та назву" - формат: "ID: назва"
   - Якщо просить "категорії" - список категорій
   - Якщо просить "ціни" - покажи ціни з валютою

ПРИКЛАДИ ВІДПОВІДЕЙ:

Для запиту "Покажи тільки назви товарів":
📋 Список назв товарів:
• Синя сукня
• Червона футболка
• Зелена куртка

Для запиту "Покажи ID та назву":
🆔 Товари:
• 1: Синя сукня
• 2: Червона футболка
• 3: Зелена куртка

Для запиту "Категорії":
📂 Доступні категорії:
• Одяг
• Взуття
• Аксесуари

ВІДПОВІДЬ:
Створи дружелюбну відповідь українською мовою, яка відповідає запиту користувача та показує тільки потрібну інформацію.
"""

    @staticmethod
    def get_object_creation_prompt(
        user_query: str,
        endpoint_info: Dict[str, Any],
        conversation_history: List[Dict[str, Any]] = None,
    ) -> str:
        """Промпт для створення об'єктів з автоматичним заповненням полів."""

        # Аналізуємо запит користувача
        query_lower = user_query.lower()

        # Визначаємо тип створення
        is_creating_category = any(word in query_lower for word in ["категорі", "category"])
        is_creating_product = any(word in query_lower for word in ["товар", "product", "продукт"])
        is_creating_user = any(word in query_lower for word in ["користувач", "user"])

        # Витягуємо назву з запиту
        import re

        name_match = re.search(r'["""]([^"""]+)["""]', user_query)
        extracted_name = name_match.group(1) if name_match else None

        # Аналізуємо історію розмови для контексту
        context_info = ""
        if conversation_history:
            recent_messages = conversation_history[-3:]  # Останні 3 повідомлення
            context_info = "\n".join(
                [f"Попередній запит: {msg.get('user_message', '')}" for msg in recent_messages]
            )

        return f"""
Ти - експерт з створення об'єктів через API. Твоя задача - допомогти користувачу створити об'єкт з автоматичним заповненням полів.

ЗАПИТ КОРИСТУВАЧА: {user_query}
ТИП СТВОРЕННЯ: {"категорія" if is_creating_category else "товар" if is_creating_product else "користувач" if is_creating_user else "об'єкт"}

ІСТОРІЯ РОЗМОВИ:
{context_info if context_info else "Немає попереднього контексту"}

ENDPOINT ІНФОРМАЦІЯ:
{json.dumps(endpoint_info, ensure_ascii=False, indent=2)}

ПРАВИЛА СТВОРЕННЯ:

1. **Автоматичне заповнення полів:**
   - Якщо користувач вказав тільки назву - спробуй заповнити інші поля автоматично
   - Використовуй контекст з історії розмови для кращого розуміння
   - Генеруй реалістичні значення для обов'язкових полів

2. **Для категорій:**
   - Назва: з запиту користувача
   - Опис: згенеруй опис на основі назви
   - Slug: створіть URL-friendly версію назви
   - Статус: "active" за замовчуванням

3. **Для товарів:**
   - Назва: з запиту користувача
   - Опис: згенеруй детальний опис
   - Ціна: запропонуй реалістичну ціну
   - Категорія: використай з контексту або запропонуй
   - Розмір/Колір: згенеруй на основі типу товару
   - Статус: "active" за замовчуванням

4. **Для користувачів:**
   - Ім'я: з запиту користувача
   - Email: згенеруй на основі імені
   - Пароль: згенеруй безпечний пароль
   - Роль: "user" за замовчуванням

ПРИКЛАДИ АВТОМАТИЧНОГО ЗАПОВНЕННЯ:

Запит: "Створи товар з назвою Телефон"
Автоматичне заповнення:
{{
    "name": "Телефон",
    "description": "Сучасний смартфон з високоякісними характеристиками",
    "price": 15000.00,
    "category": "Електроніка",
    "brand": "Samsung",
    "model": "Galaxy S23",
    "color": "Чорний",
    "in_stock": true,
    "warranty": "24 місяці"
}}

Запит: "Створи категорію Електроніка"
Автоматичне заповнення:
{{
    "name": "Електроніка",
    "description": "Категорія для електронних пристроїв та гаджетів",
    "slug": "electronics",
    "status": "active",
    "icon": "📱"
}}

ОБРОБКА ПОМИЛОК:

Якщо виникла помилка при створенні:

1. **Помилка валідації:**
   - Покажи які поля потрібно виправити
   - Запропонуй правильні значення
   - Не проси користувача вводити все заново

2. **Помилка авторизації:**
   - Поясни проблему з токеном
   - Запропонуй перевірити налаштування

3. **Помилка мережі:**
   - Поясни проблему з'єднання
   - Запропонуй повторити спробу

4. **Інші помилки:**
   - Покажи зрозуміле пояснення
   - Запропонуй рішення

ПРИКЛАДИ ОБРОБКИ ПОМИЛОК:

Помилка: "Field 'price' is required"
Відповідь:
❌ Помилка створення товару: потрібно вказати ціну
💡 Запропонована ціна: 15000.00 UAH
🔄 Спробувати створити з цією ціною?

Помилка: "Category 'Electronics' not found"
Відповідь:
❌ Помилка: категорія "Електроніка" не знайдена
💡 Доступні категорії: Одяг, Взуття, Аксесуари
🔄 Створити товар в категорії "Одяг"?

ВІДПОВІДЬ:
Створи дружелюбну відповідь українською мовою. Якщо все добре - покажи успішне створення. Якщо є помилка - поясни її та запропонуй рішення без необхідності повторного введення всіх даних.
"""

    @staticmethod
    def get_followup_generation_prompt(
        api_request: Dict[str, Any], intent: Dict[str, Any], error_message: str
    ) -> str:
        """Промпт для генерації запиту на додаткову інформацію."""
        return f"""
Проаналізуй помилку та згенеруй запит на додаткову інформацію.

API запит: {json.dumps(api_request, ensure_ascii=False, indent=2)}
Намір: {json.dumps(intent, ensure_ascii=False, indent=2)}
Помилка: {error_message}

Створи зрозумілий запит українською мовою, який:
1. Пояснить що саме потрібно
2. Надасть конкретні приклади
3. Буде дружелюбним та корисним
4. Використає емодзі для кращого сприйняття

Формат відповіді:
❌ Помилка: [опис помилки]

📋 Для успішного виконання потрібно вказати:
• [список потрібних полів]

💡 Будь ласка, надайте недостатню інформацію. Наприклад:
• [конкретні приклади]
"""

    @staticmethod
    def get_help_prompt(user_query: str, available_resources: List[str]) -> str:
        """Промпт для допомоги користувачу."""
        return f"""
Користувач не зрозумів як використовувати API. Надай корисну допомогу.

Поточний запит: {user_query}
Доступні ресурси: {', '.join(available_resources)}

Створи зрозумілий посібник з прикладами:
- Як створювати записи
- Як отримувати дані
- Як оновлювати записи
- Як видаляти записи

Надай конкретні приклади запитів українською мовою з емодзі для кращого сприйняття.
"""

    @staticmethod
    def get_endpoint_search_prompt(
        user_query: str, intent: Dict[str, Any], endpoints: List[Dict[str, Any]]
    ) -> str:
        """Промпт для пошуку endpoints."""
        return f"""
Знайди відповідні API endpoints для запиту користувача.

Запит користувача: {user_query}
Намір: {json.dumps(intent, ensure_ascii=False, indent=2)}

Доступні endpoints:
{json.dumps(endpoints, ensure_ascii=False, indent=2)}

Поверни список найбільш відповідних endpoints з їх метаданими.
"""

    @staticmethod
    def get_request_formation_prompt(
        user_query: str, intent: Dict[str, Any], endpoint_info: Dict[str, Any]
    ) -> str:
        """Промпт для формування API запиту."""
        return f"""
Сформуй правильний API запит на основі наміру користувача.

Запит користувача: {user_query}
Намір: {json.dumps(intent, ensure_ascii=False, indent=2)}
Endpoint інформація: {json.dumps(endpoint_info, ensure_ascii=False, indent=2)}

Правила формування:
- Використовуй правильний HTTP метод
- Додай обов'язкові параметри
- Валідуй формат даних
- Врахуй path variables
- Додай query parameters якщо потрібно

Поверни готовий API запит у форматі JSON.
"""

    @staticmethod
    def get_optimization_prompt(current_request: Dict[str, Any], goal: str) -> str:
        """Промпт для оптимізації запитів."""
        return f"""
Оптимізуй API запит для кращої продуктивності.

Поточний запит: {json.dumps(current_request, ensure_ascii=False, indent=2)}
Мета: {goal}

Можливі оптимізації:
- Зменшити кількість полів
- Використати більш ефективний endpoint
- Додати кешування
- Оптимізувати параметри

Поверни оптимізований запит з поясненням змін.
"""

    @staticmethod
    def get_debugging_prompt(
        issue_description: str, api_request: Dict[str, Any], error: str
    ) -> str:
        """Промпт для налагодження проблем."""
        return f"""
Допоможи налагодити проблему з API запитом.

Проблема: {issue_description}
API запит: {json.dumps(api_request, ensure_ascii=False, indent=2)}
Помилка: {error}

Можливі причини:
- Неправильний формат даних
- Відсутні обов'язкові поля
- Проблеми з авторизацією
- Неправильний endpoint

Надай конкретні рекомендації для виправлення українською мовою.
"""

    @staticmethod
    def get_ux_improvement_prompt(original_response: str, context: str) -> str:
        """Промпт для покращення UX."""
        return f"""
Покращіть відповідь для кращого користувацького досвіду.

Оригінальна відповідь: {original_response}
Контекст: {context}

Правила покращення:
- Додай корисні підказки
- Використовуй емодзі для структурування
- Зробіть відповідь більш дружелюбною
- Додай приклади якщо потрібно
- Зберегти всю важливу інформацію

Поверни покращену версію українською мовою.
"""


# Константи для емодзі
class EmojiConstants:
    """Константи для емодзі в відповідях."""

    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "💡"
    SEARCH = "🔍"
    LOADING = "🔄"
    HELP = "🆘"
    SETTINGS = "⚙️"
    LINK = "🔗"
    METHOD = "📤"
    DATA = "📦"
    STATUS = "📊"
    TIME = "⏰"
    USER = "👤"
    BOT = "🤖"
    API = "🌐"
    DATABASE = "🗄️"
    SECURITY = "🔐"
    SPEED = "🚀"
    MAGIC = "✨"


# Приклади використання
if __name__ == "__main__":
    # Приклад використання промптів
    user_query = "Створи нову категорію з назвою 'Електроніка'"

    # Аналіз наміру
    intent_prompt = PromptTemplates.get_intent_analysis_prompt(user_query)
    print("📝 Промпт для аналізу наміру:")
    print(intent_prompt)
    print()

    # Приклад помилки
    error_message = "Validation error: description is required"
    api_request = {
        "url": "http://localhost:3030/api/categories",
        "method": "POST",
        "data": {"name": "Електроніка"},
    }

    error_prompt = PromptTemplates.get_error_analysis_prompt(error_message, user_query, api_request)
    print("⚠️ Промпт для аналізу помилки:")
    print(error_prompt)
    print()

    print("🎯 Промпт-шаблони готові для використання в InteractiveSwaggerAgent!")
