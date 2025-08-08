"""
API endpoints для роботи з промптами
Дозволяє користувачам додавати, оновлювати та видаляти кастомні промпти
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.gpt_prompt_generator import (
    GPTGeneratedPrompt,
    generate_prompts_with_gpt,
    generate_smart_suggestions_with_gpt,
)
from src.yaml_prompt_manager import PromptTemplate as YAMLPromptTemplate
from src.yaml_prompt_manager import YAMLPromptManager

from .auth import get_current_user
from .database import get_db
from .models import PromptTemplate, PromptTemplateCreate, PromptTemplateResponse, User

router = APIRouter(prefix="/prompts", tags=["prompts"])

# Глобальний менеджер промптів
prompt_manager = None


def get_prompt_manager() -> YAMLPromptManager:
    """Отримує глобальний менеджер промптів."""
    global prompt_manager
    if prompt_manager is None:
        prompt_manager = YAMLPromptManager()
    return prompt_manager


@router.get("/", response_model=List[PromptTemplateResponse])
async def get_prompts(
    category: Optional[str] = None,
    search: Optional[str] = None,
    include_public: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Отримує список промптів з фільтрацією.

    Args:
        category: Фільтр за категорією
        search: Пошуковий запит
        include_public: Чи включати публічні промпти
        current_user: Поточний користувач
        db: Сесія бази даних
    """
    manager = get_prompt_manager()

    # Отримуємо промпти з менеджера
    if search:
        prompts = manager.search_prompts(search, category)
    elif category:
        prompts = manager.get_prompts_by_category(category)
    else:
        prompts = manager.get_active_prompts()

    # Фільтруємо за доступністю користувача
    filtered_prompts = []
    for prompt in prompts:
        # Користувач може бачити:
        # 1. Свої власні промпти
        # 2. Публічні промпти (якщо include_public=True)
        if prompt.user_id == current_user.id:
            filtered_prompts.append(prompt)
        elif include_public and prompt.is_public:
            filtered_prompts.append(prompt)

    # Конвертуємо в формат відповіді
    response_prompts = []
    for prompt in filtered_prompts:
        response_prompt = PromptTemplateResponse(
            id=prompt.id,
            name=prompt.name,
            description=prompt.description,
            template=prompt.template,
            category=prompt.category,
            is_public=prompt.is_public,
            is_active=prompt.is_active,
            created_at=datetime.fromisoformat(prompt.created_at),
            updated_at=datetime.fromisoformat(prompt.updated_at),
        )
        response_prompts.append(response_prompt)

    return response_prompts


@router.get("/categories")
async def get_prompt_categories(current_user: User = Depends(get_current_user)):
    """
    Отримує список категорій промптів.
    """
    manager = get_prompt_manager()
    stats = manager.get_statistics()

    return {"categories": stats["categories"], "categories_info": stats["categories_info"]}


@router.get("/statistics")
async def get_prompt_statistics(current_user: User = Depends(get_current_user)):
    """
    Отримує статистику промптів.
    """
    manager = get_prompt_manager()
    stats = manager.get_statistics()

    return {
        "total_prompts": stats["total_prompts"],
        "active_prompts": stats["active_prompts"],
        "public_prompts": stats["public_prompts"],
        "categories": stats["categories"],
        "categories_info": stats["categories_info"],
        "usage_stats": stats["usage_stats"],
    }


