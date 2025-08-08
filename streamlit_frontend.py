"""
Streamlit фронтенд для AI Swagger Bot з FastAPI бекендом
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
import streamlit as st
from dotenv import load_dotenv

# Завантажуємо змінні середовища
load_dotenv()

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфігурація API
API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8000")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def check_environment():
    """Перевіряє налаштування середовища."""
    if not OPENAI_API_KEY:
        st.error("❌ Не знайдено OPENAI_API_KEY в змінних середовища!")
        st.info("Створіть файл .env з OPENAI_API_KEY=your_key_here")
        return False
    return True


def initialize_session_state():
    """Ініціалізує стан сесії для чату."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "swagger_id" not in st.session_state:
        st.session_state.swagger_id = None
    if "jwt_token" not in st.session_state:
        st.session_state.jwt_token = None
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False
    if "prompts_generated" not in st.session_state:
        st.session_state.prompts_generated = False


def get_auth_headers():
    """Отримує заголовки авторизації."""
    headers = {"Content-Type": "application/json"}
    if st.session_state.jwt_token and st.session_state.is_authenticated:
        headers["Authorization"] = f"Bearer {st.session_state.jwt_token}"
    return headers


def check_api_health():
    """Перевіряє стан API."""
    import time

    # Спробуємо кілька разів з затримкою
    for attempt in range(3):
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=15)
            if response.status_code == 200:
                return True
        except Exception as e:
            logger.error(f"API health check attempt {attempt + 1} failed: {e}")
            if attempt < 2:  # Не чекаємо після останньої спроби
                time.sleep(2)

    return False


def create_demo_user():
    """Створює демо користувача та отримує токен."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/users/demo", headers={"Content-Type": "application/json"}, timeout=20
        )

        if response.status_code == 200:
            data = response.json()
            st.session_state.user_id = data["user_id"]
            st.session_state.jwt_token = data["token"]
            st.session_state.is_authenticated = True
            return True
        else:
            st.error(f"Помилка створення користувача: {response.text}")
            return False
    except Exception as e:
        st.error(f"Помилка створення користувача: {e}")
        return False


def upload_swagger_file(file, auto_generate_prompts: bool = True) -> Optional[str]:
    """Завантажує Swagger файл через API та опціонально генерує промпти."""
    try:
        files = {"file": (file.name, file.getvalue(), "application/json")}
        headers = get_auth_headers()
        headers.pop("Content-Type", None)  # Remove Content-Type for file upload

        response = requests.post(
            f"{API_BASE_URL}/upload-swagger", files=files, headers=headers, timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            swagger_id = data["swagger_id"]
            st.session_state.swagger_id = swagger_id

            # Автоматично генеруємо промпти після успішного завантаження
            if auto_generate_prompts:
                st.info("🤖 Автоматично генерую промпти через GPT...")
                if auto_generate_prompts_for_swagger(swagger_id):
                    st.session_state.prompts_generated = True
                    st.success("✅ Промпти успішно згенеровано!")
                else:
                    st.warning("⚠️ Не вдалося згенерувати промпти автоматично. Спробуйте вручну.")

            return swagger_id
        else:
            st.error(f"Помилка завантаження: {response.text}")
            return None
    except Exception as e:
        st.error(f"Помилка завантаження файлу: {e}")
        return None


def send_chat_message(message: str) -> Optional[str]:
    """Відправляє повідомлення в чат через API."""
    try:
        data = {"message": message, "user_id": st.session_state.user_id}

        response = requests.post(
            f"{API_BASE_URL}/chat", json=data, headers=get_auth_headers(), timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            return data["response"]
        else:
            st.error(f"Помилка чату: {response.text}")
            return None
    except Exception as e:
        st.error(f"Помилка відправки повідомлення: {e}")
        return None


def get_chat_history() -> List[Dict[str, Any]]:
    """Отримує історію чату через API."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/chat-history", headers=get_auth_headers(), timeout=10
        )

        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        logger.error(f"Помилка отримання історії: {e}")
        return []


def display_message(content: str, role: str, timestamp: datetime = None):
    """Відображає повідомлення в чаті."""
    if role == "user":
        with st.chat_message("user", avatar="👤"):
            st.write(content)
    else:
        with st.chat_message("assistant", avatar="🤖"):
            st.write(content)

    if timestamp:
        st.caption(f"⏰ {timestamp.strftime('%H:%M:%S')}")


