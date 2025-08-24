#!/usr/bin/env python3
"""
Демонстрація роботи ClickoneSwaggerService з реальними даними
"""

import json
import os
from datetime import datetime

from dotenv import load_dotenv

# Завантажуємо змінні середовища
load_dotenv()


def print_banner():
    """Виводить банер програми"""
    print("🚀" * 50)
    print("🔍 ДЕМО CLICKONE SWAGGER SERVICE")
    print("🚀" * 50)
    print()


def demo_swagger_download():
    """Демонструє завантаження Swagger специфікації"""
    print("📋 Демонструю завантаження Swagger специфікації...")

    try:
        from src.clickone_swagger_service import get_clickone_swagger_service

        service = get_clickone_swagger_service()
        swagger_spec = service.download_swagger_spec()

        if swagger_spec:
            print(f"✅ Swagger специфікацію завантажено успішно!")
            print(f"   📊 API: {swagger_spec.get('info', {}).get('title', 'Unknown')}")
            print(f"   📊 Версія: {swagger_spec.get('info', {}).get('version', 'Unknown')}")
            print(f"   📊 Ендпоінти: {len(swagger_spec.get('paths', {}))}")
            return swagger_spec
        else:
            print("❌ Не вдалося завантажити Swagger специфікацію")
            return None

    except Exception as e:
        print(f"❌ Помилка: {e}")
        return None


def demo_swagger_parsing(swagger_spec):
    """Демонструє парсинг Swagger специфікації"""
    print("\n🔍 Демонструю парсинг Swagger специфікації...")

    try:
        from src.clickone_swagger_service import get_clickone_swagger_service

        service = get_clickone_swagger_service()
        parsed_info = service.parse_swagger_spec(swagger_spec)

        if parsed_info:
            print(f"✅ Swagger специфікацію парсовано успішно!")
            print(f"   📊 API Name: {parsed_info.get('api_name', 'Unknown')}")
            print(f"   📊 API Version: {parsed_info.get('api_version', 'Unknown')}")
            print(f"   📊 Parsed At: {parsed_info.get('parsed_at', 'Unknown')}")
            return parsed_info
        else:
            print("❌ Не вдалося розпарсити Swagger специфікацію")
            return None

    except Exception as e:
        print(f"❌ Помилка: {e}")
        return None


def demo_endpoints_summary(swagger_spec):
    """Демонструє створення опису ендпоінтів"""
    print("\n📊 Демонструю створення опису ендпоінтів...")

    try:
        from src.clickone_swagger_service import get_clickone_swagger_service

        service = get_clickone_swagger_service()
        summary = service.get_api_endpoints_summary(swagger_spec)

        if summary:
            print(f"✅ Опис ендпоінтів створено успішно!")
            print(f"   📊 Кількість ендпоінтів: {len(summary)}")

            # Показуємо деталі перших кількох ендпоінтів
            for i, (path, methods) in enumerate(summary.items()):
                if i >= 3:  # Показуємо тільки перші 3
                    break
                print(f"\n   🔗 {path}:")
                for method, details in methods.items():
                    print(f"      {method.upper()}: {details.get('summary', 'No summary')}")
                    print(f"         Теги: {', '.join(details.get('tags', []))}")
                    print(f"         Параметри: {details.get('parameters_count', 0)}")
                    print(f"         Відповіді: {details.get('responses_count', 0)}")

            return summary
        else:
            print("❌ Не вдалося створити опис ендпоінтів")
            return None

    except Exception as e:
        print(f"❌ Помилка: {e}")
        return None


def demo_spec_to_text(swagger_spec):
    """Демонструє конвертацію специфікації в текст"""
    print("\n📝 Демонструю конвертацію специфікації в текст...")

    try:
        from src.clickone_swagger_service import get_clickone_swagger_service

        service = get_clickone_swagger_service()
        text = service._convert_spec_to_text(swagger_spec)

        if text:
            print(f"✅ Специфікацію конвертовано в текст успішно!")
            print(f"   📊 Розмір тексту: {len(text)} символів")

            # Показуємо початок тексту
            lines = text.split("\n")[:20]  # Перші 20 рядків
            print("\n   📄 Початок тексту:")
            for line in lines:
                if line.strip():
                    print(f"      {line}")

            if len(text.split("\n")) > 20:
                remaining_lines = len(text.split("\n")) - 20
                print(f"      ... та ще {remaining_lines} рядків")

            return text
        else:
            print("❌ Не вдалося конвертувати специфікацію в текст")
            return None

    except Exception as e:
        print(f"❌ Помилка: {e}")
        return None