@router.get("/user-statistics")
async def get_user_prompt_statistics(current_user: User = Depends(get_current_user)):
    """
    Отримує детальну статистику промптів користувача.

    Args:
        current_user: Поточний користувач
    """
    manager = get_prompt_manager()
    all_prompts = manager.get_active_prompts()

    # Розділяємо промпти за типами
    user_prompts = []
    public_prompts = []
    other_prompts = []

    for prompt in all_prompts:
        if prompt.user_id == current_user.id:
            user_prompts.append(prompt)
        elif prompt.is_public:
            public_prompts.append(prompt)
        else:
            other_prompts.append(prompt)

    # Статистика за категоріями
    user_categories = {}
    public_categories = {}

    for prompt in user_prompts:
        category = prompt.category
        user_categories[category] = user_categories.get(category, 0) + 1

    for prompt in public_prompts:
        category = prompt.category
        public_categories[category] = public_categories.get(category, 0) + 1

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "statistics": {
            "total_available": len(user_prompts) + len(public_prompts),
            "user_prompts": {
                "count": len(user_prompts),
                "categories": user_categories,
                "categories_count": len(user_categories),
            },
            "public_prompts": {
                "count": len(public_prompts),
                "categories": public_categories,
                "categories_count": len(public_categories),
            },
            "other_prompts": {
                "count": len(other_prompts),
                "note": "Промпти інших користувачів (не публічні)",
            },
        },
        "access_rights": {
            "can_see_own": True,
            "can_see_public": True,
            "can_edit_own": True,
            "can_delete_own": True,
            "can_create_new": True,
        },
    }


@router.post("/", response_model=PromptTemplateResponse)
async def create_prompt(
    prompt_data: PromptTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Створює новий промпт.

    Args:
        prompt_data: Дані промпту
        current_user: Поточний користувач
        db: Сесія бази даних
    """
    manager = get_prompt_manager()

    # Створюємо промпт
    prompt_dict = {
        "name": prompt_data.name,
        "description": prompt_data.description,
        "template": prompt_data.template,
        "category": prompt_data.category,
        "is_public": prompt_data.is_public,
        "user_id": current_user.id,
    }

    prompt_id = manager.add_custom_prompt(prompt_dict, current_user.id)

    if not prompt_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Помилка створення промпту"
        )

    # Отримуємо створений промпт
    created_prompt = manager.get_prompt(prompt_id)

    return PromptTemplateResponse(
        id=created_prompt.id,
        name=created_prompt.name,
        description=created_prompt.description,
        template=created_prompt.template,
        category=created_prompt.category,
        is_public=created_prompt.is_public,
        is_active=created_prompt.is_active,
        created_at=datetime.fromisoformat(created_prompt.created_at),
        updated_at=datetime.fromisoformat(created_prompt.updated_at),
    )


@router.get("/{prompt_id}", response_model=PromptTemplateResponse)
async def get_prompt(
    prompt_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Отримує конкретний промпт.

    Args:
        prompt_id: ID промпту
        current_user: Поточний користувач
        db: Сесія бази даних
    """
    manager = get_prompt_manager()
    prompt = manager.get_prompt(prompt_id)

    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Промпт не знайдено")

    # Перевіряємо доступ
    if not prompt.is_public and prompt.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Немає доступу до цього промпту"
        )

    return PromptTemplateResponse(
        id=prompt.id,
        name=prompt.name,
        description=prompt.description,
        template=prompt.template,
        category=prompt.category,
        is_public=prompt.is_public,
        is_active=prompt.is_active,
        created_at=datetime.fromisoformat(prompt.created_at),
        updated_at=datetime.fromisoformat(prompt.updated_at),
    )


