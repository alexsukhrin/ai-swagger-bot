"""
Автоматичний генератор промптів на основі Swagger специфікації
Аналізує Swagger файл та створює специфічні промпти для кожного ресурсу
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ResourceType(str, Enum):
    """Типи ресурсів в API."""

    PRODUCTS = "products"
    CATEGORIES = "categories"
    ORDERS = "orders"
    USERS = "users"
    BRANDS = "brands"
    COLLECTIONS = "collections"
    ATTRIBUTES = "attributes"
    SETTINGS = "settings"
    FAMILIES = "families"
    CUSTOM = "custom"


@dataclass
class GeneratedPrompt:
    """Структура для згенерованого промпту."""

    id: str
    name: str
    description: str
    template: str
    category: str
    tags: List[str]
    resource_type: str
    endpoint_path: str
    http_method: str
    is_active: bool = True
    is_public: bool = True
    priority: int = 1
    created_at: str = ""
    updated_at: str = ""
    usage_count: int = 0
    success_rate: float = 0.0
    user_id: Optional[str] = None
    source: str = "swagger_generated"

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()


class SwaggerPromptGenerator:
    """Генератор промптів на основі Swagger специфікації."""

    def __init__(self):
        self.resource_patterns = {
            ResourceType.PRODUCTS: ["products", "product"],
            ResourceType.CATEGORIES: ["categories", "category"],
            ResourceType.ORDERS: ["orders", "order"],
            ResourceType.USERS: ["users", "user"],
            ResourceType.BRANDS: ["brands", "brand"],
            ResourceType.COLLECTIONS: ["collections", "collection"],
            ResourceType.ATTRIBUTES: ["attributes", "attribute"],
            ResourceType.SETTINGS: ["settings", "setting"],
            ResourceType.FAMILIES: ["families", "family"],
        }

        self.http_method_patterns = {
            "GET": ["показати", "отримати", "знайти", "список", "всі"],
            "POST": ["створити", "додати", "новий", "зареєструвати"],
            "PUT": ["оновити", "змінити", "редагувати", "модифікувати"],
            "PATCH": ["частинно оновити", "змінити частину"],
            "DELETE": ["видалити", "видаляти", "деактивувати"],
        }

    def analyze_swagger(self, swagger_data: Dict[str, Any]) -> List[GeneratedPrompt]:
        """
        Аналізує Swagger специфікацію та генерує промпти.

        Args:
            swagger_data: Дані Swagger специфікації

        Returns:
            Список згенерованих промптів
        """
        prompts = []

        # Аналізуємо paths
        paths = swagger_data.get("paths", {})
        for path, path_data in paths.items():
            for method, method_data in path_data.items():
                if method.upper() in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
                    prompt = self._generate_prompt_for_endpoint(
                        path, method, method_data, swagger_data
                    )
                    if prompt:
                        prompts.append(prompt)

        # Генеруємо загальні промпти для ресурсів
        resource_prompts = self._generate_resource_prompts(swagger_data)
        prompts.extend(resource_prompts)

        return prompts

    def _generate_prompt_for_endpoint(
        self, path: str, method: str, method_data: Dict[str, Any], swagger_data: Dict[str, Any]
    ) -> Optional[GeneratedPrompt]:
        """Генерує промпт для конкретного endpoint."""

        # Визначаємо тип ресурсу
        resource_type = self._detect_resource_type(path)
        if not resource_type:
            return None

        # Отримуємо інформацію про endpoint
        operation_id = method_data.get("operationId", "")
        summary = method_data.get("summary", "")
        description = method_data.get("description", "")
        tags = method_data.get("tags", [])

        # Генеруємо назву промпту
        prompt_name = self._generate_prompt_name(path, method, resource_type)

        # Генеруємо опис
        prompt_description = self._generate_prompt_description(
            path, method, summary, description, resource_type
        )

        # Генеруємо шаблон промпту
        template = self._generate_prompt_template(
            path, method, method_data, resource_type, swagger_data
        )

        # Визначаємо категорію
        category = self._determine_category(method, resource_type)

        # Генеруємо теги
        tags = self._generate_tags(path, method, resource_type, tags)

        return GeneratedPrompt(
            id=f"swagger_{resource_type}_{method}_{path.replace('/', '_')}",
            name=prompt_name,
            description=prompt_description,
            template=template,
            category=category,
            tags=tags,
            resource_type=resource_type,
            endpoint_path=path,
            http_method=method.upper(),
        )

    def _detect_resource_type(self, path: str) -> Optional[str]:
        """Визначає тип ресурсу на основі шляху."""
        path_lower = path.lower()

        for resource_type, patterns in self.resource_patterns.items():
            for pattern in patterns:
                if pattern in path_lower:
                    return resource_type.value

        return None

    def _generate_prompt_name(self, path: str, method: str, resource_type: str) -> str:
        """Генерує назву промпту."""
        method_names = {
            "GET": "Отримання",
            "POST": "Створення",
            "PUT": "Оновлення",
            "PATCH": "Частинне оновлення",
            "DELETE": "Видалення",
        }

        resource_names = {
            "products": "товарів",
            "categories": "категорій",
            "orders": "замовлень",
            "users": "користувачів",
            "brands": "брендів",
            "collections": "колекцій",
            "attributes": "атрибутів",
            "settings": "налаштувань",
            "families": "сімейств товарів",
        }

        method_name = method_names.get(method.upper(), method.upper())
        resource_name = resource_names.get(resource_type, resource_type)

        return f"{method_name} {resource_name}"

    def _generate_prompt_description(
        self, path: str, method: str, summary: str, description: str, resource_type: str
    ) -> str:
        """Генерує опис промпту."""

        descriptions = {
            "GET": f"Промпт для отримання {resource_type} через API",
            "POST": f"Промпт для створення нового {resource_type}",
            "PUT": f"Промпт для повного оновлення {resource_type}",
            "PATCH": f"Промпт для часткового оновлення {resource_type}",
            "DELETE": f"Промпт для видалення {resource_type}",
        }

        base_desc = descriptions.get(method.upper(), f"Промпт для роботи з {resource_type}")

        if summary:
            return f"{base_desc}. {summary}"

        return base_desc

    def _generate_prompt_template(
        self,
        path: str,
        method: str,
        method_data: Dict[str, Any],
        resource_type: str,
        swagger_data: Dict[str, Any],
    ) -> str:
        """Генерує шаблон промпту."""

        # Отримуємо схему запиту
        request_schema = self._get_request_schema(method_data, swagger_data)

        # Отримуємо схему відповіді
        response_schema = self._get_response_schema(method_data, swagger_data)

        # Генеруємо параметри
        parameters = self._get_parameters_info(method_data)

        template = f"""
