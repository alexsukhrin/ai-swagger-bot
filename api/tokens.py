"""
API endpoints для управління API токенами користувачів.
"""

import logging
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.token_manager import get_token_manager

from .auth import get_current_user
from .database import get_db
from .models import ApiToken, ApiTokenCreate, ApiTokenResponse, ApiTokenUpdate, SwaggerSpec, User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tokens", tags=["tokens"])


@router.post("/", response_model=ApiTokenResponse)
async def create_api_token(
    swagger_spec_id: str,
    token_data: ApiTokenCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Створює новий API токен для користувача."""
    try:
        # Перевіряємо чи належить Swagger специфікація користувачу
        swagger_spec = (
            db.query(SwaggerSpec)
            .filter(SwaggerSpec.id == swagger_spec_id, SwaggerSpec.user_id == current_user.id)
            .first()
        )

        if not swagger_spec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Swagger специфікацію не знайдено"
            )

        # Валідуємо формат токена
        token_manager = get_token_manager()
        if not token_manager.validate_token_format(token_data.token_value, token_data.token_type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Невірний формат токена для типу {token_data.token_type}",
            )

        # Шифруємо токен
        encrypted_token = token_manager.encrypt_token(token_data.token_value)

        # Перевіряємо чи існує вже токен з такою назвою
        existing_token = (
            db.query(ApiToken)
            .filter(
                ApiToken.user_id == current_user.id,
                ApiToken.swagger_spec_id == swagger_spec_id,
                ApiToken.token_name == token_data.token_name,
            )
            .first()
        )

        if existing_token:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Токен з назвою '{token_data.token_name}' вже існує для цієї Swagger специфікації",
            )

        # Створюємо новий токен
        api_token = ApiToken(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            swagger_spec_id=swagger_spec_id,
            token_name=token_data.token_name,
            token_value=encrypted_token,
            token_type=token_data.token_type,
            expires_at=token_data.expires_at,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db.add(api_token)
        db.commit()
        db.refresh(api_token)

        logger.info(
            f"✅ Створено API токен '{token_data.token_name}' для користувача {current_user.id}"
        )

        return ApiTokenResponse(
            id=api_token.id,
            token_name=api_token.token_name,
            token_type=api_token.token_type,
            is_active=api_token.is_active,
            expires_at=api_token.expires_at,
            last_used_at=api_token.last_used_at,
            created_at=api_token.created_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Помилка створення API токена: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Внутрішня помилка сервера"
        )


@router.get("/", response_model=List[ApiTokenResponse])
async def get_api_tokens(
    swagger_spec_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Отримує список API токенів користувача."""
    try:
        query = db.query(ApiToken).filter(ApiToken.user_id == current_user.id)

        if swagger_spec_id:
            # Перевіряємо чи належить Swagger специфікація користувачу
            swagger_spec = (
                db.query(SwaggerSpec)
                .filter(SwaggerSpec.id == swagger_spec_id, SwaggerSpec.user_id == current_user.id)
                .first()
            )

            if not swagger_spec:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Swagger специфікацію не знайдено"
                )

            query = query.filter(ApiToken.swagger_spec_id == swagger_spec_id)

        tokens = query.all()

        # Перевіряємо термін дії токенів
        token_manager = get_token_manager()
        for token in tokens:
            if token_manager.is_token_expired(token.expires_at):
                token.is_active = False
                db.commit()

        return [
            ApiTokenResponse(
                id=token.id,
                token_name=token.token_name,
                token_type=token.token_type,
                is_active=token.is_active,
                expires_at=token.expires_at,
                last_used_at=token.last_used_at,
                created_at=token.created_at,
            )
            for token in tokens
        ]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Помилка отримання API токенів: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Внутрішня помилка сервера"
        )


