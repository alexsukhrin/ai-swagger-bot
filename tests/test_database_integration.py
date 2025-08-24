"""
Інтеграційні тести для перевірки запитів з базою даних
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Generator
from unittest.mock import patch

import pytest
from api.auth import get_password_hash
from api.database import get_db
from api.main import app

# Імпортуємо моделі та API
from api.models import (
    ApiEmbedding,
    Base,
    ChatMessage,
    ChatSession,
    PromptTemplate,
    SwaggerSpec,
    User,
)
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Тестова база даних (SQLite для швидких тестів)
TEST_DATABASE_URL = "sqlite:///./test.db"

# Створюємо тестовий engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,  # Вимкнути логування для тестів
)

# Тестова сесія
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session")
def test_db():
    """Створення тестової бази даних"""
    # Створюємо таблиці
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    # Очищаємо після тестів
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session(test_db) -> Generator[Session, None, None]:
    """Фікстура для отримання сесії бази даних"""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session) -> Generator[TestClient, None, None]:
    """Фікстура для тестового клієнта"""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session) -> User:
    """Створення тестового користувача"""
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_swagger_spec(db_session, test_user) -> SwaggerSpec:
    """Створення тестового Swagger специфікації"""
    spec_id = str(uuid.uuid4())
    swagger_spec = SwaggerSpec(
        id=spec_id,
        user_id=test_user.id,
        filename="test_api.json",
        original_data={"openapi": "3.0.0", "info": {"title": "Test API"}},
        parsed_data={"endpoints": [{"path": "/test", "method": "GET"}]},
        base_url="https://api.example.com",
        endpoints_count=1,
        is_active=True,
    )
    db_session.add(swagger_spec)
    db_session.commit()
    db_session.refresh(swagger_spec)
    return swagger_spec


class TestDatabaseIntegration:
    """Тести інтеграції з базою даних"""

    def test_create_user(self, db_session):
        """Тест створення користувача"""
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            email="newuser@example.com",
            username="newuser",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id == user_id
        assert user.email == "newuser@example.com"
        assert user.username == "newuser"
        assert user.is_active is True

        # Перевіряємо що користувач зберігається в БД
        saved_user = db_session.query(User).filter(User.id == user_id).first()
        assert saved_user is not None
        assert saved_user.email == "newuser@example.com"

    def test_create_swagger_spec(self, db_session, test_user):
        """Тест створення Swagger специфікації"""
        spec_id = str(uuid.uuid4())
        swagger_data = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/users": {"get": {"summary": "Get users"}},
                "/posts": {"post": {"summary": "Create post"}},
            },
        }

        swagger_spec = SwaggerSpec(
            id=spec_id,
            user_id=test_user.id,
            filename="test_api.json",
            original_data=swagger_data,
            parsed_data={"endpoints": [{"path": "/users", "method": "GET"}]},
            base_url="https://api.example.com",
            endpoints_count=2,
            is_active=True,
        )

        db_session.add(swagger_spec)
        db_session.commit()
        db_session.refresh(swagger_spec)

        assert swagger_spec.id == spec_id
        assert swagger_spec.user_id == test_user.id
        assert swagger_spec.endpoints_count == 2

        # Перевіряємо зв'язок з користувачем
        assert swagger_spec.user == test_user
        assert swagger_spec in test_user.swagger_specs

    def test_create_chat_session(self, db_session, test_user, test_swagger_spec):
        """Тест створення чат сесії"""
        session_id = str(uuid.uuid4())
        chat_session = ChatSession(
            id=session_id,
            user_id=test_user.id,
            swagger_spec_id=test_swagger_spec.id,
            session_name="Test Chat Session",
            is_active=True,
        )

        db_session.add(chat_session)
        db_session.commit()
        db_session.refresh(chat_session)

        assert chat_session.id == session_id
        assert chat_session.user_id == test_user.id
        assert chat_session.swagger_spec_id == test_swagger_spec.id
        assert chat_session.session_name == "Test Chat Session"

        # Перевіряємо зв'язки
        assert chat_session.user == test_user
        assert chat_session.swagger_spec == test_swagger_spec

    def test_create_chat_message(self, db_session, test_user, test_swagger_spec):
        """Тест створення повідомлення чату"""
        session_id = str(uuid.uuid4())
        chat_session = ChatSession(
            id=session_id,
            user_id=test_user.id,
            swagger_spec_id=test_swagger_spec.id,
            session_name="Test Session",
        )
        db_session.add(chat_session)
        db_session.commit()

        message_id = str(uuid.uuid4())
        chat_message = ChatMessage(
            id=message_id,
            chat_session_id=session_id,
            role="user",
            content="Hello, how can I use this API?",
        )

        db_session.add(chat_message)
        db_session.commit()
        db_session.refresh(chat_message)

        assert chat_message.id == message_id
        assert chat_message.chat_session_id == session_id
        assert chat_message.role == "user"
        assert chat_message.content == "Hello, how can I use this API?"

        # Перевіряємо зв'язок
        assert chat_message.chat_session == chat_session

    def test_create_prompt_template(self, db_session, test_user):
        """Тест створення шаблону промпту"""
        template_id = str(uuid.uuid4())
        prompt_template = PromptTemplate(
            id=template_id,
            user_id=test_user.id,
            name="Test Prompt",
            description="A test prompt template",
            template="You are an API expert. Help with: {query}",
            category="user_defined",
            is_public=False,
            is_active=True,
        )

        db_session.add(prompt_template)
        db_session.commit()
        db_session.refresh(prompt_template)

        assert prompt_template.id == template_id
        assert prompt_template.user_id == test_user.id
        assert prompt_template.name == "Test Prompt"
        assert prompt_template.category == "user_defined"

        # Перевіряємо зв'язок
        assert prompt_template.user == test_user

    def test_create_api_token(self, db_session, test_user, test_swagger_spec):
        """Тест створення API токена"""
        token_id = str(uuid.uuid4())
        api_token = ApiToken(
            id=token_id,
            user_id=test_user.id,
            swagger_spec_id=test_swagger_spec.id,
            token_name="OpenAI API Key",
            token_value="sk-test-token-123",
            token_type="api_key",
            is_active=True,
        )

        db_session.add(api_token)
        db_session.commit()
        db_session.refresh(api_token)

        assert api_token.id == token_id
        assert api_token.user_id == test_user.id
        assert api_token.swagger_spec_id == test_swagger_spec.id
        assert api_token.token_name == "OpenAI API Key"
        assert api_token.token_type == "api_key"

        # Перевіряємо зв'язки
        assert api_token.user == test_user
        assert api_token.swagger_spec == test_swagger_spec

    def test_create_api_embedding(self, db_session, test_user, test_swagger_spec):
        """Тест створення API embedding"""
        embedding_id = str(uuid.uuid4())
        api_embedding = ApiEmbedding(
            id=embedding_id,
            user_id=test_user.id,
            swagger_spec_id=test_swagger_spec.id,
            endpoint_path="/users",
            method="GET",
            description="Get list of users",
            embedding="[0.1, 0.2, 0.3, ...]",
            embedding_metadata={"tags": ["users"], "summary": "Get users"},
        )

        db_session.add(api_embedding)
        db_session.commit()
        db_session.refresh(api_embedding)

        assert api_embedding.id == embedding_id
        assert api_embedding.user_id == test_user.id
        assert api_embedding.endpoint_path == "/users"
        assert api_embedding.method == "GET"
        assert api_embedding.description == "Get list of users"

        # Перевіряємо зв'язки
        assert api_embedding.user == test_user
        assert api_embedding.swagger_spec == test_swagger_spec

    def test_user_relationships(self, db_session, test_user, test_swagger_spec):
        """Тест зв'язків користувача"""
        # Створюємо додаткові дані
        session_id = str(uuid.uuid4())
        chat_session = ChatSession(
            id=session_id,
            user_id=test_user.id,
            swagger_spec_id=test_swagger_spec.id,
            session_name="Test Session",
        )
        db_session.add(chat_session)

        template_id = str(uuid.uuid4())
        prompt_template = PromptTemplate(
            id=template_id,
            user_id=test_user.id,
            name="Test Template",
            template="Test template",
            category="user_defined",
        )
        db_session.add(prompt_template)

        token_id = str(uuid.uuid4())
        api_token = ApiToken(
            id=token_id,
            user_id=test_user.id,
            swagger_spec_id=test_swagger_spec.id,
            token_name="Test Token",
            token_value="test-value",
            token_type="api_key",
        )
        db_session.add(api_token)

        embedding_id = str(uuid.uuid4())
        api_embedding = ApiEmbedding(
            id=embedding_id,
            user_id=test_user.id,
            swagger_spec_id=test_swagger_spec.id,
            endpoint_path="/test",
            method="POST",
            description="Test endpoint",
            embedding="[0.1, 0.2, 0.3]",
        )
        db_session.add(api_embedding)

        db_session.commit()

        # Перевіряємо що всі зв'язки працюють
        assert len(test_user.swagger_specs) == 1
        assert len(test_user.chat_sessions) == 1
        assert len(test_user.prompt_templates) == 1
        assert len(test_user.api_tokens) == 1
        assert len(test_user.api_embeddings) == 1

        assert test_user.swagger_specs[0] == test_swagger_spec
        assert test_user.chat_sessions[0] == chat_session
        assert test_user.prompt_templates[0] == prompt_template
        assert test_user.api_tokens[0] == api_token
        assert test_user.api_embeddings[0] == api_embedding

    def test_swagger_spec_relationships(self, db_session, test_user, test_swagger_spec):
        """Тест зв'язків Swagger специфікації"""
        # Створюємо додаткові дані
        session_id = str(uuid.uuid4())
        chat_session = ChatSession(
            id=session_id,
            user_id=test_user.id,
            swagger_spec_id=test_swagger_spec.id,
            session_name="Test Session",
        )
        db_session.add(chat_session)

        token_id = str(uuid.uuid4())
        api_token = ApiToken(
            id=token_id,
            user_id=test_user.id,
            swagger_spec_id=test_swagger_spec.id,
            token_name="Test Token",
            token_value="test-value",
            token_type="api_key",
        )
        db_session.add(api_token)

        embedding_id = str(uuid.uuid4())
        api_embedding = ApiEmbedding(
            id=embedding_id,
            user_id=test_user.id,
            swagger_spec_id=test_swagger_spec.id,
            endpoint_path="/test",
            method="POST",
            description="Test endpoint",
            embedding="[0.1, 0.2, 0.3]",
        )
        db_session.add(api_embedding)

        db_session.commit()

        # Перевіряємо зв'язки
        assert len(test_swagger_spec.chat_sessions) == 1
        assert len(test_swagger_spec.api_tokens) == 1
        assert len(test_swagger_spec.api_embeddings) == 1

        assert test_swagger_spec.chat_sessions[0] == chat_session
        assert test_swagger_spec.api_tokens[0] == api_token
        assert test_swagger_spec.api_embeddings[0] == api_embedding

    def test_chat_session_messages(self, db_session, test_user, test_swagger_spec):
        """Тест повідомлень чат сесії"""
        session_id = str(uuid.uuid4())
        chat_session = ChatSession(
            id=session_id,
            user_id=test_user.id,
            swagger_spec_id=test_swagger_spec.id,
            session_name="Test Session",
        )
        db_session.add(chat_session)
        db_session.commit()

        # Створюємо кілька повідомлень
        messages = []
        for i in range(3):
            message_id = str(uuid.uuid4())
            message = ChatMessage(
                id=message_id,
                chat_session_id=session_id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i + 1}",
            )
            db_session.add(message)
            messages.append(message)

        db_session.commit()

        # Перевіряємо зв'язки
        assert len(chat_session.messages) == 3
        for i, message in enumerate(chat_session.messages):
            assert message.role == ("user" if i % 2 == 0 else "assistant")
            assert message.content == f"Message {i + 1}"

    def test_query_performance(self, db_session, test_user):
        """Тест продуктивності запитів"""
        # Створюємо багато записів для тестування
        swagger_specs = []
        for i in range(10):
            spec_id = str(uuid.uuid4())
            spec = SwaggerSpec(
                id=spec_id,
                user_id=test_user.id,
                filename=f"api_{i}.json",
                original_data={"openapi": "3.0.0", "info": {"title": f"API {i}"}},
                parsed_data={"endpoints": []},
                endpoints_count=i,
                is_active=True,
            )
            db_session.add(spec)
            swagger_specs.append(spec)

        db_session.commit()

        # Тестуємо швидкість запиту
        import time

        start_time = time.time()

        # Запит з фільтрацією
        active_specs = (
            db_session.query(SwaggerSpec)
            .filter(SwaggerSpec.user_id == test_user.id, SwaggerSpec.is_active == True)
            .all()
        )

        query_time = time.time() - start_time

        assert len(active_specs) == 10
        assert query_time < 0.1  # Запит повинен виконуватися швидко

    def test_data_integrity(self, db_session, test_user):
        """Тест цілісності даних"""
        # Тестуємо унікальність email
        user1 = User(
            id=str(uuid.uuid4()),
            email="unique@example.com",
            username="user1",
            hashed_password=get_password_hash("password"),
        )
        db_session.add(user1)
        db_session.commit()

        # Спробуємо створити користувача з тим же email
        user2 = User(
            id=str(uuid.uuid4()),
            email="unique@example.com",  # Той же email
            username="user2",
            hashed_password=get_password_hash("password"),
        )
        db_session.add(user2)

        # Повинно викликати помилку унікальності
        with pytest.raises(Exception):
            db_session.commit()

        db_session.rollback()

    def test_cascade_delete(self, db_session, test_user, test_swagger_spec):
        """Тест каскадного видалення"""
        # Створюємо залежні записи
        session_id = str(uuid.uuid4())
        chat_session = ChatSession(
            id=session_id,
            user_id=test_user.id,
            swagger_spec_id=test_swagger_spec.id,
            session_name="Test Session",
        )
        db_session.add(chat_session)

        message_id = str(uuid.uuid4())
        chat_message = ChatMessage(
            id=message_id, chat_session_id=session_id, role="user", content="Test message"
        )
        db_session.add(chat_message)

        db_session.commit()

        # Перевіряємо що записи існують
        assert (
            db_session.query(ChatSession).filter(ChatSession.id == session_id).first() is not None
        )
        assert (
            db_session.query(ChatMessage).filter(ChatMessage.id == message_id).first() is not None
        )

        # Видаляємо чат сесію
        db_session.delete(chat_session)
        db_session.commit()

        # Перевіряємо що повідомлення також видалено
        assert db_session.query(ChatSession).filter(ChatSession.id == session_id).first() is None
        assert db_session.query(ChatMessage).filter(ChatMessage.id == message_id).first() is None


