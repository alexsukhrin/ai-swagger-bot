"""
GPT генератор промптів на основі Swagger специфікації
Використовує GPT для створення розумних та адаптивних промптів
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import openai
from openai import OpenAI


@dataclass
class GPTGeneratedPrompt:
    """Структура для згенерованого промпту через GPT."""

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
    source: str = "gpt_generated"

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()


class GPTPromptGenerator:
    """Генератор промптів через GPT на основі Swagger специфікації."""

    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        """
        Ініціалізація генератора.

        Args:
            api_key: OpenAI API ключ
            model: Модель GPT для використання
        """
        self.model = model
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            # Спробуємо отримати з змінних середовища
            import os

            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
            else:
                self.client = None
                print("⚠️ OpenAI API ключ не знайдено. Встановіть OPENAI_API_KEY змінну середовища.")

    def generate_prompts_from_swagger(
        self, swagger_data: Dict[str, Any]
    ) -> List[GPTGeneratedPrompt]:
        """
        Генерує промпти через GPT на основі Swagger специфікації.

        Args:
            swagger_data: Дані Swagger специфікації

        Returns:
            Список згенерованих промптів
        """
        if not self.client:
            print("❌ OpenAI клієнт не ініціалізований")
            return []

        prompts = []

        # Аналізуємо paths та генеруємо промпти для кожного endpoint
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
    ) -> Optional[GPTGeneratedPrompt]:
        """Генерує промпт для конкретного endpoint через GPT."""

        # Підготовлюємо дані для GPT
        endpoint_info = self._prepare_endpoint_info(path, method, method_data, swagger_data)

        # Генеруємо промпт через GPT
        gpt_response = self._call_gpt_for_prompt_generation(endpoint_info)

        if not gpt_response:
            return None

        # Парсимо відповідь GPT
        try:
            parsed_response = json.loads(gpt_response)

            return GPTGeneratedPrompt(
                id=parsed_response.get("id", f"gpt_{method}_{path.replace('/', '_')}"),
                name=parsed_response.get("name", f"GPT промпт для {method} {path}"),
                description=parsed_response.get("description", ""),
                template=parsed_response.get("template", ""),
                category=parsed_response.get("category", "user_defined"),
                tags=parsed_response.get("tags", []),
                resource_type=parsed_response.get("resource_type", "custom"),
                endpoint_path=path,
                http_method=method.upper(),
            )

        except json.JSONDecodeError:
            print(f"⚠️ Помилка парсингу відповіді GPT для {method} {path}")
            return None

    def _prepare_endpoint_info(
        self, path: str, method: str, method_data: Dict[str, Any], swagger_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Підготовлює інформацію про endpoint для GPT."""

        # Визначаємо тип ресурсу
        resource_type = self._detect_resource_type(path)

        # Отримуємо схеми
        request_schema = self._get_request_schema(method_data, swagger_data)
        response_schema = self._get_response_schema(method_data, swagger_data)
        parameters = self._get_parameters_info(method_data)

        return {
            "path": path,
            "method": method.upper(),
            "resource_type": resource_type,
            "operation_id": method_data.get("operationId", ""),
            "summary": method_data.get("summary", ""),
            "description": method_data.get("description", ""),
            "tags": method_data.get("tags", []),
            "parameters": parameters,
            "request_schema": request_schema,
            "response_schema": response_schema,
            "security": method_data.get("security", []),
            "responses": method_data.get("responses", {}),
        }

    def _call_gpt_for_prompt_generation(self, endpoint_info: Dict[str, Any]) -> Optional[str]:
        """Викликає GPT для генерації промпту."""

        system_prompt = """
Ти - експерт з генерації промптів для AI чат-ботів, які працюють з API.

Твоя задача - створити промпт для чат-бота, який допомагає користувачам взаємодіяти з API через природну мову.

Створи промпт на основі наданої інформації про API endpoint. Промпт повинен:
1. Бути зрозумілим та корисним
2. Включати практичні приклади
3. Пояснювати параметри та їх призначення
4. Допомагати з валідацією даних
5. Надавати приклади успішних та неуспішних сценаріїв

Відповідай у форматі JSON з наступними полями:
{
    "id": "унікальний_ідентифікатор",
    "name": "Назва промпту",
    "description": "Опис промпту",
    "template": "Шаблон промпту з {user_query}",
    "category": "категорія (data_retrieval/data_creation/data_update/data_deletion/user_defined)",
    "tags": ["тег1", "тег2"],
    "resource_type": "тип_ресурсу"
}
"""

        # Отримуємо інформацію про API
        info = swagger_data.get("info", {})
        servers = swagger_data.get("servers", [])
        base_url = servers[0].get("url", "") if servers else ""

        user_prompt = f"""
Створи промпт для наступного API endpoint:

API ІНФОРМАЦІЯ:
- Назва: {info.get('title', 'Unknown API')}
- Версія: {info.get('version', 'Unknown')}
- Опис: {info.get('description', 'Немає опису')}
- Base URL: {base_url}

ENDPOINT: {endpoint_info['method']} {endpoint_info['path']}
РЕСУРС: {endpoint_info['resource_type']}
ОПЕРАЦІЯ: {endpoint_info['operation_id']}
ОПИС: {endpoint_info['summary']}
ДЕТАЛЬНИЙ ОПИС: {endpoint_info['description']}
ТЕГИ: {endpoint_info['tags']}

ПАРАМЕТРИ:
{json.dumps(endpoint_info['parameters'], indent=2, ensure_ascii=False)}

СХЕМА ЗАПИТУ:
{json.dumps(endpoint_info['request_schema'], indent=2, ensure_ascii=False) if endpoint_info['request_schema'] else 'Немає схеми запиту'}

СХЕМА ВІДПОВІДІ:
{json.dumps(endpoint_info['response_schema'], indent=2, ensure_ascii=False) if endpoint_info['response_schema'] else 'Немає схеми відповіді'}

ВАЖЛИВО: Поверни ТІЛЬКИ JSON без markdown форматування.

Створи корисний промпт для чат-бота, який допоможе користувачам взаємодіяти з цим endpoint через природну мову. Промпт повинен бути специфічним для цього API та endpoint.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"❌ Помилка виклику GPT: {e}")
            return None

    def _detect_resource_type(self, path: str) -> str:
        """Визначає тип ресурсу на основі шляху."""
        path_lower = path.lower()

        resource_patterns = {
            "products": ["products", "product"],
            "categories": ["categories", "category"],
            "orders": ["orders", "order"],
            "users": ["users", "user"],
            "brands": ["brands", "brand"],
            "collections": ["collections", "collection"],
            "attributes": ["attributes", "attribute"],
            "settings": ["settings", "setting"],
            "families": ["families", "family"],
        }

        for resource_type, patterns in resource_patterns.items():
            for pattern in patterns:
                if pattern in path_lower:
                    return resource_type

        return "custom"

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

    def _generate_resource_prompts(self, swagger_data: Dict[str, Any]) -> List[GPTGeneratedPrompt]:
        """Генерує загальні промпти для ресурсів через GPT."""
        if not self.client:
            return []

        prompts = []

        # Знаходимо всі унікальні ресурси
        resources = set()
        paths = swagger_data.get("paths", {})

        for path in paths.keys():
            resource_type = self._detect_resource_type(path)
            if resource_type != "custom":
                resources.add(resource_type)

        # Генеруємо промпти для кожного ресурсу
        for resource in resources:
            prompt = self._generate_general_resource_prompt(resource, swagger_data)
            if prompt:
                prompts.append(prompt)

        return prompts

    def _generate_general_resource_prompt(
        self, resource_type: str, swagger_data: Dict[str, Any]
    ) -> Optional[GPTGeneratedPrompt]:
        """Генерує загальний промпт для ресурсу через GPT."""

        system_prompt = """
