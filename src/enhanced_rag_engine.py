"""
Розширений RAG двигун з можливістю виконання API запитів та обробки помилок.
"""

import json
import logging
import os
import sqlite3
import requests
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from langchain_openai import OpenAIEmbeddings

from src.config import Config
from src.ai_error_handler import AIErrorHandler

logger = logging.getLogger(__name__)


class EnhancedRAGEngine:
    """Розширений RAG двигун з можливістю виконання API запитів."""

    def __init__(self):
        """Ініціалізація розширеного RAG двигуна."""
        self.config = Config()
        self.db_path = os.path.join(self.config.CHROMA_DB_PATH, "swagger_api.db")
        
        # Створюємо папку, якщо не існує
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Ініціалізуємо базу даних
        self._init_database()
        
        # Ініціалізуємо embeddings
        self.embeddings = OpenAIEmbeddings()
        
        # Ініціалізуємо AI error handler
        self.error_handler = AIErrorHandler()
        
        # JWT токен та сесія
        self.jwt_token = None
        self.session = requests.Session()
        
        # Автоматично встановлюємо JWT токен з .env, якщо є
        self._auto_setup_jwt_tokens()
        
        logger.info("Enhanced RAG Engine ініціалізовано")
    
    def _init_database(self):
        """Ініціалізує SQLite базу даних."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Таблиця для API
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS apis (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        description TEXT,
                        base_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Таблиця для ендпоінтів
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS endpoints (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        api_name TEXT NOT NULL,
                        path TEXT NOT NULL,
                        method TEXT NOT NULL,
                        summary TEXT,
                        description TEXT,
                        operation_id TEXT,
                        tags TEXT,
                        parameters TEXT,
                        responses TEXT,
                        request_body TEXT,
                        security TEXT,
                        deprecated BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(api_name, path, method),
                        FOREIGN KEY (api_name) REFERENCES apis (name)
                    )
                """)
                
                # Таблиця для промптів
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS prompts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        api_name TEXT NOT NULL,
                        prompt_type TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (api_name) REFERENCES apis (name)
                    )
                """)
                
                # Таблиця для embeddings
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS embeddings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        endpoint_id INTEGER NOT NULL,
                        chunk_text TEXT NOT NULL,
                        embedding_vector TEXT NOT NULL,
                        chunk_index INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (endpoint_id) REFERENCES endpoints (id)
                    )
                """)
                
                # Таблиця для JWT токенів
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS jwt_tokens (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        api_name TEXT NOT NULL,
                        token TEXT NOT NULL,
                        expires_at TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (api_name) REFERENCES apis (name)
                    )
                """)
                
                # Таблиця для історії запитів
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS request_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        api_name TEXT NOT NULL,
                        endpoint_path TEXT NOT NULL,
                        method TEXT NOT NULL,
                        request_data TEXT,
                        response_data TEXT,
                        status_code INTEGER,
                        error_message TEXT,
                        execution_time REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (api_name) REFERENCES apis (name)
                    )
                """)
                
                conn.commit()
                logger.info("SQLite база даних ініціалізована")
                
        except Exception as e:
            logger.error(f"Помилка ініціалізації бази даних: {e}")
            raise
    
    def add_swagger_spec(self, name: str, swagger_data: List[Dict[str, Any]], base_url: str = "") -> bool:
        """
        Додає Swagger специфікацію до RAG системи.
        
        Args:
            name: Назва API
            swagger_data: Парсовані дані Swagger
            base_url: Базовий URL для API
            
        Returns:
            True якщо успішно додано
        """
        try:
            logger.info(f"Додавання Swagger API '{name}' до Enhanced RAG системи...")
            
            # Спочатку видаляємо старі дані для цього API
            self._remove_api_data(name)
            
            # Додаємо API з base_url
            self._add_api(name, base_url)
            
            # Додаємо ендпоінти
            for endpoint in swagger_data:
                self._add_endpoint(name, endpoint)
            
            # Створюємо embeddings для пошуку
            self._create_endpoint_embeddings(name)
            
            # Створюємо спеціалізовані промпти
            self._create_specialized_prompts(name)
            
            logger.info(f"Swagger API '{name}' успішно додано до Enhanced RAG системи")
            return True
            
        except Exception as e:
            logger.error(f"Помилка додавання Swagger API '{name}': {e}")
            return False
    
    def _add_api(self, name: str, base_url: str):
        """Додає API до бази даних."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO apis (name, description, base_url) VALUES (?, ?, ?)",
                    (name, f"Swagger API: {name}", base_url)
                )
                conn.commit()
                
        except Exception as e:
            logger.error(f"Помилка додавання API '{name}': {e}")
            raise
    
    def _add_endpoint(self, api_name: str, endpoint: Dict[str, Any]):
        """Додає ендпоінт до бази даних."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Конвертуємо складні об'єкти в JSON
                parameters = json.dumps(endpoint.get("parameters", []), ensure_ascii=False)
                responses = json.dumps(endpoint.get("responses", {}), ensure_ascii=False)
                request_body = json.dumps(endpoint.get("request_body", {}), ensure_ascii=False)
                security = json.dumps(endpoint.get("security", []), ensure_ascii=False)
                tags = json.dumps(endpoint.get("tags", []), ensure_ascii=False)
                
                cursor.execute("""
                    INSERT INTO endpoints 
                    (api_name, path, method, summary, description, operation_id, tags, 
                     parameters, responses, request_body, security, deprecated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    api_name,
                    endpoint.get("path", ""),
                    endpoint.get("method", ""),
                    endpoint.get("summary", ""),
                    endpoint.get("description", ""),
                    endpoint.get("operation_id", ""),
                    tags,
                    parameters,
                    responses,
                    request_body,
                    security,
                    endpoint.get("deprecated", False)
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Помилка додавання ендпоінту: {e}")
            raise
    
    def _create_endpoint_embeddings(self, api_name: str):
        """Створює embeddings для ендпоінтів."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Отримуємо всі ендпоінти для цього API
                cursor.execute(
                    "SELECT id, path, method, summary, description FROM endpoints WHERE api_name = ?",
                    (api_name,)
                )
                endpoints = cursor.fetchall()
                
                for endpoint_id, path, method, summary, description in endpoints:
                    # Створюємо текст для embedding
                    endpoint_text = f"{method} {path}: {summary}"
                    if description:
                        endpoint_text += f" {description}"
                    
                    # Створюємо embedding
                    embedding = self.embeddings.embed_query(endpoint_text)
                    
                    # Зберігаємо embedding
                    cursor.execute("""
                        INSERT INTO embeddings (endpoint_id, chunk_text, embedding_vector, chunk_index)
                        VALUES (?, ?, ?, ?)
                    """, (
                        endpoint_id,
                        endpoint_text,
                        json.dumps(embedding),
                        0
                    ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Помилка створення embeddings: {e}")
            raise
    
    def _create_specialized_prompts(self, api_name: str):
        """Створює спеціалізовані промпти для API."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Отримуємо всі ендпоінти для цього API
                cursor.execute(
                    "SELECT method, path, summary, description FROM endpoints WHERE api_name = ? ORDER BY method, path",
                    (api_name,)
                )
                endpoints = cursor.fetchall()
                
                # Створюємо промпти за типами
                prompt_types = {
                    "data_retrieval": [],
                    "data_creation": [],
                    "data_update": [],
                    "data_deletion": [],
                    "general": []
                }
                
                for method, path, summary, description in endpoints:
                    endpoint_info = {
                        "method": method,
                        "path": path,
                        "summary": summary,
                        "description": description
                    }
                    
                    if method.upper() == "GET":
                        prompt_types["data_retrieval"].append(endpoint_info)
                    elif method.upper() == "POST":
                        prompt_types["data_creation"].append(endpoint_info)
                    elif method.upper() in ["PUT", "PATCH"]:
                        prompt_types["data_update"].append(endpoint_info)
                    elif method.upper() == "DELETE":
                        prompt_types["data_deletion"].append(endpoint_info)
                    
                    prompt_types["general"].append(endpoint_info)
                
                # Зберігаємо промпти
                for prompt_type, endpoints_list in prompt_types.items():
                    if endpoints_list:
                        content = self._format_prompt_content(prompt_type, endpoints_list, api_name)
                        
                        cursor.execute("""
                            INSERT OR REPLACE INTO prompts (api_name, prompt_type, content)
                            VALUES (?, ?, ?)
                        """, (api_name, prompt_type, content))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Помилка створення промптів: {e}")
            raise
    
    def _format_prompt_content(self, prompt_type: str, endpoints: List[Dict], api_name: str) -> str:
        """Форматує зміст промпту для AI помічника."""
        if prompt_type == "data_retrieval":
            title = "🔍 Отримання даних"
            description = "Як AI помічник, я можу допомогти вам отримати дані з системи через ці ендпоінти:"
        elif prompt_type == "data_creation":
            title = "➕ Створення даних"
            description = "Як AI помічник, я можу допомогти вам створити нові ресурси через ці ендпоінти:"
        elif prompt_type == "data_update":
            title = "✏️ Оновлення даних"
            description = "Як AI помічник, я можу допомогти вам оновити існуючі ресурси через ці ендпоінти:"
        elif prompt_type == "data_deletion":
            title = "🗑️ Видалення даних"
            description = "Як AI помічник, я можу допомогти вам видалити ресурси через ці ендпоінти:"
        else:
            title = "📚 Загальний огляд"
            description = f"Як AI помічник, я можу допомогти вам працювати з {len(endpoints)} ендпоінтами цього API."
        
        content = [f"=== {api_name} - {title} ===", description, ""]
        
        for endpoint in endpoints:
            content.append(f"• {endpoint['method'].upper()} {endpoint['path']}")
            if endpoint['summary']:
                content.append(f"  📝 Опис: {endpoint['summary']}")
            content.append("")
        
        if prompt_type == "data_retrieval":
            content.append("🤖 Як AI помічник, я можу:")
            content.append("  • Розуміти ваші запити на отримання даних")
            content.append("  • Автоматично виконувати GET запити")
            content.append("  • Надавати детальну інформацію про результати")
        elif prompt_type == "data_creation":
            content.append("🤖 Як AI помічник, я можу:")
            content.append("  • Розуміти ваші запити на створення")
            content.append("  • Автоматично виконувати POST запити")
            content.append("  • Допомагати з форматуванням даних")
        elif prompt_type == "data_update":
            content.append("🤖 Як AI помічник, я можу:")
            content.append("  • Розуміти ваші запити на оновлення")
            content.append("  • Автоматично виконувати PUT/PATCH запити")
            content.append("  • Перевіряти структуру даних")
        elif prompt_type == "data_deletion":
            content.append("🤖 Як AI помічник, я можу:")
            content.append("  • Розуміти ваші запити на видалення")
            content.append("  • Автоматично виконувати DELETE запити")
            content.append("  • Підтверджувати операції")
        else:
            content.append("🤖 Як AI помічник, я можу:")
            content.append("  • Розуміти ваші запити українською мовою")
            content.append("  • Автоматично виконувати API запити")
            content.append("  • Надавати детальні пояснення та приклади")
            content.append("  • Допомагати з усіма операціями CRUD")
        
        return "\n".join(content)
    
    def set_jwt_token(self, api_name: str, token: str, expires_in: int = 3600):
        """
        Встановлює JWT токен для API.
        
        Args:
            api_name: Назва API
            token: JWT токен
            expires_in: Час життя токена в секундах
        """
        try:
            expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO jwt_tokens (api_name, token, expires_at)
                    VALUES (?, ?, ?)
                """, (api_name, token, expires_at.isoformat()))
                conn.commit()
            
            # Встановлюємо токен для поточної сесії
            self.jwt_token = token
            self.session.headers.update({
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            })
            
            logger.info(f"JWT токен встановлено для API '{api_name}'")
            
        except Exception as e:
            logger.error(f"Помилка встановлення JWT токена: {e}")
    
    def _auto_setup_jwt_tokens(self):
        """Автоматично встановлює JWT токени з .env файлу."""
        try:
            from src.token_manager import TokenManager
            
            token_manager = TokenManager()
            
            # Отримуємо всі доступні API
            apis = self.list_swagger_specs()
            
            for api_name in apis:
                # Перевіряємо, чи є JWT токен для цього API
                jwt_token = token_manager.get_jwt_token(api_name)
                if jwt_token:
                    logger.info(f"Автоматично встановлюємо JWT токен для API '{api_name}'")
                    expires_in = token_manager.get_jwt_expires_in()
                    self.set_jwt_token(api_name, jwt_token, expires_in)
                
                # Перевіряємо, чи є base_url для цього API
                base_url = token_manager.get_api_base_url(api_name)
                if base_url:
                    logger.info(f"Оновлюємо base_url для API '{api_name}': {base_url}")
                    self._update_api_base_url(api_name, base_url)
            
            # Якщо немає API, але є загальний JWT токен, встановлюємо його
            if not apis:
                general_jwt_token = token_manager.get_jwt_token()
                if general_jwt_token:
                    logger.info("Встановлюємо загальний JWT токен")
                    expires_in = token_manager.get_jwt_expires_in()
                    # Створюємо тимчасовий API для загального токена
                    self._set_general_jwt_token(general_jwt_token, expires_in)
                    
        except Exception as e:
            logger.warning(f"Не вдалося автоматично налаштувати JWT токени: {e}")
    
    def _update_api_base_url(self, api_name: str, base_url: str):
        """Оновлює base_url для API."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE apis SET base_url = ? WHERE name = ?",
                    (base_url, api_name)
                )
                conn.commit()
                
        except Exception as e:
            logger.error(f"Помилка оновлення base_url для API '{api_name}': {e}")
    
    def _set_general_jwt_token(self, token: str, expires_in: int):
        """Встановлює загальний JWT токен для всіх API."""
        try:
            # Зберігаємо токен в базі даних з назвою "general"
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                cursor.execute("""
                    INSERT OR REPLACE INTO jwt_tokens (api_name, token, expires_at)
                    VALUES (?, ?, ?)
                """, ("general", token, expires_at.isoformat()))
                conn.commit()
            
            # Встановлюємо токен для поточної сесії
            self.jwt_token = token
            self.session.headers.update({
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            })
            
            logger.info("Загальний JWT токен встановлено")
            
        except Exception as e:
            logger.error(f"Помилка встановлення загального JWT токена: {e}")
    
    def get_jwt_token(self, api_name: str) -> Optional[str]:
        """Отримує дійсний JWT токен для API."""
        try:
            # Спочатку шукаємо специфічний токен для API
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT token, expires_at FROM jwt_tokens 
                    WHERE api_name = ? AND expires_at > ?
                """, (api_name, datetime.now().isoformat()))
                
                result = cursor.fetchone()
                if result:
                    token, expires_at = result
                    self.jwt_token = token
                    self.session.headers.update({
                        'Authorization': f'Bearer {token}',
                        'Content-Type': 'application/json'
                    })
                    return token
            
            # Якщо не знайдено специфічний токен, шукаємо загальний
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT token, expires_at FROM jwt_tokens 
                    WHERE api_name = 'general' AND expires_at > ?
                """, (datetime.now().isoformat(),))
                
                result = cursor.fetchone()
                if result:
                    token, expires_at = result
                    self.jwt_token = token
                    self.session.headers.update({
                        'Authorization': f'Bearer {token}',
                        'Content-Type': 'application/json'
                    })
                    return token
                
                return None
                
        except Exception as e:
            logger.error(f"Помилка отримання JWT токена: {e}")
            return None
    
    def execute_api_request(self, api_name: str, method: str, path: str, 
                           data: Optional[Dict] = None, params: Optional[Dict] = None) -> Tuple[bool, Any, str]:
        """
        Виконує API запит.
        
        Args:
            api_name: Назва API
            method: HTTP метод
            path: Шлях ендпоінту
            data: Дані для запиту (для POST/PUT/PATCH)
            params: Параметри запиту (для GET)
            
        Returns:
            Tuple: (успіх, відповідь, повідомлення)
        """
        try:
            start_time = datetime.now()
            
            # Отримуємо base_url та JWT токен
            base_url = self._get_api_base_url(api_name)
            if not base_url:
                return False, None, "Base URL не знайдено для API"
            
            jwt_token = self.get_jwt_token(api_name)
            if not jwt_token:
                return False, None, "JWT токен не знайдено або застарів"
            
            # Формуємо повний URL
            full_url = f"{base_url}{path}"
            
            # Виконуємо запит
            response = self._make_request(method, full_url, data, params)
            
            # Обчислюємо час виконання
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Зберігаємо історію запиту
            self._save_request_history(api_name, path, method, data, response, execution_time)
            
            if response.status_code < 400:
                return True, response.json(), "Запит виконано успішно"
            else:
                # Обробляємо помилку через AI error handler з можливістю автоматичного виправлення
                error_message = self._handle_api_error(response, api_name, method, path, data, params)
                return False, response.text, error_message
                
        except Exception as e:
            error_message = f"Помилка виконання API запиту: {str(e)}"
            logger.error(error_message)
            return False, None, error_message
    
    def _get_api_base_url(self, api_name: str) -> Optional[str]:
        """Отримує base URL для API."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT base_url FROM apis WHERE name = ?", (api_name,))
                result = cursor.fetchone()
                return result[0] if result else None
                
        except Exception as e:
            logger.error(f"Помилка отримання base URL: {e}")
            return None
    
    def _make_request(self, method: str, url: str, data: Optional[Dict] = None, 
                     params: Optional[Dict] = None) -> requests.Response:
        """Виконує HTTP запит."""
        method = method.upper()
        
        if method == "GET":
            return self.session.get(url, params=params)
        elif method == "POST":
            return self.session.post(url, json=data)
        elif method == "PUT":
            return self.session.put(url, json=data)
        elif method == "PATCH":
            return self.session.patch(url, json=data)
        elif method == "DELETE":
            return self.session.delete(url, json=data)
        else:
            raise ValueError(f"Непідтримуваний HTTP метод: {method}")
    
    def _handle_api_error(self, response: requests.Response, api_name: str, 
                         method: str, path: str, request_data: Optional[Dict] = None,
                         request_params: Optional[Dict] = None) -> str:
        """Обробляє помилки API через AI error handler з можливістю автоматичного виправлення."""
        try:
            error_context = {
                "api_name": api_name,
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "response_text": response.text,
                "headers": dict(response.headers)
            }
            
            # Створюємо контекст оригінального запиту
            original_request = {
                "method": method,
                "path": path,
                "data": request_data,
                "params": request_params
            }
            
            # Спробуємо створити план автоматичного виправлення
            fix_plan = self.error_handler.create_fix_plan(error_context, original_request)
            
            if fix_plan and fix_plan.get("can_fix", False):
                # Спробуємо автоматично виправити помилку
                return self._attempt_automatic_fix(fix_plan, error_context, original_request)
            else:
                # Використовуємо звичайний AI аналіз помилки
                error_analysis = self.error_handler.analyze_error(error_context)
                return f"Помилка API ({response.status_code}): {error_analysis}"
            
        except Exception as e:
            logger.error(f"Помилка обробки помилки через AI: {e}")
            return f"Помилка API ({response.status_code}): {response.text}"
    
    def _attempt_automatic_fix(self, fix_plan: Dict[str, Any], error_context: Dict[str, Any], 
                              original_request: Dict[str, Any]) -> str:
        """
        Спроба автоматичного виправлення помилки на основі плану від GPT.
        
        Args:
            fix_plan: План виправлення від GPT
            error_context: Контекст помилки
            original_request: Оригінальний запит
            
        Returns:
            Результат спроби виправлення
        """
        try:
            logger.info(f"Спроба автоматичного виправлення помилки: {fix_plan.get('fix_type')}")
            
            # Показуємо користувачу план виправлення
            fix_info = f"""
🤖 AI помічник виявив можливість автоматичного виправлення помилки!

🔧 План виправлення:
• Тип виправлення: {fix_plan.get('fix_type', 'Невідомо')}
• Опис: {fix_plan.get('fix_description', 'Невідомо')}
• Пояснення: {fix_plan.get('explanation', 'Невідомо')}

🚀 Виконую автоматичне виправлення...
            """.strip()
            
            # Отримуємо виправлений запит
            corrected_request = fix_plan.get("corrected_request", {})
            
            # Виконуємо виправлений запит
            success, result, error_message = self.execute_api_request(
                error_context["api_name"],
                corrected_request.get("method", original_request["method"]),
                corrected_request.get("path", original_request["path"]),
                corrected_request.get("data", original_request.get("data")),
                corrected_request.get("params", original_request.get("params"))
            )
            
            if success:
                return f"""
{fix_info}

✅ Помилка автоматично виправлена!

📊 Результат виправленого запиту:
{json.dumps(result, indent=2, ensure_ascii=False)}

🎉 Як AI помічник, я успішно виправив помилку та виконав запит!
                """.strip()
            else:
                return f"""
{fix_info}

❌ Автоматичне виправлення не вдалося

📋 Оригінальна помилка:
• Код: {error_context.get('status_code')}
• Опис: {error_context.get('response_text')}

🔧 Спробуйте виправити помилку вручну або зверніться до технічної підтримки.
                """.strip()
                
        except Exception as e:
            error_message = f"Помилка автоматичного виправлення: {str(e)}"
            logger.error(error_message)
            return f"""
🤖 Як AI помічник, я зіткнувся з помилкою при спробі автоматичного виправлення:

❌ {error_message}

🔧 Спробуйте виправити помилку вручну або зверніться до технічної підтримки.
            """.strip()
    
    def _save_request_history(self, api_name: str, path: str, method: str, 
                            request_data: Optional[Dict], response: requests.Response, 
                            execution_time: float):
        """Зберігає історію запиту."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO request_history 
                    (api_name, endpoint_path, method, request_data, response_data, 
                     status_code, error_message, execution_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    api_name,
                    path,
                    method,
                    json.dumps(request_data) if request_data else None,
                    response.text,
                    response.status_code,
                    response.text if response.status_code >= 400 else None,
                    execution_time
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Помилка збереження історії запиту: {e}")
    
    def query(self, message: str) -> str:
        """
        Виконує запит до RAG системи як AI помічник з можливістю виконання API запитів.
        
        Args:
            message: Повідомлення користувача
            
        Returns:
            Відповідь від AI помічника
        """
        try:
            logger.info(f"AI помічник обробляє запит: {message}")
            
            # Аналізуємо запит на наявність команд виконання
            if self._is_execution_request(message):
                return self._execute_action_request(message)
            
            # Звичайний RAG запит
            return self._execute_rag_query(message)
            
        except Exception as e:
            logger.error(f"Помилка AI помічника при обробці запиту: {e}")
            return f"""
