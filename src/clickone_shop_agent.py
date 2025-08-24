"""
Спеціалізований агент для роботи з Clickone Shop API
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
import yaml

from .ai_error_handler import APIError, get_ai_error_handler
from .clickone_prompt_manager import ClickonePromptManager, get_clickone_prompt_manager


@dataclass
class ClickoneAPIConfig:
    """Конфігурація для Clickone Shop API"""

    base_url: str = "https://api.oneshop.click"
    api_version: str = "1.0"
    timeout: int = 30
    verify_ssl: bool = True


@dataclass
class ClickoneAPIResponse:
    """Відповідь від Clickone Shop API"""

    success: bool
    status_code: int
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None
    headers: Optional[Dict[str, str]] = None


class ClickoneShopAgent:
    """Спеціалізований агент для роботи з Clickone Shop API"""

    def __init__(self, config: Optional[ClickoneAPIConfig] = None):
        self.config = config or ClickoneAPIConfig()
        self.prompt_manager = get_clickone_prompt_manager()
        self.ai_error_handler = get_ai_error_handler()
        self.jwt_token: Optional[str] = None
        self.session = requests.Session()
        self.session.headers.update(
            {"Content-Type": "application/json", "User-Agent": "ClickoneShopAgent/2.0"}
        )

    def set_jwt_token(self, token: str) -> None:
        """Встановлює JWT токен для автентифікації"""
        self.jwt_token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        print("✅ JWT токен встановлено")

    def clear_jwt_token(self) -> None:
        """Очищає JWT токен"""
        self.jwt_token = None
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]
        print("✅ JWT токен очищено")

    def _make_request(
        self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None
    ) -> ClickoneAPIResponse:
        """Виконує HTTP запит до API"""
        url = f"{self.config.base_url}{endpoint}"

        try:
            if method.upper() == "GET":
                response = self.session.get(
                    url, params=params, timeout=self.config.timeout, verify=self.config.verify_ssl
                )
            elif method.upper() == "POST":
                response = self.session.post(
                    url, json=data, timeout=self.config.timeout, verify=self.config.verify_ssl
                )
            elif method.upper() == "PATCH":
                response = self.session.patch(
                    url, json=data, timeout=self.config.timeout, verify=self.config.verify_ssl
                )
            elif method.upper() == "DELETE":
                response = self.session.delete(
                    url, timeout=self.config.timeout, verify=self.config.verify_ssl
                )
            else:
                return ClickoneAPIResponse(
                    success=False, status_code=0, error=f"Непідтримуваний HTTP метод: {method}"
                )

            # Обробляємо відповідь
            if response.status_code >= 200 and response.status_code < 300:
                try:
                    response_data = response.json() if response.content else None
                except json.JSONDecodeError:
                    response_data = response.text

                return ClickoneAPIResponse(
                    success=True,
                    status_code=response.status_code,
                    data=response_data,
                    message="Успішно",
                    headers=dict(response.headers),
                )
            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get("message", "Помилка API")
                except json.JSONDecodeError:
                    error_message = response.text or f"HTTP {response.status_code}"

                # Створюємо об'єкт помилки для AI аналізу
                api_error = APIError(
                    error_message=error_message,
                    status_code=response.status_code,
                    endpoint=endpoint,
                    method=method,
                    input_data=data,
                    response_data=error_data if "error_data" in locals() else None,
                )

                # Аналізуємо помилку за допомогою AI
                ai_fix = self.ai_error_handler.analyze_api_error(api_error)

                # Створюємо зрозуміле повідомлення для користувача
                user_friendly_message = self.ai_error_handler.get_user_friendly_message(
                    api_error, ai_fix
                )

                # Додаємо AI виправлення до відповіді
                return ClickoneAPIResponse(
                    success=False,
                    status_code=response.status_code,
                    error=user_friendly_message,
                    headers=dict(response.headers),
                    data={"ai_fix": ai_fix.__dict__},  # Додаємо AI виправлення
                )

        except requests.exceptions.RequestException as e:
            return ClickoneAPIResponse(
                success=False, status_code=0, error=f"Помилка мережі: {str(e)}"
            )

    def create_category(self, category_data: Dict[str, Any]) -> ClickoneAPIResponse:
        """Створює нову категорію"""
        # Валідуємо обов'язкові поля
        required_fields = ["name", "slug"]
        missing_fields = [field for field in required_fields if field not in category_data]

        if missing_fields:
            return ClickoneAPIResponse(
                success=False,
                status_code=400,
                error=f"Відсутні обов'язкові поля: {', '.join(missing_fields)}",
            )

        # Перевіряємо JWT токен для admin операцій
        if not self.jwt_token:
            return ClickoneAPIResponse(
                success=False,
                status_code=401,
                error="JWT токен потрібен для створення категорії (Admin only)",
            )

        return self._make_request("POST", "/api/categories", data=category_data)

    def get_categories(
        self, is_active: Optional[bool] = None, parent_id: Optional[str] = None
    ) -> ClickoneAPIResponse:
        """Отримує список категорій"""
        params = {}
        if is_active is not None:
            params["isActive"] = is_active
        if parent_id is not None:
            params["parentId"] = parent_id

        return self._make_request("GET", "/api/categories", params=params)

    def get_category_by_id(self, category_id: str) -> ClickoneAPIResponse:
        """Отримує категорію за ID"""
        return self._make_request("GET", f"/api/categories/{category_id}")

    def update_category(self, category_id: str, update_data: Dict[str, Any]) -> ClickoneAPIResponse:
        """Оновлює категорію"""
        # Перевіряємо JWT токен для admin операцій
        if not self.jwt_token:
            return ClickoneAPIResponse(
                success=False,
                status_code=401,
                error="JWT токен потрібен для оновлення категорії (Admin only)",
            )

        return self._make_request("PATCH", f"/api/categories/{category_id}", data=update_data)

    def delete_category(self, category_id: str) -> ClickoneAPIResponse:
        """Видаляє категорію"""
        # Перевіряємо JWT токен для admin операцій
        if not self.jwt_token:
            return ClickoneAPIResponse(
                success=False,
                status_code=401,
                error="JWT токен потрібен для видалення категорії (Admin only)",
            )

        return self._make_request("DELETE", f"/api/categories/{category_id}")

    def analyze_user_intent(self, user_query: str) -> Dict[str, Any]:
        """Аналізує намір користувача"""
        # Використовуємо промпт для аналізу наміру
        intent_prompt = self.prompt_manager.get_intent_analysis_prompt()

        # Простий аналіз наміру (в реальному проекті тут буде GPT)
        query_lower = user_query.lower()

        intent_analysis = {
            "action": "unknown",
            "entity": "unknown",
            "context": "unknown",
            "access_level": "public",
            "endpoints": [],
            "confidence": 0.0,
        }

        # Визначаємо дію
        if any(word in query_lower for word in ["створи", "додай", "додати", "create"]):
            intent_analysis["action"] = "create"
            intent_analysis["access_level"] = "admin"
        elif any(word in query_lower for word in ["покажи", "знайди", "отримай", "get", "show"]):
            intent_analysis["action"] = "retrieve"
            intent_analysis["access_level"] = "public"
        elif any(word in query_lower for word in ["онови", "зміни", "update", "change"]):
            intent_analysis["action"] = "update"
            intent_analysis["access_level"] = "admin"
        elif any(word in query_lower for word in ["видали", "delete", "remove"]):
            intent_analysis["action"] = "delete"
            intent_analysis["access_level"] = "admin"

        # Визначаємо сутність
        if any(word in query_lower for word in ["категорію", "категорії", "category"]):
            intent_analysis["entity"] = "categories"
            intent_analysis["endpoints"] = ["/api/categories"]
        elif any(word in query_lower for word in ["товар", "товари", "product"]):
            intent_analysis["entity"] = "products"
        elif any(word in query_lower for word in ["замовлення", "order"]):
            intent_analysis["entity"] = "orders"
        elif any(word in query_lower for word in ["клієнт", "customer"]):
            intent_analysis["entity"] = "customers"

        # Визначаємо контекст
        if any(word in query_lower for word in ["магазин", "shop", "ecommerce"]):
            intent_analysis["context"] = "ecommerce_management"

        # Встановлюємо впевненість
        if intent_analysis["action"] != "unknown" and intent_analysis["entity"] != "unknown":
            intent_analysis["confidence"] = 0.8
        elif intent_analysis["action"] != "unknown" or intent_analysis["entity"] != "unknown":
            intent_analysis["confidence"] = 0.5

        return intent_analysis

    def process_user_query(self, user_query: str) -> Dict[str, Any]:
        """Обробляє запит користувача та виконує відповідну дію"""
        print(f"🔍 Аналіз запиту: {user_query}")

        # Аналізуємо намір
        intent = self.analyze_user_intent(user_query)
        print(f"📊 Намір: {intent}")

        # Виконуємо дію на основі наміру
        if intent["entity"] == "categories":
            if intent["action"] == "create":
                # Створення категорії
                return self._handle_category_creation(user_query, intent)
            elif intent["action"] == "retrieve":
                # Отримання категорій
                return self._handle_category_retrieval(user_query, intent)
            elif intent["action"] == "update":
                # Оновлення категорії
                return self._handle_category_update(user_query, intent)
            elif intent["action"] == "delete":
                # Видалення категорії
                return self._handle_category_deletion(user_query, intent)

        # Якщо не можемо обробити запит
        return {
            "success": False,
            "message": "Не вдалося обробити запит",
            "intent": intent,
            "suggestion": "Спробуйте переформулювати запит або зверніться за допомогою",
        }

    def _handle_category_creation(self, user_query: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Обробляє створення категорії"""
        if not self.jwt_token:
            return {
                "success": False,
                "message": "JWT токен потрібен для створення категорії",
                "action_required": "set_jwt_token",
                "intent": intent,
            }

        # Простий парсинг даних з запиту (в реальному проекті тут буде GPT)
        category_data = self._parse_category_data_from_query(user_query)

        if not category_data:
            return {
                "success": False,
                "message": "Не вдалося визначити дані для категорії",
                "required_fields": ["name", "slug"],
                "intent": intent,
            }

        # Створюємо категорію
        response = self.create_category(category_data)

        return {
            "success": response.success,
            "message": response.message or response.error,
            "data": response.data,
            "status_code": response.status_code,
            "intent": intent,
            "action_performed": "create_category",
        }

    def _handle_category_retrieval(self, user_query: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Обробляє отримання категорій"""
        # Отримуємо всі категорії
        response = self.get_categories()

        return {
            "success": response.success,
            "message": response.message or response.error,
            "data": response.data,
            "status_code": response.status_code,
            "intent": intent,
            "action_performed": "get_categories",
        }

    def _handle_category_update(self, user_query: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Обробляє оновлення категорії"""
        if not self.jwt_token:
            return {
                "success": False,
                "message": "JWT токен потрібен для оновлення категорії",
                "action_required": "set_jwt_token",
                "intent": intent,
            }

        # Парсимо дані для оновлення
        update_data = self._parse_update_data_from_query(user_query)
        category_id = self._extract_category_id_from_query(user_query)

        if not category_id:
            return {
                "success": False,
                "message": "Не вдалося визначити ID категорії для оновлення",
                "intent": intent,
            }

        # Оновлюємо категорію
        response = self.update_category(category_id, update_data)

        return {
            "success": response.success,
            "message": response.message or response.error,
            "data": response.data,
            "status_code": response.status_code,
            "intent": intent,
            "action_performed": "update_category",
        }

    def _handle_category_deletion(self, user_query: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Обробляє видалення категорії"""
        if not self.jwt_token:
            return {
                "success": False,
                "message": "JWT токен потрібен для видалення категорії",
                "action_required": "set_jwt_token",
                "intent": intent,
            }

        # Парсимо ID категорії
        category_id = self._extract_category_id_from_query(user_query)

        if not category_id:
            return {
                "success": False,
                "message": "Не вдалося визначити ID категорії для видалення",
                "intent": intent,
            }

        # Видаляємо категорію
        response = self.delete_category(category_id)

        return {
            "success": response.success,
            "message": response.message or response.error,
            "data": response.data,
            "status_code": response.status_code,
            "intent": intent,
            "action_performed": "delete_category",
        }

    def _parse_category_data_from_query(self, user_query: str) -> Optional[Dict[str, Any]]:
        """Парсить дані категорії з запиту користувача"""
        # Простий парсинг (в реальному проекті тут буде GPT)
        query_lower = user_query.lower()

        category_data = {}

        # Шукаємо назву категорії
        if "назва" in query_lower or "name" in query_lower:
            # Простий екстрактор назви
            words = user_query.split()
            for i, word in enumerate(words):
                if word.lower() in ["назва", "name"] and i + 1 < len(words):
                    category_data["name"] = words[i + 1]
                    break

        # Якщо назва не знайдена, намагаємося витягти з контексту
        if "name" not in category_data:
            # Шукаємо слова, які можуть бути назвою категорії
            potential_names = ["електроніка", "одяг", "взуття", "побутова техніка"]
            for name in potential_names:
                if name in query_lower:
                    category_data["name"] = name.title()
                    break

        # Генеруємо slug з назви
        if "name" in category_data:
            name = category_data["name"]
            slug = name.lower().replace(" ", "-").replace("ь", "").replace("ї", "i")
            category_data["slug"] = slug

        # Додаємо опис за замовчуванням
        if "name" in category_data:
            category_data["description"] = f"Категорія: {category_data['name']}"
            category_data["isActive"] = True
            category_data["sortOrder"] = 1

        return category_data if "name" in category_data and "slug" in category_data else None

    def _parse_update_data_from_query(self, user_query: str) -> Dict[str, Any]:
        """Парсить дані для оновлення з запиту користувача"""
        update_data = {}
        query_lower = user_query.lower()

        # Шукаємо поля для оновлення
        if "назва" in query_lower or "name" in query_lower:
            words = user_query.split()
            for i, word in enumerate(words):
                if word.lower() in ["назва", "name"] and i + 1 < len(words):
                    update_data["name"] = words[i + 1]
                    break

        if "опис" in query_lower or "description" in query_lower:
            words = user_query.split()
            for i, word in enumerate(words):
                if word.lower() in ["опис", "description"] and i + 1 < len(words):
                    update_data["description"] = words[i + 1]
                    break

        if "активна" in query_lower or "active" in query_lower:
            update_data["isActive"] = True
        elif "неактивна" in query_lower or "inactive" in query_lower:
            update_data["isActive"] = False

        return update_data

    def _extract_category_id_from_query(self, user_query: str) -> Optional[str]:
        """Витягує ID категорії з запиту користувача"""
        # Простий екстрактор ID (в реальному проекті тут буде GPT)
        words = user_query.split()

        for word in words:
            # Шукаємо UUID або числові ID
            if len(word) > 10 and "-" in word:  # UUID формат
                return word
            elif word.isdigit():  # Числовий ID
                return word

        return None

    def get_api_info(self) -> Dict[str, Any]:
        """Отримує інформацію про API"""
        return self.prompt_manager.get_api_info()

    def get_prompts_info(self) -> Dict[str, Any]:
        """Отримує інформацію про промпти"""
        return self.prompt_manager.get_categories_info()

    def validate_prompts(self) -> List[str]:
        """Валідує промпти"""
        return self.prompt_manager.validate_prompts()

    def export_prompts(self, output_file: str = "clickone_prompts_export.yaml") -> bool:
        """Експортує промпти"""
        return self.prompt_manager.export_prompts(output_file)

    def get_validation_rules(self, entity_type: str = "category") -> str:
        """Отримує правила валідації для сутності за допомогою AI"""
        return self.ai_error_handler.get_validation_rules("/api/categories", entity_type)

    def retry_with_ai_fix(self, original_response: ClickoneAPIResponse) -> ClickoneAPIResponse:
        """
        Спроба повторного виконання з виправленням від AI

        Args:
            original_response: Початкова відповідь з помилкою

        Returns:
            Нова спроба з виправленими даними
        """
        if original_response.success or "ai_fix" not in (original_response.data or {}):
            return original_response

        ai_fix_data = original_response.data["ai_fix"]
        fixed_data = ai_fix_data.get("fixed_data", {})

        if not fixed_data:
            print("⚠️ AI не зміг запропонувати виправлення")
            return original_response

        print(f"🔄 Спроба повторного виконання з виправленням від AI...")
        print(f"📝 Виправлені дані: {fixed_data}")

        # Отримуємо оригінальні дані з помилки
        original_data = ai_fix_data.get("input_data", {})

        # Замінюємо тільки виправлені поля
        retry_data = {**original_data, **fixed_data}

        # Визначаємо метод та ендпоінт на основі оригінального запиту
        # Це спрощена логіка - в реальному проекті потрібно зберігати більше контексту
        if "create" in str(original_response.error).lower():
            return self.create_category(retry_data)
        elif "update" in str(original_response.error).lower():
            # Потрібно знати ID для оновлення
            print("⚠️ Для оновлення потрібен ID категорії")
            return original_response
        else:
            print("⚠️ Невідомий тип операції для повторної спроби")
            return original_response

    def get_ai_error_analysis(self, error_message: str, input_data: Dict[str, Any]) -> str:
        """
        Отримує аналіз помилки від AI

        Args:
            error_message: Повідомлення про помилку
            input_data: Вхідні дані, які викликали помилку

        Returns:
            Аналіз помилки українською мовою
        """
        api_error = APIError(
            error_message=error_message,
            status_code=400,  # Приблизний код помилки
            endpoint="/api/categories",
            method="POST",
            input_data=input_data,
        )

        ai_fix = self.ai_error_handler.analyze_api_error(api_error)
        return self.ai_error_handler.get_user_friendly_message(api_error, ai_fix)


# Глобальний екземпляр агента
clickone_shop_agent = ClickoneShopAgent()


def get_clickone_shop_agent() -> ClickoneShopAgent:
    """Отримує глобальний екземпляр агента"""
    return clickone_shop_agent
