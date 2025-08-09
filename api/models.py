"""
Моделі бази даних для AI Swagger Bot API
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# SQLAlchemy моделі
class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)  # UUID
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    swagger_specs = relationship("SwaggerSpec", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")
    prompt_templates = relationship("PromptTemplate", back_populates="user")
    api_embeddings = relationship("ApiEmbedding", back_populates="user")


class SwaggerSpec(Base):
    __tablename__ = "swagger_specs"

    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_data = Column(JSON, nullable=False)  # Зберігаємо оригінальний JSON
    parsed_data = Column(JSON, nullable=False)  # Зберігаємо розпарсені дані
    base_url = Column(String(500), nullable=True)  # Base URL з Swagger специфікації
    endpoints_count = Column(Integer, default=0)
    jwt_token = Column(Text, nullable=True)  # JWT токен для автентифікації
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="swagger_specs")
    chat_sessions = relationship("ChatSession", back_populates="swagger_spec")
    api_embeddings = relationship("ApiEmbedding", back_populates="swagger_spec")

    # Унікальний констрейнт для уникнення дублювання файлів у одного користувача
    __table_args__ = (
        UniqueConstraint("user_id", "filename", name="uq_user_filename"),
        Index("idx_swagger_user_active", "user_id", "is_active"),
        Index("idx_swagger_created", "created_at"),
    )


class ApiEmbedding(Base):
    __tablename__ = "api_embeddings"

    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    swagger_spec_id = Column(String(36), ForeignKey("swagger_specs.id"), nullable=False)
    endpoint_path = Column(String(500), nullable=False)
    method = Column(String(10), nullable=False)
    description = Column(Text, nullable=False)
    embedding = Column(Text, nullable=False)  # JSON string з вектором
    embedding_metadata = Column(JSON, nullable=True)  # Метадані для embedding
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="api_embeddings")
    swagger_spec = relationship("SwaggerSpec", back_populates="api_embeddings")

    # Унікальний констрейнт для уникнення дублювання embeddings
    # Один endpoint може бути тільки один раз для конкретного користувача та Swagger файлу
    __table_args__ = (
        UniqueConstraint(
            "user_id", "swagger_spec_id", "endpoint_path", "method", name="uq_user_swagger_endpoint"
        ),
        Index("idx_embedding_user_swagger", "user_id", "swagger_spec_id"),
        Index("idx_embedding_method_path", "method", "endpoint_path"),
        Index("idx_embedding_created", "created_at"),
    )


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    swagger_spec_id = Column(String(36), ForeignKey("swagger_specs.id"), nullable=True)
    session_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    swagger_spec = relationship("SwaggerSpec", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="chat_session")

    # Індекси для швидкого пошуку
    __table_args__ = (
        Index("idx_session_user_active", "user_id", "is_active"),
        Index("idx_session_created", "created_at"),
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True)  # UUID
    chat_session_id = Column(String(36), ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    chat_session = relationship("ChatSession", back_populates="messages")

    # Індекси для швидкого пошуку
    __table_args__ = (
        Index("idx_message_session", "chat_session_id"),
        Index("idx_message_created", "created_at"),
        Index("idx_message_role", "role"),
    )


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(
        String(36), ForeignKey("users.id"), nullable=True
    )  # null для системних промптів
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    template = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    is_public = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    success_rate = Column(Integer, default=0)  # у відсотках
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Нові поля для GPT-генерованих промптів
    swagger_spec_id = Column(
        String(36), ForeignKey("swagger_specs.id", ondelete="CASCADE"), nullable=True
    )
    endpoint_path = Column(String(500), nullable=True)  # /api/users/{id}
    http_method = Column(String(10), nullable=True)  # GET, POST, etc
    resource_type = Column(String(100), nullable=True)  # users, orders, etc
    tags = Column(JSON, nullable=True)  # ["user", "management", "api"]
    source = Column(String(50), nullable=True, default="manual")  # manual, gpt_generated, imported
    priority = Column(Integer, nullable=True, default=1)  # для сортування

    # Relationships
    user = relationship("User", back_populates="prompt_templates")
    swagger_spec = relationship("SwaggerSpec", backref="prompt_templates")

    # Унікальний констрейнт для уникнення дублювання промптів
    __table_args__ = (
        UniqueConstraint("user_id", "name", "category", name="uq_user_prompt_name_category"),
        Index("idx_prompt_user_active", "user_id", "is_active"),
        Index("idx_prompt_category", "category"),
        Index("idx_prompt_public", "is_public"),
        Index("idx_prompt_swagger_spec", "swagger_spec_id"),
        Index("idx_prompt_endpoint", "endpoint_path", "http_method"),
        Index("idx_prompt_source", "source"),
    )


class ApiCall(Base):
    __tablename__ = "api_calls"

    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    swagger_spec_id = Column(String(36), ForeignKey("swagger_specs.id"), nullable=False)
    endpoint_path = Column(String(500), nullable=False)
    method = Column(String(10), nullable=False)
    request_data = Column(JSON, nullable=True)
    response_data = Column(JSON, nullable=True)
    status_code = Column(Integer, nullable=True)
    execution_time = Column(Integer, nullable=True)  # в мілісекундах
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")
    swagger_spec = relationship("SwaggerSpec")

    # Індекси для аналітики
    __table_args__ = (
        Index("idx_apicall_user_swagger", "user_id", "swagger_spec_id"),
        Index("idx_apicall_endpoint", "endpoint_path", "method"),
        Index("idx_apicall_status", "status_code"),
        Index("idx_apicall_created", "created_at"),
    )


# Pydantic моделі для API
class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: str
    username: str
    password: str


class SwaggerSpecResponse(BaseModel):
    id: str
    filename: str
    base_url: Optional[str]
    endpoints_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class ChatMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class PromptTemplateResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    template: str
    category: str
    is_public: bool
    usage_count: int
    success_rate: int

    class Config:
        from_attributes = True


class PromptTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    template: str
    category: str
    is_public: bool = False


class ApiEmbeddingResponse(BaseModel):
    id: str
    endpoint_path: str
    method: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True