🤖 Як AI помічник, я зіткнувся з неочікуваною помилкою:

❌ {str(e)}

🔧 Спробуйте ще раз або зверніться до технічної підтримки.
            """.strip()
    
    def _is_execution_request(self, message: str) -> bool:
        """Перевіряє, чи є запит командою виконання для AI помічника."""
        execution_keywords = [
            # Українська мова
            "виконай", "відправ", "зроби", "викликай", "запусти", "виконати",
            "покажи", "створи", "додай", "видали", "оновіть", "зміни",
            "запустити", "виконати", "відправити", "зробити", "викликати",
            "показати", "створити", "додати", "видалити", "оновити", "змінити",
            
            # Англійська мова
            "execute", "send", "make", "call", "run", "perform",
            "show", "create", "add", "delete", "update", "change",
            "get", "post", "put", "patch", "delete"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in execution_keywords)
    
    def _execute_action_request(self, message: str) -> str:
        """Виконує запит на виконання дії як AI помічник."""
        try:
            # Аналізуємо запит для визначення дії
            action_plan = self._analyze_action_request(message)
            
            if not action_plan:
                return "🤖 Як AI помічник, я не зміг зрозуміти, яку дію потрібно виконати. Спробуйте переформулювати запит українською мовою."
            
            # Перевіряємо чи потрібен пошук ID
            if action_plan.get("requires_lookup", False):
                return self._execute_lookup_action(action_plan)
            
            # Показуємо план дії користувачу
            plan_info = f"""
