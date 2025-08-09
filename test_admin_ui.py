#!/usr/bin/env python3

import sys
from pathlib import Path

# Додаємо кореневу директорію до шляху
sys.path.append(str(Path(__file__).parent))

try:
    from api.admin_ui import admin_app

    print("✅ admin_app імпортовано успішно")
    print(f"admin_app: {admin_app}")
    print(f"admin_app routes: {len(admin_app.routes)}")

    # Перевіряємо маршрути
    for route in admin_app.routes:
        if hasattr(route, "path"):
            print(f"  {route.methods} {route.path}")

except Exception as e:
    print(f"❌ Помилка імпорту admin_ui: {e}")
    import traceback

    traceback.print_exc()
