"""
Конфігурація проекту AI Swagger Bot.
"""

import os
from typing import Any, Dict

from dotenv import load_dotenv

# Завантажуємо змінні середовища
load_dotenv()


class Config:
    """Централізована конфігурація проекту."""

    # API налаштування
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0"))

    # JWT налаштування
    JWT_TOKEN = os.getenv("JWT_TOKEN")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "ai_swagger_bot_secret_key_2024")

    # Swagger налаштування
    SWAGGER_SPEC_PATH = os.getenv("SWAGGER_SPEC_PATH", "examples/swagger_specs/shop_api.json")
    BASE_URL = os.getenv("BASE_URL", "https://db62d2b2c3a5.ngrok-free.app/api")

    # Clickone Shop API налаштування
    CLICKONE_SHOP_API_URL = "https://api.oneshop.click"
    CLICKONE_SHOP_SWAGGER_URL = "https://api.oneshop.click/docs/ai-json"
    CLICKONE_SHOP_JWT_TOKEN = os.getenv("CLICKONE_JWT_TOKEN")
    CLICKONE_SHOP_JWT_SECRET = os.getenv("JWT_SECRET_KEY")

    # База даних налаштування
    DATABASE_URL = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@127.0.0.1:5432/ai_swagger_bot"
    )

    # RAG налаштування (тільки PostgreSQL)
    USE_PGVECTOR = True

    # Логування
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # RAG налаштування
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    SEARCH_K_RESULTS = int(os.getenv("SEARCH_K_RESULTS", "3"))

    # Streamlit налаштування
    STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))
    STREAMLIT_HOST = os.getenv("STREAMLIT_HOST", "localhost")

    # Історія розмов
    CONVERSATION_HISTORY_DIR = os.getenv("CONVERSATION_HISTORY_DIR", "./conversation_history")

    # Налаштування для очищення дублікатів
    CLEANUP_DUPLICATES_ON_STARTUP = (
        os.getenv("CLEANUP_DUPLICATES_ON_STARTUP", "false").lower() == "true"
    )

    # Налаштування Auto Retry системи
    AUTO_RETRY_ENABLED = os.getenv("AUTO_RETRY_ENABLED", "true").lower() == "true"
    MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
    RETRY_DELAY_SECONDS = float(os.getenv("RETRY_DELAY_SECONDS", "1.0"))

    # Типи помилок для автоматичного retry - БІЛЬШ ОБЕРЕЖНО
    RETRY_ON_STATUS_CODES = [422, 500, 502, 503, 504]  # Прибрали загальний 400
    RETRY_ON_CONNECTION_ERRORS = True
    RETRY_ON_TIMEOUT_ERRORS = True

    # Специфічні помилки для retry (тільки коли точно знаємо що можна виправити)
    RETRY_ON_MISSING_SLUG = True  # slug must be a string
    RETRY_ON_MISSING_REQUIRED_FIELDS = True  # відсутні обов'язкові поля

    @classmethod
    def get_database_config(cls) -> Dict[str, Any]:
        """Отримує конфігурацію бази даних."""
        return {
            "database_url": cls.DATABASE_URL,
            "use_pgvector": cls.USE_PGVECTOR,
        }

    @classmethod
    def get_rag_config(cls) -> Dict[str, Any]:
        """Отримує конфігурацію RAG."""
        return {
            "chunk_size": cls.CHUNK_SIZE,
            "chunk_overlap": cls.CHUNK_OVERLAP,
            "search_k_results": cls.SEARCH_K_RESULTS,
            "use_pgvector": cls.USE_PGVECTOR,
        }
