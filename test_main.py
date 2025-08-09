#!/usr/bin/env python3

import sys
from pathlib import Path

# Додаємо кореневу директорію до шляху
sys.path.append(str(Path(__file__).parent))

try:
    # Імпортуємо main.py
    from api.main import app

    print("✅ main.py імпортовано успішно")
    print(f"app routes: {len(app.routes)}")

    # Перевіряємо монти
    mounts = [
        route for route in app.routes if hasattr(route, "path") and "/admin-ui" in str(route.path)
    ]
    print(f"Found {len(mounts)} admin-ui mounts")

    if len(mounts) > 0:
        print("✅ admin-ui монт знайдено!")
        for mount in mounts:
            print(f"  {mount.path} -> {mount.app}")
    else:
        print("❌ admin-ui монт не знайдено")

        # Перевіряємо всі монти
        all_mounts = [route for route in app.routes if hasattr(route, "path")]
        print(f"Всі монти ({len(all_mounts)}):")
        for mount in all_mounts:
            print(f"  {mount.path} -> {mount.app}")

except Exception as e:
    print(f"❌ Помилка імпорту main.py: {e}")
    import traceback

    traceback.print_exc()