Ти - експерт з генерації загальних промптів для AI чат-ботів, які працюють з API.

Створи загальний промпт для роботи з конкретним типом ресурсу (наприклад, товари, категорії, замовлення).

Промпт повинен бути універсальним та покривати всі основні операції з ресурсом.
"""

        # Отримуємо інформацію про API
        info = swagger_data.get("info", {})
        paths = swagger_data.get("paths", {})

        # Збираємо endpoints для цього ресурсу
        resource_endpoints = []
        for path, methods in paths.items():
            if self._detect_resource_type(path) == resource_type:
                for method, method_data in methods.items():
                    if isinstance(method_data, dict):
                        resource_endpoints.append(
                            {
                                "path": path,
                                "method": method.upper(),
                                "summary": method_data.get("summary", ""),
                                "operation_id": method_data.get("operationId", ""),
                            }
                        )

        user_prompt = f"""
Створи загальний промпт для роботи з ресурсом типу: {resource_type}

API ІНФОРМАЦІЯ:
- Назва: {info.get('title', 'Unknown API')}
- Версія: {info.get('version', 'Unknown')}
- Опис: {info.get('description', 'Немає опису')}

ДОСТУПНІ ENDPOINTS ДЛЯ {resource_type.upper()}:
{chr(10).join([f"- {ep['method']} {ep['path']}: {ep['summary']}" for ep in resource_endpoints[:5]])}

Цей промпт повинен допомагати користувачам взаємодіяти з API для {resource_type} через природну мову.

ВАЖЛИВО: Поверни ТІЛЬКИ JSON без markdown форматування.