@router.put("/{prompt_id}", response_model=PromptTemplateResponse)
async def update_prompt(
    prompt_id: str,
    prompt_data: PromptTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Оновлює промпт.

    Args:
        prompt_id: ID промпту
        prompt_data: Нові дані промпту
        current_user: Поточний користувач
        db: Сесія бази даних
    """
    manager = get_prompt_manager()
    prompt = manager.get_prompt(prompt_id)

    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Промпт не знайдено")

    # Перевіряємо права на редагування
    if prompt.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Немає прав на редагування цього промпту"
        )

    # Оновлюємо промпт
    update_data = {
        "name": prompt_data.name,
        "description": prompt_data.description,
        "template": prompt_data.template,
        "category": prompt_data.category,
        "is_public": prompt_data.is_public,
    }

    success = manager.update_prompt(prompt_id, update_data)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Помилка оновлення промпту"
        )

    # Отримуємо оновлений промпт
    updated_prompt = manager.get_prompt(prompt_id)

    return PromptTemplateResponse(
        id=updated_prompt.id,
        name=updated_prompt.name,
        description=updated_prompt.description,
        template=updated_prompt.template,
        category=updated_prompt.category,
        is_public=updated_prompt.is_public,
        is_active=updated_prompt.is_active,
        created_at=datetime.fromisoformat(updated_prompt.created_at),
        updated_at=datetime.fromisoformat(updated_prompt.updated_at),
    )


@router.delete("/{prompt_id}")
async def delete_prompt(
    prompt_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Видаляє промпт.

    Args:
        prompt_id: ID промпту
        current_user: Поточний користувач
        db: Сесія бази даних
    """
    manager = get_prompt_manager()
    prompt = manager.get_prompt(prompt_id)

    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Промпт не знайдено")

    # Перевіряємо права на видалення
    if prompt.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Немає прав на видалення цього промпту"
        )

    # Видаляємо промпт
    success = manager.delete_prompt(prompt_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Помилка видалення промпту"
        )

    return {"message": "Промпт успішно видалено"}


@router.get("/suggestions")
async def get_prompt_suggestions(
    query: str, context: Optional[str] = "", current_user: User = Depends(get_current_user)
):
    """
    Отримує пропозиції промптів для запиту.

    Args:
        query: Запит користувача
        context: Додатковий контекст
        current_user: Поточний користувач
    """
    manager = get_prompt_manager()
    all_suggestions = manager.get_prompt_suggestions(query, context)

    # Фільтруємо за правами доступу
    filtered_suggestions = []
    for prompt in all_suggestions:
        # Користувач може бачити:
        # 1. Свої власні промпти
        # 2. Публічні промпти
        if prompt.user_id == current_user.id or prompt.is_public:
            filtered_suggestions.append(prompt)

    return {
        "query": query,
        "context": context,
        "suggestions": [
            {
                "id": prompt.id,
                "name": prompt.name,
                "description": prompt.description,
                "category": prompt.category,
                "relevance_score": getattr(prompt, "relevance_score", 0.0),
                "is_public": prompt.is_public,
                "is_owner": prompt.user_id == current_user.id,
            }
            for prompt in filtered_suggestions
        ],
        "total_suggestions": len(filtered_suggestions),
        "total_found": len(all_suggestions),
    }


@router.post("/format")
async def format_prompt(
    prompt_id: str, parameters: Dict[str, Any], current_user: User = Depends(get_current_user)
):
    """
    Форматує промпт з параметрами.

    Args:
        prompt_id: ID промпту
        parameters: Параметри для форматування
        current_user: Поточний користувач
    """
    manager = get_prompt_manager()
    prompt = manager.get_prompt(prompt_id)

    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Промпт не знайдено")

    # Перевіряємо доступ
    if not prompt.is_public and prompt.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Немає доступу до цього промпту"
        )

    # Форматуємо промпт
    try:
        formatted_prompt = manager.format_prompt(prompt_id, **parameters)
        return {"formatted_prompt": formatted_prompt}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Помилка форматування промпту: {str(e)}",
        )


