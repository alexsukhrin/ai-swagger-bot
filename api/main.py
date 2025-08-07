"""
FastAPI сервіс для AI Swagger Bot
"""

import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import jwt
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from src.config import Config
from src.enhanced_swagger_parser import EnhancedSwaggerParser
from src.interactive_api_agent import InteractiveAPIAgent
from src.rag_engine import RAGEngine

from .admin import setup_admin

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

# Security
security = HTTPBearer()


# Моделі Pydantic
class UserRequest(BaseModel):
    message: str
    user_id: Optional[str] = None


class SwaggerUploadResponse(BaseModel):
    swagger_id: str
    message: str
    endpoints_count: int


class ChatResponse(BaseModel):
    response: str
    user_id: str
    timestamp: datetime
    swagger_id: Optional[str] = None


class PromptTemplate(BaseModel):
    name: str
    description: str
    template: str
    category: str


# Глобальні змінні (в продакшені замінити на БД)
swagger_specs: Dict[str, Any] = {}
user_sessions: Dict[str, Dict[str, Any]] = {}
prompt_templates: Dict[str, PromptTemplate] = {}

# Конфігурація
config = Config()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Перевірка JWT токена"""
    try:
        payload = jwt.decode(credentials.credentials, config.jwt_secret_key, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_user_session(user_id: str) -> Dict[str, Any]:
    """Отримання сесії користувача"""
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "swagger_id": None,
            "chat_history": [],
            "created_at": datetime.now(),
        }
    return user_sessions[user_id]


@app.get("/")
async def root():
    """Кореневий endpoint"""
    return {"message": "AI Swagger Bot API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "active_users": len(user_sessions),
        "swagger_specs_count": len(swagger_specs),
    }


@app.post("/upload-swagger", response_model=SwaggerUploadResponse)
async def upload_swagger(file: UploadFile = File(...), user_id: str = Depends(verify_token)):
    """Завантаження Swagger специфікації"""
    try:
        # Читаємо файл
        content = await file.read()

        # Парсимо JSON
        try:
            swagger_data = json.loads(content.decode())
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON file")

        # Створюємо унікальний ID для специфікації
        swagger_id = str(uuid.uuid4())

        # Парсимо Swagger
        parser = EnhancedSwaggerParser()
        parsed_data = parser.parse_swagger_spec(swagger_data)

        # Зберігаємо специфікацію
        swagger_specs[swagger_id] = {
            "data": swagger_data,
            "parsed": parsed_data,
            "uploaded_by": user_id,
            "uploaded_at": datetime.now(),
            "filename": file.filename,
        }

        # Оновлюємо сесію користувача
        session = get_user_session(user_id)
        session["swagger_id"] = swagger_id

        return SwaggerUploadResponse(
            swagger_id=swagger_id,
            message="Swagger специфікація успішно завантажена",
            endpoints_count=len(parsed_data.get("endpoints", [])),
        )

    except Exception as e:
        logger.error(f"Error uploading swagger: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: UserRequest, user_id: str = Depends(verify_token)):
    """Чат з AI агентом"""
    try:
        session = get_user_session(user_id)

        if not session["swagger_id"]:
            raise HTTPException(status_code=400, detail="Спочатку завантажте Swagger специфікацію")

        swagger_data = swagger_specs[session["swagger_id"]]

        # Створюємо RAG engine
        rag_engine = RAGEngine()
        rag_engine.add_swagger_data(swagger_data["parsed"])

        # Створюємо API агента
        agent = InteractiveAPIAgent(swagger_parser=EnhancedSwaggerParser(), rag_engine=rag_engine)

        # Виконуємо запит
        response = await agent.process_user_query(
            request.message, user_id=user_id, chat_history=session["chat_history"]
        )

        # Зберігаємо в історію
        chat_entry = {
            "user_message": request.message,
            "ai_response": response,
            "timestamp": datetime.now(),
        }
        session["chat_history"].append(chat_entry)

        return ChatResponse(
            response=response,
            user_id=user_id,
            timestamp=datetime.now(),
            swagger_id=session["swagger_id"],
        )

    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/chat-history")
async def get_chat_history(user_id: str = Depends(verify_token)):
    """Отримання історії чату"""
    session = get_user_session(user_id)
    return {
        "user_id": user_id,
        "chat_history": session["chat_history"],
        "swagger_id": session["swagger_id"],
    }


@app.post("/prompts")
async def create_prompt_template(prompt: PromptTemplate, user_id: str = Depends(verify_token)):
    """Створення нового промпт шаблону"""
    prompt_id = str(uuid.uuid4())
    prompt_templates[prompt_id] = prompt
    return {"prompt_id": prompt_id, "message": "Промпт шаблон створено"}


@app.get("/prompts")
async def get_prompt_templates(user_id: str = Depends(verify_token)):
    """Отримання всіх промпт шаблонів"""
    return {"prompts": list(prompt_templates.values())}


@app.delete("/swagger/{swagger_id}")
async def delete_swagger(swagger_id: str, user_id: str = Depends(verify_token)):
    """Видалення Swagger специфікації"""
    if swagger_id not in swagger_specs:
        raise HTTPException(status_code=404, detail="Swagger специфікація не знайдена")

    # Перевіряємо права доступу
    if swagger_specs[swagger_id]["uploaded_by"] != user_id:
        raise HTTPException(status_code=403, detail="Немає прав для видалення")

    del swagger_specs[swagger_id]

    # Очищаємо сесії користувачів, які використовували цю специфікацію
    for session in user_sessions.values():
        if session["swagger_id"] == swagger_id:
            session["swagger_id"] = None

    return {"message": "Swagger специфікація видалена"}


@app.get("/swagger-specs")
async def get_swagger_specs(user_id: str = Depends(verify_token)):
    """Отримання списку Swagger специфікацій користувача"""
    user_specs = []
    for spec_id, spec_data in swagger_specs.items():
        if spec_data["uploaded_by"] == user_id:
            user_specs.append(
                {
                    "swagger_id": spec_id,
                    "filename": spec_data["filename"],
                    "uploaded_at": spec_data["uploaded_at"],
                    "endpoints_count": len(spec_data["parsed"].get("endpoints", [])),
                }
            )
    return {"specs": user_specs}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
