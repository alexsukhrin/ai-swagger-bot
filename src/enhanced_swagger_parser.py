"""
Розширений парсер Swagger специфікацій для CLI версії.
"""

import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class EnhancedSwaggerParser:
    """Розширений парсер Swagger специфікацій для CLI версії."""

    def __init__(self):
        """Ініціалізація парсера."""
        self.swagger_data = None

    def parse_swagger(self, swagger_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Парсить Swagger специфікацію та повертає список ендпоінтів.
        
        Args:
            swagger_data: Дані Swagger специфікації
            
        Returns:
            Список парсованих ендпоінтів
        """
        self.swagger_data = swagger_data
        
        try:
            logger.info("Парсинг Swagger специфікації...")
            
            # Отримуємо base URL
            base_url = self._get_base_url()
            
            # Отримуємо всі ендпоінти
            endpoints = self._extract_endpoints(base_url)
            
            # Отримуємо схеми
            schemas = self._extract_schemas()
            
            # Збагачуємо ендпоінти інформацією про схеми
            enriched_endpoints = self._enrich_endpoints_with_schemas(endpoints, schemas)
            
            logger.info(f"✅ Розпарсено {len(enriched_endpoints)} ендпоінтів")
            return enriched_endpoints
            
        except Exception as e:
            logger.error(f"❌ Помилка парсингу Swagger специфікації: {e}")
            raise
    
    def _get_base_url(self) -> str:
        """Отримує base URL з Swagger специфікації."""
        try:
            # Спробуємо отримати з servers
            servers = self.swagger_data.get("servers", [])
            if servers:
                server_url = servers[0].get("url", "")
                if server_url:
                    return server_url.rstrip('/')
            
            # Якщо немає servers, використовуємо host + basePath
            host = self.swagger_data.get("host", "")
            base_path = self.swagger_data.get("basePath", "")
            
            if host:
                protocol = "https" if "https" in host else "http"
                if not host.startswith(("http://", "https://")):
                    host = f"{protocol}://{host}"
                return f"{host}{base_path}".rstrip('/')
            
            return ""
            
        except Exception as e:
            logger.warning(f"Не вдалося отримати base URL: {e}")
            return ""
    
    def _extract_endpoints(self, base_url: str) -> List[Dict[str, Any]]:
        """Витягує всі ендпоінти з Swagger специфікації."""
        endpoints = []
        
        try:
            paths = self.swagger_data.get("paths", {})
            
            for path, path_item in paths.items():
                # Обробляємо кожен HTTP метод
                for method, operation in path_item.items():
                    if method.upper() in ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]:
                        endpoint = self._parse_operation(path, method, operation, base_url)
                        if endpoint:
                            endpoints.append(endpoint)
            
            return endpoints
            
        except Exception as e:
            logger.error(f"Помилка витягування ендпоінтів: {e}")
            return []
    
    def _parse_operation(self, path: str, method: str, operation: Dict[str, Any], base_url: str) -> Optional[Dict[str, Any]]:
        """Парсить окрему операцію (ендпоінт)."""
        try:
            # Отримуємо основну інформацію
            summary = operation.get("summary", "")
            description = operation.get("description", "")
            operation_id = operation.get("operationId", "")
            tags = operation.get("tags", [])
            
            # Отримуємо параметри
            parameters = self._extract_parameters(operation.get("parameters", []))
            
            # Отримуємо відповіді
            responses = self._extract_responses(operation.get("responses", {}))
            
            # Отримуємо request body
            request_body = self._extract_request_body(operation.get("requestBody", {}))
            
            # Формуємо повний URL
            full_url = f"{base_url}{path}" if base_url else path
            
            endpoint = {
                "path": path,
                "method": method.upper(),
                "full_url": full_url,
                "summary": summary,
                "description": description,
                "operation_id": operation_id,
                "tags": tags,
                "parameters": parameters,
                "responses": responses,
                "request_body": request_body,
                "security": operation.get("security", []),
                "deprecated": operation.get("deprecated", False)
            }
            
            return endpoint
            
        except Exception as e:
            logger.warning(f"Помилка парсингу операції {method} {path}: {e}")
            return None
    
    def _extract_parameters(self, parameters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Витягує параметри ендпоінту."""
        extracted_params = []
        
        for param in parameters:
            try:
                param_info = {
                    "name": param.get("name", ""),
                    "in": param.get("in", ""),
                    "required": param.get("required", False),
                    "type": param.get("type", ""),
                    "description": param.get("description", ""),
                    "example": param.get("example", ""),
                    "schema": param.get("schema", {})
                }
                extracted_params.append(param_info)
            except Exception as e:
                logger.warning(f"Помилка парсингу параметра: {e}")
                continue
        
        return extracted_params
    
    def _extract_responses(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Витягує відповіді ендпоінту."""
        extracted_responses = {}
        
        for status_code, response in responses.items():
            try:
                response_info = {
                    "description": response.get("description", ""),
                    "content": response.get("content", {}),
                    "headers": response.get("headers", {}),
                    "schema": response.get("schema", {})
                }
                extracted_responses[status_code] = response_info
            except Exception as e:
                logger.warning(f"Помилка парсингу відповіді {status_code}: {e}")
                continue
        
        return extracted_responses
    
    def _extract_request_body(self, request_body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Витягує request body ендпоінту."""
        if not request_body:
            return None
        
        try:
            return {
                "required": request_body.get("required", False),
                "description": request_body.get("description", ""),
                "content": request_body.get("content", {})
            }
        except Exception as e:
            logger.warning(f"Помилка парсингу request body: {e}")
            return None
    
    def _extract_schemas(self) -> Dict[str, Any]:
        """Витягує схеми з Swagger специфікації."""
        try:
            components = self.swagger_data.get("components", {})
            schemas = components.get("schemas", {})
            
            extracted_schemas = {}
            for schema_name, schema in schemas.items():
                try:
                    schema_info = {
                        "type": schema.get("type", ""),
                        "description": schema.get("description", ""),
                        "properties": schema.get("properties", {}),
                        "required": schema.get("required", []),
                        "example": schema.get("example", {}),
                        "enum": schema.get("enum", [])
                    }
                    extracted_schemas[schema_name] = schema_info
                except Exception as e:
                    logger.warning(f"Помилка парсингу схеми {schema_name}: {e}")
                    continue
            
            return extracted_schemas
            
        except Exception as e:
            logger.warning(f"Помилка витягування схем: {e}")
            return {}
    
    def _enrich_endpoints_with_schemas(self, endpoints: List[Dict[str, Any]], schemas: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Збагачує ендпоінти інформацією про схеми."""
        enriched_endpoints = []
        
        for endpoint in endpoints:
            try:
                # Додаємо інформацію про схеми параметрів
                enriched_params = []
                for param in endpoint.get("parameters", []):
                    enriched_param = param.copy()
                    if "schema" in param and param["schema"]:
                        schema_ref = param["schema"].get("$ref", "")
                        if schema_ref:
                            schema_name = schema_ref.split("/")[-1]
                            if schema_name in schemas:
                                enriched_param["schema_details"] = schemas[schema_name]
                    enriched_params.append(enriched_param)
                
                # Додаємо інформацію про схеми відповідей
                enriched_responses = {}
                for status_code, response in endpoint.get("responses", {}).items():
                    enriched_response = response.copy()
                    if "schema" in response and response["schema"]:
                        schema_ref = response["schema"].get("$ref", "")
                        if schema_ref:
                            schema_name = schema_ref.split("/")[-1]
                            if schema_name in schemas:
                                enriched_response["schema_details"] = schemas[schema_name]
                    enriched_responses[status_code] = enriched_response
                
                # Створюємо збагачений ендпоінт
                enriched_endpoint = endpoint.copy()
                enriched_endpoint["parameters"] = enriched_params
                enriched_endpoint["responses"] = enriched_responses
                
                enriched_endpoints.append(enriched_endpoint)
                
            except Exception as e:
                logger.warning(f"Помилка збагачення ендпоінту {endpoint.get('path', '')}: {e}")
                enriched_endpoints.append(endpoint)
        
        return enriched_endpoints