🤖 AI помічник розуміє ваш запит!

📋 План дії:
• API: {action_plan.get('api_name', 'Невідомо')}
• Метод: {action_plan.get('method', 'Невідомо')}
• Шлях: {action_plan.get('path', 'Невідомо')}
• Опис: {action_plan.get('description', 'Виконання запиту')}

🚀 Виконую запит...
            """.strip()
            
            # Виконуємо дію
            success, result, error_message = self.execute_api_request(
                action_plan["api_name"],
                action_plan["method"],
                action_plan["path"],
                action_plan.get("data"),
                action_plan.get("params")
            )
            
            if success:
                return f"""
{plan_info}

✅ Дію виконано успішно!

📊 Результат:
{json.dumps(result, indent=2, ensure_ascii=False)}

🎉 Як AI помічник, я успішно виконав ваш запит! Тепер ви можете продовжувати роботу з системою.
                """.strip()
            else:
                return f"""
{plan_info}

❌ Помилка виконання дії:
{error_message}

🔧 Як AI помічник, я виявив помилку. Спробуйте перевірити параметри або зверніться до адміністратора.
                """.strip()
                
        except Exception as e:
            error_message = f"Помилка виконання дії: {str(e)}"
            logger.error(error_message)
            return f"""
🤖 Як AI помічник, я зіткнувся з неочікуваною помилкою:

❌ {error_message}

🔧 Спробуйте ще раз або зверніться до технічної підтримки.
            """.strip()
    
    def _analyze_action_request(self, message: str) -> Optional[Dict[str, Any]]:
        """Аналізує запит користувача для визначення плану дії через GPT."""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.config.OPENAI_API_KEY)
            
            # Створюємо детальний промпт для аналізу
            analysis_prompt = f"""
            Ти - AI помічник, який аналізує запити користувача та створює плани дій для API.
            
            Завдання: Проаналізуй запит користувача та створи детальний план дії для API.
            
            Запит користувача: {message}
            
            Доступні API: {', '.join(self.list_swagger_specs())}
            
            Створи JSON план дії з наступною структурою:
            {{
                "api_name": "назва API для використання",
                "method": "HTTP метод (GET, POST, PUT, PATCH, DELETE)",
                "path": "шлях ендпоінту з API",
                "data": {{}} // дані для запиту (для POST, PUT, PATCH)
                "params": {{}} // параметри запиту (для GET, DELETE)
                "description": "пояснення що робить цей запит",
                "requires_lookup": false // чи потрібно спочатку знайти ID ресурсу
            }}
            
            Приклади:
            - "покажи категорії" → {{"method": "GET", "path": "/api/categories", "requires_lookup": false}}
            - "створи категорію" → {{"method": "POST", "path": "/api/categories", "data": {{"name": "Назва", "slug": "slug"}}, "requires_lookup": false}}
            - "видали категорію з id 5" → {{"method": "DELETE", "path": "/api/categories/5", "requires_lookup": false}}
            - "видали категорію Книги" → {{"method": "DELETE", "path": "/api/categories/{{id}}", "requires_lookup": true, "lookup_field": "name", "lookup_value": "Книги"}}
            - "оновіть категорію Спорт" → {{"method": "PATCH", "path": "/api/categories/{{id}}", "requires_lookup": true, "lookup_field": "name", "lookup_value": "Спорт"}}
            
            Якщо не вдається визначити план, поверни null.
            """
            
            # Використовуємо GPT для аналізу
            response = client.chat.completions.create(
                model=self.config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Ти - експерт з аналізу запитів та створення планів дій для API."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            # Парсимо відповідь GPT
            gpt_response = response.choices[0].message.content.strip()
            
            # Спробуємо знайти JSON у відповіді
            import re
            json_match = re.search(r'\{.*\}', gpt_response, re.DOTALL)
            
            if json_match:
                try:
                    import json
                    action_plan = json.loads(json_match.group())
                    logger.info(f"GPT створив план дії: {action_plan}")
                    return action_plan
                except json.JSONDecodeError:
                    logger.warning(f"Не вдалося розпарсити JSON від GPT: {gpt_response}")
            
            # Fallback: простий аналіз для тестування
            message_lower = message.lower()
            
            if "категорії" in message_lower and "створи" in message_lower:
                return {
                    "api_name": "oneshop",
                    "method": "POST",
                    "path": "/api/categories",
                    "data": {"name": "Нова категорія", "slug": "new-category"},
                    "description": "Створення нової категорії",
                    "requires_lookup": False
                }
            elif "категорії" in message_lower and "покажи" in message_lower:
                return {
                    "api_name": "oneshop",
                    "method": "GET",
                    "path": "/api/categories",
                    "description": "Отримання списку категорій",
                    "requires_lookup": False
                }
            elif "категорії" in message_lower and "видали" in message_lower:
                # Перевіряємо чи є назва категорії
                import re
                name_match = re.search(r'видали\s+категорію\s+([^\s]+)', message_lower)
                if name_match:
                    category_name = name_match.group(1)
                    return {
                        "api_name": "oneshop",
                        "method": "DELETE",
                        "path": "/api/categories/{id}",
                        "description": f"Видалення категорії '{category_name}'",
                        "requires_lookup": True,
                        "lookup_field": "name",
                        "lookup_value": category_name
                    }
                else:
                    return {
                        "api_name": "oneshop",
                        "method": "DELETE",
                        "path": "/api/categories/1",
                        "description": "Видалення категорії",
                        "requires_lookup": False
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Помилка аналізу запиту дії через GPT: {e}")
            # Fallback до простого аналізу
            return self._simple_action_analysis(message)
    
    def _simple_action_analysis(self, message: str) -> Optional[Dict[str, Any]]:
        """Простий аналіз запиту без GPT (fallback)."""
        message_lower = message.lower()
        
        if "категорії" in message_lower and "створи" in message_lower:
            # Перевіряємо чи є назва категорії
            import re
            name_match = re.search(r'створи\s+категорію\s+([^\s]+)', message_lower)
            if name_match:
                category_name = name_match.group(1)
                # Генеруємо slug з назви
                slug = category_name.lower().replace(' ', '-')
                return {
                    "api_name": "oneshop",
                    "method": "POST",
                    "path": "/api/categories",
                    "data": {"name": category_name, "slug": slug},
                    "description": f"Створення нової категорії '{category_name}'",
                    "requires_lookup": False
                }
            else:
                return {
                    "api_name": "oneshop",
                    "method": "POST",
                    "path": "/api/categories",
                    "data": {"name": "Нова категорія", "slug": "new-category"},
                    "description": "Створення нової категорії",
                    "requires_lookup": False
                }
        elif "категорії" in message_lower and "покажи" in message_lower:
            # Перевіряємо чи є назва конкретної категорії
            import re
            name_match = re.search(r'покажи\s+(?:деталі\s+)?категорії\s+([^\s]+)', message_lower)
            if name_match:
                category_name = name_match.group(1)
                return {
                    "api_name": "oneshop",
                    "method": "GET",
                    "path": "/api/categories/{id}",
                    "description": f"Отримання деталей категорії '{category_name}'",
                    "requires_lookup": True,
                    "lookup_field": "name",
                    "lookup_value": category_name
                }
            else:
                return {
                    "api_name": "oneshop",
                    "method": "GET",
                    "path": "/api/categories",
                    "description": "Отримання списку категорій",
                    "requires_lookup": False
                }
        elif "категорії" in message_lower and "видали" in message_lower:
            # Перевіряємо чи є назва категорії
            import re
            name_match = re.search(r'видали\s+категорію\s+([^\s]+)', message_lower)
            if name_match:
                category_name = name_match.group(1)
                return {
                    "api_name": "oneshop",
                    "method": "DELETE",
                    "path": "/api/categories/{id}",
                    "description": f"Видалення категорії '{category_name}'",
                    "requires_lookup": True,
                    "lookup_field": "name",
                    "lookup_value": category_name
                }
        
        return None
    
    def _execute_lookup_action(self, action_plan: Dict[str, Any]) -> str:
        """
        Виконує дію, яка потребує попереднього пошуку ID ресурсу.
        
        Args:
            action_plan: План дії з інформацією про пошук
            
        Returns:
            Результат виконання дії
        """
        try:
            lookup_field = action_plan.get("lookup_field")
            lookup_value = action_plan.get("lookup_value")
            
            if not lookup_field or not lookup_value:
                return "🤖 Як AI помічник, я не можу виконати пошук без необхідних параметрів."
            
            # Показуємо план дії користувачу
            plan_info = f"""
