#!/usr/bin/env python3
"""
Скрипт для витягування повної Swagger специфікації з Clickone Shop API
"""

import json
import re

import requests


def extract_swagger_from_js():
    """Витягує повну Swagger специфікацію з JavaScript файлу"""
    print("🔍 Витягую повну Swagger специфікацію...")

    try:
        # Завантажуємо JavaScript файл
        response = requests.get(
            "https://api.oneshop.click/docs/swagger-ui-init.js",
            timeout=30,
            headers={"User-Agent": "AI-Swagger-Bot/1.0"},
        )

        if response.status_code != 200:
            print(f"❌ Помилка завантаження: HTTP {response.status_code}")
            return None

        js_content = response.text
        print(f"✅ JavaScript файл завантажено: {len(js_content)} символів")

        # Шукаємо Swagger специфікацію
        # Спробуємо знайти JSON об'єкт
        json_pattern = r"(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})"
        matches = re.findall(json_pattern, js_content)

        for match in matches:
            try:
                # Спробуємо розпарсити як JSON
                data = json.loads(match)

                # Перевіряємо, чи це Swagger специфікація
                if isinstance(data, dict) and "openapi" in data and "paths" in data:
                    print("✅ Знайдено повну Swagger специфікацію!")
                    print(f"   📊 OpenAPI версія: {data.get('openapi', 'Unknown')}")
                    print(f"   📊 API: {data.get('info', {}).get('title', 'Unknown')}")
                    print(f"   📊 Ендпоінти: {len(data.get('paths', {}))}")
                    print(f"   📊 Схеми: {len(data.get('components', {}).get('schemas', {}))}")

                    # Зберігаємо повну специфікацію
                    with open("full_clickone_swagger.json", "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)

                    print("💾 Повна специфікація збережена в full_clickone_swagger.json")
                    return data

            except json.JSONDecodeError:
                continue

        print("❌ Не вдалося знайти повну Swagger специфікацію")
        return None

    except Exception as e:
        print(f"❌ Помилка: {e}")
        return None


def analyze_full_spec(swagger_spec):
    """Аналізує повну Swagger специфікацію"""
    if not swagger_spec:
        return

    print("\n🔍 Аналізую повну специфікацію...")

    paths = swagger_spec.get("paths", {})
    components = swagger_spec.get("components", {})
    schemas = components.get("schemas", {})

    print(f"📊 Загальна статистика:")
    print(f"   🔗 Ендпоінти: {len(paths)}")
    print(f"   📋 Схеми даних: {len(schemas)}")

    # Аналізуємо ендпоінти за тегами
    endpoints_by_tag = {}
    for path, methods in paths.items():
        for method, details in methods.items():
            if isinstance(details, dict):
                tags = details.get("tags", ["Без тегу"])
                for tag in tags:
                    if tag not in endpoints_by_tag:
                        endpoints_by_tag[tag] = []
                    endpoints_by_tag[tag].append(f"{method.upper()} {path}")

    print(f"\n📊 Ендпоінти за тегами:")
    for tag, endpoints in endpoints_by_tag.items():
        print(f"   🏷️  {tag}: {len(endpoints)} ендпоінтів")
        for endpoint in endpoints[:5]:  # Показуємо перші 5
            print(f"      • {endpoint}")
        if len(endpoints) > 5:
            print(f"      ... та ще {len(endpoints) - 5}")

    # Аналізуємо схеми
    print(f"\n📊 Приклади схем даних:")
    schema_names = list(schemas.keys())[:15]  # Показуємо перші 15
    for i, name in enumerate(schema_names, 1):
        print(f"   {i:2d}. {name}")

    if len(schemas) > 15:
        print(f"   ... та ще {len(schemas) - 15} схем")


def main():
    """Головна функція"""
    print("🚀 Витяг повної Swagger специфікації Clickone Shop API")
    print("=" * 60)

    # Витягуємо повну специфікацію
    full_spec = extract_swagger_from_js()

    if full_spec:
        # Аналізуємо її
        analyze_full_spec(full_spec)

        print("\n✅ Витяг завершено успішно!")
        print("📁 Файл: full_clickone_swagger.json")
    else:
        print("\n❌ Витяг не вдався")


if __name__ == "__main__":
    main()