def demo_api_connection():
    """Демонструє перевірку з'єднання з API"""
    print("\n🔌 Демонструю перевірку з'єднання з API...")

    try:
        from src.clickone_swagger_service import get_clickone_swagger_service

        service = get_clickone_swagger_service()
        connection_works = service.validate_api_connection()

        if connection_works:
            print("✅ З'єднання з Clickone Shop API працює")
        else:
            print("⚠️ З'єднання з Clickone Shop API не працює")

        return connection_works

    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False


def demo_full_processing():
    """Демонструє повну обробку Clickone Shop API Swagger"""
    print("\n🔄 Демонструю повну обробку Clickone Shop API Swagger...")

    try:
        from src.clickone_swagger_service import get_clickone_swagger_service

        service = get_clickone_swagger_service()

        # Створюємо тестові ID
        user_id = "demo_user_123"
        spec_id = f"clickone_shop_api_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        print(f"   📊 User ID: {user_id}")
        print(f"   📊 Spec ID: {spec_id}")

        result = service.process_clickone_swagger(user_id, spec_id)

        if result and result.get("success"):
            print("✅ Обробку Clickone Shop API Swagger завершено успішно!")
            spec_info = result.get("spec_info", {})
            print(f"   📊 API Name: {spec_info.get('api_name', 'Unknown')}")
            print(f"   📊 API Version: {spec_info.get('api_version', 'Unknown')}")
            print(f"   📊 Endpoints Count: {spec_info.get('endpoints_count', 0)}")
            print(f"   📊 Parsed At: {spec_info.get('parsed_at', 'Unknown')}")

            return result
        else:
            error = result.get("error", "Unknown error") if result else "No result"
            print(f"❌ Помилка обробки: {error}")
            return None

    except Exception as e:
        print(f"❌ Помилка: {e}")
        return None


def main():
    """Головна функція"""
    print_banner()

    print("🔍 Починаю демонстрацію роботи з реальними даними Clickone Shop API...")

    # 1. Демонструємо завантаження Swagger
    swagger_spec = demo_swagger_download()

    if not swagger_spec:
        print("\n❌ Не вдалося завантажити Swagger специфікацію. Демонстрація зупинена.")
        return

    # 2. Демонструємо парсинг
    parsed_info = demo_swagger_parsing(swagger_spec)

    # 3. Демонструємо створення опису ендпоінтів
    endpoints_summary = demo_endpoints_summary(swagger_spec)

    # 4. Демонструємо конвертацію в текст
    spec_text = demo_spec_to_text(swagger_spec)

    # 5. Демонструємо перевірку з'єднання з API
    api_connection = demo_api_connection()

    # 6. Демонструємо повну обробку (без створення embeddings)
    print("\n⚠️  Пропуск створення embeddings (потребує PostgreSQL з pgvector)")
    print("   Для повного тестування запустіть в Docker з PostgreSQL")

    print("\n" + "🚀" * 50)
    print("✅ ДЕМОНСТРАЦІЯ ЗАВЕРШЕНА")
    print("🚀" * 50)
    print("\n📋 Підсумок:")
    print(f"   ✅ Swagger завантажено: {'Так' if swagger_spec else 'Ні'}")
    print(f"   ✅ Парсинг: {'Так' if parsed_info else 'Ні'}")
    print(f"   ✅ Опис ендпоінтів: {'Так' if endpoints_summary else 'Ні'}")
    print(f"   ✅ Конвертація в текст: {'Так' if spec_text else 'Ні'}")
    print(f"   ✅ З'єднання з API: {'Так' if api_connection else 'Ні'}")


if __name__ == "__main__":
    main()
