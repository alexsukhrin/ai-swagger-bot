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
from .models import User, UserCreate, UserResponse

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
    """Створює нового користувача"""
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
    """Створює демо користувача"""
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
    db.commit()
    db.refresh(user)

    # Створюємо токен
    token = create_user_token(user_id=user_id, user_name="Demo User", user_email=user.email)

    return {
        "user_id": user_id,
        "token": token,
        "message": "Демо користувач створено успішно",
        "expires_in": "24 hours",
    }
