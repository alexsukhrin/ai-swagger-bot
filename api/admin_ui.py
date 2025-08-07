"""
Веб-інтерфейс для адмінки AI Swagger Bot
"""

import json
from typing import Any, Dict, List

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .auth import get_current_user
from .database import get_db
from .models import APICall, ChatMessage, ChatSession, PromptTemplate, SwaggerSpec, User

# Створюємо окремий FastAPI додаток для адмінки
admin_app = FastAPI(title="AI Swagger Bot Admin", docs_url=None, redoc_url=None)

# Налаштування шаблонів
templates = Jinja2Templates(directory="api/templates")

# Статичні файли
admin_app.mount("/static", StaticFiles(directory="api/static"), name="static")


@admin_app.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    """Головна сторінка адмінки"""
    try:
        # Отримуємо статистику
        stats = {
            "users_count": db.query(User).count(),
            "swagger_specs_count": db.query(SwaggerSpec).count(),
            "chat_sessions_count": db.query(ChatSession).count(),
            "messages_count": db.query(ChatMessage).count(),
            "prompts_count": db.query(PromptTemplate).count(),
            "api_calls_count": db.query(APICall).count(),
        }

        # Останні користувачі
        recent_users = db.query(User).order_by(User.created_at.desc()).limit(5).all()

        # Останні Swagger специфікації
        recent_specs = db.query(SwaggerSpec).order_by(SwaggerSpec.created_at.desc()).limit(5).all()

        return templates.TemplateResponse(
            "admin_dashboard.html",
            {
                "request": request,
                "stats": stats,
                "recent_users": recent_users,
                "recent_specs": recent_specs,
            },
        )
    except Exception as e:
        return templates.TemplateResponse("error.html", {"request": request, "error": str(e)})


@admin_app.get("/users", response_class=HTMLResponse)
async def admin_users(request: Request, db: Session = Depends(get_db)):
    """Сторінка управління користувачами"""
    users = db.query(User).order_by(User.created_at.desc()).all()
    return templates.TemplateResponse("admin_users.html", {"request": request, "users": users})


@admin_app.get("/swagger-specs", response_class=HTMLResponse)
async def admin_swagger_specs(request: Request, db: Session = Depends(get_db)):
    """Сторінка управління Swagger специфікаціями"""
    specs = db.query(SwaggerSpec).order_by(SwaggerSpec.created_at.desc()).all()
    return templates.TemplateResponse(
        "admin_swagger_specs.html", {"request": request, "specs": specs}
    )


@admin_app.get("/chat-sessions", response_class=HTMLResponse)
async def admin_chat_sessions(request: Request, db: Session = Depends(get_db)):
    """Сторінка управління сесіями чату"""
    sessions = db.query(ChatSession).order_by(ChatSession.created_at.desc()).all()
    return templates.TemplateResponse(
        "admin_chat_sessions.html", {"request": request, "sessions": sessions}
    )


@admin_app.get("/messages", response_class=HTMLResponse)
async def admin_messages(request: Request, db: Session = Depends(get_db)):
    """Сторінка управління повідомленнями"""
    messages = db.query(ChatMessage).order_by(ChatMessage.created_at.desc()).limit(100).all()
    return templates.TemplateResponse(
        "admin_messages.html", {"request": request, "messages": messages}
    )


@admin_app.get("/prompts", response_class=HTMLResponse)
async def admin_prompts(request: Request, db: Session = Depends(get_db)):
    """Сторінка управління промпт шаблонами"""
    prompts = db.query(PromptTemplate).order_by(PromptTemplate.created_at.desc()).all()
    return templates.TemplateResponse(
        "admin_prompts.html", {"request": request, "prompts": prompts}
    )


@admin_app.get("/api-calls", response_class=HTMLResponse)
async def admin_api_calls(request: Request, db: Session = Depends(get_db)):
    """Сторінка перегляду API викликів"""
    api_calls = db.query(APICall).order_by(APICall.created_at.desc()).limit(100).all()
    return templates.TemplateResponse(
        "admin_api_calls.html", {"request": request, "api_calls": api_calls}
    )


# API endpoints для адмінки
@admin_app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Отримання статистики"""
    return {
        "users_count": db.query(User).count(),
        "swagger_specs_count": db.query(SwaggerSpec).count(),
        "chat_sessions_count": db.query(ChatSession).count(),
        "messages_count": db.query(ChatMessage).count(),
        "prompts_count": db.query(PromptTemplate).count(),
        "api_calls_count": db.query(APICall).count(),
    }


@admin_app.delete("/api/users/{user_id}")
async def delete_user(user_id: str, db: Session = Depends(get_db)):
    """Видалення користувача"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


@admin_app.delete("/api/swagger-specs/{spec_id}")
async def delete_swagger_spec(spec_id: str, db: Session = Depends(get_db)):
    """Видалення Swagger специфікації"""
    spec = db.query(SwaggerSpec).filter(SwaggerSpec.id == spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="Swagger spec not found")

    db.delete(spec)
    db.commit()
    return {"message": "Swagger spec deleted successfully"}