@router.post("/export")
async def export_prompts(
    include_custom: bool = True,
    include_public: bool = False,
    current_user: User = Depends(get_current_user),
):
    """
    Експортує промпти в YAML формат.

    Args:
        include_custom: Чи включати кастомні промпти користувача
        include_public: Чи включати публічні промпти
        current_user: Поточний користувач
    """
    manager = get_prompt_manager()

    # Генеруємо унікальне ім'я файлу
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"prompts_export_{current_user.username}_{timestamp}.yaml"
    file_path = f"exports/{filename}"

    # Експортуємо промпти з фільтрацією за користувачем
    try:
        # Отримуємо всі активні промпти
        all_prompts = manager.get_active_prompts()

        # Фільтруємо за користувачем
        user_prompts = []
        for prompt in all_prompts:
            # Користувач може експортувати:
            # 1. Свої власні промпти (якщо include_custom=True)
            # 2. Публічні промпти (якщо include_public=True)
            if include_custom and prompt.user_id == current_user.id:
                user_prompts.append(prompt)
            elif include_public and prompt.is_public:
                user_prompts.append(prompt)

        # Експортуємо відфільтровані промпти
        manager.export_specific_prompts_to_yaml(file_path, user_prompts)

        return {
            "message": f"Експортовано {len(user_prompts)} промптів",
            "filename": filename,
            "file_path": file_path,
            "exported_count": len(user_prompts),
            "user_prompts_count": len([p for p in user_prompts if p.user_id == current_user.id]),
            "public_prompts_count": len([p for p in user_prompts if p.is_public]),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Помилка експорту: {str(e)}"
        )


@router.post("/import")
async def import_prompts(
    file_path: str, overwrite: bool = False, current_user: User = Depends(get_current_user)
):
    """
    Імпортує промпти з YAML файлу.

    Args:
        file_path: Шлях до файлу
        overwrite: Чи перезаписувати існуючі промпти
        current_user: Поточний користувач
    """
    manager = get_prompt_manager()

    try:
        manager.import_prompts_from_yaml(file_path, overwrite)
        return {"message": "Промпти успішно імпортовано"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Помилка імпорту: {str(e)}"
        )


@router.post("/reload")
async def reload_base_prompts(current_user: User = Depends(get_current_user)):
    """
    Перезавантажує базові промпти.

    Args:
        current_user: Поточний користувач
    """
    manager = get_prompt_manager()

    try:
        manager.reload_base_prompts()
        return {"message": "Базові промпти успішно перезавантажено"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка перезавантаження: {str(e)}",
        )


@router.get("/search")
async def search_prompts(
    query: str, category: Optional[str] = None, current_user: User = Depends(get_current_user)
):
    """
    Шукає промпти за запитом.

    Args:
        query: Пошуковий запит
        category: Фільтр за категорією
        current_user: Поточний користувач
    """
    manager = get_prompt_manager()
    all_results = manager.search_prompts(query, category)

    # Фільтруємо за правами доступу
    filtered_results = []
    for prompt in all_results:
        # Користувач може бачити:
        # 1. Свої власні промпти
        # 2. Публічні промпти
        if prompt.user_id == current_user.id or prompt.is_public:
            filtered_results.append(prompt)

    return {
        "query": query,
        "category": category,
        "results": [
            {
                "id": prompt.id,
                "name": prompt.name,
                "description": prompt.description,
                "category": prompt.category,
                "tags": prompt.tags,
                "is_public": prompt.is_public,
                "is_owner": prompt.user_id == current_user.id,
            }
            for prompt in filtered_results
        ],
        "total": len(filtered_results),
        "total_found": len(all_results),
        "filtered_count": len(filtered_results),
    }


# НОВІ ENDPOINTS ДЛЯ GPT ГЕНЕРАЦІЇ


