"""
AI Error Handler для автоматичного виправлення помилок API та спілкування з користувачем
"""

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import openai

from .config import Config


@dataclass
class APIError:
    """Структура помилки API"""

    error_message: str
    status_code: int
    endpoint: str
    method: str
    input_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None


@dataclass
class AIFixSuggestion:
    """Пропозиція виправлення від AI"""

    fixed_data: Dict[str, Any]
    explanation: str
    confidence: float
    suggestions: List[str]


class AIErrorHandler:
    """AI обробник помилок для автоматичного виправлення та спілкування з користувачем"""

    def __init__(self, openai_api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Ініціалізація AI Error Handler

        Args:
            openai_api_key: API ключ OpenAI (якщо не передано, береться з .env)
            model: Модель OpenAI для використання
        """
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4")

        if not self.api_key:
            raise ValueError("OpenAI API ключ не знайдено. Встановіть OPENAI_API_KEY в .env файлі")

        self.client = openai.OpenAI(api_key=self.api_key)

        # Кеш для збереження помилок та їх виправлень
        self.error_cache: Dict[str, AIFixSuggestion] = {}

        print(f"🤖 AI Error Handler ініціалізовано з моделлю {self.model}")

    def analyze_api_error(self, error: APIError) -> AIFixSuggestion:
        """
        Аналізує помилку API та пропонує виправлення

        Args:
            error: Об'єкт помилки API

        Returns:
            Пропозиція виправлення від AI
        """
        # Перевіряємо кеш
        cache_key = self._generate_cache_key(error)
        if cache_key in self.error_cache:
            print("📋 Використовуємо кешоване виправлення")
            return self.error_cache[cache_key]

        print(f"🔍 Аналізую помилку API: {error.error_message}")

        # Створюємо промпт для AI
        prompt = self._create_error_analysis_prompt(error)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Ти експерт з API та валідації даних.
                        Аналізуй помилки та запропонуй конкретні виправлення українською мовою.
                        Повертай відповідь у форматі JSON з полями:
                        - fixed_data: виправлені дані
                        - explanation: пояснення українською мовою
                        - confidence: впевненість у виправленні (0.0-1.0)
                        - suggestions: список порад для користувача""",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=500,
                temperature=0.1,
            )

            ai_response = response.choices[0].message.content
            print(f"🤖 AI відповідь: {ai_response}")

            # Парсимо JSON відповідь
            try:
                parsed_response = json.loads(ai_response)
                fix_suggestion = AIFixSuggestion(
                    fixed_data=parsed_response.get("fixed_data", {}),
                    explanation=parsed_response.get("explanation", "Виправлення не знайдено"),
                    confidence=parsed_response.get("confidence", 0.0),
                    suggestions=parsed_response.get("suggestions", []),
                )
            except json.JSONDecodeError:
                # Якщо JSON не парситься, створюємо базове виправлення
                fix_suggestion = self._create_fallback_fix(error)

            # Зберігаємо в кеш
            self.error_cache[cache_key] = fix_suggestion

            return fix_suggestion

        except Exception as e:
            print(f"❌ Помилка AI аналізу: {e}")
            return self._create_fallback_fix(error)

    def get_user_friendly_message(self, error: APIError, fix: AIFixSuggestion) -> str:
        """
        Створює зрозуміле повідомлення для користувача українською мовою

        Args:
            error: Помилка API
            fix: Пропозиція виправлення

        Returns:
            Зрозуміле повідомлення українською мовою
        """
        message_parts = []

        # Заголовок
        message_parts.append("🚨 **Помилка API**")
        message_parts.append(f"**Ендпоінт:** {error.method} {error.endpoint}")
        message_parts.append(f"**Код помилки:** {error.status_code}")
        message_parts.append("")

        # Пояснення помилки
        message_parts.append("**Що сталося:**")
        message_parts.append(f"{fix.explanation}")
        message_parts.append("")

        # Виправлені дані
        if fix.fixed_data:
            message_parts.append("**Виправлені дані:**")
            for key, value in fix.fixed_data.items():
                message_parts.append(f"• **{key}:** `{value}`")
            message_parts.append("")

        # Поради
        if fix.suggestions:
            message_parts.append("**Поради:**")
            for i, suggestion in enumerate(fix.suggestions, 1):
                message_parts.append(f"{i}. {suggestion}")
            message_parts.append("")

        # Впевненість
        confidence_text = (
            "Висока" if fix.confidence > 0.7 else "Середня" if fix.confidence > 0.4 else "Низька"
        )
        message_parts.append(
            f"**Впевненість у виправленні:** {confidence_text} ({fix.confidence:.1%})"
        )

        return "\n".join(message_parts)

    def suggest_retry_with_fix(self, error: APIError, fix: AIFixSuggestion) -> Dict[str, Any]:
        """
        Пропонує спробувати знову з виправленими даними

        Args:
            error: Помилка API
            fix: Пропозиція виправлення

        Returns:
            Словар з виправленими даними та інструкціями
        """
        return {
            "retry_data": fix.fixed_data,
            "instructions": f"Спробуйте знову з виправленими даними: {fix.explanation}",
            "confidence": fix.confidence,
            "suggestions": fix.suggestions,
        }

    def get_validation_rules(self, endpoint: str, entity_type: str) -> str:
        """
        Отримує правила валідації для конкретного ендпоінту та типу сутності

        Args:
            endpoint: Ендпоінт API
            entity_type: Тип сутності (наприклад, "category", "product")

        Returns:
            Правила валідації українською мовою
        """
        prompt = f"""
        Опиши правила валідації для {entity_type} в API ендпоінті {endpoint} українською мовою.

        Дай зрозуміле пояснення правил з прикладами:
        - Обов'язкові поля
        - Формати даних
        - Обмеження
        - Приклади правильних значень
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Ти експерт з API валідації та e-commerce систем. Пояснюй українською мовою.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=400,
                temperature=0.1,
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"❌ Помилка отримання правил валідації: {e}")
            return f"Не вдалося отримати правила валідації для {entity_type}: {str(e)}"

    def _create_error_analysis_prompt(self, error: APIError) -> str:
        """Створює промпт для аналізу помилки"""
        prompt = f"""
        Аналізуй помилку API та запропонуй виправлення українською мовою:

        **Помилка:** {error.error_message}
        **Код статусу:** {error.status_code}
        **Ендпоінт:** {error.method} {error.endpoint}
        **Вхідні дані:** {json.dumps(error.input_data, indent=2, ensure_ascii=False) if error.input_data else 'Немає'}

        Запропонуй виправлення та поверни відповідь у форматі JSON:
        {{
            "fixed_data": {{"поле": "виправлене значення"}},
            "explanation": "Пояснення українською мовою",
            "confidence": 0.8,
            "suggestions": ["порада 1", "порада 2"]
        }}
        """
        return prompt

    def _create_fallback_fix(self, error: APIError) -> AIFixSuggestion:
        """Створює базове виправлення у випадку помилки AI"""
        return AIFixSuggestion(
            fixed_data=error.input_data or {},
            explanation=f"Не вдалося автоматично виправити помилку: {error.error_message}",
            confidence=0.1,
            suggestions=[
                "Перевірте формат даних",
                "Переконайтеся, що всі обов'язкові поля заповнені",
                "Зверніться до документації API",
            ],
        )

    def _generate_cache_key(self, error: APIError) -> str:
        """Генерує ключ для кешу помилок"""
        key_parts = [
            error.method,
            error.endpoint,
            str(error.status_code),
            error.error_message[:100],  # Перші 100 символів помилки
        ]
        return "|".join(key_parts)

    def clear_cache(self) -> None:
        """Очищає кеш помилок"""
        self.error_cache.clear()
        print("🗑️ Кеш помилок очищено")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Отримує статистику кешу"""
        return {
            "total_errors": len(self.error_cache),
            "cache_size": len(str(self.error_cache)),
            "model": self.model,
        }


# Глобальний екземпляр для використання в проекті
_ai_error_handler: Optional[AIErrorHandler] = None


def get_ai_error_handler() -> AIErrorHandler:
    """Отримує глобальний екземпляр AI Error Handler"""
    global _ai_error_handler
    if _ai_error_handler is None:
        _ai_error_handler = AIErrorHandler()
    return _ai_error_handler


def set_ai_error_handler(handler: AIErrorHandler) -> None:
    """Встановлює глобальний екземпляр AI Error Handler"""
    global _ai_error_handler
    _ai_error_handler = handler
