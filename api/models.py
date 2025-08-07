"""
Моделі бази даних для AI Swagger Bot API
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Text
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


class SwaggerSpec(Base):
    __tablename__ = "swagger_specs"

    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_data = Column(JSON, nullable=False)  # Зберігаємо оригінальний JSON
    parsed_data = Column(JSON, nullable=False)  # Зберігаємо розпарсені дані
    endpoints_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="swagger_specs")
    chat_sessions = relationship("ChatSession", back_populates="swagger_spec")


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


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True)  # UUID
    chat_session_id = Column(String(36), ForeignKey("chat_sessions.id"), nullable=False)
    message_type = Column(String(20), nullable=False)  # 'user' або 'assistant'
    content = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=True)  # Додаткові дані (токени, час виконання, тощо)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    chat_session = relationship("ChatSession", back_populates="messages")


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    template = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    is_public = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="prompt_templates")


class APICall(Base):
    __tablename__ = "api_calls"

    id = Column(String(36), primary_key=True)  # UUID
    chat_message_id = Column(String(36), ForeignKey("chat_messages.id"), nullable=False)
    endpoint = Column(String(500), nullable=False)
    method = Column(String(10), nullable=False)
    request_data = Column(JSON, nullable=True)
    response_data = Column(JSON, nullable=True)
    status_code = Column(Integer, nullable=True)
    execution_time = Column(Integer, nullable=True)  # в мілісекундах
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    chat_message = relationship("ChatMessage")


# Pydantic моделі для API
class UserCreate(BaseModel):
    email: str
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SwaggerSpecCreate(BaseModel):
    filename: str
    original_data: dict
    parsed_data: dict
    endpoints_count: int


class SwaggerSpecResponse(BaseModel):
    id: str
    filename: str
    endpoints_count: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionCreate(BaseModel):
    session_name: Optional[str] = None
    swagger_spec_id: Optional[str] = None


class ChatSessionResponse(BaseModel):
    id: str
    session_name: Optional[str]
    swagger_spec_id: Optional[str]
    is_active: bool
    created_at: datetime
    message_count: int

    class Config:
        from_attributes = True


class ChatMessageCreate(BaseModel):
    content: str
    message_type: str = "user"
    metadata: Optional[dict] = None


class ChatMessageResponse(BaseModel):
    id: str
    message_type: str
    content: str
    metadata: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True


class PromptTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    template: str
    category: str
    is_public: bool = False


class PromptTemplateResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    template: str
    category: str
    is_public: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class APICallResponse(BaseModel):
    id: str
    endpoint: str
    method: str
    request_data: Optional[dict]
    response_data: Optional[dict]
    status_code: Optional[int]
    execution_time: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True
