"""
Система авторизації та управління користувачами
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.config import Config

from .database import get_db
from .models import PromptTemplate, User, UserCreate


def load_base_prompts_for_user(db: Session, user_id: str) -> bool:
    """Загружает базовые промпты для пользователя из YAML файла"""
    try:
        # Импортируем функцию безпосередньо
        import os
        from pathlib import Path

        import yaml

        # Шлях до YAML файлу з промптами
        yaml_path = Path("prompts/base_prompts.yaml")

        if not yaml_path.exists():
            print("⚠️ Файл prompts/base_prompts.yaml не знайдено")
            return False

        with open(yaml_path, "r", encoding="utf-8") as file:
            yaml_data = yaml.safe_load(file)

        # Обробляємо промпти з секції prompts
        prompts_data = yaml_data.get("prompts", {})
        base_prompts = []

        for prompt_id, prompt_data in prompts_data.items():
            prompt = {
                "name": prompt_data.get("name", ""),
                "description": prompt_data.get("description", ""),
                "template": prompt_data.get("template", ""),
                "category": prompt_data.get("category", "general"),
            }
            base_prompts.append(prompt)

        print(f"📋 Знайдено {len(base_prompts)} базових промптів")

        for i, prompt_data in enumerate(base_prompts):
            print(f"📝 Створюю промпт {i+1}/{len(base_prompts)}: {prompt_data['name']}")
            # Створюємо копію промпту для користувача
            user_prompt = PromptTemplate(
                id=str(uuid.uuid4()),
                user_id=user_id,  # Прив'язуємо до користувача
                name=prompt_data["name"],
                description=prompt_data["description"],
                template=prompt_data["template"],
                category=prompt_data["category"],
                is_public=False,  # Промпти користувача не публічні
                is_active=True,
                usage_count=0,
                success_rate=0,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            db.add(user_prompt)

        print(f"✅ Створено {len(base_prompts)} базових промптів для користувача {user_id}")
        return True

    except Exception as e:
        print(f"⚠️ Помилка завантаження базових промптів: {e}")
        import traceback

        traceback.print_exc()
        return False


# Налаштування
config = Config()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Перевіряє пароль"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хешує пароль"""
    return pwd_context.hash(password)


def create_user_token(user_id: str, user_name: str = None, user_email: str = None) -> str:
    """Створює JWT токен для користувача"""
    payload = {
        "sub": user_id,
        "name": user_name or f"User {user_id}",
        "email": user_email or f"{user_id}@demo.com",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=24),
    }
    return jwt.encode(payload, config.JWT_SECRET_KEY, algorithm="HS256")


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Перевірка JWT токена"""
    try:
        payload = jwt.decode(credentials.credentials, config.JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(user_id: str = Depends(verify_token), db: Session = Depends(get_db)) -> User:
    """Отримує поточного користувача"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Користувача не знайдено")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Користувач неактивний")
    return user


def create_user(db: Session, user_create: UserCreate) -> User:
    """Створює нового користувача з базовими промптами"""
    # Перевіряємо чи існує користувач з таким email
    existing_user = db.query(User).filter(User.email == user_create.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Користувач з таким email вже існує"
        )

    # Перевіряємо чи існує користувач з таким username
    existing_user = db.query(User).filter(User.username == user_create.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Користувач з таким username вже існує"
        )

    # Створюємо нового користувача
    user = User(
        id=str(uuid.uuid4()),
        email=user_create.email,
        username=user_create.username,
        hashed_password=get_password_hash(user_create.password),
        is_active=True,
    )

    db.add(user)
    db.flush()  # Отримуємо ID користувача без коміту
    db.refresh(user)

    # Завантажуємо базові промпти для користувача
    print(f"🔍 Завантажую базові промпти для користувача {user.id}")
    load_base_prompts_for_user(db, user.id)

    # Комітуємо всі зміни
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Аутентифікує користувача"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_demo_user(db: Session) -> dict:
    """Створює демо користувача з базовими промптами"""
    user_id = f"demo_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Створюємо користувача в базі даних
    user = User(
        id=user_id,
        email=f"{user_id}@demo.com",
        username=user_id,
        hashed_password=get_password_hash("demo_password"),
        is_active=True,
    )

    db.add(user)
    db.flush()  # Отримуємо ID користувача без коміту
    db.refresh(user)

    # Завантажуємо базові промпти для користувача
    print(f"🔍 Завантажую базові промпти для користувача {user.id}")
    load_base_prompts_for_user(db, user.id)

    # Комітуємо всі зміни
    db.commit()

    # Створюємо токен
    token = create_user_token(user_id=user_id, user_name="Demo User", user_email=user.email)

    return {
        "user_id": user_id,
        "token": token,
        "message": "Демо користувач створено успішно з базовими промптами",
        "expires_in": "24 hours",
    }
