"""
Інтерактивний API агент з діалогом для виправлення помилок сервера.
"""

import hashlib
import json
import logging
import os
import pickle
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

# Налаштовуємо logger
logger = logging.getLogger(__name__)

# Імпортуємо модулі
try:
    from .enhanced_prompt_manager import EnhancedPromptManager
    from .enhanced_swagger_parser import EnhancedSwaggerParser
    from .rag_engine import PostgresRAGEngine
except ImportError:
    try:
        from enhanced_prompt_manager import EnhancedPromptManager
        from enhanced_swagger_parser import EnhancedSwaggerParser
        from rag_engine import PostgresRAGEngine
    except ImportError as e:
        print(f"❌ Помилка імпорту: {e}")
        raise

try:
    from langchain.schema import HumanMessage, SystemMessage
    from langchain_openai import ChatOpenAI
except ImportError:
    logging.error("LangChain не встановлено. Встановіть: pip install langchain langchain-openai")
    raise


class InteractiveConversationHistory:
    """Клас для збереження інтерактивної історії розмови."""

    def __init__(self, storage_dir: str = "./interactive_conversation_history"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

    def _get_user_file(self, user_id: str) -> Path:
        """Отримує файл для збереження історії користувача."""
        return self.storage_dir / f"{user_id}.pkl"

    def save_conversation(self, user_id: str, conversation: List[Dict[str, Any]]):
        """Зберігає інтерактивну історію розмови."""
        file_path = self._get_user_file(user_id)
        with open(file_path, "wb") as f:
            pickle.dump(conversation, f)

    def load_conversation(self, user_id: str) -> List[Dict[str, Any]]:
        """Завантажує інтерактивну історію розмови."""
        file_path = self._get_user_file(user_id)
        if file_path.exists():
            with open(file_path, "rb") as f:
                return pickle.load(f)
        return []

    def add_interaction(self, user_id: str, interaction: Dict[str, Any]):
        """Додає нову взаємодію до історії."""
        conversation = self.load_conversation(user_id)
        interaction["timestamp"] = datetime.now()
        conversation.append(interaction)

        # Обмежуємо історію до останніх 20 взаємодій
        if len(conversation) > 20:
            conversation = conversation[-20:]

        self.save_conversation(user_id, conversation)

    def get_recent_context(self, user_id: str, max_interactions: int = 3) -> str:
        """Отримує контекст останніх взаємодій."""
        conversation = self.load_conversation(user_id)
        if not conversation:
            return ""

        recent = conversation[-max_interactions:]
        context_parts = []

        for interaction in recent:
            timestamp = interaction.get("timestamp", datetime.now()).strftime("%H:%M")
            user_msg = interaction.get("user_message", "")
            bot_msg = interaction.get("bot_response", "")
            status = interaction.get("status", "unknown")

            context_parts.append(f"Користувач ({timestamp}): {user_msg}")
            context_parts.append(f"Бот ({timestamp}) [{status}]: {bot_msg}")

        return "\n".join(context_parts)


class InteractiveSwaggerAgent:
    """
    Інтерактивний агент для роботи з Swagger/OpenAPI специфікаціями.
    Підтримує діалог для виправлення помилок сервера.
    """

    def __init__(
        self,
        swagger_spec_path: str,
        enable_api_calls: bool = False,
        openai_api_key: Optional[str] = None,
        jwt_token: Optional[str] = None,
        base_url_override: Optional[str] = None,
        user_id: Optional[str] = None,
        swagger_spec_id: Optional[str] = None,
    ):
        """
        Ініціалізація інтерактивного агента.

        Args:
            swagger_spec_path: Шлях до Swagger/OpenAPI файлу
            enable_api_calls: Чи дозволити реальні API виклики
            openai_api_key: OpenAI API ключ (опціонально)
            jwt_token: JWT токен для авторизації (опціонально)
        """
        try:
            # Перевіряємо наявність файлу
            if not os.path.exists(swagger_spec_path):
                raise FileNotFoundError(f"Swagger файл не знайдено: {swagger_spec_path}")

            # Отримуємо API ключ
            self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
            if not self.openai_api_key:
                raise ValueError(
                    "OPENAI_API_KEY не знайдено. Додайте в .env файл або передайте як параметр."
                )

            # Отримуємо JWT токен
            self.jwt_token = jwt_token or os.getenv("JWT_TOKEN")

            # Парсимо Swagger специфікацію
            self.parser = EnhancedSwaggerParser(swagger_spec_path)
            self.base_url = base_url_override or self.parser.get_base_url()
            self.api_info = self.parser.get_api_info()

            # Налаштування
            self.enable_api_calls = enable_api_calls
            self.user_id = user_id
            self.swagger_spec_id = swagger_spec_id
            self.model = os.getenv("OPENAI_MODEL", "gpt-4")
            self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0"))

            # Ініціалізуємо LangChain LLM
            self.llm = ChatOpenAI(
                model=self.model, temperature=self.temperature, openai_api_key=self.openai_api_key
            )

            # Ініціалізуємо RAG engine
            self._initialize_rag()

            # Ініціалізуємо менеджер промптів
            self.prompt_manager = EnhancedPromptManager()

            # Ініціалізуємо збереження історії
            self.conversation_history = InteractiveConversationHistory()

            logging.info(f"Ініціалізовано інтерактивний агент з базовим URL: {self.base_url}")

        except Exception as e:
            logging.error(f"Помилка ініціалізації інтерактивного агента: {e}")
            raise

    def _initialize_rag(self):
        """Ініціалізація RAG engine з покращеним парсером."""
        try:
            # Використовуємо PostgresRAGEngine з правильними ID
            user_id = getattr(self, "user_id", "default_user")
            swagger_spec_id = getattr(self, "swagger_spec_id", "default_spec")

            self.rag_engine = PostgresRAGEngine(user_id=user_id, swagger_spec_id=swagger_spec_id)

            logging.info(
                f"RAG engine ініціалізовано для user_id={user_id}, swagger_spec_id={swagger_spec_id}"
            )
        except Exception as e:
            logging.error(f"Помилка ініціалізації RAG: {e}")
            raise

    def _generate_user_id(self, user_identifier: str) -> str:
        """Генерує унікальний ID користувача."""
        return hashlib.md5(user_identifier.encode()).hexdigest()

    def process_interactive_query(
        self, user_query: str, user_identifier: str = "default_user"
    ) -> Dict[str, Any]:
        """
        Обробка інтерактивного запиту з підтримкою діалогу.

        Args:
            user_query: Запит користувача
            user_identifier: Ідентифікатор користувача

        Returns:
            Словник з відповіддю та статусом
        """
        try:
            if not user_query.strip():
                return {
                    "response": "Будь ласка, введіть запит.",
                    "status": "error",
                    "needs_followup": False,
                }

            user_id = self._generate_user_id(user_identifier)
            logging.info(f"Обробка інтерактивного запиту для користувача {user_id}: {user_query}")

            # Перевіряємо чи це запит на створення об'єкта
            is_creation = self._is_creation_request(user_query)
            logger.info(f"🏗️ Чи запит на створення: {is_creation}")
            if is_creation:
                logger.info("➡️ Перенаправляю на створення об'єкта")
                return self._handle_creation_request(user_query, user_id)

            # Отримуємо контекст попередніх взаємодій
            context = self.conversation_history.get_recent_context(user_id)

            # Аналізуємо намір користувача
            logger.info("🧠 Аналізую намір користувача")
            intent = self._analyze_user_intent(user_query, context)
            logger.info(f"💡 Результат аналізу наміру: {intent}")
            if not intent:
                response = self._generate_helpful_error_response(user_query)
                self.conversation_history.add_interaction(
                    user_id,
                    {
                        "user_message": user_query,
                        "bot_response": response,
                        "status": "error",
                        "needs_followup": False,
                    },
                )
                return {"response": response, "status": "error", "needs_followup": False}

            # Шукаємо відповідні endpoints
            endpoints = self.rag_engine.search_similar_endpoints(user_query)
            if not endpoints:
                response = self._generate_no_endpoint_response(user_query)
                self.conversation_history.add_interaction(
                    user_id,
                    {
                        "user_message": user_query,
                        "bot_response": response,
                        "status": "error",
                        "needs_followup": False,
                    },
                )
                return {"response": response, "status": "error", "needs_followup": False}

            logging.info(f"Знайдено {len(endpoints)} відповідних endpoints")

            # Перевіряємо чи це інформаційний запит
            if intent.get("is_informational", False) or intent.get("operation") == "INFO":
                response = self._handle_informational_request(user_query, endpoints)
                self.conversation_history.add_interaction(
                    user_id,
                    {
                        "user_message": user_query,
                        "bot_response": response,
                        "status": "informational",
                        "needs_followup": False,
                    },
                )
                return {"response": response, "status": "informational", "needs_followup": False}

            # Формуємо API запит
            api_request = self._form_api_request(user_query, intent, endpoints)
            if not api_request:
                response = self._generate_request_formation_error(user_query, intent)
                self.conversation_history.add_interaction(
                    user_id,
                    {
                        "user_message": user_query,
                        "bot_response": response,
                        "status": "error",
                        "needs_followup": False,
                    },
                )
                return {"response": response, "status": "error", "needs_followup": False}

            # Якщо API виклики вимкнені, показуємо превью
            if not self.enable_api_calls:
                response = self._format_response(api_request, preview=True)
                self.conversation_history.add_interaction(
                    user_id,
                    {
                        "user_message": user_query,
                        "bot_response": response,
                        "status": "preview",
                        "needs_followup": False,
                    },
                )
                return {"response": response, "status": "preview", "needs_followup": False}

            # Виконуємо API виклик з автоматичним retry
            logger.info(f"🚀 Готовий до виконання API запиту: {api_request}")
            api_response = self._call_api_with_retry(api_request, user_query, intent)
            logger.info(f"📬 Отримано відповідь від API: {api_response}")

            # Аналізуємо відповідь сервера
            if self._is_server_error(api_response):
                # Аналізуємо помилку та генеруємо запит на додаткову інформацію
                followup_question = self._analyze_error_and_generate_followup(
                    api_response, api_request, user_query, intent
                )

                response = self._format_response(api_request, api_response)
                response += f"\n\n{followup_question}"

                self.conversation_history.add_interaction(
                    user_id,
                    {
                        "user_message": user_query,
                        "bot_response": response,
                        "status": "needs_followup",
                        "needs_followup": True,
                        "api_request": api_request,
                        "intent": intent,
                        "server_error": api_response,
                    },
                )

                return {
                    "response": response,
                    "status": "needs_followup",
                    "needs_followup": True,
                    "api_request": api_request,
                    "intent": intent,
                    "server_error": api_response,
                }
            else:
                # Успішна відповідь
                response = self._format_response(api_request, api_response)
                self.conversation_history.add_interaction(
                    user_id,
                    {
                        "user_message": user_query,
                        "bot_response": response,
                        "status": "success",
                        "needs_followup": False,
                    },
                )

                return {"response": response, "status": "success", "needs_followup": False}

        except Exception as e:
            logging.error(f"Помилка при обробці інтерактивного запиту: {e}")
            error_response = self._generate_error_response(str(e))
            self.conversation_history.add_interaction(
                user_id,
                {
                    "user_message": user_query,
                    "bot_response": error_response,
                    "status": "error",
                    "needs_followup": False,
                },
            )
            return {"response": error_response, "status": "error", "needs_followup": False}

    def process_followup_query(
        self, user_query: str, user_identifier: str = "default_user"
    ) -> Dict[str, Any]:
        """
        Обробка додаткового запиту для виправлення помилки.

        Args:
            user_query: Додатковий запит користувача
            user_identifier: Ідентифікатор користувача

        Returns:
            Словник з відповіддю та статусом
        """
        try:
            user_id = self._generate_user_id(user_identifier)
            conversation = self.conversation_history.load_conversation(user_id)

            if not conversation:
                return {
                    "response": "Немає активного діалогу для продовження.",
                    "status": "error",
                    "needs_followup": False,
                }

            # Знаходимо останню взаємодію, яка потребує додаткової інформації
            last_interaction = None
            for interaction in reversed(conversation):
                if interaction.get("needs_followup"):
                    last_interaction = interaction
                    break

            if not last_interaction:
                return {
                    "response": "Немає активного діалогу для продовження.",
                    "status": "error",
                    "needs_followup": False,
                }

            # Отримуємо оригінальний запит та API запит
            original_query = last_interaction.get("user_message", "")
            api_request = last_interaction.get("api_request", {})
            intent = last_interaction.get("intent", {})
            server_error = last_interaction.get("server_error", {})

            # Оновлюємо intent з новою інформацією
            updated_intent = self._update_intent_with_followup(intent, user_query)

            # Оновлюємо API запит
            updated_api_request = self._update_api_request_with_followup(
                api_request, updated_intent
            )

            # Повторно виконуємо API виклик з автоматичним retry
            api_response = self._call_api_with_retry(
                updated_api_request, user_query, updated_intent
            )

            if self._is_server_error(api_response):
                # Ще одна помилка - генеруємо новий запит
                followup_question = self._analyze_error_and_generate_followup(
                    api_response, updated_api_request, user_query, updated_intent
                )

                response = self._format_response(updated_api_request, api_response)
                response += f"\n\n{followup_question}"

                self.conversation_history.add_interaction(
                    user_id,
                    {
                        "user_message": user_query,
                        "bot_response": response,
                        "status": "needs_followup",
                        "needs_followup": True,
                        "api_request": updated_api_request,
                        "intent": updated_intent,
                        "server_error": api_response,
                    },
                )

                return {
                    "response": response,
                    "status": "needs_followup",
                    "needs_followup": True,
                    "api_request": updated_api_request,
                    "intent": updated_intent,
                    "server_error": api_response,
                }
            else:
                # Успішна відповідь
                response = self._format_response(updated_api_request, api_response)
                response += "\n\n✅ Запит успішно виконано!"

                self.conversation_history.add_interaction(
                    user_id,
                    {
                        "user_message": user_query,
                        "bot_response": response,
                        "status": "success",
                        "needs_followup": False,
                    },
                )

                return {"response": response, "status": "success", "needs_followup": False}

        except Exception as e:
            logging.error(f"Помилка при обробці додаткового запиту: {e}")
            return {
                "response": f"Помилка при обробці додаткового запиту: {e}",
                "status": "error",
                "needs_followup": False,
            }

    def _is_server_error(self, api_response: Dict[str, Any]) -> bool:
        """Перевіряє чи є помилка сервера."""
        if not api_response:
            return True

        # Перевіряємо справжні server errors (не auth помилки)
        if "error" in api_response:
            return True

        status_code = api_response.get("status_code", 200)

        # 401/403 - це auth помилки, а не server errors
        # Вони повинні оброблятися окремо
        if status_code in [401, 403]:
            return True  # Але все ж таки треба показати користувачу

        return status_code >= 400

    def _analyze_error_and_generate_followup(
        self,
        api_response: Dict[str, Any],
        api_request: Dict[str, Any],
        user_query: str,
        intent: Dict[str, Any],
    ) -> str:
        """Аналізує помилку сервера та генерує запит на додаткову інформацію."""
        try:
            # Перевіряємо auth помилки спочатку
            if "auth_error" in api_response:
                auth_error = api_response.get("auth_error", "")
                auth_details = api_response.get("auth_details", "")
                return f"🔐 Помилка авторизації: {auth_error}\n\n{auth_details}\n\n💡 Додайте JWT токен для доступу до API."

            # Потім перевіряємо загальні помилки
            error_message = api_response.get("error", "")
            error_details = api_response.get("details", "")

            # Аналізуємо тип помилки
            if "validation" in error_message.lower() or "required" in error_message.lower():
                return self._generate_validation_followup(api_request, intent, error_message)
            elif "unauthorized" in error_message.lower() or "401" in str(
                api_response.get("status_code")
            ):
                return "🔐 Помилка авторизації. Перевірте ваш JWT токен."
            elif "not found" in error_message.lower() or "404" in str(
                api_response.get("status_code")
            ):
                return "🔍 Ресурс не знайдено. Перевірте правильність ID або шляху."
            elif "conflict" in error_message.lower() or "409" in str(
                api_response.get("status_code")
            ):
                return "⚠️ Конфлікт даних. Можливо, запис вже існує."
            else:
                return f"❓ Сервер повернув помилку: {error_message}\n\n💡 Спробуйте уточнити ваш запит або перевірте правильність даних."

        except Exception as e:
            logging.error(f"Помилка аналізу помилки: {e}")
            return "❓ Виникла невідома помилка. Спробуйте уточнити ваш запит."

    def _generate_validation_followup(
        self, api_request: Dict[str, Any], intent: Dict[str, Any], error_message: str
    ) -> str:
        """Генерує запит на додаткову інформацію для валідаційних помилок."""
        try:
            endpoint_info = api_request.get("endpoint_info", {})
            required_fields = endpoint_info.get("required_parameters", [])

            if required_fields:
                fields_text = ", ".join(required_fields)
                return f"""
❌ Помилка валідації: {error_message}

📋 Для успішного виконання запиту потрібно вказати:
• {fields_text}

💡 Будь ласка, надайте недостатню інформацію. Наприклад:
• "Додай назву категорії: Електроніка"
• "Вкажи опис: Категорія для електронних пристроїв"
                """
            else:
                return f"""
❌ Помилка валідації: {error_message}

💡 Будь ласка, уточніть ваш запит або надайте додаткову інформацію.
                """

        except Exception as e:
            logging.error(f"Помилка генерації followup: {e}")
            return "❓ Помилка валідації. Будь ласка, уточніть ваш запит."

    def _update_intent_with_followup(
        self, original_intent: Dict[str, Any], followup_query: str
    ) -> Dict[str, Any]:
        """Оновлює intent з новою інформацією з followup запиту."""
        try:
            # Аналізуємо followup запит
            followup_intent = self._analyze_user_intent(followup_query, "")

            if not followup_intent:
                return original_intent

            # Об'єднуємо параметри
            updated_intent = original_intent.copy()

            # Оновлюємо параметри
            if "parameters" in followup_intent:
                if "parameters" not in updated_intent:
                    updated_intent["parameters"] = {}
                updated_intent["parameters"].update(followup_intent["parameters"])

            # Оновлюємо дані
            if "data" in followup_intent:
                if "data" not in updated_intent:
                    updated_intent["data"] = {}
                updated_intent["data"].update(followup_intent["data"])

            return updated_intent

        except Exception as e:
            logging.error(f"Помилка оновлення intent: {e}")
            return original_intent

    def _update_api_request_with_followup(
        self, original_request: Dict[str, Any], updated_intent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Оновлює API запит з новою інформацією."""
        try:
            updated_request = original_request.copy()

            # Оновлюємо дані
            if "data" in updated_intent and updated_intent["data"]:
                updated_request["data"] = updated_intent["data"]

            # Оновлюємо параметри
            if "parameters" in updated_intent and updated_intent["parameters"]:
                if "params" not in updated_request:
                    updated_request["params"] = {}
                updated_request["params"].update(updated_intent["parameters"])

            return updated_request

        except Exception as e:
            logging.error(f"Помилка оновлення API запиту: {e}")
            return original_request

    def _analyze_user_intent(self, user_query: str, context: str = "") -> Optional[Dict[str, Any]]:
        """Аналізує намір користувача з урахуванням контексту."""
        try:
            # Спочатку перевіряємо чи це інформаційний запит
            query_lower = user_query.lower()
            info_keywords = [
                "покажи",
                "показати",
                "які є",
                "що можна",
                "endpoints",
                "api",
                "список endpoints",
                "доступні операції",
                "що я можу",
                "які методи",
                "документація",
            ]

            is_info_request = any(keyword in query_lower for keyword in info_keywords)

            system_prompt = f"""
            Ти - експерт з API. Аналізуй запит користувача та визначай:
            1. Чи це інформаційний запит (показати endpoints, документацію) чи операційний (виконати дію)
            2. Тип операції (GET, POST, PUT, DELETE) - тільки для операційних запитів
            3. Ресурс або endpoint
            4. Параметри та дані
            5. Мета або ціль запиту

            Контекст попередніх взаємодій:
            {context}

            ВАЖЛИВО: Якщо користувач просить показати endpoints, список операцій, або документацію - це інформаційний запит, НЕ операційний!

            Відповідай у форматі JSON:
            {{
                "is_informational": true/false,
                "operation": "GET|POST|PUT|DELETE|INFO",
                "resource": "назва ресурсу",
                "parameters": {{"param1": "value1"}},
                "data": {{"field1": "value1"}},
                "intent": "опис мети запиту"
            }}
            """

            messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_query)]

            response = self.llm.invoke(messages)

            # Парсимо JSON відповідь
            try:
                intent_data = json.loads(response.content)
                return intent_data
            except json.JSONDecodeError:
                logging.warning("Не вдалося розпарсити JSON відповідь LLM")
                return None

        except Exception as e:
            logging.error(f"Помилка аналізу наміру: {e}")
            return None

    def _form_api_request(
        self, user_query: str, intent: Dict[str, Any], endpoints: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Формує API запит з детальною валідацією."""
        try:
            # Знаходимо найкращий endpoint
            logger.info(f"🔍 Шукаю endpoint для intent: {intent}")
            best_endpoint = self._find_best_endpoint(intent, endpoints)
            logger.info(f"🎯 Знайдено endpoint: {best_endpoint}")
            if not best_endpoint:
                return None

            # Отримуємо детальну інформацію про endpoint
            endpoint_info = self._get_endpoint_details(best_endpoint)

            # Валідуємо та формуємо запит
            request_data = self._validate_and_form_request(intent, endpoint_info)
            if not request_data:
                return None

            # Використовуємо endpoint_path з результатів пошуку (вже містить повний URL)
            endpoint_url = best_endpoint.get(
                "endpoint_path", f"{self.base_url}{endpoint_info['path']}"
            )

            return {
                "url": endpoint_url,
                "method": endpoint_info["method"],
                "headers": self._get_headers(),
                "data": request_data.get("data"),
                "params": request_data.get("params"),
                "endpoint_info": endpoint_info,
            }

        except Exception as e:
            logging.error(f"Помилка формування API запиту: {e}")
            return None

    def _find_best_endpoint(
        self, intent: Dict[str, Any], endpoints: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Знаходить найкращий endpoint для запиту з покращеною логікою."""
        target_method = intent.get("operation", "").upper()
        target_resource = intent.get("resource", "").lower()
        user_intent = intent.get("intent", "").lower()

        best_score = 0
        best_endpoint = None

        logger.info(
            f"🔍 Пошук endpoint для: method={target_method}, resource={target_resource}, intent={user_intent}"
        )

        for endpoint in endpoints:
            metadata = endpoint.get("metadata", {})
            method = metadata.get("method", "").upper()
            path = metadata.get("path", "").lower()
            summary = metadata.get("summary", "").lower()

            score = 0

            # Співпадіння методу (найважливіше)
            if method == target_method:
                score += 5

            # Співпадіння ресурсу в шляху
            if target_resource in path:
                score += 3

            # Співпадіння в описі
            if target_resource in summary:
                score += 2

            # Покращена логіка для "всі" запитів
            if any(
                word in user_intent for word in ["всі", "all", "список", "показати", "отримати всі"]
            ):
                # Віддаємо перевагу endpoints без параметрів ID
                if "{id}" not in path and "{" not in path:
                    score += 4  # Бонус за відсутність параметрів
                    logger.info(f"  ✅ Бонус за відсутність параметрів: {method} {path}")
                elif "{id}" in path:
                    score -= 2  # Штраф за наявність ID параметра
                    logger.info(f"  ⚠️ Штраф за ID параметр: {method} {path}")

            # Додаткові бонуси за ключові слова в summary
            if any(word in summary for word in ["get all", "список", "всі", "отримати всі"]):
                score += 2
                logger.info(f"  ✅ Бонус за ключові слова в описі: {method} {path}")

            logger.info(f"  📊 Endpoint: {method} {path} - score: {score}")

            if score > best_score:
                best_score = score
                best_endpoint = endpoint

        if best_endpoint:
            final_method = best_endpoint.get("metadata", {}).get("method", "")
            final_path = best_endpoint.get("metadata", {}).get("path", "")
            logger.info(f"🎯 Обраний endpoint: {final_method} {final_path} (score: {best_score})")

        return best_endpoint

    def _get_endpoint_details(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Отримує детальну інформацію про endpoint."""
        metadata = endpoint.get("metadata", {})

        # Знаходимо повну інформацію про endpoint
        for ep in self.parser.get_endpoints():
            if ep["method"] == metadata.get("method") and ep["path"] == metadata.get("path"):
                return {
                    "method": ep["method"],
                    "path": ep["path"],
                    "summary": ep.get("summary", ""),
                    "description": ep.get("description", ""),
                    "parameters": ep.get("parameters", []),
                    "request_body": ep.get("request_body", {}),
                    "required_parameters": ep.get("required_parameters", []),
                    "optional_parameters": ep.get("optional_parameters", []),
                    "path_variables": ep.get("path_variables", []),
                    "query_parameters": ep.get("query_parameters", []),
                }

        return metadata

    def _validate_and_form_request(
        self, intent: Dict[str, Any], endpoint_info: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Валідує та формує запит."""
        try:
            request_data = {}
            params = {}

            # Обробляємо параметри
            intent_params = intent.get("parameters", {})
            intent_data = intent.get("data", {})

            # Path variables
            for param in endpoint_info.get("parameters", []):
                if hasattr(param, "location") and param.location == "path":
                    param_name = param.name
                    if param_name in intent_params:
                        # Замінюємо в шляху
                        path = endpoint_info["path"].replace(
                            f"{{{param_name}}}", str(intent_params[param_name])
                        )
                        endpoint_info["path"] = path

            # Query parameters
            for param in endpoint_info.get("parameters", []):
                if hasattr(param, "location") and param.location == "query":
                    param_name = param.name
                    if param_name in intent_params:
                        params[param_name] = intent_params[param_name]

            # Request body - додаємо дані для POST/PUT/PATCH запитів
            if intent_data:
                # Перевіряємо чи є request_body в endpoint_info або чи це POST/PUT/PATCH запит
                method = endpoint_info.get("method", "").upper()
                if endpoint_info.get("request_body") or method in ["POST", "PUT", "PATCH"]:
                    request_data["data"] = intent_data

            return {"data": request_data.get("data"), "params": params}

        except Exception as e:
            logging.error(f"Помилка валідації запиту: {e}")
            return None

    def _get_headers(self) -> Dict[str, str]:
        """Формує заголовки для запиту."""
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        # Отримуємо JWT токен з бази даних
        jwt_token = self._get_jwt_token_from_db()
        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"
            logger.info("🔑 Використовую JWT токен з бази даних для авторизації")
        elif self.jwt_token:
            # Fallback до внутрішнього JWT токена
            headers["Authorization"] = f"Bearer {self.jwt_token}"
            logger.info("🔑 Використовую внутрішній JWT токен для авторизації")
        else:
            # Використовуємо зовнішній API токен для викликів зовнішніх API
            external_api_token = os.getenv("EXTERNAL_API_TOKEN")
            if external_api_token:
                headers["Authorization"] = f"Bearer {external_api_token}"
                logger.info("🔑 Використовую зовнішній API токен для авторизації")
            else:
                logger.info("🌐 API роути можуть бути публічними (без авторизації)")

        return headers

    def _get_jwt_token_from_db(self) -> Optional[str]:
        """Отримує JWT токен з бази даних."""
        try:
            import os
            import sys

            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

            try:
                from api.database import SessionLocal
                from api.models import ApiToken
            except ImportError:
                return None

            db = SessionLocal()
            try:
                # Отримуємо JWT токен для цієї Swagger специфікації
                token = (
                    db.query(ApiToken)
                    .filter(
                        ApiToken.user_id == self.user_id,
                        ApiToken.swagger_spec_id == self.swagger_spec_id,
                        ApiToken.token_name == "jwt_auth",
                        ApiToken.is_active == True,
                    )
                    .first()
                )

                return token.token_value if token else None

            finally:
                db.close()

        except Exception as e:
            print(f"❌ Помилка отримання JWT токена з БД: {e}")
            return None

    def _call_api(self, api_request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Виконує API виклик з обробкою помилок."""
        try:
            timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
            start_time = time.time()

            logger.info(f"🌐 Виконую API запит: {api_request['method']} {api_request['url']}")

            response = requests.request(
                method=api_request["method"],
                url=api_request["url"],
                headers=api_request["headers"],
                params=api_request.get("params"),
                json=api_request.get("data"),
                timeout=timeout,
            )

            execution_time = int((time.time() - start_time) * 1000)  # в мілісекундах

            api_response = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "data": response.json() if response.content else None,
                "text": response.text,
            }

            logger.info(
                f"📊 API відповідь: status={response.status_code}, data={response.text[:100]}..."
            )

            # Перевіряємо помилки авторизації та додаємо деталі для кращого сповіщення
            if response.status_code == 401:
                logger.warning("🔒 Помилка авторизації (401). Можливо потрібен JWT токен.")
                api_response["auth_error"] = "Unauthorized"
                api_response["auth_details"] = "Потрібна авторизація. Перевірте JWT токен."
            elif response.status_code == 403:
                logger.warning("🚫 Доступ заборонено (403). Недостатньо прав.")
                api_response["auth_error"] = "Forbidden"
                api_response["auth_details"] = "Недостатньо прав для доступу до цього endpoint."

            # Записуємо API виклик в базу даних
            self._record_api_call(api_request, api_response, execution_time)

            return api_response

        except requests.exceptions.Timeout:
            error_response = {
                "error": "Таймаут запиту",
                "details": "Сервер не відповідає протягом 30 секунд",
            }
            self._record_api_call(api_request, error_response, 0)
            return error_response
        except requests.exceptions.ConnectionError:
            error_response = {
                "error": "Помилка з'єднання",
                "details": "Не вдалося підключитися до сервера",
            }
            self._record_api_call(api_request, error_response, 0)
            return error_response
        except UnicodeEncodeError as e:
            error_response = {
                "error": "Помилка кодування",
                "details": f"Неможливо закодувати символи: {str(e)}. Використовуйте тільки латинські символи для slug.",
                "encoding_error": True,
            }
            self._record_api_call(api_request, error_response, 0)
            return error_response
        except Exception as e:
            error_response = {"error": str(e), "details": "Невідома помилка при виконанні запиту"}
            self._record_api_call(api_request, error_response, 0)
            return error_response

    def _record_api_call(
        self, api_request: Dict[str, Any], api_response: Dict[str, Any], execution_time: int
    ):
        """Записує API виклик в базу даних."""
        try:
            # Імпортуємо необхідні модулі
            import os
            import sys

            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

            try:
                from api.database import SessionLocal
                from api.models import ApiCall
            except ImportError:
                print("⚠️ Не вдалося імпортувати модулі для запису API викликів")
                return

            import uuid
            from datetime import datetime

            # Отримуємо user_id та swagger_spec_id з контексту
            user_id = getattr(self, "user_id", "default_user")
            swagger_spec_id = getattr(self, "swagger_spec_id", None)

            if not swagger_spec_id:
                # Спробуємо отримати з URL
                url = api_request.get("url", "")
                if "api-service" in url:
                    swagger_spec_id = "api-service"

            # Створюємо запис про API виклик
            api_call = ApiCall(
                id=str(uuid.uuid4()),
                user_id=user_id,
                swagger_spec_id=swagger_spec_id or "unknown",
                endpoint_path=api_request.get("url", ""),
                method=api_request.get("method", "GET"),
                request_data=api_request,
                response_data=api_response,
                status_code=api_response.get("status_code"),
                execution_time=execution_time,
                created_at=datetime.now(),
            )

            # Зберігаємо в базу даних
            db = SessionLocal()
            try:
                db.add(api_call)
                db.commit()
                print(
                    f"✅ Записано API виклик: {api_request.get('method')} {api_request.get('url')}"
                )
            except Exception as e:
                print(f"❌ Помилка запису API виклику: {e}")
                db.rollback()
            finally:
                db.close()

        except Exception as e:
            print(f"❌ Помилка запису API виклику: {e}")

    def _call_api_with_retry(
        self, api_request: Dict[str, Any], user_query: str = "", intent: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """Виконує API виклик з автоматичним retry та GPT-виправленнями."""
        import time

        from src.config import Config

        if not Config.AUTO_RETRY_ENABLED:
            return self._call_api(api_request)

        original_request = api_request.copy()
        current_request = api_request.copy()

        for attempt in range(1, Config.MAX_RETRY_ATTEMPTS + 1):
            logger.info(
                f"🔄 Спроба {attempt}/{Config.MAX_RETRY_ATTEMPTS}: {current_request['method']} {current_request['url']}"
            )

            # Виконуємо API виклик
            api_response = self._call_api(current_request)

            # Перевіряємо чи потрібен retry
            if not self._should_retry(api_response, attempt, Config.MAX_RETRY_ATTEMPTS):
                # Успішна відповідь або максимум спроб - повертаємо результат
                if attempt > 1:
                    logger.info(f"✅ Запит успішний після {attempt} спроб")
                return api_response

            if attempt < Config.MAX_RETRY_ATTEMPTS:
                logger.warning(
                    f"🔧 Спроба {attempt} не вдалась, аналізуємо помилку для автоматичного виправлення..."
                )

                # Отримуємо GPT-виправлення
                fix_result = self._analyze_and_fix_with_gpt(
                    original_request=original_request,
                    current_request=current_request,
                    api_response=api_response,
                    user_query=user_query,
                    attempt=attempt,
                    max_attempts=Config.MAX_RETRY_ATTEMPTS,
                )

                if fix_result and fix_result.get("can_retry", False):
                    # Застосовуємо виправлення
                    current_request = fix_result.get("updated_request", current_request)
                    logger.info(
                        f"🛠️ Застосовуємо виправлення: {fix_result.get('analysis', 'Невідоме виправлення')}"
                    )

                    # Затримка перед наступною спробою
                    if Config.RETRY_DELAY_SECONDS > 0:
                        time.sleep(Config.RETRY_DELAY_SECONDS)
                else:
                    logger.warning(f"❌ GPT не може запропонувати виправлення, припиняємо retry")
                    break

        # Повертаємо останню відповідь
        logger.warning(f"⚠️ Максимум спроб ({Config.MAX_RETRY_ATTEMPTS}) вичерпано")
        return api_response

    def _should_retry(
        self, api_response: Dict[str, Any], current_attempt: int, max_attempts: int
    ) -> bool:
        """Визначає чи потрібен retry для цієї помилки."""
        from src.config import Config

        if not api_response or current_attempt >= max_attempts:
            return False

        # Перевіряємо connection errors
        if "error" in api_response:
            error_msg = api_response.get("error", "").lower()
            if Config.RETRY_ON_CONNECTION_ERRORS and "з'єднання" in error_msg:
                return True
            if Config.RETRY_ON_TIMEOUT_ERRORS and "таймаут" in error_msg:
                return True
            if "кодування" in error_msg or api_response.get("encoding_error", False):
                return True  # Retry на помилки кодування - GPT може виправити slug

        # Перевіряємо HTTP status codes
        status_code = api_response.get("status_code")
        if status_code and status_code in Config.RETRY_ON_STATUS_CODES:
            return True

        # Специфічна перевірка для 400 помилок - тільки певні випадки
        if status_code == 400:
            error_message = str(api_response.get("data", {})).lower()

            # Дозволяємо retry тільки для відомих виправних помилок
            if Config.RETRY_ON_MISSING_SLUG and "slug must be a string" in error_message:
                logger.info("🔧 Дозволено retry: відсутній slug")
                return True

            if Config.RETRY_ON_MISSING_REQUIRED_FIELDS and (
                "required" in error_message or "missing" in error_message
            ):
                logger.info("🔧 Дозволено retry: відсутні обов'язкові поля")
                return True

            # Інші 400 помилки НЕ retry
            logger.info(f"❌ 400 помилка НЕ для retry: {error_message[:100]}")
            return False

        return False

    def _analyze_and_fix_with_gpt(
        self,
        original_request: Dict[str, Any],
        current_request: Dict[str, Any],
        api_response: Dict[str, Any],
        user_query: str,
        attempt: int,
        max_attempts: int,
    ) -> Optional[Dict[str, Any]]:
        """Використовує GPT для аналізу помилки та пропозиції виправлень."""
        try:
            import json

            from src.enhanced_prompt_manager import EnhancedPromptManager

            # Отримуємо промпт для аналізу помилок з заповненими параметрами
            prompt_manager = EnhancedPromptManager()

            # Формуємо контекст для GPT
            error_info = {
                "user_query": user_query,
                "original_request": json.dumps(original_request, ensure_ascii=False),
                "current_request": json.dumps(current_request, ensure_ascii=False),
                "api_error": str(api_response.get("error", api_response.get("data", {}))),
                "status_code": api_response.get("status_code", "Unknown"),
                "retry_attempt": attempt,
                "max_retries": max_attempts,
            }

            # Вибираємо промпт залежно від типу помилки
            if api_response.get("encoding_error", False) or "кодування" in str(
                api_response.get("error", "")
            ):
                prompt_name = "encoding_error_fix"
                # Для помилок кодування потрібен спеціальний контекст
                error_info["error_details"] = api_response.get(
                    "details", str(api_response.get("error", ""))
                )
            else:
                prompt_name = "error_analysis_and_fix"

            # Отримуємо відформатований промпт
            filled_prompt = prompt_manager.get_prompt_by_name(prompt_name, **error_info)

            if not filled_prompt or "Помилка завантаження промпту" in filled_prompt:
                logger.error("❌ Не знайдено промпт для аналізу помилок")
                return None

            # Викликаємо GPT через LangChain
            messages = [HumanMessage(content=filled_prompt)]
            response = self.llm(messages)

            if not response or not response.content:
                logger.error("❌ GPT не надав відповіді для аналізу помилки")
                return None

            response_text = response.content

            # Логуємо повну відповідь GPT для дебагу
            logger.debug(f"🤖 Повна GPT відповідь: {response_text}")

            # Парсимо JSON відповідь
            import json

            try:
                # Спочатку пробуємо парсити всю відповідь як JSON
                try:
                    fix_result = json.loads(response_text.strip())
                    logger.info(f"🤖 GPT аналіз: {fix_result.get('analysis', 'Аналіз відсутній')}")
                    return fix_result
                except json.JSONDecodeError:
                    pass

                # Якщо не вдалося, витягуємо JSON блок
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    json_response = response_text[json_start:json_end]
                    logger.debug(f"📝 Витягнутий JSON: {json_response}")

                    # Пробуємо знайти правильний кінець JSON
                    import re

                    # Шукаємо перший валідний JSON об'єкт
                    brace_count = 0
                    valid_end = json_start
                    for i, char in enumerate(response_text[json_start:], json_start):
                        if char == "{":
                            brace_count += 1
                        elif char == "}":
                            brace_count -= 1
                            if brace_count == 0:
                                valid_end = i + 1
                                break

                    json_response = response_text[json_start:valid_end]
                    fix_result = json.loads(json_response)

                    logger.info(f"🤖 GPT аналіз: {fix_result.get('analysis', 'Аналіз відсутній')}")
                    return fix_result
                else:
                    logger.error("❌ Не знайдено JSON в відповіді GPT")
                    return None

            except json.JSONDecodeError as e:
                logger.error(f"❌ Помилка парсингу JSON від GPT: {e}")
                logger.debug(f"GPT відповідь: {response_text}")
                return None

        except Exception as e:
            logger.error(f"❌ Помилка GPT аналізу: {e}")
            return None

    def _format_response(
        self,
        api_request: Dict[str, Any],
        response: Optional[Dict[str, Any]] = None,
        preview: bool = False,
    ) -> str:
        """Форматує відповідь користувачу."""
        try:
            if preview:
                return self._format_preview_response(api_request)

            if not response:
                return self._generate_error_response("Немає відповіді від сервера")

            # Використовуємо новий промпт для обробки відповіді API
            return self._process_api_response_with_gpt(api_request, response)

        except Exception as e:
            logging.error(f"Помилка форматування відповіді: {e}")
            return self._generate_error_response(f"Помилка форматування: {str(e)}")

    def _process_api_response_with_gpt(
        self, api_request: Dict[str, Any], api_response: Dict[str, Any]
    ) -> str:
        """Обробляє відповідь API сервера через GPT для створення дружелюбного тексту."""
        try:
            # Отримуємо контекст запиту користувача
            user_query = self._get_last_user_query()

            # Генеруємо промпт для обробки відповіді
            processing_prompt = self.prompt_manager.get_api_response_processing_prompt(
                user_query=user_query,
                api_response=api_response,
                available_fields=self._extract_available_fields(api_response),
            )

            # Викликаємо GPT для обробки
            messages = [
                SystemMessage(content="Ти експерт з обробки даних та форматування відповідей."),
                HumanMessage(content=processing_prompt),
            ]

            llm_response = self.llm.invoke(messages)
            processed_response = llm_response.content

            # Додаємо інформацію про API запит
            api_info = f"""
🔗 **API Запит:**
• URL: {api_request.get('url', 'Невідомо')}
• Метод: {api_request.get('method', 'GET')}
• Статус: ✅ Успішно

📊 **Результат:**
{processed_response}
"""

            return api_info

        except Exception as e:
            logging.error(f"Помилка обробки відповіді через GPT: {e}")
            # Fallback до базового форматування
            return self._format_basic_response(api_request, api_response)

    def _create_object_with_auto_fill(
        self, user_query: str, endpoint_info: Dict[str, Any], user_identifier: str = "default_user"
    ) -> str:
        """Створює об'єкт з автоматичним заповненням полів та обробкою помилок."""
        try:
            # Отримуємо історію розмови
            conversation_history = self.conversation_history.load_conversation(user_identifier)

            # Генеруємо промпт для створення об'єкта
            creation_prompt = self.prompt_manager.get_object_creation_prompt(
                user_query=user_query,
                endpoint_info=endpoint_info,
                conversation_history=conversation_history,
            )

            # Викликаємо GPT для створення об'єкта
            messages = [
                SystemMessage(
                    content="Ти експерт з створення об'єктів через API та автоматичного заповнення полів."
                ),
                HumanMessage(content=creation_prompt),
            ]

            llm_response = self.llm.invoke(messages)
            creation_response = llm_response.content

            # Парсимо відповідь GPT для отримання даних об'єкта
            object_data = self._parse_object_creation_response(creation_response)

            if object_data:
                # Формуємо API запит для створення
                api_request = self._form_creation_request(endpoint_info, object_data)

                # Виконуємо запит
                response = self._call_api(api_request)

                if response and not self._is_server_error(response):
                    # Успішне створення
                    # Серіалізуємо відповідь з обробкою datetime
                    try:
                        response_json = self._serialize_response(response)
                    except Exception:
                        response_json = str(response)

                    success_message = f"""
✅ **Об'єкт успішно створено!**

📋 **Деталі створення:**
{creation_response}

🔗 **API Запит:**
• URL: {api_request.get('url', 'Невідомо')}
• Метод: {api_request.get('method', 'POST')}
• Статус: ✅ Успішно

📊 **Відповідь сервера:**
```json
{response_json}
```
"""
                    return success_message
                else:
                    # Помилка при створенні
                    return self._handle_creation_error(response, creation_response, user_query)
            else:
                return f"""
❌ **Помилка аналізу запиту:**
Не вдалося зрозуміти, який об'єкт потрібно створити.

💡 **Приклади правильних запитів:**
• "Створи товар з назвою Телефон"
• "Створи категорію Електроніка"
• "Створи користувача Іван Петренко"

🔄 Спробуйте переформулювати запит.
"""

        except Exception as e:
            logging.error(f"Помилка створення об'єкта: {e}")
            return f"""
❌ **Помилка створення об'єкта:**
{str(e)}

🔄 Спробуйте ще раз або зверніться до адміністратора.
"""

    def _parse_object_creation_response(self, gpt_response: str) -> Optional[Dict[str, Any]]:
        """Парсить відповідь GPT для отримання даних об'єкта."""
        try:
            # Шукаємо JSON блок в відповіді GPT
            import re

            json_match = re.search(r"\{[^{}]*\}", gpt_response, re.DOTALL)

            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)

            # Якщо JSON не знайдено, спробуємо витягти дані з тексту
            return self._extract_data_from_text(gpt_response)

        except Exception as e:
            logging.error(f"Помилка парсингу відповіді GPT: {e}")
            return None

    def _extract_data_from_text(self, text: str) -> Dict[str, Any]:
        """Витягує дані з текстової відповіді GPT."""
        data = {}

        # Шукаємо пари ключ-значення
        import re

        patterns = [
            r'"name":\s*"([^"]+)"',
            r'"description":\s*"([^"]+)"',
            r'"price":\s*([\d.]+)',
            r'"category":\s*"([^"]+)"',
            r'"email":\s*"([^"]+)"',
            r'"status":\s*"([^"]+)"',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                key = pattern.split('"')[1]
                value = match.group(1)
                data[key] = value

        return data

    def _form_creation_request(
        self, endpoint_info: Dict[str, Any], object_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Формує API запит для створення об'єкта."""
        return {
            "url": endpoint_info.get("url", ""),
            "method": "POST",
            "headers": self._get_headers(),
            "data": object_data,
            "endpoint_info": endpoint_info,
        }

    def _handle_creation_error(
        self, response: Dict[str, Any], creation_response: str, user_query: str
    ) -> str:
        """Обробляє помилки при створенні об'єкта."""
        error_message = response.get("error", "Невідома помилка")

        # Аналізуємо тип помилки
        if "validation" in error_message.lower() or "required" in error_message.lower():
            return f"""
❌ **Помилка валідації при створенні:**
{error_message}

💡 **Запропоновані дані:**
{creation_response}

🔄 **Рішення:**
Будь ласка, уточніть необхідні поля або спробуйте ще раз.
"""
        elif "authorization" in error_message.lower() or "token" in error_message.lower():
            return f"""
❌ **Помилка авторизації:**
{error_message}

🔐 **Рішення:**
Перевірте налаштування токену або зверніться до адміністратора.
"""
        elif "not found" in error_message.lower():
            return f"""
❌ **Ресурс не знайдено:**
{error_message}

💡 **Рішення:**
Перевірте правильність URL або зверніться до адміністратора.
"""
        else:
            return f"""
❌ **Помилка створення об'єкта:**
{error_message}

💡 **Запропоновані дані:**
{creation_response}

🔄 **Рішення:**
Спробуйте ще раз або зверніться до адміністратора.
"""

    def _get_last_user_query(self) -> str:
        """Отримує останній запит користувача з контексту."""
        # Тут можна реалізувати логіку отримання останнього запиту
        # Наразі повертаємо базовий запит
        return "Покажи результати запиту"

    def _is_creation_request(self, user_query: str) -> bool:
        """Визначає чи є запит на створення об'єкта."""
        query_lower = user_query.lower()

        # Перевіряємо чи це запит на перегляд/показ/отримання
        view_keywords = [
            "покажи",
            "показати",
            "отримати",
            "список",
            "всі",
            "show",
            "get",
            "list",
            "view",
            "як отримати",
            "як отримати список",
            "endpoints для",
            "endpoints",
        ]
        if any(keyword in query_lower for keyword in view_keywords):
            return False

        # Тільки якщо є експліцитні дії створення
        creation_keywords = ["створи", "create", "додай", "add", "новий", "new"]
        return any(keyword in query_lower for keyword in creation_keywords)

    def _handle_creation_request(self, user_query: str, user_id: str) -> Dict[str, Any]:
        """Обробляє запит на створення об'єкта."""
        try:
            # Визначаємо тип об'єкта для створення
            object_type = self._determine_creation_type(user_query)

            # Знаходимо відповідний endpoint для створення
            endpoint_info = self._find_creation_endpoint(object_type)

            if not endpoint_info:
                response = f"""
❌ **Помилка: Не знайдено endpoint для створення {object_type}**

💡 **Доступні типи об'єктів:**
• Товари (products)
• Категорії (categories)
• Користувачі (users)

🔄 Спробуйте переформулювати запит.
"""
                return {"success": False, "response": response, "status": "no_creation_endpoint"}

            # Створюємо об'єкт з автоматичним заповненням
            creation_response = self._create_object_with_auto_fill(
                user_query, endpoint_info, user_id
            )

            # Зберігаємо взаємодію
            self.conversation_history.add_interaction(
                user_id,
                {
                    "user_message": user_query,
                    "bot_response": creation_response,
                    "status": "creation_processed",
                },
            )

            return {"success": True, "response": creation_response, "status": "creation_processed"}

        except Exception as e:
            logging.error(f"Помилка обробки запиту створення: {e}")
            return {
                "success": False,
                "response": self._generate_error_response(str(e)),
                "status": "creation_error",
            }

    def _determine_creation_type(self, user_query: str) -> str:
        """Визначає тип об'єкта для створення."""
        query_lower = user_query.lower()

        if any(word in query_lower for word in ["категорію", "category"]):
            return "category"
        elif any(word in query_lower for word in ["товар", "product", "продукт"]):
            return "product"
        elif any(word in query_lower for word in ["користувача", "user"]):
            return "user"
        else:
            # За замовчуванням вважаємо товаром
            return "product"

    def _find_creation_endpoint(self, object_type: str) -> Optional[Dict[str, Any]]:
        """Знаходить endpoint для створення об'єкта."""
        try:
            # Шукаємо POST endpoints для створення
            all_endpoints = self.rag_engine.get_all_endpoints()
            logging.info(f"Знайдено {len(all_endpoints)} endpoints для пошуку {object_type}")

            for endpoint in all_endpoints:
                metadata = endpoint.get("metadata", {})
                method = metadata.get("method", "").upper()
                path = metadata.get("path", "").lower()

                logging.info(f"Перевіряю endpoint: {method} {path} для {object_type}")

                # Перевіряємо чи це POST endpoint для створення
                if method == "POST":
                    if object_type == "category" and "category" in path:
                        logging.info(f"Знайдено endpoint для category: {method} {path}")
                        return endpoint
                    elif object_type == "product" and ("product" in path or "item" in path):
                        logging.info(f"Знайдено endpoint для product: {method} {path}")
                        return endpoint
                    elif object_type == "user" and "user" in path:
                        logging.info(f"Знайдено endpoint для user: {method} {path}")
                        return endpoint

            # Якщо не знайдено специфічний endpoint, шукаємо загальний
            for endpoint in all_endpoints:
                metadata = endpoint.get("metadata", {})
                method = metadata.get("method", "").upper()
                if method == "POST":
                    path = metadata.get("path", "").lower()
                    logging.info(f"Використовую загальний POST endpoint: {method} {path}")
                    return endpoint

            logging.warning(f"Не знайдено POST endpoint для створення {object_type}")
            return None

        except Exception as e:
            logging.error(f"Помилка пошуку endpoint для створення: {e}")
            return None

    def _extract_available_fields(self, api_response: Dict[str, Any]) -> List[str]:
        """Витягує доступні поля з відповіді API."""
        fields = set()

        def extract_fields_from_obj(obj, prefix=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    field_name = f"{prefix}.{key}" if prefix else key
                    fields.add(field_name)
                    if isinstance(value, (dict, list)):
                        extract_fields_from_obj(value, field_name)
            elif isinstance(obj, list) and obj:
                extract_fields_from_obj(obj[0], prefix)

        extract_fields_from_obj(api_response)
        return list(fields)

    def _format_basic_response(
        self, api_request: Dict[str, Any], api_response: Dict[str, Any]
    ) -> str:
        """Базове форматування відповіді (fallback)."""
        return f"""
🔗 **API Запит:**
• URL: {api_request.get('url', 'Невідомо')}
• Метод: {api_request.get('method', 'GET')}
• Статус: ✅ Успішно

📊 **Відповідь сервера:**
```json
{self._serialize_response(api_response)}
```
"""

    def _format_preview_response(self, api_request: Dict[str, Any]) -> str:
        """Форматує попередній перегляд запиту."""
        return f"""
🔍 **Попередній перегляд запиту:**
• URL: {api_request.get('url', 'Невідомо')}
• Метод: {api_request.get('method', 'GET')}
• Параметри: {api_request.get('params', {})}
• Дані: {api_request.get('data', {})}

💡 Це попередній перегляд. Запит ще не виконано.
"""

    def _generate_helpful_error_response(self, user_query: str) -> str:
        """Генерує корисну відповідь при незрозумілому запиті."""
        return f"""
🤔 Не вдалося зрозуміти ваш запит: "{user_query}"

💡 Спробуйте переформулювати запит, наприклад:
• "Покажи всі товари"
• "Створи новий товар з назвою 'Тест'"
• "Отримай товар з ID 123"
• "Онови товар 456 - зміни ціну на 1000"

📚 Доступні операції:
• GET - отримання даних
• POST - створення нових записів
• PUT - оновлення існуючих записів
• DELETE - видалення записів
        """

    def _generate_no_endpoint_response(self, user_query: str) -> str:
        """Генерує відповідь коли не знайдено endpoint."""
        return f"""
🔍 На жаль, не знайшов відповідного API endpoint для запиту: "{user_query}"

💡 Можливі причини:
• Неправильна назва ресурсу
• Непідтримувана операція
• Відсутній endpoint для цієї функціональності

📋 Доступні ресурси:
• Товари (products)
• Категорії (categories)
• Користувачі (users)
• Замовлення (orders)

🔄 Спробуйте інший запит або перевірте правильність назви ресурсу.
        """

    def _generate_request_formation_error(self, user_query: str, intent: Dict[str, Any]) -> str:
        """Генерує відповідь при помилці формування запиту."""
        return f"""
⚠️ Не вдалося сформувати API запит для: "{user_query}"

🔍 Аналіз наміру:
• Операція: {intent.get('operation', 'Невідомо')}
• Ресурс: {intent.get('resource', 'Невідомо')}
• Параметри: {intent.get('parameters', {})}

💡 Можливі причини:
• Відсутні обов'язкові параметри
• Неправильний формат даних
• Непідтримувана комбінація параметрів

🛠️ Спробуйте:
• Додати відсутні параметри
• Перевірити формат даних
• Використати інший endpoint
        """

    def _generate_error_response(self, error_message: str) -> str:
        """Генерує відповідь при загальній помилці."""
        return f"""
❌ Виникла помилка при обробці запиту: {error_message}

🔧 Що можна спробувати:
• Перевірити підключення до інтернету
• Перезавантажити сторінку
• Спробувати інший запит
• Звернутися до адміністратора

📞 Якщо проблема повторюється, збережіть цю помилку для зворотного зв'язку.
        """

    def get_available_endpoints(self) -> List[Dict[str, Any]]:
        """Отримує список доступних endpoints."""
        try:
            return self.rag_engine.get_all_endpoints()
        except Exception as e:
            logging.error(f"Помилка отримання endpoints: {e}")
            return []

    def get_api_summary(self) -> Dict[str, Any]:
        """Отримує загальну інформацію про API."""
        endpoints = self.parser.get_endpoints()
        schemas = self.parser.get_all_schemas_info()

        return {
            "api_info": self.api_info,
            "total_endpoints": len(endpoints),
            "total_schemas": len(schemas),
            "methods": list(set(ep["method"] for ep in endpoints)),
            "tags": list(set(tag for ep in endpoints for tag in ep.get("tags", []))),
            "base_url": self.base_url,
        }

    def get_conversation_history(self, user_identifier: str) -> List[Dict[str, Any]]:
        """Отримує історію розмови користувача."""
        user_id = self._generate_user_id(user_identifier)
        return self.conversation_history.load_conversation(user_id)

    def clear_conversation_history(self, user_identifier: str):
        """Очищає історію розмови користувача."""
        user_id = self._generate_user_id(user_identifier)
        file_path = self.conversation_history._get_user_file(user_id)
        if file_path.exists():
            file_path.unlink()

    def _serialize_response(self, response: Any) -> str:
        """Серіалізує відповідь з обробкою datetime об'єктів."""

        def json_serializer(obj):
            """Кастомний серіалізатор для datetime та інших об'єктів."""
            if hasattr(obj, "isoformat"):
                return obj.isoformat()
            elif hasattr(obj, "__dict__"):
                return str(obj)
            else:
                return str(obj)

        return json.dumps(response, ensure_ascii=False, indent=2, default=json_serializer)

    def _handle_informational_request(
        self, user_query: str, endpoints: List[Dict[str, Any]]
    ) -> str:
        """Обробляє інформаційні запити про endpoints та API документацію."""
        try:
            if not endpoints:
                return "❌ Не знайдено відповідних endpoints для вашого запиту."

            query_lower = user_query.lower()

            # Перевіряємо чи це запит про ВСІ endpoints
            if any(
                word in query_lower
                for word in [
                    "всі",
                    "всі доступні",
                    "all",
                    "список",
                    "покажи endpoints",
                    "доступні endpoints",
                ]
            ):
                return self._format_all_endpoints()  # Показуємо всі endpoints групами

            # Перевіряємо чи це запит про конкретний endpoint з деталями
            elif any(
                word in query_lower
                for word in ["детальна", "детально", "параметри", "як використати"]
            ):
                return self._format_detailed_endpoints(endpoints[:3])  # Показуємо детально перші 3
            else:
                return self._format_basic_endpoints(endpoints)  # Показуємо базовий список знайдених

        except Exception as e:
            logging.error(f"Помилка обробки інформаційного запиту: {e}")
            return f"❌ Помилка при обробці інформаційного запиту: {str(e)}"

    def _format_basic_endpoints(self, endpoints: List[Dict[str, Any]]) -> str:
        """Форматує базовий список endpoints."""
        response_parts = ["📚 **Доступні API Endpoints:**\n"]

        for i, endpoint in enumerate(endpoints[:10], 1):  # Показуємо перші 10
            metadata = endpoint.get("metadata", {})
            method = metadata.get("method", "GET")
            # Використовуємо full_url якщо є, інакше path
            path = metadata.get("full_url", metadata.get("path", ""))
            summary = metadata.get("summary", "")

            response_parts.append(f"**{i}. {method} {path}**")
            if summary:
                response_parts.append(f"   📝 {summary}")
            response_parts.append("")

        if len(endpoints) > 10:
            response_parts.append(f"... і ще {len(endpoints) - 10} endpoints")

        response_parts.extend(
            [
                "\n💡 **Як використати:**",
                '• Щоб виконати запит, напишіть: "Отримай всі товари" або "Створи нову категорію"',
                '• Щоб дізнатися більше про конкретний endpoint, спитайте: "Детальна інформація про GET /products"',
                '• Щоб отримати документацію з параметрами, напишіть: "Параметри для {назва endpoint}"',
            ]
        )

        return "\n".join(response_parts)

    def _format_detailed_endpoints(self, endpoints: List[Dict[str, Any]]) -> str:
        """Форматує детальну інформацію про endpoints з параметрами та прикладами."""
        response_parts = ["📖 **Детальна інформація про API Endpoints:**\n"]

        for i, endpoint in enumerate(endpoints, 1):
            # Отримуємо детальну інформацію про endpoint
            endpoint_details = self._get_endpoint_details(endpoint)

            metadata = endpoint.get("metadata", {})
            method = metadata.get("method", "GET")
            path = metadata.get("full_url", metadata.get("path", ""))
            summary = metadata.get("summary", "")

            response_parts.append(f"## {i}. {method} {path}")
            if summary:
                response_parts.append(f"**Опис:** {summary}")

            # Додаємо інформацію про параметри
            parameters_info = self._format_endpoint_parameters(endpoint_details, method, path)
            if parameters_info:
                response_parts.append(parameters_info)

            # Додаємо приклади використання
            examples = self._generate_usage_examples(endpoint_details, method, path)
            if examples:
                response_parts.append(examples)

            response_parts.append("---\n")

        return "\n".join(response_parts)

    def _format_endpoint_parameters(
        self, endpoint_details: Dict[str, Any], method: str, path: str
    ) -> str:
        """Форматує параметри endpoint'а з детальною інформацією."""
        try:
            parameters = endpoint_details.get("parameters", [])
            if not parameters:
                return ""

            params_parts = ["\n**📋 Параметри:**"]

            # Групуємо параметри за типом
            query_params = []
            path_params = []
            header_params = []

            for param in parameters:
                param_type = param.get("in", "query")
                if param_type == "query":
                    query_params.append(param)
                elif param_type == "path":
                    path_params.append(param)
                elif param_type == "header":
                    header_params.append(param)

            # Path параметри
            if path_params:
                params_parts.append("**🔗 Path параметри:**")
                for param in path_params:
                    name = param.get("name", "")
                    description = param.get("description", "")
                    required = "✅ обов'язковий" if param.get("required") else "⚪ опціональний"
                    params_parts.append(f"  • `{name}` - {description} ({required})")
                params_parts.append("")

            # Query параметри (фільтри, пагінація тощо)
            if query_params:
                params_parts.append("**🔍 Query параметри (фільтри):**")
                for param in query_params:
                    name = param.get("name", "")
                    description = param.get("description", "")
                    required = "✅ обов'язковий" if param.get("required") else "⚪ опціональний"

                    # Додаємо приклад використання з schema
                    schema = param.get("schema", {})
                    example = schema.get("example", "")
                    param_type = schema.get("type", "")

                    param_line = f"  • `{name}` ({param_type}) - {description} ({required})"
                    if example:
                        param_line += f"\n    💡 Приклад: `{name}={example}`"

                    # Додаємо enum значення якщо є
                    enum_values = schema.get("enum", [])
                    if enum_values:
                        param_line += (
                            f"\n    🎯 Допустимі значення: {', '.join(map(str, enum_values))}"
                        )

                    params_parts.append(param_line)
                params_parts.append("")

            return "\n".join(params_parts)

        except Exception as e:
            logging.error(f"Помилка форматування параметрів: {e}")
            return ""

    def _generate_usage_examples(
        self, endpoint_details: Dict[str, Any], method: str, path: str
    ) -> str:
        """Генерує приклади використання endpoint'а."""
        try:
            parameters = endpoint_details.get("parameters", [])
            examples_parts = ["\n**💡 Приклади використання:**"]

            # Базовий приклад
            base_url = path.split("?")[0]  # Видаляємо query параметри якщо є
            examples_parts.append(f"**Базовий запит:**")
            examples_parts.append(f"```")
            examples_parts.append(f"{method} {base_url}")
            examples_parts.append(f"```")

            # Приклади з параметрами
            query_params = [p for p in parameters if p.get("in") == "query"]
            if query_params:
                examples_parts.append("\n**З параметрами:**")

                # Приклад з пагінацією
                pagination_example = self._generate_pagination_example(base_url, query_params)
                if pagination_example:
                    examples_parts.append(pagination_example)

                # Приклад з фільтрами
                filter_example = self._generate_filter_example(base_url, query_params)
                if filter_example:
                    examples_parts.append(filter_example)

                # Приклад з сортуванням
                sort_example = self._generate_sort_example(base_url, query_params)
                if sort_example:
                    examples_parts.append(sort_example)

            # Розшифровка ключових фільтрів
            filter_help = self._generate_filter_help(query_params)
            if filter_help:
                examples_parts.append(filter_help)

            return "\n".join(examples_parts)

        except Exception as e:
            logging.error(f"Помилка генерації прикладів: {e}")
            return ""

    def _generate_pagination_example(self, base_url: str, query_params: List[Dict]) -> str:
        """Генерує приклад з пагінацією."""
        page_param = next((p for p in query_params if p.get("name") == "page"), None)
        limit_param = next((p for p in query_params if p.get("name") == "limit"), None)

        if page_param and limit_param:
            return f"```\n{base_url}?page=1&limit=10  # Перша сторінка, 10 записів\n```"
        return ""

    def _generate_filter_example(self, base_url: str, query_params: List[Dict]) -> str:
        """Генерує приклад з фільтрами."""
        filters_param = next((p for p in query_params if p.get("name") == "filters"), None)
        if filters_param:
            schema = filters_param.get("schema", {})
            example = schema.get("example", "")
            if example:
                return f"```\n{base_url}?filters={example}\n```"
        return ""

    def _generate_sort_example(self, base_url: str, query_params: List[Dict]) -> str:
        """Генерує приклад з сортуванням."""
        sort_by = next((p for p in query_params if p.get("name") == "sortBy"), None)
        sort_order = next((p for p in query_params if p.get("name") == "sortOrder"), None)

        if sort_by and sort_order:
            sort_by_example = sort_by.get("schema", {}).get("example", "name")
            sort_order_example = sort_order.get("schema", {}).get("example", "asc")
            return f"```\n{base_url}?sortBy={sort_by_example}&sortOrder={sort_order_example}\n```"
        return ""

    def _generate_filter_help(self, query_params: List[Dict]) -> str:
        """Генерує довідку по фільтрах."""
        filters_param = next((p for p in query_params if p.get("name") == "filters"), None)
        if not filters_param:
            return ""

        help_parts = ["\n**🔧 Довідка по фільтрах:**"]
        help_parts.append("Фільтри передаються як JSON string з операторами:")
        help_parts.append('• `{"name":{"like":"iPhone"}}` - пошук по частині назви')
        help_parts.append('• `{"price":{"gte":100,"lte":1000}}` - ціна від 100 до 1000')
        help_parts.append('• `{"status":{"eq":"active"}}` - точна відповідність')
        help_parts.append('• `{"createdAt":{"gte":"2024-01-01"}}` - дата після 1 січня 2024')

        return "\n".join(help_parts)

    def _format_all_endpoints(self) -> str:
        """Форматує всі доступні endpoints, згруповані за ресурсами."""
        try:
            # Отримуємо всі endpoints з парсера
            all_endpoints = self.parser.get_endpoints()

            if not all_endpoints:
                return "❌ Не знайдено endpoints в API."

            # Групуємо endpoints за тегами/ресурсами
            grouped_endpoints = self._group_endpoints_by_resource(all_endpoints)

            response_parts = ["📚 **Всі доступні API Endpoints:**\n"]

            # Додаємо статистику
            total_count = len(all_endpoints)
            response_parts.append(f"**📊 Загальна статистика:** {total_count} endpoints\n")

            # Показуємо по групах
            for resource, endpoints in grouped_endpoints.items():
                if not endpoints:
                    continue

                response_parts.append(f"### 🔸 {resource} ({len(endpoints)} endpoints)")

                # Показуємо endpoints в групі
                for endpoint in endpoints:
                    method = endpoint.get("method", "GET")
                    path = endpoint.get("path", "")
                    summary = endpoint.get("summary", "")
                    base_url = self.parser.get_base_url() or ""
                    full_url = f"{base_url}{path}" if base_url else path

                    endpoint_line = f"  • **{method}** `{full_url}`"
                    if summary:
                        endpoint_line += f" - {summary}"

                    response_parts.append(endpoint_line)

                response_parts.append("")  # Порожній рядок між групами

            # Додаємо корисні поради
            response_parts.extend(
                [
                    "---",
                    "💡 **Як використати:**",
                    '• Для деталей: "Детальна інформація про GET /products"',
                    '• Для виконання: "Отримай всі товари" або "Створи нову категорію"',
                    '• Для фільтрації: "Покажи endpoints для товарів"',
                    "",
                    "🔍 **Основні ресурси:**",
                    "• **Products** - управління товарами",
                    "• **Categories** - управління категоріями",
                    "• **Orders** - управління замовленнями",
                    "• **Brands** - управління брендами",
                    "• **Collections** - управління колекціями",
                ]
            )

            return "\n".join(response_parts)

        except Exception as e:
            logging.error(f"Помилка форматування всіх endpoints: {e}")
            return f"❌ Помилка при отриманні всіх endpoints: {str(e)}"

    def _group_endpoints_by_resource(
        self, endpoints: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Групує endpoints за ресурсами/тегами."""
        grouped = {}

        for endpoint in endpoints:
            # Визначаємо ресурс за тегами або шляхом
            tags = endpoint.get("tags", [])
            if tags:
                resource = tags[0]  # Беремо перший тег
            else:
                # Якщо немає тегів, визначаємо за шляхом
                path = endpoint.get("path", "")
                resource = self._extract_resource_from_path(path)

            # Нормалізуємо назву ресурсу
            resource = resource.capitalize() if resource else "Other"

            if resource not in grouped:
                grouped[resource] = []

            grouped[resource].append(endpoint)

        # Сортуємо групи за важливістю
        priority_order = [
            "Product",
            "Category",
            "Order",
            "Brand",
            "Collection",
            "Setting",
            "Family",
            "Attribute",
        ]
        sorted_grouped = {}

        # Спочатку додаємо пріоритетні групи
        for resource in priority_order:
            if resource in grouped:
                sorted_grouped[resource] = grouped[resource]

        # Потім додаємо решту
        for resource, endpoints in grouped.items():
            if resource not in sorted_grouped:
                sorted_grouped[resource] = endpoints

        return sorted_grouped

    def _extract_resource_from_path(self, path: str) -> str:
        """Визначає ресурс з шляху endpoint'а."""
        if not path:
            return "Other"

        # Видаляємо leading slash та беремо перший сегмент
        segments = path.strip("/").split("/")
        if segments:
            return segments[0]

        return "Other"
