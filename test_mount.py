#!/usr/bin/env python3

import sys
from pathlib import Path

# Додаємо кореневу директорію до шляху
sys.path.append(str(Path(__file__).parent))

from fastapi import FastAPI

# Створюємо простий тестовий додаток
test_app = FastAPI()


@test_app.get("/")
def test_root():
    return {"message": "Test app works"}


# Тестуємо монтування
from api.admin_ui import admin_app

print("✅ admin_app імпортовано")
print(f"admin_app routes: {len(admin_app.routes)}")

# Монтуємо admin_app
test_app.mount("/admin-ui", admin_app)

print("✅ admin_app змонтовано")

# Перевіряємо монти
mounts = [
    route for route in test_app.routes if hasattr(route, "path") and "/admin-ui" in str(route.path)
]
print(f"Found {len(mounts)} admin-ui mounts")

if len(mounts) > 0:
    print("✅ Монтування працює!")
else:
    print("❌ Монтування не працює")
