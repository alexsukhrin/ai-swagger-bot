"""
Конфігурація проекту AI Swagger Bot CLI.
"""

import os
from typing import Any, Dict

from dotenv import load_dotenv

# Завантажуємо змінні середовища
load_dotenv()


class Config:
    """Централізована конфігурація проекту CLI."""

    # API налаштування
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0"))

    # JWT налаштування
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "ai_swagger_bot_secret_key_2024")

    # Swagger налаштування
    CLICKONE_SHOP_SWAGGER_URL = "https://api.oneshop.click/docs/ai-json"

    # RAG налаштування
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    SEARCH_K_RESULTS = int(os.getenv("SEARCH_K_RESULTS", "3"))

    # ChromaDB налаштування
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "swagger_specs")

    # Логування
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @classmethod
    def get_rag_config(cls) -> Dict[str, Any]:
        """Отримує конфігурацію RAG."""
        return {
            "chunk_size": cls.CHUNK_SIZE,
            "chunk_overlap": cls.CHUNK_OVERLAP,
            "search_k_results": cls.SEARCH_K_RESULTS,
        }

    @classmethod
    def get_chroma_config(cls) -> Dict[str, Any]:
        """Отримує конфігурацію ChromaDB."""
        return {
            "path": cls.CHROMA_DB_PATH,
            "collection_name": cls.CHROMA_COLLECTION_NAME,
        }