@router.post("/generate-from-swagger")
async def generate_prompts_from_swagger(
    swagger_data: Dict[str, Any],
    api_key: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """
    Генерує промпти через GPT на основі Swagger специфікації.

    Args:
        swagger_data: Дані Swagger специфікації
        api_key: OpenAI API ключ (опціонально)
        current_user: Поточний користувач
    """
    try:
        # Генеруємо промпти через GPT
        generated_prompts = generate_prompts_with_gpt(swagger_data, api_key)

        if not generated_prompts:
            return {
                "message": "Не вдалося згенерувати промпти",
                "generated_count": 0,
                "prompts": [],
            }

        # Зберігаємо згенеровані промпти
        manager = get_prompt_manager()
        saved_prompts = []

        for prompt in generated_prompts:
            # Конвертуємо GPT промпт в формат системи
            prompt_dict = {
                "name": prompt.name,
                "description": prompt.description,
                "template": prompt.template,
                "category": prompt.category,
                "is_public": prompt.is_public,
                "user_id": current_user.id,
                "tags": prompt.tags,
            }

            prompt_id = manager.add_custom_prompt(prompt_dict, current_user.id)
            if prompt_id:
                saved_prompts.append(
                    {
                        "id": prompt_id,
                        "name": prompt.name,
                        "category": prompt.category,
                        "resource_type": prompt.resource_type,
                        "endpoint_path": prompt.endpoint_path,
                        "http_method": prompt.http_method,
                    }
                )

        return {
            "message": f"Успішно згенеровано {len(saved_prompts)} промптів",
            "generated_count": len(generated_prompts),
            "saved_count": len(saved_prompts),
            "prompts": saved_prompts,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка генерації промптів: {str(e)}",
        )


@router.post("/generate-suggestions")
async def generate_smart_suggestions(
    swagger_data: Dict[str, Any],
    api_key: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """
    Генерує розумні підказки через GPT на основі Swagger специфікації.

    Args:
        swagger_data: Дані Swagger специфікації
        api_key: OpenAI API ключ (опціонально)
        current_user: Поточний користувач
    """
    try:
        # Генеруємо підказки через GPT
        suggestions = generate_smart_suggestions_with_gpt(swagger_data, api_key)

        return {
            "message": f"Згенеровано {len(suggestions)} підказок",
            "suggestions_count": len(suggestions),
            "suggestions": suggestions,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка генерації підказок: {str(e)}",
        )


@router.post("/auto-generate-for-user")
async def auto_generate_prompts_for_user(
    request_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    swagger_spec_id = request_data.get("swagger_spec_id")
    api_key = request_data.get("api_key")
    """
    Автоматично генерує промпти для користувача на основі його Swagger специфікації.

    Args:
        swagger_spec_id: ID Swagger специфікації користувача
        api_key: OpenAI API ключ (опціонально)
        current_user: Поточний користувач
        db: Сесія бази даних
    """
    try:
        # Отримуємо Swagger специфікацію користувача
        from .models import SwaggerSpec

        swagger_spec = (
            db.query(SwaggerSpec)
            .filter(SwaggerSpec.id == swagger_spec_id, SwaggerSpec.user_id == current_user.id)
            .first()
        )

        if not swagger_spec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Swagger специфікацію не знайдено"
            )

        # Генеруємо промпти
        generated_prompts = generate_prompts_with_gpt(swagger_spec.parsed_data, api_key)

        if not generated_prompts:
            return {
                "message": "Не вдалося згенерувати промпти для цієї специфікації",
                "generated_count": 0,
                "prompts": [],
            }

        # Зберігаємо промпти для користувача
        manager = get_prompt_manager()
        saved_prompts = []

        for prompt in generated_prompts:
            prompt_dict = {
                "name": prompt.name,
                "description": prompt.description,
                "template": prompt.template,
                "category": prompt.category,
                "is_public": False,  # Приватні для користувача
                "user_id": current_user.id,
                "tags": prompt.tags,
            }

            prompt_id = manager.add_custom_prompt(prompt_dict, current_user.id)
            if prompt_id:
                saved_prompts.append(
                    {
                        "id": prompt_id,
                        "name": prompt.name,
                        "category": prompt.category,
                        "resource_type": prompt.resource_type,
                        "endpoint_path": prompt.endpoint_path,
                        "http_method": prompt.http_method,
                    }
                )

        return {
            "message": f"Успішно згенеровано {len(saved_prompts)} промптів для вашої Swagger специфікації",
            "swagger_spec_id": swagger_spec_id,
            "generated_count": len(generated_prompts),
            "saved_count": len(saved_prompts),
            "prompts": saved_prompts,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка автоматичної генерації промптів: {str(e)}",
        )
