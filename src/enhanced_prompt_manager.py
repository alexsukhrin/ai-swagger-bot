"""
Покращений менеджер промптів для AI Swagger Bot
Використовує промпти з YAML файлів замість хардкоду в коді
"""

import json
import logging
from typing import Any, Dict, List, Optional

from .yaml_prompt_manager import YAMLPromptManager

logger = logging.getLogger(__name__)


class EnhancedPromptManager:
    """
    Покращений менеджер промптів, який використовує YAML файли
    замість хардкоду промптів в коді.
    """

    def __init__(self, yaml_path: str = "prompts/base_prompts.yaml", db_manager=None):
        """
        Ініціалізація менеджера.

        Args:
            yaml_path: Шлях до YAML файлу з промптами
            db_manager: Менеджер бази даних
        """
        self.yaml_manager = YAMLPromptManager(yaml_path, db_manager)
        self._load_prompts()

    def _load_prompts(self):
        """Завантажує всі промпти з YAML файлу."""
        try:
            self.yaml_manager.load_base_prompts()
            logger.info("✅ Промпти успішно завантажено з YAML файлу")
        except Exception as e:
            logger.error(f"❌ Помилка завантаження промптів: {e}")

    def get_system_prompt(self) -> str:
        """Отримує системний промпт з YAML."""
        return self.yaml_manager.format_prompt("system_base")

    def get_intent_analysis_prompt(self, user_query: str, context: str = "") -> str:
        """Отримує промпт для аналізу наміру з YAML."""
        return self.yaml_manager.format_prompt(
            "intent_analysis_base", user_query=user_query, context=context
        )

    def get_error_analysis_prompt(
        self, error_message: str, original_query: str, api_request: Dict[str, Any]
    ) -> str:
        """Отримує промпт для аналізу помилок з YAML."""
        return self.yaml_manager.format_prompt(
            "error_analysis_base",
            error_message=error_message,
            original_query=original_query,
            api_request=json.dumps(api_request, ensure_ascii=False, indent=2),
        )

    def get_response_formatting_prompt(
        self,
        api_request: Dict[str, Any],
        server_response: Optional[Dict[str, Any]] = None,
        status: str = "success",
    ) -> str:
        """Отримує промпт для форматування відповіді з YAML."""
        return self.yaml_manager.format_prompt(
            "response_formatting_base",
            api_request=json.dumps(api_request, ensure_ascii=False, indent=2),
            server_response=(
                json.dumps(server_response, ensure_ascii=False, indent=2)
                if server_response
                else "Немає"
            ),
            status=status,
        )

    def get_endpoint_search_prompt(
        self, user_query: str, intent: Dict[str, Any], endpoints: List[Dict[str, Any]]
    ) -> str:
        """Отримує промпт для пошуку endpoints з YAML."""
        return self.yaml_manager.format_prompt(
            "endpoint_search_base",
            user_query=user_query,
            intent=json.dumps(intent, ensure_ascii=False, indent=2),
            endpoints=json.dumps(endpoints, ensure_ascii=False, indent=2),
        )

    def get_request_formation_prompt(
        self, user_query: str, intent: Dict[str, Any], endpoint_info: Dict[str, Any]
    ) -> str:
        """Отримує промпт для формування запиту з YAML."""
        return self.yaml_manager.format_prompt(
            "request_formation_base",
            user_query=user_query,
            intent=json.dumps(intent, ensure_ascii=False, indent=2),
            endpoint_info=json.dumps(endpoint_info, ensure_ascii=False, indent=2),
        )

    def get_optimization_prompt(self, current_request: Dict[str, Any], goal: str) -> str:
        """Отримує промпт для оптимізації з YAML."""
        return self.yaml_manager.format_prompt(
            "optimization_base",
            current_request=json.dumps(current_request, ensure_ascii=False, indent=2),
            goal=goal,
        )

    def get_debugging_prompt(
        self, issue_description: str, api_request: Dict[str, Any], error: str
    ) -> str:
        """Отримує промпт для налагодження з YAML."""
        return self.yaml_manager.format_prompt(
            "debugging_base",
            issue_description=issue_description,
            api_request=json.dumps(api_request, ensure_ascii=False, indent=2),
            error=error,
        )

    def get_ux_improvement_prompt(self, original_response: str, context: str) -> str:
        """Отримує промпт для покращення UX з YAML."""
        return self.yaml_manager.format_prompt(
            "ux_improvement_base", original_response=original_response, context=context
        )

    def get_object_creation_prompt(
        self,
        user_query: str,
        endpoint_info: Dict[str, Any],
        conversation_history: List[Dict[str, Any]] = None,
    ) -> str:
        """Отримує промпт для створення об'єктів з YAML."""
        history_context = ""
        if conversation_history:
            history_context = json.dumps(conversation_history[-3:], ensure_ascii=False, indent=2)

        return self.yaml_manager.format_prompt(
            "object_creation_base",
            user_query=user_query,
            endpoint_info=json.dumps(endpoint_info, ensure_ascii=False, indent=2),
            conversation_history=history_context,
        )

    def get_followup_generation_prompt(
        self, api_request: Dict[str, Any], intent: Dict[str, Any], error_message: str
    ) -> str:
        """Отримує промпт для генерації follow-up запитів з YAML."""
        return self.yaml_manager.format_prompt(
            "followup_generation_base",
            api_request=json.dumps(api_request, ensure_ascii=False, indent=2),
            intent=json.dumps(intent, ensure_ascii=False, indent=2),
            error_message=error_message,
        )

    def get_help_prompt(self, user_query: str, available_resources: List[str]) -> str:
        """Отримує промпт для допомоги з YAML."""
        return self.yaml_manager.format_prompt(
            "help_base",
            user_query=user_query,
            available_resources=json.dumps(available_resources, ensure_ascii=False, indent=2),
        )

    def get_validation_prompt(self, data: Dict[str, Any], rules: Dict[str, Any]) -> str:
        """Отримує промпт для валідації з YAML."""
        return self.yaml_manager.format_prompt(
            "validation_base",
            data=json.dumps(data, ensure_ascii=False, indent=2),
            rules=json.dumps(rules, ensure_ascii=False, indent=2),
        )

    def get_api_response_processing_prompt(
        self, user_query: str, api_response: Dict[str, Any], available_fields: List[str] = None
    ) -> str:
        """Отримує промпт для обробки API відповіді з YAML."""
        return self.yaml_manager.format_prompt(
            "api_response_processing_base",
            user_query=user_query,
            processing_type="standard",  # Додаємо відсутню змінну
            api_response=json.dumps(api_response, ensure_ascii=False, indent=2),
            available_fields=json.dumps(available_fields or [], ensure_ascii=False, indent=2),
        )

    # E-commerce специфічні промпти
    def get_ecommerce_search_prompt(self, query: str, filters: Dict[str, Any]) -> str:
        """Отримує промпт для пошуку в e-commerce з YAML."""
        return self.yaml_manager.format_prompt(
            "ecommerce_search_base",
            query=query,
            filters=json.dumps(filters, ensure_ascii=False, indent=2),
        )

    def get_content_creation_prompt(self, product_info: Dict[str, Any], content_type: str) -> str:
        """Отримує промпт для створення контенту з YAML."""
        return self.yaml_manager.format_prompt(
            "content_creation_base",
            product_info=json.dumps(product_info, ensure_ascii=False, indent=2),
            content_type=content_type,
        )

    def get_customer_support_prompt(self, issue: str, user_context: Dict[str, Any]) -> str:
        """Отримує промпт для підтримки клієнтів з YAML."""
        return self.yaml_manager.format_prompt(
            "customer_support_base",
            issue=issue,
            user_context=json.dumps(user_context, ensure_ascii=False, indent=2),
        )

    def get_order_management_prompt(self, order_data: Dict[str, Any], action: str) -> str:
        """Отримує промпт для управління замовленнями з YAML."""
        return self.yaml_manager.format_prompt(
            "order_management_base",
            order_data=json.dumps(order_data, ensure_ascii=False, indent=2),
            action=action,
        )

    def get_recommendations_prompt(
        self, user_preferences: Dict[str, Any], available_products: List[Dict[str, Any]]
    ) -> str:
        """Отримує промпт для рекомендацій з YAML."""
        return self.yaml_manager.format_prompt(
            "recommendations_base",
            user_preferences=json.dumps(user_preferences, ensure_ascii=False, indent=2),
            available_products=json.dumps(available_products, ensure_ascii=False, indent=2),
        )

    def get_analytics_prompt(self, data: Dict[str, Any], analysis_type: str) -> str:
        """Отримує промпт для аналітики з YAML."""
        return self.yaml_manager.format_prompt(
            "analytics_base",
            data=json.dumps(data, ensure_ascii=False, indent=2),
            analysis_type=analysis_type,
        )

    def get_notifications_prompt(self, notification_type: str, user_data: Dict[str, Any]) -> str:
        """Отримує промпт для сповіщень з YAML."""
        return self.yaml_manager.format_prompt(
            "notifications_base",
            notification_type=notification_type,
            user_data=json.dumps(user_data, ensure_ascii=False, indent=2),
        )

    def get_prompt_by_name(self, prompt_name: str, **kwargs) -> str:
        """
        Універсальний метод для отримання промпту за назвою.

        Args:
            prompt_name: Назва промпту в YAML файлі
            **kwargs: Параметри для форматування промпту

        Returns:
            Відформатований промпт
        """
        try:
            return self.yaml_manager.format_prompt(prompt_name, **kwargs)
        except Exception as e:
            logger.error(f"Помилка отримання промпту '{prompt_name}': {e}")
            return f"Помилка завантаження промпту: {prompt_name}"

    def get_available_prompts(self) -> List[str]:
        """Отримує список доступних промптів."""
        return list(self.yaml_manager.prompts.keys())

    def reload_prompts(self):
        """Перезавантажує промпти з YAML файлу."""
        self.yaml_manager.reload_base_prompts()
        logger.info("✅ Промпти перезавантажено")

    def get_prompt_statistics(self) -> Dict[str, Any]:
        """Отримує статистику по промптах."""
        return self.yaml_manager.get_statistics()


# Емодзі константи (залишаємо для зворотної сумісності)
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
    SPEED = "��"
    MAGIC = "✨"