Ти - експерт з API для роботи з {resource_type}.

ENDPOINT: {method.upper()} {path}

Твоя задача - допомогти користувачу взаємодіяти з цим endpoint через природну мову.

ІНФОРМАЦІЯ ПРО ENDPOINT:
- Метод: {method.upper()}
- Шлях: {path}
- Ресурс: {resource_type}

{self._generate_parameters_help(parameters)}

{self._generate_schema_help(request_schema, response_schema, method)}

ПРАВИЛА ВІДПОВІДІ:
1. Завжди відповідай українською мовою
2. Використовуй емодзі для кращого сприйняття
3. Надавай практичні приклади
4. Пояснюй параметри та їх призначення
5. Допомагай з валідацією даних
6. Показуй приклади успішних та неуспішних сценаріїв

КОРИСТУВАЧ ЗАПИТУЄ: {{user_query}}

Твоя відповідь:
"""

        return template

    def _get_request_schema(
        self, method_data: Dict[str, Any], swagger_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Отримує схему запиту."""
        request_body = method_data.get("requestBody", {})
        if not request_body:
            return None

        content = request_body.get("content", {})
        for content_type, content_data in content.items():
            if "schema" in content_data:
                return content_data["schema"]

        return None

    def _get_response_schema(
        self, method_data: Dict[str, Any], swagger_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Отримує схему відповіді."""
        responses = method_data.get("responses", {})

        # Шукаємо успішну відповідь
        for status_code in ["200", "201", "202"]:
            if status_code in responses:
                response = responses[status_code]
                content = response.get("content", {})
                for content_type, content_data in content.items():
                    if "schema" in content_data:
                        return content_data["schema"]

        return None

    def _get_parameters_info(self, method_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Отримує інформацію про параметри."""
        parameters = method_data.get("parameters", [])
        return [
            {
                "name": param.get("name", ""),
                "in": param.get("in", ""),
                "required": param.get("required", False),
                "description": param.get("description", ""),
                "schema": param.get("schema", {}),
            }
            for param in parameters
        ]

    def _generate_parameters_help(self, parameters: List[Dict[str, Any]]) -> str:
        """Генерує допомогу по параметрам."""
        if not parameters:
            return ""

        help_text = "ПАРАМЕТРИ:\n"
        for param in parameters:
            name = param["name"]
            param_type = param["in"]
            required = "обов'язковий" if param["required"] else "опціональний"
            description = param["description"] or "Без опису"

            help_text += f"- {name} ({param_type}, {required}): {description}\n"

        return help_text

    def _generate_schema_help(
        self,
        request_schema: Optional[Dict[str, Any]],
        response_schema: Optional[Dict[str, Any]],
        method: str,
    ) -> str:
        """Генерує допомогу по схемам."""
        help_text = ""

        if request_schema and method.upper() in ["POST", "PUT", "PATCH"]:
            help_text += "СХЕМА ЗАПИТУ:\n"
            help_text += self._format_schema(request_schema)
            help_text += "\n"

        if response_schema:
            help_text += "СХЕМА ВІДПОВІДІ:\n"
            help_text += self._format_schema(response_schema)
            help_text += "\n"

        return help_text

    def _format_schema(self, schema: Dict[str, Any]) -> str:
        """Форматує схему для відображення."""
        if not schema:
            return "Схема не визначена"

        # Простий формат для початку
        return json.dumps(schema, indent=2, ensure_ascii=False)

    def _determine_category(self, method: str, resource_type: str) -> str:
        """Визначає категорію промпту."""
        if method.upper() == "GET":
            return "data_retrieval"
        elif method.upper() in ["POST", "PUT", "PATCH"]:
            return "data_creation"
        elif method.upper() == "DELETE":
            return "data_deletion"
        else:
            return "user_defined"

    def _generate_tags(
        self, path: str, method: str, resource_type: str, original_tags: List[str]
    ) -> List[str]:
        """Генерує теги для промпту."""
        tags = ["swagger_generated", resource_type, method.lower(), "api", "endpoint"]

        # Додаємо оригінальні теги
        tags.extend(original_tags)

        return list(set(tags))  # Видаляємо дублікати

    def _generate_resource_prompts(self, swagger_data: Dict[str, Any]) -> List[GeneratedPrompt]:
        """Генерує загальні промпти для ресурсів."""
        prompts = []

        # Знаходимо всі унікальні ресурси
        resources = set()
        paths = swagger_data.get("paths", {})

        for path in paths.keys():
            resource_type = self._detect_resource_type(path)
            if resource_type:
                resources.add(resource_type)

        # Генеруємо промпти для кожного ресурсу
        for resource in resources:
            prompt = self._generate_general_resource_prompt(resource, swagger_data)
            if prompt:
                prompts.append(prompt)

        return prompts

    def _generate_general_resource_prompt(
        self, resource_type: str, swagger_data: Dict[str, Any]
    ) -> Optional[GeneratedPrompt]:
        """Генерує загальний промпт для ресурсу."""

        resource_names = {
            "products": "товарів",
            "categories": "категорій",
            "orders": "замовлень",
            "users": "користувачів",
            "brands": "брендів",
            "collections": "колекцій",
            "attributes": "атрибутів",
            "settings": "налаштувань",
            "families": "сімейств товарів",
        }

        resource_name = resource_names.get(resource_type, resource_type)

        template = f"""
Ти - експерт з API для роботи з {resource_name}.

Твоя задача - допомогти користувачу взаємодіяти з API для {resource_name} через природну мову.

ДОСТУПНІ ОПЕРАЦІЇ:
- Отримання списку {resource_name}
- Створення нового {resource_name}
- Отримання конкретного {resource_name} за ID
- Оновлення {resource_name}
- Видалення {resource_name}
- Фільтрація та пошук {resource_name}

ПРАВИЛА ВІДПОВІДІ:
1. Завжди відповідай українською мовою
2. Використовуй емодзі для кращого сприйняття
3. Надавай практичні приклади
4. Пояснюй параметри та їх призначення
5. Допомагай з валідацією даних
6. Показуй приклади успішних та неуспішних сценаріїв

КОРИСТУВАЧ ЗАПИТУЄ: {{user_query}}

Твоя відповідь:
"""

        return GeneratedPrompt(
            id=f"swagger_general_{resource_type}",
            name=f"Загальний промпт для роботи з {resource_name}",
            description=f"Загальний промпт для роботи з {resource_name} через API",
            template=template,
            category="data_retrieval",
            tags=["swagger_generated", resource_type, "general", "api"],
            resource_type=resource_type,
            endpoint_path="",
            http_method="",
        )


def generate_prompts_from_swagger(swagger_data: Dict[str, Any]) -> List[GeneratedPrompt]:
    """
    Генерує промпти на основі Swagger специфікації.

    Args:
        swagger_data: Дані Swagger специфікації

    Returns:
        Список згенерованих промптів
    """
    generator = SwaggerPromptGenerator()
    return generator.analyze_swagger(swagger_data)


def save_generated_prompts_to_yaml(prompts: List[GeneratedPrompt], file_path: str) -> None:
    """
    Зберігає згенеровані промпти в YAML файл.

    Args:
        prompts: Список промптів
        file_path: Шлях до файлу
    """
    import yaml

    yaml_data = {
        "version": "1.0",
        "created_at": datetime.now().isoformat(),
        "description": "Автоматично згенеровані промпти на основі Swagger специфікації",
        "source": "swagger_generated",
        "prompts": {},
    }

    for prompt in prompts:
        yaml_data["prompts"][prompt.id] = {
            "name": prompt.name,
            "description": prompt.description,
            "template": prompt.template,
            "category": prompt.category,
            "tags": prompt.tags,
            "is_active": prompt.is_active,
            "is_public": prompt.is_public,
            "priority": prompt.priority,
            "resource_type": prompt.resource_type,
            "endpoint_path": prompt.endpoint_path,
            "http_method": prompt.http_method,
            "source": prompt.source,
        }

    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(yaml_data, f, default_flow_style=False, allow_unicode=True, indent=2)