def get_example_queries():
    """Повертає приклади запитів для різних категорій."""
    return {
        "🔍 Аналіз API": [
            "Покажи всі доступні endpoints",
            "Які методи HTTP підтримуються?",
            "Скільки endpoints у цьому API?",
            "Покажи endpoints для роботи з користувачами",
            "Які схеми даних використовуються?",
        ],
        "📝 Приклади запитів": [
            "Створи приклад POST запиту для створення користувача",
            "Покажи як зробити GET запит для отримання списку товарів",
            "Як оновити дані користувача через PUT?",
            "Створи приклад DELETE запиту",
            "Покажи приклад з параметрами запиту",
        ],
        "🔧 Технічні деталі": [
            "Які параметри потрібні для endpoint /users?",
            "Покажи схему відповіді для GET /products",
            "Які заголовки потрібні для авторизації?",
            "Як обробляти помилки в цьому API?",
            "Покажи валідаційні правила для полів",
        ],
        "🚀 Практичні сценарії": [
            "Як створити нового користувача та додати йому товар?",
            "Покажи послідовність запитів для реєстрації",
            "Як отримати список товарів з фільтрацією?",
            "Створи приклад для оновлення профілю користувача",
            "Як видалити товар та очистити кошик?",
        ],
        "❓ Допомога та навчання": [
            "Поясни різницю між POST та PUT",
            "Що таке статус коди HTTP?",
            "Як працює авторизація Bearer token?",
            "Поясни структуру JSON відповіді",
            "Як обробляти масиви в API запитах?",
        ],
    }


def get_swagger_based_suggestions():
    """Генерує підказки на основі завантаженої Swagger специфікації."""
    if not st.session_state.get("swagger_spec_id"):
        return {}

    try:
        # Отримуємо підказки з API
        headers = get_auth_headers()
        response = requests.post(
            f"{API_BASE_URL}/prompts/generate-suggestions",
            headers=headers,
            json={"swagger_data": st.session_state.get("swagger_data", {})},
        )

        if response.status_code == 200:
            data = response.json()
            suggestions = data.get("suggestions", [])

            # Групуємо підказки за категоріями
            grouped_suggestions = {}
            for suggestion in suggestions:
                category = suggestion.get("category", "Інші")
                if category not in grouped_suggestions:
                    grouped_suggestions[category] = []
                grouped_suggestions[category].append(suggestion)

            return grouped_suggestions
        else:
            st.error(f"Помилка отримання підказок: {response.status_code}")
            return {}

    except Exception as e:
        st.error(f"Помилка генерації підказок: {e}")
        return {}


def auto_generate_prompts():
    """Автоматично генерує промпти на основі Swagger специфікації."""
    if not st.session_state.get("swagger_spec_id"):
        st.error("Спочатку завантажте Swagger специфікацію!")
        return False

    return auto_generate_prompts_for_swagger(st.session_state.swagger_spec_id)


def auto_generate_prompts_for_swagger(swagger_spec_id: str) -> bool:
    """Генерує промпти для конкретного Swagger специфікації."""
    try:
        with st.spinner("🤖 Генерую промпти через GPT..."):
            headers = get_auth_headers()
            response = requests.post(
                f"{API_BASE_URL}/prompts/auto-generate-for-user",
                headers=headers,
                json={"swagger_spec_id": swagger_spec_id},
            )

        if response.status_code == 200:
            data = response.json()
            st.success(f"✅ {data['message']}")
            st.info(f"📊 Згенеровано: {data['saved_count']} промптів")

            # Показуємо деталі згенерованих промптів
            if data.get("prompts"):
                with st.expander("📋 Деталі згенерованих промптів"):
                    for prompt in data["prompts"]:
                        st.write(f"**{prompt['name']}** ({prompt['category']})")
                        st.write(f"Ресурс: {prompt['resource_type']}")
                        st.write(f"Endpoint: {prompt['http_method']} {prompt['endpoint_path']}")
                        st.divider()

            return True
        else:
            st.error(f"Помилка генерації промптів: {response.status_code}")
            return False

    except Exception as e:
        st.error(f"Помилка автоматичної генерації: {e}")
        return False


