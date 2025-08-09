"""
Менеджер для безпечного зберігання та управління API токенами.
"""

import base64
import os
from datetime import datetime, timedelta
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class TokenManager:
    """Менеджер для безпечного зберігання та управління API токенами."""

    def __init__(self, secret_key: str = None):
        """
        Ініціалізація менеджера токенів.

        Args:
            secret_key: Секретний ключ для шифрування (якщо не вказано, генерується автоматично)
        """
        self.secret_key = secret_key or os.getenv("TOKEN_ENCRYPTION_KEY")
        if not self.secret_key:
            # Генеруємо ключ якщо не вказано
            self.secret_key = self._generate_key()
            print(
                "⚠️  Згенеровано новий ключ шифрування токенів. Рекомендується встановити TOKEN_ENCRYPTION_KEY"
            )

        self.fernet = self._create_fernet()

    def _generate_key(self) -> str:
        """Генерує новий ключ шифрування."""
        return Fernet.generate_key().decode()

    def _create_fernet(self) -> Fernet:
        """Створює Fernet інстанс для шифрування."""
        # Конвертуємо строку в bytes
        if isinstance(self.secret_key, str):
            key = self.secret_key.encode()
        else:
            key = self.secret_key

        # Якщо ключ занадто короткий, розширюємо його
        if len(key) < 32:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b"ai_swagger_bot_salt",
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(key))

        return Fernet(key)

    def encrypt_token(self, token: str) -> str:
        """
        Шифрує токен для зберігання в БД.

        Args:
            token: Оригінальний токен

        Returns:
            Зашифрований токен
        """
        try:
            encrypted = self.fernet.encrypt(token.encode())
            return encrypted.decode()
        except Exception as e:
            print(f"❌ Помилка шифрування токена: {e}")
            raise

    def decrypt_token(self, encrypted_token: str) -> str:
        """
        Розшифровує токен з БД.

        Args:
            encrypted_token: Зашифрований токен

        Returns:
            Розшифрований токен
        """
        try:
            decrypted = self.fernet.decrypt(encrypted_token.encode())
            return decrypted.decode()
        except Exception as e:
            print(f"❌ Помилка розшифрування токена: {e}")
            raise

    def is_token_expired(self, expires_at: Optional[datetime]) -> bool:
        """
        Перевіряє чи закінчився термін дії токена.

        Args:
            expires_at: Дата закінчення токена

        Returns:
            True якщо токен закінчився
        """
        if not expires_at:
            return False

        return datetime.utcnow() > expires_at

    def get_token_expiry_warning(
        self, expires_at: Optional[datetime], days_warning: int = 7
    ) -> Optional[str]:
        """
        Отримує попередження про закінчення токена.

        Args:
            expires_at: Дата закінчення токена
            days_warning: За скільки днів попереджати

        Returns:
            Повідомлення попередження або None
        """
        if not expires_at:
            return None

        days_until_expiry = (expires_at - datetime.utcnow()).days

        if days_until_expiry <= 0:
            return "⚠️ Токен закінчився! Потрібно оновити."
        elif days_until_expiry <= days_warning:
            return f"⚠️ Токен закінчиться через {days_until_expiry} днів. Рекомендується оновити."

        return None

    def validate_token_format(self, token: str, token_type: str) -> bool:
        """
        Валідує формат токена.

        Args:
            token: Токен для валідації
            token_type: Тип токена

        Returns:
            True якщо токен валідний
        """
        if not token or len(token.strip()) == 0:
            return False

        if token_type == "api_key":
            # API ключі зазвичай мають мінімум 20 символів
            return len(token) >= 20
        elif token_type == "bearer":
            # Bearer токени зазвичай починаються з "Bearer "
            return token.startswith("Bearer ") and len(token) > 7
        elif token_type == "oauth2":
            # OAuth2 токени зазвичай мають мінімум 10 символів
            return len(token) >= 10

        return True

    def mask_token_for_display(self, token: str, token_type: str) -> str:
        """
        Маскує токен для безпечного відображення.

        Args:
            token: Оригінальний токен
            token_type: Тип токена

        Returns:
            Замаскований токен
        """
        if not token:
            return ""

        if token_type == "api_key":
            # Показуємо перші 4 та останні 4 символи
            if len(token) <= 8:
                return "*" * len(token)
            return token[:4] + "*" * (len(token) - 8) + token[-4:]
        elif token_type == "bearer":
            # Для bearer токенів показуємо "Bearer ****"
            return "Bearer ****"
        else:
            # Загальне маскування
            if len(token) <= 4:
                return "*" * len(token)
            return token[:2] + "*" * (len(token) - 4) + token[-2:]


# Глобальний екземпляр менеджера токенів
token_manager = TokenManager()


def get_token_manager() -> TokenManager:
    """Отримує глобальний екземпляр менеджера токенів."""
    return token_manager