🤖 AI помічник розуміє ваш запит!

📋 План дії:
• API: {action_plan.get('api_name', 'Невідомо')}
• Метод: {action_plan.get('method', 'Невідомо')}
• Шлях: {action_plan.get('path', 'Невідомо')}
• Опис: {action_plan.get('description', 'Виконання запиту')}
• 🔍 Потрібен пошук: {lookup_field} = "{lookup_value}"

🚀 Спочатку шукаю ID ресурсу...
            """.strip()
            
            # Шукаємо ресурс за назвою
            resource_id = self._find_resource_by_name(
                action_plan["api_name"], 
                lookup_field, 
                lookup_value
            )
            
            if not resource_id:
                return f"""
{plan_info}

❌ Ресурс не знайдено!

🔍 Я шукав {lookup_field} = "{lookup_value}" в API {action_plan['api_name']}, але не знайшов.

💡 Спробуйте:
• Перевірити правильність назви
• Використати інше поле для пошуку
• Спочатку отримати список всіх ресурсів
                """.strip()
            
            # Оновлюємо шлях з знайденим ID
            updated_path = action_plan["path"].replace("{id}", str(resource_id))
            
            # Виконуємо основну дію
            success, result, error_message = self.execute_api_request(
                action_plan["api_name"],
                action_plan["method"],
                updated_path,
                action_plan.get("data"),
                action_plan.get("params")
            )
            
            if success:
                return f"""
{plan_info}

