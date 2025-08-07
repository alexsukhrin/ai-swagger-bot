"""
Покращений парсер для Swagger/OpenAPI специфікацій.
Детально аналізує всі поля, enum, параметри, типізацію та валідацію.
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml


@dataclass
class ParameterInfo:
    """Детальна інформація про параметр."""

    name: str
    location: str  # path, query, header, cookie
    type: str
    required: bool = False
    description: str = ""
    default: Any = None
    enum_values: List[Any] = field(default_factory=list)
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    format: Optional[str] = None  # date, email, uuid, etc.


@dataclass
class SchemaField:
    """Детальна інформація про поле схеми."""

    name: str
    type: str
    description: str = ""
    required: bool = False
    default: Any = None
    enum_values: List[Any] = field(default_factory=list)
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    format: Optional[str] = None
    example: Any = None
    nullable: bool = False
    read_only: bool = False
    write_only: bool = False


@dataclass
class SchemaInfo:
    """Детальна інформація про схему."""

    name: str
    type: str  # object, array, string, number, integer, boolean
    description: str = ""
    properties: Dict[str, SchemaField] = field(default_factory=dict)
    required_fields: List[str] = field(default_factory=list)
    enum_values: List[Any] = field(default_factory=list)
    example: Any = None
    additional_properties: bool = False


@dataclass
class EndpointInfo:
    """Розширена інформація про API endpoint."""

    method: str
    path: str
    summary: str
    description: str
    parameters: List[ParameterInfo]
    request_body: Optional[Dict[str, Any]]
    responses: Dict[str, Any]
    tags: List[str]
    operation_id: Optional[str] = None
    deprecated: bool = False
    security: List[Dict[str, Any]] = field(default_factory=list)

    # Додаткова інформація для кращого розуміння
    path_variables: List[str] = field(default_factory=list)
    query_parameters: List[str] = field(default_factory=list)
    required_parameters: List[str] = field(default_factory=list)
    optional_parameters: List[str] = field(default_factory=list)


class EnhancedSwaggerParser:
    """Покращений парсер для Swagger/OpenAPI специфікацій."""

    def __init__(self, spec_path: str):
        """
        Ініціалізація парсера.

        Args:
            spec_path: Шлях до Swagger/OpenAPI файлу
        """
        self.swagger_spec_path = spec_path
        self.spec_path = Path(spec_path)
        self.spec_data = self._load_spec()
        self.schemas_cache = {}
        self._parse_schemas()

    def _load_spec(self) -> Dict[str, Any]:
        """Завантажує специфікацію з файлу."""
        if not self.spec_path.exists():
            raise FileNotFoundError(f"Файл {self.spec_path} не знайдено")

        with open(self.spec_path, "r", encoding="utf-8") as f:
            if self.spec_path.suffix.lower() in [".yaml", ".yml"]:
                return yaml.safe_load(f)
            else:
                return json.load(f)

    def _parse_schemas(self):
        """Парсить всі схеми та кешує їх."""
        schemas = self.get_schemas()
        for schema_name, schema_data in schemas.items():
            self.schemas_cache[schema_name] = self._parse_schema(schema_name, schema_data)

    def _parse_schema(self, name: str, schema_data: Dict[str, Any]) -> SchemaInfo:
        """Парсить окрему схему."""
        schema_type = schema_data.get("type", "object")
        description = schema_data.get("description", "")
        required_fields = schema_data.get("required", [])
        properties = schema_data.get("properties", {})

        schema_fields = {}
        for field_name, field_data in properties.items():
            field = self._parse_schema_field(field_name, field_data, field_name in required_fields)
            schema_fields[field_name] = field

        return SchemaInfo(
            name=name,
            type=schema_type,
            description=description,
            properties=schema_fields,
            required_fields=required_fields,
            enum_values=schema_data.get("enum", []),
            example=schema_data.get("example"),
            additional_properties=schema_data.get("additionalProperties", False),
        )

    def _parse_schema_field(
        self, name: str, field_data: Dict[str, Any], required: bool
    ) -> SchemaField:
        """Парсить поле схеми."""
        field_type = field_data.get("type", "string")
        description = field_data.get("description", "")
        default = field_data.get("default")
        enum_values = field_data.get("enum", [])
        example = field_data.get("example")

        # Валідаційні правила
        min_value = field_data.get("minimum")
        max_value = field_data.get("maximum")
        min_length = field_data.get("minLength")
        max_length = field_data.get("maxLength")
        pattern = field_data.get("pattern")
        format_type = field_data.get("format")

        return SchemaField(
            name=name,
            type=field_type,
            description=description,
            required=required,
            default=default,
            enum_values=enum_values,
            min_value=min_value,
            max_value=max_value,
            min_length=min_length,
            max_length=max_length,
            pattern=pattern,
            format=format_type,
            example=example,
            nullable=field_data.get("nullable", False),
            read_only=field_data.get("readOnly", False),
            write_only=field_data.get("writeOnly", False),
        )

    def _parse_parameter(self, param_data: Dict[str, Any]) -> ParameterInfo:
        """Парсить параметр endpoint."""
        name = param_data.get("name", "")
        location = param_data.get("in", "query")
        schema = param_data.get("schema", {})
        param_type = schema.get("type", "string")
        required = param_data.get("required", False)
        description = param_data.get("description", "")
        default = param_data.get("default")

        # Enum значення
        enum_values = schema.get("enum", [])

        # Валідаційні правила
        min_value = schema.get("minimum")
        max_value = schema.get("maximum")
        min_length = schema.get("minLength")
        max_length = schema.get("maxLength")
        pattern = schema.get("pattern")
        format_type = schema.get("format")

        return ParameterInfo(
            name=name,
            location=location,
            type=param_type,
            required=required,
            description=description,
            default=default,
            enum_values=enum_values,
            min_value=min_value,
            max_value=max_value,
            min_length=min_length,
            max_length=max_length,
            pattern=pattern,
            format=format_type,
        )

    def get_endpoints(self) -> List[EndpointInfo]:
        """Отримує всі endpoints з детальним аналізом."""
        endpoints = []

        if "paths" not in self.spec_data:
            return endpoints

        for path, path_data in self.spec_data["paths"].items():
            for method, method_data in path_data.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    # Парсимо параметри
                    parameters = []
                    for param_data in method_data.get("parameters", []):
                        param = self._parse_parameter(param_data)
                        parameters.append(param)

                    # Аналізуємо path variables
                    path_variables = [p.name for p in parameters if p.location == "path"]
                    query_parameters = [p.name for p in parameters if p.location == "query"]
                    required_parameters = [p.name for p in parameters if p.required]
                    optional_parameters = [p.name for p in parameters if not p.required]

                    endpoint = EndpointInfo(
                        method=method.upper(),
                        path=path,
                        summary=method_data.get("summary", ""),
                        description=method_data.get("description", ""),
                        parameters=parameters,
                        request_body=method_data.get("requestBody"),
                        responses=method_data.get("responses", {}),
                        tags=method_data.get("tags", []),
                        operation_id=method_data.get("operationId"),
                        deprecated=method_data.get("deprecated", False),
                        security=method_data.get("security", []),
                        path_variables=path_variables,
                        query_parameters=query_parameters,
                        required_parameters=required_parameters,
                        optional_parameters=optional_parameters,
                    )
                    endpoints.append(endpoint)

        return endpoints

    def get_schemas(self) -> Dict[str, Any]:
        """Отримує схеми даних зі специфікації."""
        return self.spec_data.get("components", {}).get("schemas", {})

    def get_schema_info(self, schema_name: str) -> Optional[SchemaInfo]:
        """Отримує детальну інформацію про схему."""
        return self.schemas_cache.get(schema_name)

    def get_all_schemas_info(self) -> Dict[str, SchemaInfo]:
        """Отримує інформацію про всі схеми."""
        return self.schemas_cache

    def get_base_url(self) -> str:
        """Отримує базовий URL API."""
        servers = self.spec_data.get("servers", [])
        if servers:
            return servers[0].get("url", "")
        return ""

    def get_api_info(self) -> Dict[str, Any]:
        """Отримує загальну інформацію про API."""
        info = self.spec_data.get("info", {})
        return {
            "title": info.get("title", ""),
            "version": info.get("version", ""),
            "description": info.get("description", ""),
            "contact": info.get("contact", {}),
            "license": info.get("license", {}),
            "base_url": self.get_base_url(),
            "servers": self.spec_data.get("servers", []),
        }

    def get_security_schemes(self) -> Dict[str, Any]:
        """Отримує схеми безпеки."""
        return self.spec_data.get("components", {}).get("securitySchemes", {})

    def find_endpoints_by_tag(self, tag: str) -> List[EndpointInfo]:
        """Знаходить endpoints за тегом."""
        return [ep for ep in self.get_endpoints() if tag in ep.tags]

    def find_endpoints_by_method(self, method: str) -> List[EndpointInfo]:
        """Знаходить endpoints за методом."""
        return [ep for ep in self.get_endpoints() if ep.method.upper() == method.upper()]

    def get_required_fields_for_endpoint(self, endpoint: EndpointInfo) -> List[str]:
        """Отримує всі обов'язкові поля для endpoint."""
        required_fields = []

        # Параметри
        for param in endpoint.parameters:
            if param.required:
                required_fields.append(param.name)

        # Request body
        if endpoint.request_body:
            content = endpoint.request_body.get("content", {})
            for content_type, content_data in content.items():
                if content_type == "application/json":
                    schema_ref = content_data.get("schema", {}).get("$ref", "")
                    if schema_ref:
                        schema_name = schema_ref.split("/")[-1]
                        schema_info = self.get_schema_info(schema_name)
                        if schema_info:
                            required_fields.extend(schema_info.required_fields)

        return required_fields

    def get_validation_rules_for_field(self, schema_name: str, field_name: str) -> Dict[str, Any]:
        """Отримує правила валідації для поля."""
        schema_info = self.get_schema_info(schema_name)
        if schema_info and field_name in schema_info.properties:
            field = schema_info.properties[field_name]
            return {
                "type": field.type,
                "required": field.required,
                "enum_values": field.enum_values,
                "min_value": field.min_value,
                "max_value": field.max_value,
                "min_length": field.min_length,
                "max_length": field.max_length,
                "pattern": field.pattern,
                "format": field.format,
                "example": field.example,
                "nullable": field.nullable,
            }
        return {}

    def create_enhanced_endpoint_chunks(self) -> List[Dict[str, Any]]:
        """
        Створює покращені chunks для RAG системи з детальною інформацією.

        Returns:
            Список chunks з метаданими для векторної бази
        """
        chunks = []
        endpoints = self.get_endpoints()

        for endpoint in endpoints:
            # Створюємо детальний опис endpoint
            chunk_text = self._create_enhanced_endpoint_description(endpoint)

            chunk = {
                "text": chunk_text,
                "metadata": {
                    "method": endpoint.method,
                    "path": endpoint.path,
                    "summary": endpoint.summary,
                    "tags": ", ".join(endpoint.tags) if endpoint.tags else "",
                    "operation_id": endpoint.operation_id or "",
                    "deprecated": endpoint.deprecated,
                    "has_request_body": endpoint.request_body is not None,
                    "required_parameters": (
                        ", ".join(endpoint.required_parameters)
                        if endpoint.required_parameters
                        else ""
                    ),
                    "optional_parameters": (
                        ", ".join(endpoint.optional_parameters)
                        if endpoint.optional_parameters
                        else ""
                    ),
                    "path_variables": (
                        ", ".join(endpoint.path_variables) if endpoint.path_variables else ""
                    ),
                    "query_parameters": (
                        ", ".join(endpoint.query_parameters) if endpoint.query_parameters else ""
                    ),
                },
            }
            chunks.append(chunk)

        return chunks

    def _create_enhanced_endpoint_description(self, endpoint: EndpointInfo) -> str:
        """Створює детальний опис endpoint для RAG."""
        description_parts = [
            f"Endpoint: {endpoint.method} {endpoint.path}",
            f"Summary: {endpoint.summary}",
            f"Description: {endpoint.description}",
        ]

        if endpoint.operation_id:
            description_parts.append(f"Operation ID: {endpoint.operation_id}")

        if endpoint.deprecated:
            description_parts.append("⚠️ DEPRECATED")

        if endpoint.tags:
            description_parts.append(f"Tags: {', '.join(endpoint.tags)}")

        # Детальна інформація про параметри
        if endpoint.parameters:
            description_parts.append("\nParameters:")
            for param in endpoint.parameters:
                param_desc = f"- {param.name} ({param.type}) [{param.location}]"
                if param.required:
                    param_desc += " [REQUIRED]"
                if param.description:
                    param_desc += f": {param.description}"
                if param.enum_values:
                    param_desc += f" [Enum: {', '.join(map(str, param.enum_values))}]"
                if param.min_value is not None:
                    param_desc += f" [Min: {param.min_value}]"
                if param.max_value is not None:
                    param_desc += f" [Max: {param.max_value}]"
                if param.pattern:
                    param_desc += f" [Pattern: {param.pattern}]"
                description_parts.append(param_desc)

        # Детальна інформація про request body
        if endpoint.request_body:
            description_parts.append("\nRequest Body:")
            content = endpoint.request_body.get("content", {})
            for content_type, content_data in content.items():
                if content_type == "application/json":
                    schema_ref = content_data.get("schema", {}).get("$ref", "")
                    if schema_ref:
                        schema_name = schema_ref.split("/")[-1]
                        schema_info = self.get_schema_info(schema_name)
                        if schema_info:
                            description_parts.append(f"Schema: {schema_name}")
                            description_parts.append(f"Type: {schema_info.type}")
                            if schema_info.description:
                                description_parts.append(f"Description: {schema_info.description}")

                            if schema_info.properties:
                                description_parts.append("Fields:")
                                for field_name, field in schema_info.properties.items():
                                    field_desc = f"  - {field_name} ({field.type})"
                                    if field.required:
                                        field_desc += " [REQUIRED]"
                                    if field.description:
                                        field_desc += f": {field.description}"
                                    if field.enum_values:
                                        field_desc += (
                                            f" [Enum: {', '.join(map(str, field.enum_values))}]"
                                        )
                                    if field.example:
                                        field_desc += f" [Example: {field.example}]"
                                    description_parts.append(field_desc)

        # Responses
        if endpoint.responses:
            description_parts.append("\nResponses:")
            for status_code, response in endpoint.responses.items():
                response_desc = f"- {status_code}: {response.get('description', '')}"
                description_parts.append(response_desc)

        return "\n".join(description_parts)
