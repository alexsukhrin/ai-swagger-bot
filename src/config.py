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
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-full")
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0"))

    # JWT налаштування
    JWT_TOKEN = os.getenv("JWT_TOKEN")

    # Swagger налаштування
    SWAGGER_SPEC_PATH = os.getenv("SWAGGER_SPEC_PATH", "examples/swagger_specs/shop_api.json")
    BASE_URL = os.getenv("BASE_URL", "https://db62d2b2c3a5.ngrok-free.app/api")

    # База даних налаштування
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./temp_chroma_db")
    PROMPTS_DB_PATH = os.getenv("PROMPTS_DB_PATH", "prompts.db")

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
    MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "50"))

    @classmethod
    def validate(cls) -> bool:
        """Валідує конфігурацію."""
        if not cls.OPENAI_API_KEY:
            print("❌ OPENAI_API_KEY не знайдено в змінних середовища")
            return False

        if not os.path.exists(cls.SWAGGER_SPEC_PATH):
            print(f"❌ Swagger файл не знайдено: {cls.SWAGGER_SPEC_PATH}")
            return False

        print("✅ Конфігурація валідна")
        return True

    @classmethod
    def get_rag_config(cls) -> Dict[str, Any]:
        """Повертає конфігурацію для RAG."""
        return {
            "chunk_size": cls.CHUNK_SIZE,
            "chunk_overlap": cls.CHUNK_OVERLAP,
            "search_k": cls.SEARCH_K_RESULTS,
            "persist_directory": cls.CHROMA_DB_PATH,
        }

    @classmethod
    def get_agent_config(cls) -> Dict[str, Any]:
        """Повертає конфігурацію для агентів."""
        return {
            "openai_api_key": cls.OPENAI_API_KEY,
            "model": cls.OPENAI_MODEL,
            "temperature": cls.OPENAI_TEMPERATURE,
            "jwt_token": cls.JWT_TOKEN,
            "base_url": cls.BASE_URL,
        }