def display_example_queries():
    """Відображає приклади запитів з можливістю кліку."""
    st.subheader("💡 Приклади запитів")

    # Базові приклади
    examples = get_example_queries()

    # Додаємо підказки на основі Swagger
    swagger_suggestions = get_swagger_based_suggestions()

    # Показуємо базові приклади
    st.subheader("📚 Базові приклади")
    for category, queries in examples.items():
        st.write(f"**{category}**")
        for i, query in enumerate(queries):
            if st.button(f"📝 {query}", key=f"base_example_{category}_{i}"):
                return query
        st.divider()

    # Показуємо підказки на основі Swagger
    if swagger_suggestions:
        st.subheader("🎯 Підказки для вашого API")
        for category, suggestions in swagger_suggestions.items():
            st.write(f"**{category} ({len(suggestions)})**")
            for i, suggestion in enumerate(suggestions):
                title = suggestion.get("title", "Підказка")
                description = suggestion.get("description", "")
                example_query = suggestion.get("example_query", "")
                difficulty = suggestion.get("difficulty", "medium")

                # Іконка складності
                difficulty_icon = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(difficulty, "🟡")

                st.write(f"**{difficulty_icon} {title}**")
                if description:
                    st.write(f"*{description}*")
                if example_query:
                    if st.button(f"💬 {example_query}", key=f"swagger_suggestion_{category}_{i}"):
                        return example_query
                st.divider()

    return None


