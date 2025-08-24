#!/usr/bin/env python3
"""
Streamlit додаток для демонстрації роботи з Clickone Shop API
"""

import json
import os
from datetime import datetime

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

# Завантажуємо змінні середовища
load_dotenv()

# Конфігурація
CLICKONE_SHOP_API_URL = "https://api.oneshop.click"
CLICKONE_SHOP_SWAGGER_URL = "https://api.oneshop.click/docs/ai-json"
JWT_TOKEN = os.getenv("JWT_SECRET_KEY")

# Налаштування сторінки
st.set_page_config(
    page_title="Clickone Shop API Demo",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    """Головна функція Streamlit додатку"""

    # Заголовок
    st.title("🛍️ Clickone Shop API Demo")
    st.markdown("Демонстрація роботи з реальними ендпоінтами Clickone Shop API")

    # Бічна панель
    with st.sidebar:
        st.header("⚙️ Налаштування")

        # Перевірка JWT токена
        if JWT_TOKEN:
            st.success("✅ JWT токен знайдено")
            st.info(f"Токен: {JWT_TOKEN[:20]}...")
        else:
            st.warning("⚠️ JWT токен не знайдено")
            st.info("Додайте JWT_SECRET_KEY в .env файл для повного доступу")

        st.divider()

        # Навігація
        st.header("🧭 Навігація")
        page = st.radio(
            "Виберіть сторінку:",
            ["🏠 Головна", "📋 Аналіз Swagger", "📂 Категорії", "🔍 Тестування API"],
        )

    # Основний контент
    if page == "🏠 Головна":
        show_home_page()
    elif page == "📋 Аналіз Swagger":
        show_swagger_page()
    elif page == "📂 Категорії":
        show_categories_page()
    elif page == "🔍 Тестування API":
        show_api_testing_page()


def show_home_page():
    """Головна сторінка"""
    st.header("🏠 Головна сторінка")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Статистика API")

        # Тестуємо доступні ендпоінти
        endpoints_stats = test_api_endpoints()

        st.metric("Працюючі ендпоінти", len(endpoints_stats["working"]))
        st.metric("Потребують авторизації", len(endpoints_stats["unauthorized"]))
        st.metric("Не знайдені", len(endpoints_stats["not_found"]))

        # Показуємо список доступних ендпоінтів з Swagger
        st.info("📋 Доступні ендпоінти в Swagger для AI:")
        st.write("• GET /api/categories - Отримати категорії")
        st.write("• POST /api/categories - Створити категорію")
        st.write("• GET /api/categories/{id} - Отримати категорію")
        st.write("• PUT /api/categories/{id} - Оновити категорію")
        st.write("• DELETE /api/categories/{id} - Видалити категорію")

    with col2:
        st.subheader("📊 Swagger статистика")

        # Показуємо статистику завантаженої специфікації
        swagger_spec = download_swagger_spec()
        if swagger_spec:
            st.success("✅ Swagger специфікація доступна")
            st.metric("Ендпоінти", len(swagger_spec.get("paths", {})))
            st.metric("Схеми", len(swagger_spec.get("components", {}).get("schemas", {})))
        else:
            st.warning("⚠️ Swagger специфікація не знайдена")
            st.info("💡 Перевірте підключення до API")

        st.subheader("📈 Швидкі статистики")
        st.info("💡 Використовуйте бічну панель для навігації між різними розділами API")


def show_swagger_page():
    """Сторінка аналізу Swagger специфікації"""
    st.header("📋 Аналіз Swagger специфікації")

    # Отримуємо завантажену Swagger специфікацію
    swagger_spec = download_swagger_spec()

    if swagger_spec:
        st.info("💡 Ця сторінка показує аналіз Swagger специфікації, яка вже завантажена в систему")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Основна інформація")
            st.write(f"**API:** {swagger_spec.get('info', {}).get('title', 'Unknown')}")
            st.write(f"**Версія:** {swagger_spec.get('info', {}).get('version', 'Unknown')}")
            st.write(f"**Ендпоінти:** {len(swagger_spec.get('paths', {}))}")
            st.write(f"**Схеми:** {len(swagger_spec.get('components', {}).get('schemas', {}))}")

        with col2:
            st.subheader("🔗 Доступні ендпоінти")
            paths = swagger_spec.get("paths", {})
            for path, methods in paths.items():
                st.write(f"**{path}:**")
                for method, details in methods.items():
                    if isinstance(details, dict):
                        summary = details.get("summary", "No summary")
                        st.write(f"  • {method.upper()}: {summary}")

        # Показуємо схеми
        st.subheader("📋 Схеми даних")
        schemas = swagger_spec.get("components", {}).get("schemas", {})

        # Створюємо DataFrame для схем
        schema_data = []
        for name, schema in schemas.items():
            schema_data.append(
                {
                    "Назва": name,
                    "Тип": schema.get("type", "unknown"),
                    "Властивості": len(schema.get("properties", {})),
                    "Обов'язкові": len(schema.get("required", [])),
                }
            )

        if schema_data:
            df = pd.DataFrame(schema_data)
            st.dataframe(df, use_container_width=True)

        # Детальний перегляд схеми
        if schemas:
            selected_schema = st.selectbox(
                "Виберіть схему для детального перегляду:", list(schemas.keys())
            )
            if selected_schema:
                schema = schemas[selected_schema]
                st.subheader(f"📋 Схема: {selected_schema}")
                st.json(schema)

    else:
        st.error("❌ Swagger специфікація не знайдена")
        st.info("💡 Перевірте, чи завантажена специфікація в систему")


def show_categories_page():
    """Сторінка категорій"""
    st.header("📂 Категорії")

    if not JWT_TOKEN:
        st.warning("⚠️ JWT токен не знайдено. Деякі функції недоступні.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📥 Отримати категорії")
        if st.button("🔄 Оновити список"):
            with st.spinner("Отримую категорії..."):
                categories = get_categories()
                if categories:
                    st.session_state.categories = categories
                    st.success(f"✅ Отримано {len(categories)} категорій")
                else:
                    st.error("❌ Помилка отримання категорій")

    with col2:
        st.subheader("➕ Створити категорію")

        with st.form("create_category"):
            name = st.text_input("Назва категорії", placeholder="Введіть назву")
            slug = st.text_input("Slug", placeholder="Введіть slug")
            description = st.text_area("Опис", placeholder="Введіть опис")
            is_active = st.checkbox("Активна", value=True)
            sort_order = st.number_input("Порядок сортування", value=0, step=1)

            submitted = st.form_submit_button("Створити")
            if submitted and name and slug:
                with st.spinner("Створюю категорію..."):
                    result = create_category(
                        {
                            "name": name,
                            "slug": slug,
                            "description": description,
                            "isActive": is_active,
                            "sortOrder": sort_order,
                        }
                    )
                    if result:
                        st.success("✅ Категорію створено!")
                        st.json(result)
                    else:
                        st.error("❌ Помилка створення")

    # Показуємо список категорій
    if hasattr(st.session_state, "categories") and st.session_state.categories:
        st.subheader("📋 Список категорій")

        # Конвертуємо в DataFrame
        categories_df = pd.DataFrame(st.session_state.categories)
        st.dataframe(categories_df, use_container_width=True)

        # Детальний перегляд
        if len(st.session_state.categories) > 0:
            selected_category = st.selectbox(
                "Виберіть категорію для детального перегляду:",
                options=range(len(st.session_state.categories)),
                format_func=lambda x: st.session_state.categories[x].get("name", f"Категорія {x}"),
            )

            if selected_category is not None:
                category = st.session_state.categories[selected_category]
                st.subheader(f"📋 Деталі категорії: {category.get('name', 'Unknown')}")
                st.json(category)


def show_products_page():
    """Сторінка продуктів"""
    st.header("📦 Продукти")

    if not JWT_TOKEN:
        st.warning("⚠️ JWT токен не знайдено. Деякі функції недоступні.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📥 Отримати продукти")
        if st.button("🔄 Оновити список"):
            with st.spinner("Отримую продукти..."):
                products = get_products()
                if products:
                    st.session_state.products = products
                    st.success(f"✅ Отримано {len(products)} продуктів")
                else:
                    st.error("❌ Помилка отримання продуктів")

    with col2:
        st.subheader("🔍 Фільтри")
        if hasattr(st.session_state, "products") and st.session_state.products:
            # Фільтр за статусом
            statuses = list(set([p.get("status", "unknown") for p in st.session_state.products]))
            selected_status = st.selectbox("Статус:", ["Всі"] + statuses)

            # Фільтр за брендом
            brands = list(
                set(
                    [
                        p.get("brand", {}).get("name", "Unknown")
                        for p in st.session_state.products
                        if p.get("brand")
                    ]
                )
            )
            selected_brand = st.selectbox("Бренд:", ["Всі"] + brands)

    # Показуємо список продуктів
    if hasattr(st.session_state, "products") and st.session_state.products:
        st.subheader("📋 Список продуктів")

        # Застосовуємо фільтри
        filtered_products = st.session_state.products

        if "selected_status" in locals() and selected_status != "Всі":
            filtered_products = [p for p in filtered_products if p.get("status") == selected_status]

        if "selected_brand" in locals() and selected_brand != "Всі":
            filtered_products = [
                p for p in filtered_products if p.get("brand", {}).get("name") == selected_brand
            ]

        # Конвертуємо в DataFrame
        products_data = []
        for product in filtered_products:
            products_data.append(
                {
                    "ID": product.get("id", "Unknown"),
                    "Назва": product.get("name", "Unknown"),
                    "Ціна": product.get("price", "Unknown"),
                    "Статус": product.get("status", "Unknown"),
                    "SKU": product.get("sku", "Unknown"),
                    "Бренд": product.get("brand", {}).get("name", "Unknown"),
                    "Категорія": product.get("category", {}).get("name", "Unknown"),
                    "Сімейство": product.get("family", {}).get("name", "Unknown"),
                }
            )

        if products_data:
            df = pd.DataFrame(products_data)
            st.dataframe(df, use_container_width=True)

            # Детальний перегляд
            if len(filtered_products) > 0:
                selected_product = st.selectbox(
                    "Виберіть продукт для детального перегляду:",
                    options=range(len(filtered_products)),
                    format_func=lambda x: filtered_products[x].get("name", f"Продукт {x}"),
                )

                if selected_product is not None:
                    product = filtered_products[selected_product]
                    st.subheader(f"📋 Деталі продукту: {product.get('name', 'Unknown')}")
                    st.json(product)


def show_brands_page():
    """Сторінка брендів"""
    st.header("🏷️ Бренди")

    if not JWT_TOKEN:
        st.warning("⚠️ JWT токен не знайдено. Деякі функції недоступні.")
        return

    # Отримуємо бренди
    if st.button("🔄 Оновити список брендів"):
        with st.spinner("Отримую бренди..."):
            brands = get_brands()
            if brands:
                st.session_state.brands = brands
                st.success(f"✅ Отримано {len(brands)} брендів")
            else:
                st.error("❌ Помилка отримання брендів")

    # Показуємо список брендів
    if hasattr(st.session_state, "brands") and st.session_state.brands:
        st.subheader("📋 Список брендів")

        # Конвертуємо в DataFrame
        brands_data = []
        for brand in st.session_state.brands:
            brands_data.append(
                {
                    "ID": brand.get("id", "Unknown"),
                    "Назва": brand.get("name", "Unknown"),
                    "Slug": brand.get("slug", "Unknown"),
                    "Країна": brand.get("country", "Unknown"),
                    "Статус": brand.get("status", "Unknown"),
                    "Кількість продуктів": brand.get("productsCount", 0),
                    "Веб-сайт": brand.get("website", "Unknown"),
                }
            )

        if brands_data:
            df = pd.DataFrame(brands_data)
            st.dataframe(df, use_container_width=True)

            # Детальний перегляд
            if len(st.session_state.brands) > 0:
                selected_brand = st.selectbox(
                    "Виберіть бренд для детального перегляду:",
                    options=range(len(st.session_state.brands)),
                    format_func=lambda x: st.session_state.brands[x].get("name", f"Бренд {x}"),
                )

                if selected_brand is not None:
                    brand = st.session_state.brands[selected_brand]
                    st.subheader(f"📋 Деталі бренду: {brand.get('name', 'Unknown')}")
                    st.json(brand)


def show_customers_page():
    """Сторінка клієнтів"""
    st.header("👥 Клієнти")

    if not JWT_TOKEN:
        st.warning("⚠️ JWT токен не знайдено. Деякі функції недоступні.")
        return

    # Отримуємо клієнтів
    if st.button("🔄 Оновити список клієнтів"):
        with st.spinner("Отримую клієнтів..."):
            customers = get_customers()
            if customers:
                st.session_state.customers = customers
                st.success(f"✅ Отримано {len(customers)} клієнтів")
            else:
                st.error("❌ Помилка отримання клієнтів")

    # Показуємо список клієнтів
    if hasattr(st.session_state, "customers") and st.session_state.customers:
        st.subheader("📋 Список клієнтів")

        # Конвертуємо в DataFrame
        customers_data = []
        for customer in st.session_state.customers:
            customers_data.append(
                {
                    "ID": customer.get("id", "Unknown"),
                    "Email": customer.get("email", "Unknown"),
                    "Ім'я": customer.get("firstName", "Unknown"),
                    "Прізвище": customer.get("lastName", "Unknown"),
                    "Телефон": customer.get("phone", "Unknown"),
                    "Статус": customer.get("status", "Unknown"),
                    "Сегмент": customer.get("segment", "Unknown"),
                }
            )

        if customers_data:
            df = pd.DataFrame(customers_data)
            st.dataframe(df, use_container_width=True)


def show_collections_page():
    """Сторінка колекцій"""
    st.header("📚 Колекції")

    if not JWT_TOKEN:
        st.warning("⚠️ JWT токен не знайдено. Деякі функції недоступні.")
        return

    # Отримуємо колекції
    if st.button("🔄 Оновити список колекцій"):
        with st.spinner("Отримую колекції..."):
            collections = get_collections()
            if collections:
                st.session_state.collections = collections
                st.success(f"✅ Отримано {len(collections)} колекцій")
            else:
                st.error("❌ Помилка отримання колекцій")

    # Показуємо список колекцій
    if hasattr(st.session_state, "collections") and st.session_state.collections:
        st.subheader("📋 Список колекцій")

        # Конвертуємо в DataFrame
        collections_data = []
        for collection in st.session_state.collections:
            collections_data.append(
                {
                    "ID": collection.get("id", "Unknown"),
                    "Назва": collection.get("name", "Unknown"),
                    "Slug": collection.get("slug", "Unknown"),
                    "Тип": collection.get("type", "Unknown"),
                    "Статус": collection.get("status", "Unknown"),
                    "Кількість продуктів": collection.get("productsCount", 0),
                }
            )

        if collections_data:
            df = pd.DataFrame(collections_data)
            st.dataframe(df, use_container_width=True)


def show_families_page():
    """Сторінка сімейств"""
    st.header("👨‍👩‍👧‍👦 Сімейства продуктів")

    if not JWT_TOKEN:
        st.warning("⚠️ JWT токен не знайдено. Деякі функції недоступні.")
        return

    # Отримуємо сімейства
    if st.button("🔄 Оновити список сімейств"):
        with st.spinner("Отримую сімейства..."):
            families = get_families()
            if families:
                st.session_state.families = families
                st.success(f"✅ Отримано {len(families)} сімейств")
            else:
                st.error("❌ Помилка отримання сімейств")

    # Показуємо список сімейств
    if hasattr(st.session_state, "families") and st.session_state.families:
        st.subheader("📋 Список сімейств")

        # Конвертуємо в DataFrame
        families_data = []
        for family in st.session_state.families:
            families_data.append(
                {
                    "ID": family.get("id", "Unknown"),
                    "Назва": family.get("name", "Unknown"),
                    "Опис": family.get("description", "Unknown"),
                }
            )

        if families_data:
            df = pd.DataFrame(families_data)
            st.dataframe(df, use_container_width=True)


def show_settings_page():
    """Сторінка налаштувань"""
    st.header("⚙️ Налаштування")

    if not JWT_TOKEN:
        st.warning("⚠️ JWT токен не знайдено. Деякі функції недоступні.")
        return

    # Отримуємо налаштування
    if st.button("🔄 Оновити список налаштувань"):
        with st.spinner("Отримую налаштування..."):
            settings = get_settings()
            if settings:
                st.session_state.settings = settings
                st.success(f"✅ Отримано {len(settings)} налаштувань")
            else:
                st.error("❌ Помилка отримання налаштувань")

    # Показуємо список налаштувань
    if hasattr(st.session_state, "settings") and st.session_state.settings:
        st.subheader("📋 Список налаштувань")

        # Конвертуємо в DataFrame
        settings_data = []
        for setting in st.session_state.settings:
            settings_data.append(
                {
                    "ID": setting.get("id", "Unknown"),
                    "Ключ": setting.get("key", "Unknown"),
                    "Значення": setting.get("value", "Unknown"),
                    "Продукт ID": setting.get("productId", "Unknown"),
                }
            )

        if settings_data:
            df = pd.DataFrame(settings_data)
            st.dataframe(df, use_container_width=True)


def show_api_testing_page():
    """Сторінка тестування API"""
    st.header("🔍 Тестування API")

    st.subheader("📊 Тестування доступності ендпоінтів")

    if st.button("🧪 Запустити тестування"):
        with st.spinner("Тестую API ендпоінти..."):
            endpoints_stats = test_api_endpoints()

            # Показуємо результати
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("✅ Працюючі", len(endpoints_stats["working"]))
                if endpoints_stats["working"]:
                    st.write("**Працюючі ендпоінти:**")
                    for endpoint in endpoints_stats["working"]:
                        st.write(f"• {endpoint}")

            with col2:
                st.metric("🔒 Потребують авторизації", len(endpoints_stats["unauthorized"]))
                if endpoints_stats["unauthorized"]:
                    st.write("**Потребують токен:**")
                    for endpoint in endpoints_stats["unauthorized"]:
                        st.write(f"• {endpoint}")

            with col3:
                st.metric("❌ Не знайдені", len(endpoints_stats["not_found"]))
                if endpoints_stats["not_found"]:
                    st.write("**Не знайдені:**")
                    for endpoint in endpoints_stats["not_found"]:
                        st.write(f"• {endpoint}")

    st.divider()

    st.subheader("📈 Статистика використання")
    st.info("💡 Ця сторінка показує реальну доступність різних ендпоінтів API")


# Допоміжні функції
def download_swagger_spec():
    """Завантажує Swagger специфікацію"""
    try:
        response = requests.get(
            CLICKONE_SHOP_SWAGGER_URL, timeout=30, headers={"User-Agent": "AI-Swagger-Bot/1.0"}
        )

        if response.status_code == 200:
            return response.json()
        else:
            return None

    except Exception as e:
        st.error(f"Помилка завантаження: {e}")
        return None


def test_api_endpoints():
    """Тестує доступність API ендпоінтів"""
    # Тільки ендпоінти, доступні в Swagger для AI
    endpoints_to_test = [
        ("/api/categories", "GET"),
        ("/api/categories", "POST"),
        ("/api/categories/{id}", "GET"),
        ("/api/categories/{id}", "PUT"),
        ("/api/categories/{id}", "DELETE"),
    ]

    working = []
    unauthorized = []
    not_found = []

    for endpoint, method in endpoints_to_test:
        try:
            response = requests.get(
                f"{CLICKONE_SHOP_API_URL}{endpoint}",
                timeout=10,
                headers={"User-Agent": "AI-Swagger-Bot/1.0"},
            )

            if response.status_code == 200:
                working.append(endpoint)
            elif response.status_code == 401:
                unauthorized.append(endpoint)
            elif response.status_code == 404:
                not_found.append(endpoint)

        except Exception:
            not_found.append(endpoint)

    return {"working": working, "unauthorized": unauthorized, "not_found": not_found}


def get_categories():
    """Отримує список категорій"""
    if not JWT_TOKEN:
        return None

    try:
        headers = {
            "Authorization": f"Bearer {JWT_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "AI-Swagger-Bot/1.0",
        }

        response = requests.get(
            f"{CLICKONE_SHOP_API_URL}/api/categories", headers=headers, timeout=30
        )

        if response.status_code == 200:
            return response.json()
        else:
            return None

    except Exception:
        return None


def create_category(category_data):
    """Створює нову категорію"""
    if not JWT_TOKEN:
        return None

    try:
        headers = {
            "Authorization": f"Bearer {JWT_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "AI-Swagger-Bot/1.0",
        }

        response = requests.post(
            f"{CLICKONE_SHOP_API_URL}/api/categories",
            headers=headers,
            json=category_data,
            timeout=30,
        )

        if response.status_code == 201:
            return response.json()
        else:
            return None

    except Exception:
        return None


def get_products():
    """Отримує список продуктів"""
    try:
        response = requests.get(
            f"{CLICKONE_SHOP_API_URL}/api/products",
            timeout=30,
            headers={"User-Agent": "AI-Swagger-Bot/1.0"},
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("products", [])
        else:
            return None

    except Exception:
        return None


def get_brands():
    """Отримує список брендів"""
    try:
        response = requests.get(
            f"{CLICKONE_SHOP_API_URL}/api/brands",
            timeout=30,
            headers={"User-Agent": "AI-Swagger-Bot/1.0"},
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("brands", [])
        else:
            return None

    except Exception:
        return None


def get_customers():
    """Отримує список клієнтів"""
    try:
        response = requests.get(
            f"{CLICKONE_SHOP_API_URL}/api/customers",
            timeout=30,
            headers={"User-Agent": "AI-Swagger-Bot/1.0"},
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("customers", [])
        else:
            return None

    except Exception:
        return None


def get_collections():
    """Отримує список колекцій"""
    try:
        response = requests.get(
            f"{CLICKONE_SHOP_API_URL}/api/collections",
            timeout=30,
            headers={"User-Agent": "AI-Swagger-Bot/1.0"},
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("collections", [])
        else:
            return None

    except Exception:
        return None


def get_families():
    """Отримує список сімейств"""
    try:
        response = requests.get(
            f"{CLICKONE_SHOP_API_URL}/api/families",
            timeout=30,
            headers={"User-Agent": "AI-Swagger-Bot/1.0"},
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("families", [])
        else:
            return None

    except Exception:
        return None


def get_settings():
    """Отримує список налаштувань"""
    try:
        response = requests.get(
            f"{CLICKONE_SHOP_API_URL}/api/settings",
            timeout=30,
            headers={"User-Agent": "AI-Swagger-Bot/1.0"},
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("settings", [])
        else:
            return None

    except Exception:
        return None


if __name__ == "__main__":
    main()