✅ ID знайдено: {resource_id}
✅ Дію виконано успішно!

📊 Результат:
{json.dumps(result, indent=2, ensure_ascii=False)}

🎉 Як AI помічник, я успішно знайшов ресурс та виконав ваш запит!
                """.strip()
            else:
                return f"""
{plan_info}

✅ ID знайдено: {resource_id}
❌ Помилка виконання дії:
{error_message}

🔧 Як AI помічник, я знайшов ресурс, але не зміг виконати основну дію. Спробуйте перевірити параметри.
                """.strip()
                
        except Exception as e:
            error_message = f"Помилка виконання дії з пошуком: {str(e)}"
            logger.error(error_message)
            return f"""
🤖 Як AI помічник, я зіткнувся з помилкою при пошуку ресурсу:

❌ {error_message}

🔧 Спробуйте ще раз або зверніться до технічної підтримки.
            """.strip()
    
    def _find_resource_by_name(self, api_name: str, field: str, value: str) -> Optional[str]:
        """
        Знаходить ID ресурсу за значенням поля через API запит.
        
        Args:
            api_name: Назва API
            field: Поле для пошуку (наприклад, 'name')
            value: Значення для пошуку
            
        Returns:
            ID ресурсу або None якщо не знайдено
        """
        try:
            # Отримуємо список всіх ресурсів
            success, result, error_message = self.execute_api_request(
                api_name,
                "GET",
                "/api/categories",  # Поки що тільки для категорій
                None,
                None
            )
            
            if not success:
                logger.error(f"Помилка отримання ресурсів для пошуку: {error_message}")
                return None
            
            # Шукаємо ресурс за значенням поля
            if isinstance(result, list):
                for resource in result:
                    if isinstance(resource, dict) and resource.get(field) == value:
                        return resource.get("id")
            
            logger.info(f"Ресурс з {field} = '{value}' не знайдено")
            return None
            
        except Exception as e:
            logger.error(f"Помилка пошуку ресурсу: {e}")
            return None
    
    def _execute_rag_query(self, message: str) -> str:
        """Виконує звичайний RAG запит як AI помічник."""
        try:
            # Створюємо embedding для запиту
            query_embedding = self.embeddings.embed_query(message)
            
            # Шукаємо релевантні ендпоінти
            relevant_endpoints = self._find_relevant_endpoints(query_embedding)
            
            if not relevant_endpoints:
                return """
