"""
Інтерактивний API агент з діалогом для виправлення помилок сервера.
"""

import hashlib
import json
import logging
import os
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

# Імпортуємо модулі
try:
    from .enhanced_swagger_parser import EnhancedSwaggerParser
    from .prompt_templates import PromptTemplates
    from .rag_engine import RAGEngine
except ImportError:
    try:
        from enhanced_swagger_parser import EnhancedSwaggerParser
        from prompt_templates import PromptTemplates
        from rag_engine import RAGEngine
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
            self.base_url = self.parser.get_base_url()
            self.api_info = self.parser.get_api_info()

            # Налаштування
            self.enable_api_calls = enable_api_calls
            self.model = os.getenv("OPENAI_MODEL", "gpt-4")
            self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0"))

            # Ініціалізуємо LangChain LLM
            self.llm = ChatOpenAI(
                model=self.model, temperature=self.temperature, openai_api_key=self.openai_api_key
            )

            # Ініціалізуємо RAG engine
            self._initialize_rag()

            # Ініціалізуємо збереження історії
            self.conversation_history = InteractiveConversationHistory()

            logging.info(f"Ініціалізовано інтерактивний агент з базовим URL: {self.base_url}")

        except Exception as e:
            logging.error(f"Помилка ініціалізації інтерактивного агента: {e}")
            raise

    def _initialize_rag(self):
        """Ініціалізація RAG engine з покращеним парсером."""
        try:
            self.rag_engine = RAGEngine(self.parser.swagger_spec_path)
            logging.info("RAG engine ініціалізовано успішно")
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
            if self._is_creation_request(user_query):
                return self._handle_creation_request(user_query, user_id)

            # Отримуємо контекст попередніх взаємодій
            context = self.conversation_history.get_recent_context(user_id)

            # Аналізуємо намір користувача
            intent = self._analyze_user_intent(user_query, context)
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

            # Виконуємо API виклик
            api_response = self._call_api(api_request)

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

            # Повторно виконуємо API виклик
            api_response = self._call_api(updated_api_request)

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

        if "error" in api_response:
            return True

        status_code = api_response.get("status_code", 200)
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
            system_prompt = f"""
            Ти - експерт з API. Аналізуй запит користувача та визначай:
            1. Тип операції (GET, POST, PUT, DELETE)
            2. Ресурс або endpoint
            3. Параметри та дані
            4. Мета або ціль запиту

            Контекст попередніх взаємодій:
            {context}

            Відповідай у форматі JSON:
            {{
                "operation": "GET|POST|PUT|DELETE",
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
            best_endpoint = self._find_best_endpoint(intent, endpoints)
            if not best_endpoint:
                return None

            # Отримуємо детальну інформацію про endpoint
            endpoint_info = self._get_endpoint_details(best_endpoint)

            # Валідуємо та формуємо запит
            request_data = self._validate_and_form_request(intent, endpoint_info)
            if not request_data:
                return None

            return {
                "url": f"{self.base_url}{endpoint_info['path']}",
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
        """Знаходить найкращий endpoint для запиту."""
        target_method = intent.get("operation", "").upper()
        target_resource = intent.get("resource", "").lower()

        best_score = 0
        best_endpoint = None

        for endpoint in endpoints:
            metadata = endpoint.get("metadata", {})
            method = metadata.get("method", "").upper()
            path = metadata.get("path", "").lower()
            summary = metadata.get("summary", "").lower()

            score = 0

            # Співпадіння методу
            if method == target_method:
                score += 3

            # Співпадіння ресурсу в шляху
            if target_resource in path:
                score += 2

            # Співпадіння в описі
            if target_resource in summary:
                score += 1

            if score > best_score:
                best_score = score
                best_endpoint = endpoint

        return best_endpoint

    def _get_endpoint_details(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Отримує детальну інформацію про endpoint."""
        metadata = endpoint.get("metadata", {})

        # Знаходимо повну інформацію про endpoint
        for ep in self.parser.get_endpoints():
            if ep.method == metadata.get("method") and ep.path == metadata.get("path"):
                return {
                    "method": ep.method,
                    "path": ep.path,
                    "summary": ep.summary,
                    "description": ep.description,
                    "parameters": ep.parameters,
                    "request_body": ep.request_body,
                    "required_parameters": ep.required_parameters,
                    "optional_parameters": ep.optional_parameters,
                    "path_variables": ep.path_variables,
                    "query_parameters": ep.query_parameters,
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

            # Request body
            if endpoint_info.get("request_body") and intent_data:
                request_data["data"] = intent_data

            return {"data": request_data.get("data"), "params": params}

        except Exception as e:
            logging.error(f"Помилка валідації запиту: {e}")
            return None

    def _get_headers(self) -> Dict[str, str]:
        """Формує заголовки для запиту."""
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        if self.jwt_token:
            headers["Authorization"] = f"Bearer {self.jwt_token}"

        return headers

    def _call_api(self, api_request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Виконує API виклик з обробкою помилок."""
        try:
            timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))

            response = requests.request(
                method=api_request["method"],
                url=api_request["url"],
                headers=api_request["headers"],
                params=api_request.get("params"),
                json=api_request.get("data"),
                timeout=timeout,
            )

            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "data": response.json() if response.content else None,
                "text": response.text,
            }

        except requests.exceptions.Timeout:
            return {"error": "Таймаут запиту", "details": "Сервер не відповідає протягом 30 секунд"}
        except requests.exceptions.ConnectionError:
            return {"error": "Помилка з'єднання", "details": "Не вдалося підключитися до сервера"}
        except Exception as e:
            return {"error": str(e), "details": "Невідома помилка при виконанні запиту"}

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
            processing_prompt = PromptTemplates.get_api_response_processing_prompt(
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
            creation_prompt = PromptTemplates.get_object_creation_prompt(
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
{json.dumps(response, ensure_ascii=False, indent=2)}
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
        creation_keywords = [
            "створи",
            "create",
            "додай",
            "add",
            "новий",
            "new",
            "категорію",
            "category",
            "товар",
            "product",
            "користувача",
            "user",
        ]
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

            for endpoint in all_endpoints:
                method = endpoint.get("method", "").upper()
                path = endpoint.get("path", "").lower()

                # Перевіряємо чи це POST endpoint для створення
                if method == "POST":
                    if object_type == "category" and "category" in path:
                        return endpoint
                    elif object_type == "product" and ("product" in path or "item" in path):
                        return endpoint
                    elif object_type == "user" and "user" in path:
                        return endpoint

            # Якщо не знайдено специфічний endpoint, шукаємо загальний
            for endpoint in all_endpoints:
                method = endpoint.get("method", "").upper()
                if method == "POST":
                    return endpoint

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
{json.dumps(api_response, ensure_ascii=False, indent=2)}
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
            "methods": list(set(ep.method for ep in endpoints)),
            "tags": list(set(tag for ep in endpoints for tag in ep.tags)),
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
