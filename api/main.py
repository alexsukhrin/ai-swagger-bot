"""
FastAPI сервіс для AI Swagger Bot
"""

import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.config import Config
from src.enhanced_swagger_parser import EnhancedSwaggerParser
from src.interactive_api_agent import InteractiveSwaggerAgent
from src.rag_engine import PostgresRAGEngine

from .admin import setup_admin
from .auth import create_demo_user, get_current_user, verify_token
from .database import get_db
from .models import (
    ApiEmbedding,
    ApiToken,
    ChatMessage,
    ChatSession,
)
from .models import PromptTemplate as DBPromptTemplate
from .models import (
    SwaggerSpec,
    User,
)
from .prompts import router as prompts_router
from .tokens import router as tokens_router
from .users import router as users_router

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Swagger Bot API",
    description="API для роботи зі Swagger специфікаціями та виконання API запитів",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшені вкажіть конкретні домени
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Налаштування адмін панелі
admin = setup_admin(app)

# Підключаємо адмін веб-інтерфейс
from .admin_ui import admin_app

app.mount("/admin", admin_app)

# Підключаємо роутери
app.include_router(prompts_router)
app.include_router(users_router)
app.include_router(tokens_router)

# Security
security = HTTPBearer()


# Моделі Pydantic
class UserRequest(BaseModel):
    message: str
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    user_id: str
    timestamp: datetime
    swagger_id: Optional[str] = None


class SwaggerUploadResponse(BaseModel):
    swagger_id: str
    message: str
    endpoints_count: int
    requires_tokens: bool = False
    token_requirements: List[str] = []


class EmbeddingsResponse(BaseModel):
    embeddings_count: int
    user_id: str
    swagger_spec_id: str
    message: str


