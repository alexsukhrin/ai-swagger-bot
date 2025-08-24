#!/usr/bin/env python3
"""
Тестування реальних ендпоінтів Clickone Shop API
"""

import requests

# Конфігурація
CLICKONE_SHOP_API_URL = "https://api.oneshop.click"


def test_real_api_endpoints():
    """Тестує реальні ендпоінти API та показує їх кількість"""
    print("🔍 Тестую реальні ендпоінти API...")

    # Список ендпоінтів для тестування
    endpoints_to_test = [
        ("/api/categories", "GET"),
        ("/api/products", "GET"),
        ("/api/brands", "GET"),
        ("/api/orders", "GET"),
        ("/api/customers", "GET"),
        ("/api/users", "GET"),
        ("/api/collections", "GET"),
        ("/api/families", "GET"),
        ("/api/attributes", "GET"),
        ("/api/settings", "GET"),
        ("/api/warehouse", "GET"),
    ]

    working_endpoints = []

    for endpoint, method in endpoints_to_test:
        try:
            response = requests.get(
                f"{CLICKONE_SHOP_API_URL}{endpoint}",
                timeout=10,
                headers={"User-Agent": "AI-Swagger-Bot/1.0"},
            )

            if response.status_code == 200:
                print(f"✅ {method} {endpoint}: HTTP {response.status_code}")
                working_endpoints.append(endpoint)
            elif response.status_code == 401:
                print(
                    f"🔒 {method} {endpoint}: HTTP {response.status_code} (Unauthorized - потребує токен)"
                )
                working_endpoints.append(endpoint)
            elif response.status_code == 404:
                print(f"❌ {method} {endpoint}: HTTP {response.status_code} (Not Found)")
            else:
                print(f"⚠️  {method} {endpoint}: HTTP {response.status_code}")

        except Exception as e:
            print(f"❌ {method} {endpoint}: Помилка - {e}")

    print(f"\n📊 Результат тестування:")
    print(f"   ✅ Працюючі ендпоінти: {len(working_endpoints)}")
    print(f"   📋 Список працюючих ендпоінтів:")
    for endpoint in working_endpoints:
        print(f"      • {endpoint}")

    return working_endpoints


def main():
    """Головна функція"""
    print("🚀 Тестування реальних ендпоінтів Clickone Shop API")
    print("=" * 60)

    working_endpoints = test_real_api_endpoints()

    print(f"\n🎯 Висновок:")
    print(f"   Swagger документація показує тільки 2 ендпоінти категорій")
    print(f"   Але реально API має {len(working_endpoints)}+ працюючих ендпоінтів")
    print(f"   Це означає, що /docs/ai-json - це обмежена версія для AI")


if __name__ == "__main__":
    main()