class TestDatabaseAPI:
    """Тести API інтеграції з базою даних"""

    def test_health_check(self, client):
        """Тест health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_create_user_api(self, client, db_session):
        """Тест створення користувача через API"""
        user_data = {"email": "api@example.com", "username": "apiuser", "password": "testpassword"}

        response = client.post("/users/", json=user_data)
        assert response.status_code == 201

        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "id" in data

    def test_get_user_api(self, client, test_user):
        """Тест отримання користувача через API"""
        response = client.get(f"/users/{test_user.id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username

    def test_create_swagger_spec_api(self, client, test_user):
        """Тест створення Swagger специфікації через API"""
        swagger_data = {
            "filename": "test_api.json",
            "original_data": {"openapi": "3.0.0", "info": {"title": "Test API"}},
            "parsed_data": {"endpoints": []},
            "base_url": "https://api.example.com",
        }

        response = client.post(f"/users/{test_user.id}/swagger-specs/", json=swagger_data)
        assert response.status_code == 201

        data = response.json()
        assert data["filename"] == swagger_data["filename"]
        assert data["base_url"] == swagger_data["base_url"]
        assert "id" in data

    def test_get_swagger_specs_api(self, client, test_user, test_swagger_spec):
        """Тест отримання Swagger специфікацій через API"""
        response = client.get(f"/users/{test_user.id}/swagger-specs/")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == test_swagger_spec.id
        assert data[0]["filename"] == test_swagger_spec.filename


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