def get_user_session(db: Session, user_id: str) -> ChatSession:
    """Отримує або створює сесію чату для користувача."""
    logger.info(f"🔍 Шукаємо активну сесію для користувача {user_id}")

    # Спочатку очищаємо старі сесії
    cleanup_old_sessions(db, user_id)

    session = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id, ChatSession.is_active == True)
        .first()
    )

    if session:
        logger.info(f"✅ Знайдено активну сесію: {session.id} (створена: {session.created_at})")
        return session

    # Якщо активна сесія не знайдена, шукаємо останню неактивну
    last_session = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .order_by(ChatSession.created_at.desc())
        .first()
    )

    if last_session:
        logger.warning(f"⚠️ Активна сесія не знайдена, але є неактивна: {last_session.id}")
        logger.warning(f"   Остання сесія створена: {last_session.created_at}")
        logger.warning(f"   Статус: is_active={last_session.is_active}")

        # Активуємо останню сесію замість створення нової
        last_session.is_active = True
        last_session.updated_at = datetime.now()
        db.commit()
        db.refresh(last_session)

        logger.info(f"✅ Активовано існуючу сесію: {last_session.id}")
        return last_session

    # Створюємо нову сесію тільки якщо немає жодної
    logger.info(f"🆕 Створюємо нову сесію для користувача {user_id}")
    session = ChatSession(
        id=str(uuid.uuid4()),
        user_id=user_id,
        session_name="Default Session",
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    logger.info(f"✅ Створено нову сесію: {session.id}")
    return session


def check_swagger_token_requirements(swagger_data: dict) -> tuple[bool, List[str]]:
    """
    Перевіряє чи потребує Swagger специфікація API токенів.

    Args:
        swagger_data: Дані Swagger специфікації

    Returns:
        Tuple (потребує токенів, список назв токенів)
    """
    requires_tokens = False
    token_requirements = []

    try:
        # Перевіряємо security schemes
        security_schemes = swagger_data.get("components", {}).get("securitySchemes", {})

        for scheme_name, scheme_data in security_schemes.items():
            scheme_type = scheme_data.get("type", "")

            if scheme_type in ["apiKey", "http", "oauth2"]:
                requires_tokens = True
                token_requirements.append(scheme_name)

        # Перевіряємо глобальні security вимоги
        global_security = swagger_data.get("security", [])
        if global_security:
            requires_tokens = True
            for security_req in global_security:
                for req_name in security_req.keys():
                    if req_name not in token_requirements:
                        token_requirements.append(req_name)

        return requires_tokens, token_requirements

    except Exception as e:
        logger.error(f"Помилка перевірки вимог токенів: {e}")
        return False, []


def cleanup_old_sessions(db: Session, user_id: str, keep_last: int = 5):
    """Очищає старі неактивні сесії користувача, залишаючи останні N."""
    try:
        # Отримуємо всі неактивні сесії користувача
        inactive_sessions = (
            db.query(ChatSession)
            .filter(ChatSession.user_id == user_id, ChatSession.is_active == False)
            .order_by(ChatSession.created_at.desc())
            .all()
        )

        # Залишаємо тільки останні N сесій
        sessions_to_delete = (
            inactive_sessions[keep_last:] if len(inactive_sessions) > keep_last else []
        )

        if sessions_to_delete:
            logger.info(
                f"🗑️ Видаляємо {len(sessions_to_delete)} старих сесій для користувача {user_id}"
            )

            for session in sessions_to_delete:
                # Спочатку видаляємо повідомлення
                db.query(ChatMessage).filter(ChatMessage.chat_session_id == session.id).delete()

                # Потім видаляємо сесію
                db.delete(session)

            db.commit()
            logger.info(f"✅ Видалено {len(sessions_to_delete)} старих сесій")

        return len(sessions_to_delete)

    except Exception as e:
        logger.error(f"Помилка очищення сесій: {e}")
        db.rollback()
        return 0


@app.get("/health")
async def health_check():
    """Перевірка стану сервісу."""
    try:
        from api.database import get_db

        db = next(get_db())

        # Отримуємо статистику
        users_count = db.query(User).filter(User.is_active == True).count()
        swagger_specs_count = db.query(SwaggerSpec).filter(SwaggerSpec.is_active == True).count()

        return {
            "status": "healthy",
            "timestamp": datetime.now(),
            "active_users": users_count,
            "swagger_specs_count": swagger_specs_count,
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"status": "error", "timestamp": datetime.now(), "error": str(e)}


@app.post("/upload-swagger", response_model=SwaggerUploadResponse)
async def upload_swagger(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Завантаження Swagger специфікації."""
    try:
        # Перевіряємо тип файлу
        if not file.filename.endswith(".json"):
            raise HTTPException(status_code=400, detail="Підтримуються тільки JSON файли")

        # Читаємо файл
        content = await file.read()
        swagger_data = json.loads(content.decode("utf-8"))

        # Парсимо Swagger
        parser = EnhancedSwaggerParser()
        parsed_data = parser.parse_swagger_spec(swagger_data)

        # Перевіряємо вимоги токенів
        requires_tokens, token_requirements = check_swagger_token_requirements(swagger_data)

        # Генеруємо ID
        swagger_id = str(uuid.uuid4())

        # Зберігаємо специфікацію в базу даних
        swagger_spec = SwaggerSpec(
            id=swagger_id,
            user_id=current_user.id,  # Прив'язуємо до користувача
            filename=file.filename,
            original_data=swagger_data,
            parsed_data=parsed_data,
            endpoints_count=len(parsed_data.get("endpoints", [])),
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db.add(swagger_spec)

        # Оновлюємо сесію користувача
        session = get_user_session(db, current_user.id)
        session.swagger_spec_id = swagger_id
        db.commit()

        # Створюємо embeddings для цього Swagger файлу
        try:
            # Створюємо тимчасовий файл
            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
                temp_file.write(json.dumps(swagger_data))
                temp_file_path = temp_file.name

            try:
                # Створюємо RAG engine для конкретного користувача
                rag_engine = PostgresRAGEngine(user_id=current_user.id, swagger_spec_id=swagger_id)

                # Створюємо embeddings
                success = rag_engine.create_vectorstore_from_swagger(temp_file_path)

                if success:
                    logger.info(f"✅ Створено embeddings для користувача {current_user.id}")
                else:
                    logger.warning(
                        f"⚠️ Не вдалося створити embeddings для користувача {current_user.id}"
                    )

            finally:
                # Видаляємо тимчасовий файл
                os.unlink(temp_file_path)

        except Exception as e:
            logger.error(f"Помилка створення embeddings: {e}")
            # Не блокуємо завантаження Swagger, якщо embeddings не створилися

        return SwaggerUploadResponse(
            swagger_id=swagger_id,
            message="Swagger специфікація успішно завантажена",
            endpoints_count=len(parsed_data.get("endpoints", [])),
            requires_tokens=requires_tokens,
            token_requirements=token_requirements,
        )

    except Exception as e:
        logger.error(f"Error uploading swagger: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: UserRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Чат з AI агентом."""
    try:
        session = get_user_session(db, current_user.id)

        if not session.swagger_spec_id:
            raise HTTPException(status_code=400, detail="Спочатку завантажте Swagger специфікацію")

        # Отримуємо Swagger специфікацію з бази даних (тільки для поточного користувача)
        swagger_spec = (
            db.query(SwaggerSpec)
            .filter(
                SwaggerSpec.id == session.swagger_spec_id, SwaggerSpec.user_id == current_user.id
            )
            .first()
        )
        if not swagger_spec:
            raise HTTPException(status_code=404, detail="Swagger специфікація не знайдена")

        # Перевіряємо чи є активні токени для цієї специфікації
        active_tokens = (
            db.query(ApiToken)
            .filter(
                ApiToken.user_id == current_user.id,
                ApiToken.swagger_spec_id == session.swagger_spec_id,
                ApiToken.is_active == True,
            )
            .all()
        )

        # Перевіряємо термін дії токенів
        from src.token_manager import get_token_manager

        token_manager = get_token_manager()

        expired_tokens = []
        for token in active_tokens:
            if token_manager.is_token_expired(token.expires_at):
                token.is_active = False
                expired_tokens.append(token.token_name)

        if expired_tokens:
            db.commit()
            raise HTTPException(
                status_code=400,
                detail=f"Наступні токени закінчилися: {', '.join(expired_tokens)}. Будь ласка, оновіть їх.",
            )

        # Створюємо RAG engine для конкретного користувача
        rag_engine = PostgresRAGEngine(
            user_id=current_user.id, swagger_spec_id=session.swagger_spec_id
        )

        # Створюємо API агента з тимчасовим файлом
        import os
        import tempfile

        # Створюємо тимчасовий файл з даними Swagger
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
            temp_file.write(json.dumps(swagger_spec.original_data))
            temp_file_path = temp_file.name

        try:
            # Створюємо API агента з тимчасовим файлом
            agent = InteractiveSwaggerAgent(temp_file_path)

            # Отримуємо контекст з RAG для конкретного користувача
            similar_endpoints = rag_engine.search_similar_endpoints(request.message, limit=3)

            # Додаємо контекст до запиту
            context = ""
            if similar_endpoints:
                context = "Релевантні endpoints:\n"
                for endpoint in similar_endpoints:
                    context += f"- {endpoint['method']} {endpoint['endpoint_path']}: {endpoint['description']}\n"

            # Виконуємо запит з контекстом
            if context:
                enhanced_message = f"{request.message}\n\nКонтекст:\n{context}"
            else:
                enhanced_message = request.message

            response = agent.process_query(enhanced_message)

        finally:
            # Видаляємо тимчасовий файл
            os.unlink(temp_file_path)

        # Зберігаємо повідомлення в чат
        chat_message = ChatMessage(
            id=str(uuid.uuid4()),
            chat_session_id=session.id,
            role="user",
            content=request.message,
            created_at=datetime.now(),
        )
        db.add(chat_message)

        assistant_message = ChatMessage(
            id=str(uuid.uuid4()),
            chat_session_id=session.id,
            role="assistant",
            content=response,
            created_at=datetime.now(),
        )
        db.add(assistant_message)
        db.commit()

        return ChatResponse(
            response=response,
            user_id=current_user.id,
            timestamp=datetime.now(),
            swagger_id=session.swagger_spec_id,
        )

    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/chat-history")
async def get_chat_history(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Отримання історії чату користувача."""
    try:
        session = get_user_session(db, current_user.id)

        messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.chat_session_id == session.id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )

        return [
            {"id": msg.id, "role": msg.role, "content": msg.content, "created_at": msg.created_at}
            for msg in messages
        ]
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/swagger-specs")
async def get_swagger_specs(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Отримання списку Swagger специфікацій користувача."""
    specs = (
        db.query(SwaggerSpec)
        .filter(SwaggerSpec.user_id == current_user.id, SwaggerSpec.is_active == True)
        .all()
    )
    return [
        {"id": spec.id, "filename": spec.filename, "created_at": spec.created_at} for spec in specs
    ]


@app.get("/embeddings/{swagger_spec_id}")
async def get_embeddings(
    swagger_spec_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Отримання embeddings для конкретної Swagger специфікації користувача."""
    try:
        # Перевіряємо чи належить Swagger специфікація користувачу
        swagger_spec = (
            db.query(SwaggerSpec)
            .filter(SwaggerSpec.id == swagger_spec_id, SwaggerSpec.user_id == current_user.id)
            .first()
        )

        if not swagger_spec:
            raise HTTPException(status_code=404, detail="Swagger специфікація не знайдена")

        # Отримуємо embeddings для цього користувача та Swagger специфікації
        embeddings = (
            db.query(ApiEmbedding)
            .filter(
                ApiEmbedding.user_id == current_user.id,
                ApiEmbedding.swagger_spec_id == swagger_spec_id,
            )
            .all()
        )

        return {
            "embeddings_count": len(embeddings),
            "user_id": current_user.id,
            "swagger_spec_id": swagger_spec_id,
            "message": f"Знайдено {len(embeddings)} embeddings",
        }

    except Exception as e:
        logger.error(f"Error getting embeddings: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/embeddings/{swagger_spec_id}")
async def delete_embeddings(
    swagger_spec_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Видалення embeddings для конкретної Swagger специфікації користувача."""
    try:
        # Перевіряємо чи належить Swagger специфікація користувачу
        swagger_spec = (
            db.query(SwaggerSpec)
            .filter(SwaggerSpec.id == swagger_spec_id, SwaggerSpec.user_id == current_user.id)
            .first()
        )

        if not swagger_spec:
            raise HTTPException(status_code=404, detail="Swagger специфікація не знайдена")

        # Видаляємо embeddings через RAG engine
        rag_engine = PostgresRAGEngine(user_id=current_user.id, swagger_spec_id=swagger_spec_id)

        success = rag_engine.delete_user_embeddings()

        if success:
            return {"message": "Embeddings успішно видалено"}
        else:
            raise HTTPException(status_code=500, detail="Помилка видалення embeddings")

    except Exception as e:
        logger.error(f"Error deleting embeddings: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/statistics")
async def get_statistics(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Отримання статистики для користувача."""
    try:
        # Статистика Swagger специфікацій
        swagger_specs_count = (
            db.query(SwaggerSpec)
            .filter(SwaggerSpec.user_id == current_user.id, SwaggerSpec.is_active == True)
            .count()
        )

        # Статистика embeddings
        embeddings_count = (
            db.query(ApiEmbedding).filter(ApiEmbedding.user_id == current_user.id).count()
        )

        # Статистика повідомлень
        messages_count = (
            db.query(ChatMessage)
            .join(ChatSession)
            .filter(ChatSession.user_id == current_user.id)
            .count()
        )

        # Статистика токенів
        tokens_count = db.query(ApiToken).filter(ApiToken.user_id == current_user.id).count()

        # Перевіряємо закінчені токени
        from src.token_manager import get_token_manager

        token_manager = get_token_manager()
        expired_tokens = (
            db.query(ApiToken)
            .filter(ApiToken.user_id == current_user.id, ApiToken.is_active == True)
            .all()
        )

        expired_count = 0
        for token in expired_tokens:
            if token_manager.is_token_expired(token.expires_at):
                token.is_active = False
                expired_count += 1

        if expired_count > 0:
            db.commit()

        return {
            "user_id": current_user.id,
            "swagger_specs_count": swagger_specs_count,
            "embeddings_count": embeddings_count,
            "messages_count": messages_count,
            "tokens_count": tokens_count,
            "expired_tokens_count": expired_count,
        }

    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/debug/sessions")
async def debug_user_sessions(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Діагностика сесій користувача."""
    try:
        # Отримуємо всі сесії користувача
        sessions = (
            db.query(ChatSession)
            .filter(ChatSession.user_id == current_user.id)
            .order_by(ChatSession.created_at.desc())
            .all()
        )

        # Отримуємо повідомлення для кожної сесії
        sessions_info = []
        for session in sessions:
            messages_count = (
                db.query(ChatMessage).filter(ChatMessage.chat_session_id == session.id).count()
            )

            sessions_info.append(
                {
                    "session_id": session.id,
                    "session_name": session.session_name,
                    "is_active": session.is_active,
                    "created_at": session.created_at,
                    "updated_at": session.updated_at,
                    "swagger_spec_id": session.swagger_spec_id,
                    "messages_count": messages_count,
                }
            )

        return {
            "user_id": current_user.id,
            "total_sessions": len(sessions),
            "active_sessions": len([s for s in sessions if s.is_active]),
            "sessions": sessions_info,
        }

    except Exception as e:
        logger.error(f"Error in debug_sessions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
