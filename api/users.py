"""
Endpoints для управління користувачами
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .auth import authenticate_user, create_demo_user, create_user, get_current_user
from .database import get_db
from .models import User, UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserResponse)
async def register_user(user_create: UserCreate, db: Session = Depends(get_db)):
    """Реєстрація нового користувача"""
    try:
        user = create_user(db, user_create)
        return UserResponse.from_orm(user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка створення користувача: {str(e)}",
        )


@router.post("/demo")
async def create_demo_user_endpoint(db: Session = Depends(get_db)):
    """Створює демо користувача"""
    try:
        result = create_demo_user(db)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка створення демо користувача: {str(e)}",
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Отримує інформацію про поточного користувача"""
    return UserResponse.from_orm(current_user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Отримує інформацію про користувача (тільки власну)"""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Немає прав для перегляду інформації про іншого користувача",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Користувача не знайдено")

    return UserResponse.from_orm(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Оновлює інформацію про користувача (тільки власну)"""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Немає прав для оновлення інформації про іншого користувача",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Користувача не знайдено")

    # Оновлюємо дані
    user.email = user_update.email
    user.username = user_update.username
    user.hashed_password = user_update.password  # В реальному проекті потрібно хешувати
    user.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(user)

    return UserResponse.from_orm(user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Видаляє користувача (тільки власного)"""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Немає прав для видалення іншого користувача",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Користувача не знайдено")

    # Деактивуємо користувача замість видалення
    user.is_active = False
    user.updated_at = datetime.utcnow()

    db.commit()

    return {"message": "Користувача деактивовано успішно"}