@router.get("/{token_id}", response_model=ApiTokenResponse)
async def get_api_token(
    token_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Отримує конкретний API токен користувача."""
    try:
        token = (
            db.query(ApiToken)
            .filter(ApiToken.id == token_id, ApiToken.user_id == current_user.id)
            .first()
        )

        if not token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="API токен не знайдено"
            )

        # Перевіряємо термін дії токена
        token_manager = get_token_manager()
        if token_manager.is_token_expired(token.expires_at):
            token.is_active = False
            db.commit()

        return ApiTokenResponse(
            id=token.id,
            token_name=token.token_name,
            token_type=token.token_type,
            is_active=token.is_active,
            expires_at=token.expires_at,
            last_used_at=token.last_used_at,
            created_at=token.created_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Помилка отримання API токена: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Внутрішня помилка сервера"
        )


@router.put("/{token_id}", response_model=ApiTokenResponse)
async def update_api_token(
    token_id: str,
    token_data: ApiTokenUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Оновлює API токен користувача."""
    try:
        token = (
            db.query(ApiToken)
            .filter(ApiToken.id == token_id, ApiToken.user_id == current_user.id)
            .first()
        )

        if not token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="API токен не знайдено"
            )

        # Валідуємо формат нового токена
        token_manager = get_token_manager()
        if not token_manager.validate_token_format(token_data.token_value, token.token_type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Невірний формат токена для типу {token.token_type}",
            )

        # Шифруємо новий токен
        encrypted_token = token_manager.encrypt_token(token_data.token_value)

        # Оновлюємо токен
        token.token_value = encrypted_token
        token.expires_at = token_data.expires_at
        token.updated_at = datetime.utcnow()
        token.is_active = True  # Активуємо токен після оновлення

        db.commit()
        db.refresh(token)

        logger.info(f"✅ Оновлено API токен '{token.token_name}' для користувача {current_user.id}")

        return ApiTokenResponse(
            id=token.id,
            token_name=token.token_name,
            token_type=token.token_type,
            is_active=token.is_active,
            expires_at=token.expires_at,
            last_used_at=token.last_used_at,
            created_at=token.created_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Помилка оновлення API токена: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Внутрішня помилка сервера"
        )


@router.delete("/{token_id}")
async def delete_api_token(
    token_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Видаляє API токен користувача."""
    try:
        token = (
            db.query(ApiToken)
            .filter(ApiToken.id == token_id, ApiToken.user_id == current_user.id)
            .first()
        )

        if not token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="API токен не знайдено"
            )

        token_name = token.token_name
        db.delete(token)
        db.commit()

        logger.info(f"✅ Видалено API токен '{token_name}' для користувача {current_user.id}")

        return {"message": f"API токен '{token_name}' успішно видалено"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Помилка видалення API токена: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Внутрішня помилка сервера"
        )


@router.get("/{token_id}/check")
async def check_token_status(
    token_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Перевіряє статус API токена (активний, закінчився, тощо)."""
    try:
        token = (
            db.query(ApiToken)
            .filter(ApiToken.id == token_id, ApiToken.user_id == current_user.id)
            .first()
        )

        if not token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="API токен не знайдено"
            )

        token_manager = get_token_manager()

        # Перевіряємо термін дії
        is_expired = token_manager.is_token_expired(token.expires_at)
        warning_message = token_manager.get_token_expiry_warning(token.expires_at)

        # Оновлюємо статус якщо токен закінчився
        if is_expired and token.is_active:
            token.is_active = False
            db.commit()

        return {
            "token_id": token.id,
            "token_name": token.token_name,
            "is_active": token.is_active and not is_expired,
            "is_expired": is_expired,
            "expires_at": token.expires_at,
            "warning_message": warning_message,
            "last_used_at": token.last_used_at,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Помилка перевірки статусу API токена: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Внутрішня помилка сервера"
        )


@router.post("/{token_id}/use")
async def mark_token_as_used(
    token_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Позначає токен як використаний (оновлює last_used_at)."""
    try:
        token = (
            db.query(ApiToken)
            .filter(ApiToken.id == token_id, ApiToken.user_id == current_user.id)
            .first()
        )

        if not token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="API токен не знайдено"
            )

        # Оновлюємо час останнього використання
        token.last_used_at = datetime.utcnow()
        db.commit()

        logger.info(
            f"✅ Позначено використання API токена '{token.token_name}' для користувача {current_user.id}"
        )

        return {"message": "Токен позначено як використаний"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Помилка позначення використання API токена: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Внутрішня помилка сервера"
        )
