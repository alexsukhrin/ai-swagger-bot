"""
Адмін панель для AI Swagger Bot API
"""

from datetime import datetime
from typing import Any

from sqladmin import Admin, ModelView
from sqlalchemy.orm import Session

from .database import engine
from .models import (
    ApiCall,
    ApiEmbedding,
    ChatMessage,
    ChatSession,
    PromptTemplate,
    SwaggerSpec,
    User,
)


class UserAdmin(ModelView, model=User):
    """Адмін панель для користувачів"""

    name = "Користувач"
    name_plural = "Користувачі"
    icon = "fa-solid fa-users"

    column_list = [User.id, User.email, User.username, User.is_active, User.created_at]
    column_searchable_list = [User.email, User.username]
    column_sortable_list = [User.created_at, User.is_active]
    column_default_sort = ("created_at", True)

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    form_excluded_columns = ["hashed_password"]

    def on_model_change(self, model: Any, is_created: bool) -> None:
        """Обробка змін моделі"""
        if is_created:
            from .auth import get_password_hash

            if hasattr(model, "password") and model.password:
                model.hashed_password = get_password_hash(model.password)


class SwaggerSpecAdmin(ModelView, model=SwaggerSpec):
    """Адмін панель для Swagger специфікацій"""

    name = "Swagger Специфікація"
    name_plural = "Swagger Специфікації"
    icon = "fa-solid fa-file-code"

    column_list = [
        SwaggerSpec.id,
        SwaggerSpec.filename,
        SwaggerSpec.endpoints_count,
        SwaggerSpec.user_id,
        SwaggerSpec.jwt_token,
        SwaggerSpec.is_active,
        SwaggerSpec.created_at,
    ]
    column_searchable_list = [SwaggerSpec.filename]
    column_sortable_list = [SwaggerSpec.created_at, SwaggerSpec.endpoints_count]
    column_filters = [SwaggerSpec.user_id, SwaggerSpec.is_active]
    column_default_sort = ("created_at", True)

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    form_excluded_columns = ["original_data", "parsed_data"]

    # Форматируем JWT токен (показываем только начало)
    column_formatters = {
        SwaggerSpec.jwt_token: lambda m, a: (
            m.jwt_token[:20] + "..."
            if m.jwt_token and len(m.jwt_token) > 20
            else (m.jwt_token or "Not set")
        )
    }


class ChatSessionAdmin(ModelView, model=ChatSession):
    """Адмін панель для сесій чату"""

    name = "Сесія Чату"
    name_plural = "Сесії Чату"
    icon = "fa-solid fa-comments"

    column_list = [
        ChatSession.id,
        ChatSession.session_name,
        ChatSession.user_id,
        ChatSession.swagger_spec_id,
        ChatSession.is_active,
        ChatSession.created_at,
    ]
    column_searchable_list = [ChatSession.session_name]
    column_sortable_list = [ChatSession.created_at, ChatSession.is_active]
    column_filters = [ChatSession.user_id, ChatSession.is_active]
    column_default_sort = ("created_at", True)

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


class ChatMessageAdmin(ModelView, model=ChatMessage):
    """Адмін панель для повідомлень чату"""

    name = "Повідомлення"
    name_plural = "Повідомлення"
    icon = "fa-solid fa-message"

    column_list = [
        ChatMessage.id,
        ChatMessage.role,
        ChatMessage.chat_session_id,
        ChatMessage.created_at,
    ]
    column_searchable_list = [ChatMessage.content]
    column_sortable_list = [ChatMessage.created_at, ChatMessage.role]
    column_filters = [ChatMessage.role, ChatMessage.chat_session_id]
    column_default_sort = ("created_at", True)

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    # Обмежуємо відображення контенту
    column_formatters = {
        ChatMessage.content: lambda m, a: (
            m.content[:100] + "..." if len(m.content) > 100 else m.content
        )
    }


class PromptTemplateAdmin(ModelView, model=PromptTemplate):
    """Адмін панель для промпт шаблонів"""

    name = "Промпт Шаблон"
    name_plural = "Промпт Шаблони"
    icon = "fa-solid fa-lightbulb"

    column_list = [
        PromptTemplate.id,
        PromptTemplate.name,
        PromptTemplate.category,
        PromptTemplate.user_id,
        PromptTemplate.is_public,
        PromptTemplate.is_active,
        PromptTemplate.created_at,
    ]
    column_searchable_list = [
        PromptTemplate.name,
        PromptTemplate.description,
        PromptTemplate.user_id,
    ]
    column_sortable_list = [
        PromptTemplate.created_at,
        PromptTemplate.is_active,
        PromptTemplate.user_id,
    ]
    column_filters = [
        PromptTemplate.user_id,
        PromptTemplate.category,
        PromptTemplate.is_public,
        PromptTemplate.is_active,
    ]
    column_default_sort = ("created_at", True)

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


class ApiEmbeddingAdmin(ModelView, model=ApiEmbedding):
    """Адмін панель для API embeddings"""

    name = "API Embedding"
    name_plural = "API Embeddings"
    icon = "fa-solid fa-vector-square"

    column_list = [
        ApiEmbedding.id,
        ApiEmbedding.user_id,
        ApiEmbedding.swagger_spec_id,
        ApiEmbedding.endpoint_path,
        ApiEmbedding.method,
        ApiEmbedding.created_at,
    ]
    column_searchable_list = [
        ApiEmbedding.endpoint_path,
        ApiEmbedding.method,
        ApiEmbedding.description,
    ]
    column_sortable_list = [ApiEmbedding.created_at, ApiEmbedding.method]
    column_filters = [ApiEmbedding.user_id, ApiEmbedding.swagger_spec_id, ApiEmbedding.method]
    column_default_sort = ("created_at", True)

    can_create = False  # Embeddings створюються автоматично
    can_edit = False
    can_delete = True
    can_view_details = True

    # Скрываем большие поля
    form_excluded_columns = ["embedding", "embedding_metadata"]

    # Форматируем отображение описания
    column_formatters = {
        ApiEmbedding.description: lambda m, a: (
            m.description[:100] + "..." if len(m.description) > 100 else m.description
        )
    }


class APICallAdmin(ModelView, model=ApiCall):
    """Адмін панель для API викликів"""

    name = "API Виклик"
    name_plural = "API Виклики"
    icon = "fa-solid fa-code"

    column_list = [
        ApiCall.id,
        ApiCall.user_id,
        ApiCall.endpoint_path,
        ApiCall.method,
        ApiCall.status_code,
        ApiCall.execution_time,
        ApiCall.created_at,
    ]
    column_searchable_list = [ApiCall.endpoint_path]
    column_sortable_list = [ApiCall.created_at, ApiCall.status_code, ApiCall.execution_time]
    column_filters = [ApiCall.user_id, ApiCall.method, ApiCall.status_code]
    column_default_sort = ("created_at", True)

    can_create = False  # API виклики створюються автоматично
    can_edit = False
    can_delete = True
    can_view_details = True


def setup_admin(app):
    """Налаштування адмін панелі"""
    admin = Admin(app, engine)

    # Додаємо адмін моделі
    admin.add_view(UserAdmin)
    admin.add_view(SwaggerSpecAdmin)
    admin.add_view(ChatSessionAdmin)
    admin.add_view(ChatMessageAdmin)
    admin.add_view(PromptTemplateAdmin)
    admin.add_view(ApiEmbeddingAdmin)
    admin.add_view(APICallAdmin)

    return admin
