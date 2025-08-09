#!/usr/bin/env python3
"""
Скрипт для створення демо користувача та генерації JWT токена
"""

import os
import sys
from datetime import datetime, timedelta

from jose import jwt

# Додаємо шлях до модуля
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config


def create_demo_user():
    """Створює демо користувача та повертає токен"""
    config = Config()

    user_id = f"demo_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    payload = {
        "sub": user_id,
        "name": "Demo User",
        "email": "demo@ai-swagger-bot.com",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=24),
    }

    token = jwt.encode(payload, config.JWT_SECRET_KEY, algorithm="HS256")

    print("🎉 Демо користувач створено успішно!")
    print(f"👤 User ID: {user_id}")
    print(f"🔑 JWT Token: {token}")
    print(f"⏰ Токен дійсний: 24 години")
    print("\n📝 Використання:")
    print(f'curl -H "Authorization: Bearer {token}" http://localhost:8000/health')
    print(
        f'curl -X POST -H "Authorization: Bearer {token}" -F "file=@examples/swagger_specs/shop_api.json" http://localhost:8000/upload-swagger'
    )

    return user_id, token


if __name__ == "__main__":
    create_demo_user()
