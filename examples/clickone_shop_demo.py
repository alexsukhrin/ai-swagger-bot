#!/usr/bin/env python3
"""
Демонстрація роботи AI Swagger Bot з Clickone Shop API

Цей скрипт показує, як AI Swagger Bot може:
1. Завантажити та проаналізувати Swagger специфікацію
2. Створити embeddings для API endpoints
3. Генерувати відповіді на запити користувачів
4. Надавати інформацію про API структуру
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Додаємо src до Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


def load_swagger_spec() -> Dict[str, Any]:
    """Завантажує Clickone Shop API специфікацію"""
    spec_path = Path(__file__).parent / "swagger_specs" / "clickone_shop_api.json"

    try:
        with open(spec_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Помилка: Файл {spec_path} не знайдено")
        print("Спочатку завантажте Swagger специфікацію:")
        print(
            "curl 'https://api.oneshop.click/docs/ai-json' > examples/swagger_specs/clickone_shop_api.json"
        )
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Помилка парсингу JSON: {e}")
        sys.exit(1)


def analyze_api_structure(swagger_spec: Dict[str, Any]) -> Dict[str, Any]:
    """Аналізує структуру API та повертає статистику"""
    paths = swagger_spec.get("paths", {})
    schemas = swagger_spec.get("components", {}).get("schemas", {})

    # Підраховуємо endpoints за методами
    methods_count = {}
    total_endpoints = 0

    for path, operations in paths.items():
        for method in operations.keys():
            if method.upper() in methods_count:
                methods_count[method.upper()] += 1
            else:
                methods_count[method.upper()] = 1
            total_endpoints += 1

    # Підраховуємо схеми за типами
    schema_types = {}
    for schema_name, schema in schemas.items():
        schema_type = schema.get("type", "unknown")
        if schema_type in schema_types:
            schema_types[schema_type] += 1
        else:
            schema_types[schema_type] = 1

    return {
        "total_endpoints": total_endpoints,
        "methods_count": methods_count,
        "total_schemas": len(schemas),
        "schema_types": schema_types,
        "api_info": swagger_spec.get("info", {}),
        "security_schemes": list(
            swagger_spec.get("components", {}).get("securitySchemes", {}).keys()
        ),
    }


def get_endpoint_details(
    swagger_spec: Dict[str, Any], path: str, method: str = None
) -> Dict[str, Any]:
    """Отримує детальну інформацію про endpoint"""
    paths = swagger_spec.get("paths", {})

    if path not in paths:
        return {"error": f"Endpoint {path} не знайдено"}

    endpoint = paths[path]

    if method and method.upper() in endpoint:
        operation = endpoint[method.upper()]
        return {
            "path": path,
            "method": method.upper(),
            "summary": operation.get("summary", "Немає опису"),
            "description": operation.get("description", "Немає детального опису"),
            "operationId": operation.get("operationId", "Немає ID операції"),
            "tags": operation.get("tags", []),
            "parameters": operation.get("parameters", []),
            "responses": list(operation.get("responses", {}).keys()),
            "security": operation.get("security", []),
        }

    # Якщо метод не вказано, повертаємо всі доступні методи
    available_methods = list(endpoint.keys())
    return {
        "path": path,
        "available_methods": available_methods,
        "operations": {method: endpoint[method] for method in available_methods},
    }


def get_schema_details(swagger_spec: Dict[str, Any], schema_name: str) -> Dict[str, Any]:
    """Отримує детальну інформацію про схему"""
    schemas = swagger_spec.get("components", {}).get("schemas", {})

    if schema_name not in schemas:
        return {"error": f"Схема {schema_name} не знайдена"}

    schema = schemas[schema_name]

    return {
        "name": schema_name,
        "type": schema.get("type", "unknown"),
        "description": schema.get("description", "Немає опису"),
        "properties": list(schema.get("properties", {}).keys()),
        "required": schema.get("required", []),
        "examples": schema.get("examples", {}),
    }


def search_endpoints(swagger_spec: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
    """Шукає endpoints за запитом"""
    paths = swagger_spec.get("paths", {})
    results = []

    query_lower = query.lower()

    for path, operations in paths.items():
        for method, operation in operations.items():
            summary = operation.get("summary", "").lower()
            description = operation.get("description", "").lower()
            tags = [tag.lower() for tag in operation.get("tags", [])]

            if (
                query_lower in summary
                or query_lower in description
                or any(query_lower in tag for tag in tags)
            ):
                results.append(
                    {
                        "path": path,
                        "method": method.upper(),
                        "summary": operation.get("summary", ""),
                        "tags": operation.get("tags", []),
                    }
                )

    return results


def main():
    """Головна функція демонстрації"""
    print("🚀 AI Swagger Bot - Демонстрація роботи з Clickone Shop API")
    print("=" * 70)

    # Завантажуємо специфікацію
    print("\n📥 Завантаження Swagger специфікації...")
    swagger_spec = load_swagger_spec()
    print("✅ Специфікація завантажена успішно")

    # Аналізуємо структуру API
    print("\n🔍 Аналіз структури API...")
    analysis = analyze_api_structure(swagger_spec)

    print(f"📊 Статистика API:")
    print(f"   • Назва: {analysis['api_info'].get('title', 'Невідомо')}")
    print(f"   • Версія: {analysis['api_info'].get('version', 'Невідомо')}")
    print(f"   • Загальна кількість endpoints: {analysis['total_endpoints']}")
    print(f"   • Загальна кількість схем: {analysis['total_schemas']}")

    print(f"\n📋 Методи HTTP:")
    for method, count in analysis["methods_count"].items():
        print(f"   • {method}: {count}")

    print(f"\n🔐 Схеми безпеки:")
    for scheme in analysis["security_schemes"]:
        print(f"   • {scheme}")

    # Демонструємо пошук endpoints
    print("\n🔍 Демонстрація пошуку endpoints...")

    search_queries = ["category", "product", "order", "customer"]
    for query in search_queries:
        print(f"\n📝 Пошук: '{query}'")
        results = search_endpoints(swagger_spec, query)

        if results:
            print(f"   Знайдено {len(results)} endpoints:")
            for result in results[:3]:  # Показуємо перші 3
                print(f"     • {result['method']} {result['path']} - {result['summary']}")
            if len(results) > 3:
                print(f"     ... та ще {len(results) - 3}")
        else:
            print(f"   Endpoints не знайдено")

    # Демонструємо деталі endpoints
    print("\n📋 Деталі основних endpoints...")

    main_endpoints = [
        ("/api/categories", "GET"),
        ("/api/categories", "POST"),
        ("/api/categories/{id}", "GET"),
    ]

    for path, method in main_endpoints:
        details = get_endpoint_details(swagger_spec, path, method)
        if "error" not in details and "summary" in details:
            print(f"\n🔗 {method} {path}")
            print(f"   • Опис: {details['summary']}")
            print(f"   • Теги: {', '.join(details['tags'])}")
            print(f"   • Відповіді: {', '.join(details['responses'])}")

    # Демонструємо схеми
    print("\n📊 Деталі основних схем...")

    main_schemas = ["CreateCategoryDto", "CreateProductDto", "CreateOrderDto"]
    for schema_name in main_schemas:
        details = get_schema_details(swagger_spec, schema_name)
        if "error" not in details:
            print(f"\n📝 {schema_name}")
            print(f"   • Тип: {details['type']}")
            print(f"   • Властивості: {', '.join(details['properties'][:5])}")
            if len(details["properties"]) > 5:
                print(f"     ... та ще {len(details['properties']) - 5}")
            print(f"   • Обов'язкові: {', '.join(details['required'])}")

    print("\n🎉 Демонстрація завершена!")
    print("\n💡 Це показує, як AI Swagger Bot може:")
    print("   • Аналізувати структуру API")
    print("   • Шукати endpoints за запитами")
    print("   • Надавати детальну інформацію про endpoints та схеми")
    print("   • Допомагати розробникам розуміти API")


if __name__ == "__main__":
    main()