🤖 Як AI помічник, я не знайшов релевантної інформації для вашого запиту.

💡 Спробуйте:
• Переформулювати запит українською мовою
• Використати більш загальні терміни
• Запитати про конкретні ендпоінти або функції

🔍 Доступні API: {api_list}
                """.strip().format(api_list=', '.join(self.list_swagger_specs()))
            
            # Формуємо контекст
            context = self._format_context(relevant_endpoints)
            
            # Генеруємо відповідь за допомогою GPT
            response = self._generate_gpt_response(message, context)
            
            # Додаємо інформацію про AI помічника
            enhanced_response = f"""
🤖 AI помічник відповідає:

{response}

💡 Порада: Якщо ви хочете, щоб я автоматично виконав якусь дію, просто скажіть "виконай [дія]" або "зроби [дія]" українською мовою!
            """.strip()
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"Помилка виконання RAG запиту: {e}")
            return f"""
🤖 Як AI помічник, я зіткнувся з помилкою при обробці вашого запиту:

❌ {str(e)}

🔧 Спробуйте ще раз або зверніться до технічної підтримки.
            """.strip()
    
    def _find_relevant_endpoints(self, query_embedding: List[float]) -> List[Dict[str, Any]]:
        """Знаходить релевантні ендпоінти за допомогою косинусної подібності."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Отримуємо всі embeddings
                cursor.execute("""
                    SELECT e.id, e.api_name, e.path, e.method, e.summary, e.description, 
                           emb.embedding_vector
                    FROM endpoints e
                    JOIN embeddings emb ON e.id = emb.endpoint_id
                """)
                
                results = cursor.fetchall()
                
                if not results:
                    return []
                
                # Обчислюємо подібність
                similarities = []
                for row in results:
                    endpoint_id, api_name, path, method, summary, description, embedding_json = row
                    stored_embedding = json.loads(embedding_json)
                    
                    # Проста косинусна подібність
                    similarity = self._cosine_similarity(query_embedding, stored_embedding)
                    
                    similarities.append({
                        "id": endpoint_id,
                        "api_name": api_name,
                        "path": path,
                        "method": method,
                        "summary": summary,
                        "description": description,
                        "similarity": similarity
                    })
                
                # Сортуємо за подібністю
                similarities.sort(key=lambda x: x["similarity"], reverse=True)
                
                # Повертаємо топ результати
                return similarities[:self.config.SEARCH_K_RESULTS]
                
        except Exception as e:
            logger.error(f"Помилка пошуку релевантних ендпоінтів: {e}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Обчислює косинусну подібність між двома векторами."""
        try:
            import numpy as np
            
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
            
        except Exception:
            # Якщо numpy недоступний, використовуємо простий підхід
            if len(vec1) != len(vec2):
                return 0.0
            
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            norm1 = sum(a * a for a in vec1) ** 0.5
            norm2 = sum(a * a for a in vec2) ** 0.5
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
    
    def _format_context(self, endpoints: List[Dict[str, Any]]) -> str:
        """Форматує контекст для GPT з точки зору AI помічника."""
        context_parts = []
        
        context_parts.append("🔍 Як AI помічник, я маю доступ до наступних API ендпоінтів:")
        context_parts.append("")
        
        for i, endpoint in enumerate(endpoints, 1):
            context_parts.append(f"📌 Ендпоінт {i}:")
            context_parts.append(f"   🌐 API: {endpoint['api_name']}")
            context_parts.append(f"   📡 Метод: {endpoint['method']}")
            context_parts.append(f"   🛣️  Шлях: {endpoint['path']}")
            if endpoint['summary']:
                context_parts.append(f"   📝 Опис: {endpoint['summary']}")
            if endpoint['description']:
                context_parts.append(f"   📖 Деталі: {endpoint['description']}")
            context_parts.append("")
        
        context_parts.append("💡 Я можу допомогти вам:")
        context_parts.append("   • Зрозуміти як використовувати ці ендпоінти")
        context_parts.append("   • Автоматично виконати API запити")
        context_parts.append("   • Створити приклади використання")
        context_parts.append("   • Вирішити проблеми з API")
        
        return "\n".join(context_parts)
    
    def _generate_gpt_response(self, message: str, context: str) -> str:
        """Генерує відповідь за допомогою GPT."""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.config.OPENAI_API_KEY)
            
            system_prompt = f"""
            Ти - AI помічник, який вміє через людську мову створювати та виконувати API запити на основі Swagger документації.

            Твоя роль:
            🤖 Ти - інтелектуальний помічник для роботи з API
            🔍 Ти аналізуєш запити користувача та перетворюєш їх на конкретні API дії
            📚 Ти використовуєш Swagger документацію для розуміння доступних можливостей
            🚀 Ти можеш не тільки пояснювати, але й автоматично виконувати API запити

            Ключові принципи:
            1. Розумій намір користувача з людської мови
            2. Перетворюй людські запити на конкретні API дії
            3. Використовуй тільки інформацію з наданого контексту API
            4. Надавай практичні приклади та автоматичні рішення
            5. Пояснюй кожен крок детально
            6. Вказуй точні ендпоінти, параметри та формати запитів
            7. Відповідай українською мовою
            8. Пропонуй автоматичне виконання дій коли це можливо
            """
            
            user_prompt = f"""
            Контекст API:
            {context}
            
            Запит користувача: {message}
            
            Завдання:
            1. Розумій намір користувача з людської мови
            2. Перетворюй запит на конкретні API дії
            3. Надай детальну, практичну відповідь на основі контексту API
            4. Включи приклади, інструкції та рекомендації
            5. Якщо користувач просить виконати дію - поясни як це зробити та запропонуй автоматичне виконання
            6. Будь корисним та дієвим помічником
            """
            
            response = client.chat.completions.create(
                model=self.config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.config.OPENAI_TEMPERATURE,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Помилка генерації GPT відповіді: {e}")
            return f"На жаль, не вдалося згенерувати відповідь. Помилка: {str(e)}"
    
    def list_swagger_specs(self) -> List[str]:
        """Повертає список доступних API."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT name FROM apis")
                results = cursor.fetchall()
                return [row[0] for row in results]
                
        except Exception as e:
            logger.error(f"Помилка отримання списку API: {e}")
            return []
    
    def remove_swagger_spec(self, name: str) -> bool:
        """
        Видаляє API з RAG системи.
        
        Args:
            name: Назва API для видалення
            
        Returns:
            True якщо успішно видалено
        """
        try:
            self._remove_api_data(name)
            logger.info(f"API '{name}' успішно видалено з Enhanced RAG системи")
            return True
            
        except Exception as e:
            logger.error(f"Помилка видалення API '{name}': {e}")
            return False
    
    def _remove_api_data(self, name: str):
        """Видаляє всі дані для конкретного API."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Отримуємо ID ендпоінтів
                cursor.execute("SELECT id FROM endpoints WHERE api_name = ?", (name,))
                endpoint_ids = [row[0] for row in cursor.fetchall()]
                
                # Видаляємо embeddings
                if endpoint_ids:
                    placeholders = ','.join('?' * len(endpoint_ids))
                    cursor.execute(f"DELETE FROM embeddings WHERE endpoint_id IN ({placeholders})", endpoint_ids)
                
                # Видаляємо ендпоінти
                cursor.execute("DELETE FROM endpoints WHERE api_name = ?", (name,))
                
                # Видаляємо промпти
                cursor.execute("DELETE FROM prompts WHERE api_name = ?", (name,))
                
                # Видаляємо JWT токени
                cursor.execute("DELETE FROM jwt_tokens WHERE api_name = ?", (name,))
                
                # Видаляємо історію запитів
                cursor.execute("DELETE FROM request_history WHERE api_name = ?", (name,))
                
                # Видаляємо API
                cursor.execute("DELETE FROM apis WHERE name = ?", (name,))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Помилка видалення даних API '{name}': {e}")
            raise
    
    def create_specialized_prompts(self, api_name: str) -> Dict[str, str]:
        """
        Створює спеціалізовані промпти на основі Swagger специфікації.
        
        Args:
            name: Назва API
            
        Returns:
            Словник з різними типами промптів
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT prompt_type, content FROM prompts WHERE api_name = ?",
                    (api_name,)
                )
                results = cursor.fetchall()
                
                prompts = {}
                for prompt_type, content in results:
                    prompts[prompt_type] = content
                
                return prompts
                
        except Exception as e:
            logger.error(f"Помилка створення спеціалізованих промптів: {e}")
            return {}
    
    def get_database_info(self) -> Dict[str, Any]:
        """Повертає інформацію про базу даних."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Кількість API
                cursor.execute("SELECT COUNT(*) FROM apis")
                api_count = cursor.fetchone()[0]
                
                # Кількість ендпоінтів
                cursor.execute("SELECT COUNT(*) FROM endpoints")
                endpoint_count = cursor.fetchone()[0]
                
                # Кількість промптів
                cursor.execute("SELECT COUNT(*) FROM prompts")
                prompt_count = cursor.fetchone()[0]
                
                # Кількість embeddings
                cursor.execute("SELECT COUNT(*) FROM embeddings")
                embedding_count = cursor.fetchone()[0]
                
                # Кількість JWT токенів
                cursor.execute("SELECT COUNT(*) FROM jwt_tokens")
                jwt_count = cursor.fetchone()[0]
                
                # Кількість записів історії
                cursor.execute("SELECT COUNT(*) FROM request_history")
                history_count = cursor.fetchone()[0]
                
                # Розмір файлу бази даних
                db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                
                return {
                    "database_path": self.db_path,
                    "database_size_mb": round(db_size / (1024 * 1024), 2),
                    "api_count": api_count,
                    "endpoint_count": endpoint_count,
                    "prompt_count": prompt_count,
                    "embedding_count": embedding_count,
                    "jwt_token_count": jwt_count,
                    "request_history_count": history_count
                }
                
        except Exception as e:
            logger.error(f"Помилка отримання інформації про базу даних: {e}")
            return {}
    
    def get_request_history(self, api_name: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Отримує історію запитів.
        
        Args:
            api_name: Назва API (опціонально)
            limit: Максимальна кількість записів
            
        Returns:
            Список записів історії
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if api_name:
                    cursor.execute("""
                        SELECT api_name, endpoint_path, method, request_data, response_data, 
                               status_code, error_message, execution_time, created_at
                        FROM request_history 
                        WHERE api_name = ?
                        ORDER BY created_at DESC
                        LIMIT ?
                    """, (api_name, limit))
                else:
                    cursor.execute("""
                        SELECT api_name, endpoint_path, method, request_data, response_data, 
                               status_code, error_message, execution_time, created_at
                        FROM request_history 
                        ORDER BY created_at DESC
                        LIMIT ?
                    """, (limit,))
                
                results = cursor.fetchall()
                
                history = []
                for row in results:
                    history.append({
                        "api_name": row[0],
                        "endpoint_path": row[1],
                        "method": row[2],
                        "request_data": json.loads(row[3]) if row[3] else None,
                        "response_data": row[4],
                        "status_code": row[5],
                        "error_message": row[6],
                        "execution_time": row[7],
                        "created_at": row[8]
                    })
                
                return history
                
        except Exception as e:
            logger.error(f"Помилка отримання історії запитів: {e}")
            return []
