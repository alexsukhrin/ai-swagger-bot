"""
Сервіс для завантаження та парсингу Swagger документації Clickone Shop API
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

from .config import Config
from .enhanced_swagger_parser import EnhancedSwaggerParser
from .postgres_vector_manager import PostgresVectorManager
from .rag_engine import PostgresRAGEngine

logger = logging.getLogger(__name__)


class ClickoneSwaggerService:
    """Сервіс для роботи з Clickone Shop API Swagger документацією"""

    def __init__(self):
        """Ініціалізація сервісу"""
        self.config = Config()
        self.swagger_url = self.config.CLICKONE_SHOP_SWAGGER_URL
        self.api_url = self.config.CLICKONE_SHOP_API_URL
        self.jwt_token = self.config.CLICKONE_SHOP_JWT_TOKEN

        # Ініціалізуємо парсер та RAG двигун
        self.swagger_parser = EnhancedSwaggerParser()
        self._vector_manager = None  # Ленива ініціалізація

        logger.info(f"ClickoneSwaggerService ініціалізовано для {self.swagger_url}")

    @property
    def vector_manager(self):
        """Ленива ініціалізація PostgresVectorManager"""
        if self._vector_manager is None:
            try:
                self._vector_manager = PostgresVectorManager()
            except Exception as e:
                logger.warning(f"Не вдалося ініціалізувати PostgresVectorManager: {e}")
                self._vector_manager = None
        return self._vector_manager

    def download_swagger_spec(self) -> Optional[Dict[str, Any]]:
        """
        Завантажує Swagger специфікацію з Clickone Shop API

        Returns:
            Swagger специфікація або None при помилці
        """
        try:
            logger.info(f"Завантажую Swagger специфікацію з {self.swagger_url}")

            response = requests.get(
                self.swagger_url, timeout=30, headers={"User-Agent": "AI-Swagger-Bot/1.0"}
            )

            if response.status_code == 200:
                swagger_spec = response.json()
                logger.info(
                    f"Swagger специфікація завантажена успішно: {len(str(swagger_spec))} символів"
                )
                return swagger_spec
            else:
                logger.error(f"Помилка завантаження Swagger: HTTP {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Помилка завантаження Swagger специфікації: {e}")
            return None

    def parse_swagger_spec(self, swagger_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Парсить Swagger специфікацію та витягує корисну інформацію

        Args:
            swagger_spec: Завантажена Swagger специфікація

        Returns:
            Парсована інформація
        """
        try:
            logger.info("Парсую Swagger специфікацію...")

            # Використовуємо EnhancedSwaggerParser для парсингу
            parsed_info = self.swagger_parser.parse_swagger_spec(swagger_spec)

            # Додаємо специфічну інформацію для Clickone Shop API
            parsed_info["api_name"] = "Clickone Shop API"
            parsed_info["api_version"] = swagger_spec.get("info", {}).get("version", "1.0")
            parsed_info["parsed_at"] = datetime.utcnow().isoformat()

            logger.info(
                f"Swagger специфікацію парсовано: {len(parsed_info.get('endpoints', []))} ендпоінтів"
            )
            return parsed_info

        except Exception as e:
            logger.error(f"Помилка парсингу Swagger специфікації: {e}")
            return {}

    def create_embeddings_for_spec(
        self, swagger_spec: Dict[str, Any], user_id: str, spec_id: str
    ) -> bool:
        """
        Створює embeddings для Swagger специфікації та зберігає в БД

        Args:
            swagger_spec: Swagger специфікація
            user_id: ID користувача
            spec_id: ID специфікації

        Returns:
            True якщо embeddings створено успішно
        """
        try:
            logger.info(f"Створюю embeddings для специфікації {spec_id}")

            # Створюємо RAG двигун
            rag_engine = PostgresRAGEngine(
                user_id=user_id,
                swagger_spec_id=spec_id,
                config={
                    "chunk_size": self.config.CHUNK_SIZE,
                    "chunk_overlap": self.config.CHUNK_OVERLAP,
                },
            )

            # Конвертуємо специфікацію в текст для векторизації
            spec_text = self._convert_spec_to_text(swagger_spec)

            # Створюємо embeddings
            success = rag_engine.add_document(
                content=spec_text,
                metadata={
                    "source": "clickone_shop_api",
                    "spec_id": spec_id,
                    "api_name": "Clickone Shop API",
                    "parsed_at": datetime.utcnow().isoformat(),
                },
            )

            if success:
                logger.info(f"Embeddings створено успішно для специфікації {spec_id}")
                return True
            else:
                logger.error(f"Не вдалося створити embeddings для специфікації {spec_id}")
                return False

        except Exception as e:
            logger.error(f"Помилка створення embeddings: {e}")
            return False

    def _convert_spec_to_text(self, swagger_spec: Dict[str, Any]) -> str:
        """
        Конвертує Swagger специфікацію в текст для векторизації

        Args:
            swagger_spec: Swagger специфікація

        Returns:
            Текст для векторизації
        """
        text_parts = []

        # Інформація про API
        info = swagger_spec.get("info", {})
        text_parts.append(f"API: {info.get('title', 'Unknown')}")
        text_parts.append(f"Версія: {info.get('version', 'Unknown')}")
        text_parts.append(f"Опис: {info.get('description', 'No description')}")
        text_parts.append("")

        # Ендпоінти
        paths = swagger_spec.get("paths", {})
        for path, methods in paths.items():
            text_parts.append(f"Ендпоінт: {path}")

            for method, details in methods.items():
                if isinstance(details, dict):
                    summary = details.get("summary", "No summary")
                    description = details.get("description", "No description")
                    tags = details.get("tags", [])

                    text_parts.append(f"  Метод: {method.upper()}")
                    text_parts.append(f"  Опис: {summary}")
                    text_parts.append(f"  Деталі: {description}")

                    if tags:
                        text_parts.append(f"  Теги: {', '.join(tags)}")

                    # Параметри запиту
                    parameters = details.get("parameters", [])
                    if parameters:
                        text_parts.append("  Параметри:")
                        for param in parameters:
                            param_name = param.get("name", "Unknown")
                            param_desc = param.get("description", "No description")
                            text_parts.append(f"    {param_name}: {param_desc}")

                    # Схема запиту
                    request_body = details.get("requestBody", {})
                    if request_body:
                        text_parts.append("  Тіло запиту:")
                        content = request_body.get("content", {})
                        for content_type, schema in content.items():
                            text_parts.append(f"    Тип: {content_type}")

                    # Відповіді
                    responses = details.get("responses", {})
                    if responses:
                        text_parts.append("  Відповіді:")
                        for status_code, response in responses.items():
                            response_desc = response.get("description", "No description")
                            text_parts.append(f"    {status_code}: {response_desc}")

                    text_parts.append("")

        # Схеми
        components = swagger_spec.get("components", {})
        schemas = components.get("schemas", {})
        if schemas:
            text_parts.append("Схеми даних:")
            for schema_name, schema in schemas.items():
                text_parts.append(f"  {schema_name}:")
                properties = schema.get("properties", {})
                for prop_name, prop_details in properties.items():
                    prop_type = prop_details.get("type", "unknown")
                    prop_desc = prop_details.get("description", "No description")
                    text_parts.append(f"    {prop_name} ({prop_type}): {prop_desc}")
                text_parts.append("")

        return "\n".join(text_parts)

    def get_api_endpoints_summary(self, swagger_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Отримує короткий опис ендпоінтів API

        Args:
            swagger_spec: Swagger специфікація

        Returns:
            Опис ендпоінтів
        """
        try:
            paths = swagger_spec.get("paths", {})
            endpoints_summary = {}

            for path, methods in paths.items():
                endpoints_summary[path] = {}

                for method, details in methods.items():
                    if isinstance(details, dict):
                        endpoints_summary[path][method] = {
                            "summary": details.get("summary", "No summary"),
                            "description": details.get("description", "No description"),
                            "tags": details.get("tags", []),
                            "security": details.get("security", []),
                            "parameters_count": len(details.get("parameters", [])),
                            "responses_count": len(details.get("responses", {})),
                        }

            return endpoints_summary

        except Exception as e:
            logger.error(f"Помилка створення опису ендпоінтів: {e}")
            return {}

    def validate_api_connection(self) -> bool:
        """
        Перевіряє з'єднання з Clickone Shop API

        Returns:
            True якщо з'єднання працює
        """
        try:
            # Спробуємо отримати базову інформацію про API
            response = requests.get(
                f"{self.api_url}/health", timeout=10, headers={"User-Agent": "AI-Swagger-Bot/1.0"}
            )

            if response.status_code == 200:
                logger.info("З'єднання з Clickone Shop API працює")
                return True
            else:
                logger.warning(f"Clickone Shop API повернув статус {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Помилка з'єднання з Clickone Shop API: {e}")
            return False

    def process_clickone_swagger(self, user_id: str, spec_id: str) -> Dict[str, Any]:
        """
        Основний метод для обробки Clickone Shop API Swagger

        Args:
            user_id: ID користувача
            spec_id: ID специфікації

        Returns:
            Результат обробки
        """
        try:
            logger.info(f"Починаю обробку Clickone Shop API Swagger для користувача {user_id}")

            # 1. Завантажуємо Swagger специфікацію
            swagger_spec = self.download_swagger_spec()
            if not swagger_spec:
                return {"success": False, "error": "Не вдалося завантажити Swagger специфікацію"}

            # 2. Парсимо специфікацію
            parsed_info = self.parse_swagger_spec(swagger_spec)
            if not parsed_info:
                return {"success": False, "error": "Не вдалося розпарсити Swagger специфікацію"}

            # 3. Створюємо embeddings
            embeddings_created = self.create_embeddings_for_spec(swagger_spec, user_id, spec_id)
            if not embeddings_created:
                return {"success": False, "error": "Не вдалося створити embeddings"}

            # 4. Отримуємо опис ендпоінтів
            endpoints_summary = self.get_api_endpoints_summary(swagger_spec)

            result = {
                "success": True,
                "message": "Clickone Shop API Swagger успішно оброблено",
                "spec_info": {
                    "api_name": parsed_info.get("api_name"),
                    "api_version": parsed_info.get("api_version"),
                    "endpoints_count": len(endpoints_summary),
                    "parsed_at": parsed_info.get("parsed_at"),
                },
                "endpoints_summary": endpoints_summary,
                "user_id": user_id,
                "spec_id": spec_id,
            }

            logger.info(
                f"Обробку Clickone Shop API Swagger завершено успішно: {result['spec_info']}"
            )
            return result

        except Exception as e:
            logger.error(f"Помилка обробки Clickone Shop API Swagger: {e}")
            return {"success": False, "error": str(e)}

    def search_api_documentation(
        self, user_id: str, spec_id: str, query: str, k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Шукає в документації API за допомогою RAG

        Args:
            user_id: ID користувача
            spec_id: ID специфікації
            query: Пошуковий запит
            k: Кількість результатів

        Returns:
            Результати пошуку
        """
        try:
            logger.info(f"Пошук в документації API: {query}")

            # Створюємо RAG двигун
            rag_engine = PostgresRAGEngine(
                user_id=user_id, swagger_spec_id=spec_id, config={"search_k_results": k}
            )

            # Виконуємо пошук
            results = rag_engine.search(query)

            logger.info(f"Знайдено {len(results)} результатів пошуку")
            return results

        except Exception as e:
            logger.error(f"Помилка пошуку в документації API: {e}")
            return []


# Глобальний екземпляр сервісу (ленива ініціалізація)
_clickone_swagger_service = None


def get_clickone_swagger_service() -> ClickoneSwaggerService:
    """Отримує глобальний екземпляр Clickone Swagger Service"""
    global _clickone_swagger_service
    if _clickone_swagger_service is None:
        _clickone_swagger_service = ClickoneSwaggerService()
    return _clickone_swagger_service
