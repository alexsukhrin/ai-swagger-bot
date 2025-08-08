"""
Розширений парсер Swagger специфікацій.
"""

import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class EnhancedSwaggerParser:
    """Розширений парсер Swagger специфікацій."""

    def __init__(self, swagger_spec_path: str = None):
        """
        Ініціалізація парсера.

        Args:
            swagger_spec_path: Шлях до Swagger файлу
        """
        self.swagger_spec_path = swagger_spec_path
        self.swagger_data = None

        if swagger_spec_path:
            self.load_swagger_spec()

    def load_swagger_spec(self) -> None:
        """Завантажує Swagger специфікацію з файлу."""
        try:
            with open(self.swagger_spec_path, "r", encoding="utf-8") as f:
                self.swagger_data = json.load(f)
            logger.info(f"✅ Завантажено Swagger специфікацію: {self.swagger_spec_path}")
        except Exception as e:
            logger.error(f"❌ Помилка завантаження Swagger специфікації: {e}")
            raise

    def parse_swagger_spec(self, swagger_data: dict) -> dict:
        """
        Парсить Swagger специфікацію.

        Args:
            swagger_data: Дані Swagger специфікації

        Returns:
            Розпарсені дані
        """
        self.swagger_data = swagger_data

        try:
            # Отримуємо base URL
            base_url = self.get_base_url()

            # Отримуємо endpoints
            endpoints = self.get_endpoints()

            # Отримуємо схеми
            schemas = self.get_schemas()

            # Отримуємо інформацію про API
            api_info = self.get_api_info()

            # Отримуємо security schemes
            security_schemes = self.get_security_schemes()

            parsed_data = {
                "base_url": base_url,
                "endpoints": endpoints,
                "schemas": schemas,
                "api_info": api_info,
                "security_schemes": security_schemes,
            }

            logger.info(
                f"✅ Розпарсено Swagger специфікацію: {len(endpoints)} endpoints, base_url: {base_url}"
            )
            return parsed_data

        except Exception as e:
            logger.error(f"❌ Помилка парсингу Swagger специфікації: {e}")
            raise

    def get_base_url(self) -> Optional[str]:
        """
        Отримує base URL з Swagger специфікації.

        Returns:
            Base URL або None
        """
        try:
            if not self.swagger_data:
                return None

            # Спробуємо отримати з servers
            servers = self.swagger_data.get("servers", [])
            if servers:
                # Беремо перший сервер
                server_url = servers[0].get("url", "")
                if server_url:
                    # Якщо URL відносний, додаємо протокол
                    if server_url.startswith("/"):
                        server_url = "https://localhost" + server_url
                    elif not server_url.startswith(("http://", "https://")):
                        server_url = "https://" + server_url
                    return server_url

            # Спробуємо отримати з host та schemes
            host = self.swagger_data.get("host")
            schemes = self.swagger_data.get("schemes", ["https"])

            if host:
                scheme = schemes[0] if schemes else "https"
                base_path = self.swagger_data.get("basePath", "")
                return f"{scheme}://{host}{base_path}"

            # Спробуємо отримати з info.x-* поля
            info = self.swagger_data.get("info", {})
            for key, value in info.items():
                if key.startswith("x-") and "url" in key.lower():
                    if isinstance(value, str) and value:
                        return value

            logger.warning("⚠️ Не вдалося визначити base URL з Swagger специфікації")
            return None

        except Exception as e:
            logger.error(f"❌ Помилка отримання base URL: {e}")
            return None

    def get_endpoints(self) -> List[Dict[str, Any]]:
        """
        Отримує список endpoints з Swagger специфікації.

        Returns:
            Список endpoints
        """
        endpoints = []

        try:
            paths = self.swagger_data.get("paths", {})

            for path, path_data in paths.items():
                for method, method_data in path_data.items():
                    if method.upper() in [
                        "GET",
                        "POST",
                        "PUT",
                        "DELETE",
                        "PATCH",
                        "HEAD",
                        "OPTIONS",
                    ]:
                        endpoint = {
                            "path": path,
                            "method": method.upper(),
                            "summary": method_data.get("summary", ""),
                            "description": method_data.get("description", ""),
                            "operation_id": method_data.get("operationId", ""),
                            "tags": method_data.get("tags", []),
                            "parameters": self._parse_parameters(method_data.get("parameters", [])),
                            "responses": self._parse_responses(method_data.get("responses", {})),
                            "security": method_data.get("security", []),
                            "deprecated": method_data.get("deprecated", False),
                        }
                        endpoints.append(endpoint)

            return endpoints

        except Exception as e:
            logger.error(f"❌ Помилка отримання endpoints: {e}")
            return []

    def _parse_parameters(self, parameters: List[Dict]) -> List[Dict]:
        """Парсить параметри endpoint."""
        parsed_params = []

        for param in parameters:
            parsed_param = {
                "name": param.get("name", ""),
                "in": param.get("in", ""),
                "required": param.get("required", False),
                "type": param.get("type", ""),
                "description": param.get("description", ""),
                "schema": param.get("schema", {}),
            }
            parsed_params.append(parsed_param)

        return parsed_params

    def _parse_responses(self, responses: Dict) -> List[Dict]:
        """Парсить відповіді endpoint."""
        parsed_responses = []

        for status_code, response_data in responses.items():
            parsed_response = {
                "status_code": status_code,
                "description": response_data.get("description", ""),
                "schema": response_data.get("schema", {}),
                "headers": response_data.get("headers", {}),
            }
            parsed_responses.append(parsed_response)

        return parsed_responses

    def get_schemas(self) -> Dict[str, Any]:
        """
        Отримує схеми з Swagger специфікації.

        Returns:
            Словник схем
        """
        try:
            components = self.swagger_data.get("components", {})
            schemas = components.get("schemas", {})

            # Парсимо схеми
            parsed_schemas = {}
            for schema_name, schema_data in schemas.items():
                parsed_schema = {
                    "type": schema_data.get("type", ""),
                    "properties": schema_data.get("properties", {}),
                    "required": schema_data.get("required", []),
                    "description": schema_data.get("description", ""),
                    "example": schema_data.get("example", {}),
                }
                parsed_schemas[schema_name] = parsed_schema

            return parsed_schemas

        except Exception as e:
            logger.error(f"❌ Помилка отримання схем: {e}")
            return {}

    def get_api_info(self) -> Dict[str, Any]:
        """
        Отримує інформацію про API.

        Returns:
            Інформація про API
        """
        try:
            info = self.swagger_data.get("info", {})

            return {
                "title": info.get("title", ""),
                "description": info.get("description", ""),
                "version": info.get("version", ""),
                "contact": info.get("contact", {}),
                "license": info.get("license", {}),
                "terms_of_service": info.get("termsOfService", ""),
            }

        except Exception as e:
            logger.error(f"❌ Помилка отримання інформації про API: {e}")
            return {}

    def get_security_schemes(self) -> Dict[str, Any]:
        """
        Отримує security schemes з Swagger специфікації.

        Returns:
            Словник security schemes
        """
        try:
            components = self.swagger_data.get("components", {})
            security_schemes = components.get("securitySchemes", {})

            return security_schemes

        except Exception as e:
            logger.error(f"❌ Помилка отримання security schemes: {e}")
            return {}

    def create_enhanced_endpoint_chunks(self) -> List[Dict[str, Any]]:
        """
        Створює покращені chunks для embeddings.

        Returns:
            Список chunks з метаданими
        """
        chunks = []

        try:
            endpoints = self.get_endpoints()
            base_url = self.get_base_url()

            for endpoint in endpoints:
                # Створюємо текст для embedding
                text_parts = []

                # Основна інформація
                text_parts.append(f"Endpoint: {endpoint['method']} {endpoint['path']}")

                if endpoint["summary"]:
                    text_parts.append(f"Summary: {endpoint['summary']}")

                if endpoint["description"]:
                    text_parts.append(f"Description: {endpoint['description']}")

                if endpoint["operation_id"]:
                    text_parts.append(f"Operation ID: {endpoint['operation_id']}")

                # Параметри
                if endpoint["parameters"]:
                    text_parts.append("Parameters:")
                    for param in endpoint["parameters"]:
                        param_text = f"  - {param['name']} ({param['in']})"
                        if param["required"]:
                            param_text += " [required]"
                        if param["description"]:
                            param_text += f": {param['description']}"
                        text_parts.append(param_text)

                # Відповіді
                if endpoint["responses"]:
                    text_parts.append("Responses:")
                    for response in endpoint["responses"]:
                        response_text = f"  - {response['status_code']}"
                        if response["description"]:
                            response_text += f": {response['description']}"
                        text_parts.append(response_text)

                # Теги
                if endpoint["tags"]:
                    text_parts.append(f"Tags: {', '.join(endpoint['tags'])}")

                # Security
                if endpoint["security"]:
                    text_parts.append(f"Security: {endpoint['security']}")

                # Deprecated
                if endpoint["deprecated"]:
                    text_parts.append("⚠️ This endpoint is deprecated")

                # Об'єднуємо текст
                text = "\n".join(text_parts)

                # Створюємо metadata
                metadata = {
                    "path": endpoint["path"],
                    "method": endpoint["method"],
                    "summary": endpoint["summary"],
                    "operation_id": endpoint["operation_id"],
                    "tags": endpoint["tags"],
                    "deprecated": endpoint["deprecated"],
                    "base_url": base_url,
                    "full_url": f"{base_url}{endpoint['path']}" if base_url else endpoint["path"],
                }

                chunks.append({"text": text, "metadata": metadata})

            logger.info(f"✅ Створено {len(chunks)} chunks для embeddings")
            return chunks

        except Exception as e:
            logger.error(f"❌ Помилка створення chunks: {e}")
            return []

    def get_full_url(self, path: str) -> str:
        """
        Отримує повний URL для endpoint.

        Args:
            path: Шлях endpoint

        Returns:
            Повний URL
        """
        base_url = self.get_base_url()
        if base_url:
            # Видаляємо trailing slash з base_url якщо є
            if base_url.endswith("/"):
                base_url = base_url[:-1]

            # Додаємо leading slash до path якщо немає
            if not path.startswith("/"):
                path = "/" + path

            return base_url + path

        return path
