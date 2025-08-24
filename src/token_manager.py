"""
Менеджер токенів для CLI версії.
"""

import os
from typing import Optional

from src.config import Config


class TokenManager:
    """Менеджер токенів для CLI версії."""

    def __init__(self):
        """Ініціалізація менеджера токенів."""
        self.config = Config()
    
    def get_jwt_token(self, api_name: str = None) -> Optional[str]:
        """
        Отримує JWT токен з змінних середовища.
        
        Args:
            api_name: Назва API (опціонально, для майбутнього розширення)
            
        Returns:
            JWT токен або None, якщо не знайдено
        """
        # Спочатку шукаємо специфічний токен для API
        if api_name:
            env_key = f"JWT_TOKEN_{api_name.upper()}"
            token = os.getenv(env_key)
            if token:
                return token
        
        # Якщо не знайдено специфічний токен, шукаємо загальний
        token = os.getenv("JWT_TOKEN")
        if token:
            return token
        
        # Якщо не знайдено JWT_TOKEN, шукаємо в JWT_SECRET_KEY
        secret_key = os.getenv("JWT_SECRET_KEY")
        if secret_key:
            return secret_key
        
        return None
    
    def get_openai_api_key(self) -> Optional[str]:
        """
        Отримує OpenAI API ключ.
        
        Returns:
            OpenAI API ключ або None, якщо не знайдено
        """
        return os.getenv("OPENAI_API_KEY")
    
    def get_api_base_url(self, api_name: str = None) -> Optional[str]:
        """
        Отримує базовий URL для API.
        
        Args:
            api_name: Назва API (опціонально)
            
        Returns:
            Базовий URL або None, якщо не знайдено
        """
        # Спочатку шукаємо специфічний URL для API
        if api_name:
            env_key = f"API_BASE_URL_{api_name.upper()}"
            url = os.getenv(env_key)
            if url:
                return url
        
        # Якщо не знайдено специфічний URL, шукаємо загальний
        return os.getenv("API_BASE_URL")
    
    def get_jwt_expires_in(self) -> int:
        """
        Отримує час життя JWT токена в секундах.
        
        Returns:
            Час життя токена (за замовчуванням 3600 секунд)
        """
        expires_in = os.getenv("JWT_EXPIRES_IN")
        if expires_in:
            try:
                return int(expires_in)
            except ValueError:
                pass
        
        return 3600  # За замовчуванням 1 година
    
    def has_valid_jwt_token(self, api_name: str = None) -> bool:
        """
        Перевіряє, чи є валідний JWT токен.
        
        Args:
            api_name: Назва API (опціонально)
            
        Returns:
            True, якщо токен знайдено
        """
        token = self.get_jwt_token(api_name)
        return token is not None and token.strip() != ""
    
    def get_all_tokens_info(self) -> dict:
        """
        Отримує інформацію про всі доступні токени.
        
        Returns:
            Словник з інформацією про токени
        """
        info = {
            "jwt_token": self.get_jwt_token() is not None,
            "jwt_secret_key": os.getenv("JWT_SECRET_KEY") is not None,
            "openai_api_key": self.get_openai_api_key() is not None,
            "api_base_url": self.get_api_base_url() is not None,
            "jwt_expires_in": self.get_jwt_expires_in()
        }
        
        # Додаємо специфічні токени для API, якщо є
        api_tokens = {}
        for key, value in os.environ.items():
            if key.startswith("JWT_TOKEN_") and value:
                api_name = key[10:].lower()  # Видаляємо "JWT_TOKEN_"
                api_tokens[api_name] = True
        
        info["api_specific_tokens"] = api_tokens
        
        return info