Відповідай у форматі JSON:
{{
    "id": "gpt_general_{resource_type}",
    "name": "Назва промпту",
    "description": "Опис промпту",
    "template": "Шаблон промпту з {{user_query}}",
    "category": "data_retrieval",
    "tags": ["gpt_generated", "{resource_type}", "general", "api"],
    "resource_type": "{resource_type}"
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=1500,
            )

            gpt_response = response.choices[0].message.content

            try:
                parsed_response = json.loads(gpt_response)

                return GPTGeneratedPrompt(
                    id=parsed_response.get("id", f"gpt_general_{resource_type}"),
                    name=parsed_response.get("name", f"Загальний промпт для {resource_type}"),
                    description=parsed_response.get("description", ""),
                    template=parsed_response.get("template", ""),
                    category=parsed_response.get("category", "data_retrieval"),
                    tags=parsed_response.get("tags", []),
                    resource_type=resource_type,
                    endpoint_path="",
                    http_method="",
                )

            except json.JSONDecodeError:
                print(f"⚠️ Помилка парсингу відповіді GPT для ресурсу {resource_type}")
                return None

        except Exception as e:
            print(f"❌ Помилка виклику GPT для ресурсу {resource_type}: {e}")
            return None

    def generate_smart_suggestions(self, swagger_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Генерує розумні підказки для користувача на основі Swagger.

        Args:
            swagger_data: Дані Swagger специфікації

        Returns:
            Список підказок
        """
        if not self.client:
            return []

        system_prompt = """
Ти - експерт з API та UX. Створи корисні підказки для користувачів чат-бота, які працюють з API.

Підказки повинні бути практичними та допомагати користувачам ефективно взаємодіяти з API.
"""

        # Аналізуємо API та створюємо підказки
        paths = swagger_data.get("paths", {})
        info = swagger_data.get("info", {})
        resources = set()

        # Збираємо детальну інформацію про endpoints
        endpoints_info = []
        for path, methods in paths.items():
            resource_type = self._detect_resource_type(path)
            if resource_type != "custom":
                resources.add(resource_type)

            for method, method_data in methods.items():
                if isinstance(method_data, dict):
                    summary = method_data.get("summary", "")
                    description = method_data.get("description", "")
                    tags = method_data.get("tags", [])

                    endpoints_info.append(
                        {
                            "path": path,
                            "method": method.upper(),
                            "summary": summary,
                            "description": description,
                            "tags": tags,
                        }
                    )

        # Формуємо детальний опис API
        api_description = f"""
API: {info.get('title', 'Unknown API')}
Версія: {info.get('version', 'Unknown')}
Опис: {info.get('description', 'Немає опису')}
Base URL: {swagger_data.get('servers', [{}])[0].get('url', 'Unknown') if swagger_data.get('servers') else 'Unknown'}
"""

        user_prompt = f"""
На основі наступного API створіть корисні підказки для користувачів:

{api_description}

ДОСТУПНІ РЕСУРСИ: {list(resources)}
КІЛЬКІСТЬ ENDPOINTS: {len(endpoints_info)}

ПРИКЛАДИ ENDPOINTS:
{chr(10).join([f"- {ep['method']} {ep['path']}: {ep['summary']}" for ep in endpoints_info[:10]])}

ВАЖЛИВО: Поверни ТІЛЬКИ JSON без markdown форматування або додаткового тексту.

Створи 10-15 практичних підказок у форматі JSON, які будуть специфічними для цього API:
{{
    "suggestions": [
        {{
            "category": "категорія підказки",
            "title": "Назва підказки",
            "description": "Опис підказки",
            "example_query": "Приклад запиту",
            "difficulty": "easy/medium/hard",
            "related_endpoints": ["список пов'язаних endpoints"]
        }}
    ]
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.8,
                max_tokens=2000,
            )

            gpt_response = response.choices[0].message.content

            try:
                # Спробуємо витягти JSON з markdown коду
                if "```json" in gpt_response:
                    start = gpt_response.find("```json") + 7
                    end = gpt_response.find("```", start)
                    if end != -1:
                        json_str = gpt_response[start:end].strip()
                        parsed_response = json.loads(json_str)
                        return parsed_response.get("suggestions", [])

                # Спробуємо звичайний JSON
                parsed_response = json.loads(gpt_response)
                return parsed_response.get("suggestions", [])

            except json.JSONDecodeError:
                print("⚠️ Помилка парсингу підказок від GPT")
                print(f"   Отримана відповідь: {gpt_response[:200]}...")
                return []

        except Exception as e:
            print(f"❌ Помилка генерації підказок: {e}")
            return []


def generate_prompts_with_gpt(
    swagger_data: Dict[str, Any], api_key: str = None
) -> List[GPTGeneratedPrompt]:
    """
    Генерує промпти через GPT на основі Swagger специфікації.

    Args:
        swagger_data: Дані Swagger специфікації
        api_key: OpenAI API ключ

    Returns:
        Список згенерованих промптів
    """
    generator = GPTPromptGenerator(api_key=api_key)
    return generator.generate_prompts_from_swagger(swagger_data)


def generate_smart_suggestions_with_gpt(
    swagger_data: Dict[str, Any], api_key: str = None
) -> List[Dict[str, Any]]:
    """
    Генерує розумні підказки через GPT на основі Swagger специфікації.

    Args:
        swagger_data: Дані Swagger специфікації
        api_key: OpenAI API ключ

    Returns:
        Список підказок
    """
    generator = GPTPromptGenerator(api_key=api_key)
    return generator.generate_smart_suggestions(swagger_data)
