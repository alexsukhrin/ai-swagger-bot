"""
AWS Lambda handler для AI Swagger Bot API
Використовує Mangum для адаптації FastAPI додатку до AWS Lambda
"""

import os
import sys
from pathlib import Path

# Додаємо кореневу директорію проекту до Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Імпортуємо Mangum для AWS Lambda
from mangum import Mangum

# Імпортуємо FastAPI додаток
from api.main import app

# Створюємо Mangum handler
# lifespan="off" вимикає startup/shutdown події, що краще для Lambda
handler = Mangum(app, lifespan="off")

# Альтернативний варіант з включеними lifespan подіями
# handler = Mangum(app, lifespan="on")

# Для тестування локально можна використовувати:
if __name__ == "__main__":
    import uvicorn

    print("🚀 Запуск FastAPI додатку локально...")
    print("📝 Для AWS Lambda використовуйте handler.lambda_handler")
    uvicorn.run(app, host="0.0.0.0", port=8000)