def main():
    """Головна функція додатку."""
    st.set_page_config(
        page_title="AI Swagger Bot", page_icon="🤖", layout="wide", initial_sidebar_state="expanded"
    )

    # Перевіряємо середовище
    if not check_environment():
        st.stop()

    # Ініціалізуємо стан сесії
    initialize_session_state()

    # Заголовок
    st.title("🤖 AI Swagger Bot")
    st.markdown("**Інтерактивний чат-бот для роботи зі Swagger специфікаціями**")

    # Перевіряємо стан API
    if not check_api_health():
        st.error("❌ API сервіс недоступний. Перевірте, чи запущений FastAPI сервіс.")
        st.info("💡 Переконайтеся, що Docker Compose запущений: `docker-compose up`")
        st.stop()

    # Бічна панель
    with st.sidebar:
        st.header("⚙️ Налаштування")

        # Авторизація
        st.subheader("🔐 Авторизація")
        if not st.session_state.is_authenticated:
            if st.button("👤 Створити демо користувача"):
                with st.spinner("Створення користувача..."):
                    if create_demo_user():
                        st.success("✅ Користувач створено!")
                        st.rerun()
                    else:
                        st.error("❌ Помилка створення користувача")
        else:
            st.success(f"✅ Авторизовано як: {st.session_state.user_id}")
            if st.button("🔄 Створити нового користувача"):
                st.session_state.is_authenticated = False
                st.session_state.user_id = None
                st.session_state.jwt_token = None
                st.session_state.messages = []
                st.rerun()

        # Завантаження Swagger
        if st.session_state.is_authenticated:
            st.subheader("📁 Завантаження Swagger")
            uploaded_file = st.file_uploader(
                "Виберіть Swagger JSON файл",
                type=["json"],
                help="Завантажте Swagger/OpenAPI специфікацію у форматі JSON",
            )

            if uploaded_file is not None:
                if st.button("📤 Завантажити Swagger"):
                    with st.spinner("Завантаження..."):
                        swagger_id = upload_swagger_file(uploaded_file, auto_generate_prompts=True)
                        if swagger_id:
                            st.success("✅ Swagger файл успішно завантажено!")
                            st.session_state.swagger_spec_id = swagger_id
                            st.rerun()
                        else:
                            st.error("❌ Помилка завантаження файлу")

            # Статус генерації промптів (тільки інформація)
            if st.session_state.get("swagger_spec_id"):
                if st.session_state.get("prompts_generated"):
                    st.success("✅ Промпти згенеровано для цього API")
                else:
                    st.info(
                        "💡 Промпти будуть згенеровані автоматично при завантаженні Swagger файлу"
                    )

                # Показуємо інформацію про завантажений Swagger
                if st.session_state.get("swagger_data"):
                    with st.expander("📊 Інформація про API"):
                        swagger_data = st.session_state.swagger_data
                        st.write(
                            f"**Назва:** {swagger_data.get('info', {}).get('title', 'Невідомо')}"
                        )
                        st.write(
                            f"**Версія:** {swagger_data.get('info', {}).get('version', 'Невідомо')}"
                        )
                        st.write(f"**Endpoints:** {len(swagger_data.get('paths', {}))}")

                        # Показуємо ресурси
                        paths = swagger_data.get("paths", {})
                        resources = set()
                        for path in paths.keys():
                            if "/" in path and len(path.split("/")) > 1:
                                resource = path.split("/")[1]
                                if resource and not resource.startswith("{"):
                                    resources.add(resource)

                        if resources:
                            st.write(f"**Ресурси:** {', '.join(resources)}")

    # Основний контент
    if st.session_state.is_authenticated:
        # Статистика чату
        if st.session_state.messages:
            col1, col2, col3 = st.columns(3)
            with col1:
                total_messages = len(st.session_state.messages)
                user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
                bot_messages = len(
                    [m for m in st.session_state.messages if m["role"] == "assistant"]
                )

                st.metric("Всього повідомлень", total_messages)
                st.metric("Ваших повідомлень", user_messages)
                st.metric("Відповідей бота", bot_messages)

            # Поради та інструкції
            with st.expander("🚀 Як почати роботу"):
                st.markdown(
                    """
                **1. Авторизація:**
                - Натисніть "Створити демо користувача" в бічній панелі
                - Це створить унікальний токен для вас

                **2. Завантаження API:**
                - Виберіть Swagger JSON файл
                - Натисніть "Завантажити"
                - Бот проаналізує ваш API

                **3. Автоматична генерація промптів:**
                - Промпти генеруються автоматично при завантаженні Swagger файлу
                - GPT проаналізує ваш API та створить спеціальні промпти
                - Це покращить якість відповідей бота для вашого API
                - Додаткові дії не потрібні

                **4. Початок чату:**
                - Використовуйте приклади запитів нижче
                - Задавайте питання природною мовою
                - Бот використовуватиме згенеровані промпти для кращих відповідей
                """
                )

            with st.expander("🔧 Типи запитів"):
                st.markdown(
                    """
                **📊 Аналіз API:**
                - "Покажи всі endpoints"
                - "Скільки методів підтримується?"
                - "Які схеми даних є?"

                **📝 Приклади кодів:**
                - "Створи приклад POST запиту"
                - "Покажи як зробити GET запит"
                - "Як оновити дані через PUT?"

                **🔍 Технічні деталі:**
                - "Які параметри потрібні?"
                - "Покажи схему відповіді"
                - "Як обробляти помилки?"

                **🚀 Практичні сценарії:**
                - "Як створити користувача?"
                - "Покажи послідовність запитів"
                - "Як фільтрувати дані?"
                """
                )

            with st.expander("💡 Поради для ефективної роботи"):
                st.markdown(
                    """
                **✅ Що робити:**
                - Задавайте конкретні питання
                - Просите приклади коду
                - Питайте про помилки та їх вирішення
                - Використовуйте природну мову

                **❌ Що уникати:**
                - Занадто загальні питання
                - Питання не про API
                - Складні технічні концепції
                - Питання про інші системи
                """
                )

        # Приклади запитів для авторизованих користувачів
        st.subheader("💡 Швидкі приклади запитів:")
        example_query = display_example_queries()

        # Chat input за межами columns
        prompt = st.chat_input("Введіть ваше повідомлення...")

        # Обробляємо введений текст або приклад
        if prompt or example_query:
            # Використовуємо приклад або введений текст
            final_prompt = example_query if example_query else prompt

            # Додаємо повідомлення користувача
            user_message = {"role": "user", "content": final_prompt, "timestamp": datetime.now()}
            st.session_state.messages.append(user_message)
            display_message(final_prompt, "user")

            # Отримуємо відповідь від API
            with st.spinner("🤖 Бот думає..."):
                response = send_chat_message(final_prompt)

                if response:
                    # Додаємо відповідь бота
                    bot_message = {
                        "role": "assistant",
                        "content": response,
                        "timestamp": datetime.now(),
                    }
                    st.session_state.messages.append(bot_message)
                    display_message(response, "assistant")
                else:
                    st.error("❌ Помилка отримання відповіді від бота")

        # Історія чату
        if st.session_state.messages:
            st.subheader("💬 Історія чату")

            # Кнопка очищення історії
            if st.button("🗑️ Очистити історію"):
                st.session_state.messages = []
                st.rerun()

            # Відображаємо повідомлення
            for message in st.session_state.messages:
                display_message(message["content"], message["role"], message.get("timestamp"))
    else:
        # Повідомлення для неавторизованих користувачів
        st.info("👆 Спочатку створіть демо користувача в бічній панелі")

        # Показуємо приклади
        st.subheader("💡 Приклади можливостей:")
        st.markdown(
            """
        - 🔍 **Аналіз API** - Детальний аналіз Swagger специфікацій
        - 📝 **Приклади кодів** - Генерація прикладів запитів
        - 🔧 **Технічна підтримка** - Допомога з параметрами та схемами
        - 🚀 **Практичні сценарії** - Реальні приклади використання API
        - 🤖 **Автоматична генерація промптів** - GPT створює спеціальні промпти для вашого API
        """
        )


if __name__ == "__main__":
    main()
