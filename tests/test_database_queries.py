"""
Тести складних запитів до бази даних
"""

import uuid
from datetime import datetime, timedelta
from typing import Generator

import pytest
from api.auth import get_password_hash

# Імпортуємо моделі
from api.models import (
    ApiEmbedding,
    Base,
    ChatMessage,
    ChatSession,
    PromptTemplate,
    SwaggerSpec,
    User,
)
from sqlalchemy import and_, create_engine, func, or_
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Тестова база даних
TEST_DATABASE_URL = "sqlite:///./test_queries.db"

# Створюємо тестовий engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

# Тестова сесія
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session")
def test_db():
    """Створення тестової бази даних"""
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
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
def test_users(db_session):
    """Створення тестових користувачів"""
    users = []
    for i in range(5):
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            email=f"user{i}@example.com",
            username=f"user{i}",
            hashed_password=get_password_hash("password"),
            is_active=True,
        )
        db_session.add(user)
        users.append(user)

    db_session.commit()
    return users


@pytest.fixture
def test_swagger_specs(db_session, test_users):
    """Створення тестових Swagger специфікацій"""
    specs = []
    for i, user in enumerate(test_users):
        for j in range(3):  # 3 специфікації на користувача
            spec_id = str(uuid.uuid4())
            spec = SwaggerSpec(
                id=spec_id,
                user_id=user.id,
                filename=f"api_{i}_{j}.json",
                original_data={"openapi": "3.0.0", "info": {"title": f"API {i}_{j}"}},
                parsed_data={"endpoints": [{"path": f"/endpoint{j}", "method": "GET"}]},
                base_url=f"https://api{i}.example.com",
                endpoints_count=j + 1,
                is_active=True,
            )
            db_session.add(spec)
            specs.append(spec)

    db_session.commit()
    return specs


@pytest.fixture
def test_chat_sessions(db_session, test_users, test_swagger_specs):
    """Створення тестових чат сесій"""
    sessions = []
    for i, user in enumerate(test_users):
        for j in range(2):  # 2 сесії на користувача
            session_id = str(uuid.uuid4())
            session = ChatSession(
                id=session_id,
                user_id=user.id,
                swagger_spec_id=test_swagger_specs[i * 3 + j].id,
                session_name=f"Session {i}_{j}",
                is_active=True,
            )
            db_session.add(session)
            sessions.append(session)

    db_session.commit()
    return sessions


@pytest.fixture
def test_chat_messages(db_session, test_chat_sessions):
    """Створення тестових повідомлень чату"""
    messages = []
    for session in test_chat_sessions:
        for i in range(5):  # 5 повідомлень на сесію
            message_id = str(uuid.uuid4())
            message = ChatMessage(
                id=message_id,
                chat_session_id=session.id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i} in session {session.session_name}",
            )
            db_session.add(message)
            messages.append(message)

    db_session.commit()
    return messages


class TestComplexQueries:
    """Тести складних запитів до бази даних"""

    def test_user_with_most_swagger_specs(self, db_session, test_users, test_swagger_specs):
        """Тест пошуку користувача з найбільшою кількістю Swagger специфікацій"""
        # Запит для знаходження користувача з найбільшою кількістю специфікацій
        result = (
            db_session.query(User, func.count(SwaggerSpec.id).label("spec_count"))
            .join(SwaggerSpec)
            .group_by(User.id)
            .order_by(func.count(SwaggerSpec.id).desc())
            .first()
        )

        assert result is not None
        assert result.spec_count == 3  # Кожен користувач має 3 специфікації

        # Перевіряємо що це дійсно користувач з найбільшою кількістю
        all_counts = (
            db_session.query(User.id, func.count(SwaggerSpec.id).label("spec_count"))
            .join(SwaggerSpec)
            .group_by(User.id)
            .all()
        )

        max_count = max(count for _, count in all_counts)
        assert result.spec_count == max_count

    def test_active_swagger_specs_by_user(self, db_session, test_users, test_swagger_specs):
        """Тест пошуку активних Swagger специфікацій по користувачу"""
        user = test_users[0]

        # Запит для знаходження активних специфікацій користувача
        active_specs = (
            db_session.query(SwaggerSpec)
            .filter(and_(SwaggerSpec.user_id == user.id, SwaggerSpec.is_active == True))
            .all()
        )

        assert len(active_specs) == 3
        for spec in active_specs:
            assert spec.user_id == user.id
            assert spec.is_active is True

    def test_chat_sessions_with_message_count(
        self, db_session, test_chat_sessions, test_chat_messages
    ):
        """Тест пошуку чат сесій з кількістю повідомлень"""
        # Запит для знаходження сесій з кількістю повідомлень
        sessions_with_count = (
            db_session.query(ChatSession, func.count(ChatMessage.id).label("message_count"))
            .join(ChatMessage)
            .group_by(ChatSession.id)
            .all()
        )

        assert len(sessions_with_count) == len(test_chat_sessions)

        for session, count in sessions_with_count:
            assert count == 5  # Кожна сесія має 5 повідомлень

    def test_recent_chat_messages(self, db_session, test_chat_messages):
        """Тест пошуку нещодавніх повідомлень чату"""
        # Створюємо повідомлення з різними датами
        recent_message = ChatMessage(
            id=str(uuid.uuid4()),
            chat_session_id=test_chat_messages[0].chat_session_id,
            role="user",
            content="Recent message",
            created_at=datetime.utcnow(),
        )
        db_session.add(recent_message)

        old_message = ChatMessage(
            id=str(uuid.uuid4()),
            chat_session_id=test_chat_messages[0].chat_session_id,
            role="user",
            content="Old message",
            created_at=datetime.utcnow() - timedelta(days=7),
        )
        db_session.add(old_message)

        db_session.commit()

        # Запит для знаходження повідомлень за останні 24 години
        recent_messages = (
            db_session.query(ChatMessage)
            .filter(ChatMessage.created_at >= datetime.utcnow() - timedelta(days=1))
            .all()
        )

        # Перевіряємо що знайшли тільки нещодавні повідомлення
        for message in recent_messages:
            assert message.created_at >= datetime.utcnow() - timedelta(days=1)

    def test_user_activity_summary(
        self, db_session, test_users, test_swagger_specs, test_chat_sessions
    ):
        """Тест створення зведення активності користувача"""
        user = test_users[0]

        # Запит для створення зведення активності
        activity_summary = (
            db_session.query(
                User.username,
                func.count(SwaggerSpec.id).label("swagger_count"),
                func.count(ChatSession.id).label("session_count"),
            )
            .outerjoin(SwaggerSpec)
            .outerjoin(ChatSession)
            .filter(User.id == user.id)
            .group_by(User.id, User.username)
            .first()
        )

        assert activity_summary is not None
        assert activity_summary.username == user.username
        assert activity_summary.swagger_count == 3
        assert activity_summary.session_count == 2

    def test_search_swagger_specs_by_content(self, db_session, test_swagger_specs):
        """Тест пошуку Swagger специфікацій за вмістом"""
        # Додаємо специфікацію з певним вмістом
        search_spec = SwaggerSpec(
            id=str(uuid.uuid4()),
            user_id=test_swagger_specs[0].user_id,
            filename="search_api.json",
            original_data={
                "openapi": "3.0.0",
                "info": {"title": "Search API", "description": "API for search functionality"},
            },
            parsed_data={"endpoints": [{"path": "/search", "method": "GET"}]},
            base_url="https://search.example.com",
            endpoints_count=1,
            is_active=True,
        )
        db_session.add(search_spec)
        db_session.commit()

        # Запит для пошуку специфікацій з певним вмістом
        search_results = (
            db_session.query(SwaggerSpec)
            .filter(SwaggerSpec.original_data.contains({"info": {"title": "Search API"}}))
            .all()
        )

        assert len(search_results) == 1
        assert search_results[0].filename == "search_api.json"

    def test_chat_sessions_by_date_range(self, db_session, test_chat_sessions):
        """Тест пошуку чат сесій за діапазоном дат"""
        # Створюємо сесії з різними датами
        today = datetime.utcnow()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)

        recent_session = ChatSession(
            id=str(uuid.uuid4()),
            user_id=test_chat_sessions[0].user_id,
            swagger_spec_id=test_chat_sessions[0].swagger_spec_id,
            session_name="Recent Session",
            created_at=today,
        )
        db_session.add(recent_session)

        old_session = ChatSession(
            id=str(uuid.uuid4()),
            user_id=test_chat_sessions[0].user_id,
            swagger_spec_id=test_chat_sessions[0].swagger_spec_id,
            session_name="Old Session",
            created_at=week_ago,
        )
        db_session.add(old_session)

        db_session.commit()

        # Запит для пошуку сесій за останні 3 дні
        recent_sessions = (
            db_session.query(ChatSession)
            .filter(
                and_(
                    ChatSession.created_at >= today - timedelta(days=3),
                    ChatSession.created_at <= today,
                )
            )
            .all()
        )

        # Перевіряємо що знайшли тільки нещодавні сесії
        for session in recent_sessions:
            assert session.created_at >= today - timedelta(days=3)
            assert session.created_at <= today

    def test_user_with_most_chat_activity(
        self, db_session, test_users, test_chat_sessions, test_chat_messages
    ):
        """Тест пошуку користувача з найбільшою активністю в чаті"""
        # Запит для знаходження користувача з найбільшою кількістю повідомлень
        result = (
            db_session.query(User.username, func.count(ChatMessage.id).label("message_count"))
            .join(ChatSession)
            .join(ChatMessage)
            .group_by(User.id, User.username)
            .order_by(func.count(ChatMessage.id).desc())
            .first()
        )

        assert result is not None
        assert result.message_count > 0

        # Перевіряємо що це дійсно користувач з найбільшою активністю
        all_activity = (
            db_session.query(User.username, func.count(ChatMessage.id).label("message_count"))
            .join(ChatSession)
            .join(ChatMessage)
            .group_by(User.id, User.username)
            .all()
        )

        max_messages = max(count for _, count in all_activity)
        assert result.message_count == max_messages

    def test_swagger_specs_with_endpoint_count(self, db_session, test_swagger_specs):
        """Тест пошуку Swagger специфікацій з кількістю endpoint'ів"""
        # Запит для знаходження специфікацій з найбільшою кількістю endpoint'ів
        specs_by_endpoints = (
            db_session.query(SwaggerSpec.filename, SwaggerSpec.endpoints_count)
            .order_by(SwaggerSpec.endpoints_count.desc())
            .all()
        )

        assert len(specs_by_endpoints) == len(test_swagger_specs)

        # Перевіряємо що результати відсортовані за спаданням
        for i in range(len(specs_by_endpoints) - 1):
            assert (
                specs_by_endpoints[i].endpoints_count >= specs_by_endpoints[i + 1].endpoints_count
            )

    def test_inactive_users(self, db_session, test_users):
        """Тест пошуку неактивних користувачів"""
        # Деактивуємо одного користувача
        inactive_user = test_users[0]
        inactive_user.is_active = False
        db_session.commit()

        # Запит для знаходження неактивних користувачів
        inactive_users = db_session.query(User).filter(User.is_active == False).all()

        assert len(inactive_users) == 1
        assert inactive_users[0].id == inactive_user.id

    def test_swagger_specs_by_user_and_date(self, db_session, test_users, test_swagger_specs):
        """Тест пошуку Swagger специфікацій по користувачу та даті"""
        user = test_users[0]
        today = datetime.utcnow()

        # Створюємо специфікацію з певною датою
        dated_spec = SwaggerSpec(
            id=str(uuid.uuid4()),
            user_id=user.id,
            filename="dated_api.json",
            original_data={"openapi": "3.0.0", "info": {"title": "Dated API"}},
            parsed_data={"endpoints": []},
            base_url="https://dated.example.com",
            endpoints_count=0,
            is_active=True,
            created_at=today,
        )
        db_session.add(dated_spec)
        db_session.commit()

        # Запит для пошуку специфікацій користувача за останній тиждень
        recent_specs = (
            db_session.query(SwaggerSpec)
            .filter(
                and_(
                    SwaggerSpec.user_id == user.id,
                    SwaggerSpec.created_at >= today - timedelta(days=7),
                )
            )
            .all()
        )

        # Перевіряємо що знайшли тільки нещодавні специфікації
        for spec in recent_specs:
            assert spec.user_id == user.id
            assert spec.created_at >= today - timedelta(days=7)


class TestDatabasePerformance:
    """Тести продуктивності бази даних"""

    def test_large_dataset_query_performance(self, db_session, test_users):
        """Тест продуктивності запитів на великому наборі даних"""
        import time

        # Створюємо великий набір даних
        large_specs = []
        for i in range(100):
            spec = SwaggerSpec(
                id=str(uuid.uuid4()),
                user_id=test_users[0].id,
                filename=f"large_api_{i}.json",
                original_data={"openapi": "3.0.0", "info": {"title": f"Large API {i}"}},
                parsed_data={"endpoints": []},
                base_url=f"https://api{i}.example.com",
                endpoints_count=i,
                is_active=True,
            )
            large_specs.append(spec)

        db_session.add_all(large_specs)
        db_session.commit()

        # Тестуємо швидкість запиту з фільтрацією
        start_time = time.time()

        active_specs = (
            db_session.query(SwaggerSpec)
            .filter(and_(SwaggerSpec.user_id == test_users[0].id, SwaggerSpec.is_active == True))
            .all()
        )

        query_time = time.time() - start_time

        assert len(active_specs) == 100
        assert query_time < 1.0  # Запит повинен виконуватися швидко

    def test_complex_join_performance(
        self, db_session, test_users, test_swagger_specs, test_chat_sessions
    ):
        """Тест продуктивності складних JOIN запитів"""
        import time

        # Тестуємо складний JOIN запит
        start_time = time.time()

        user_activity = (
            db_session.query(
                User.username,
                func.count(SwaggerSpec.id).label("spec_count"),
                func.count(ChatSession.id).label("session_count"),
            )
            .outerjoin(SwaggerSpec)
            .outerjoin(ChatSession)
            .group_by(User.id, User.username)
            .all()
        )

        query_time = time.time() - start_time

        assert len(user_activity) == len(test_users)
        assert query_time < 0.5  # Складний запит повинен виконуватися швидко

    def test_index_usage(self, db_session, test_users):
        """Тест використання індексів"""
        # Створюємо записи з різними значеннями для тестування індексів
        for i in range(50):
            user = User(
                id=str(uuid.uuid4()),
                email=f"index_test_{i}@example.com",
                username=f"index_user_{i}",
                hashed_password=get_password_hash("password"),
                is_active=True,
            )
            db_session.add(user)

        db_session.commit()

        # Тестуємо запит з використанням індексу
        import time

        start_time = time.time()

        # Запит по email (повинен використовувати індекс)
        user_by_email = (
            db_session.query(User).filter(User.email == "index_test_25@example.com").first()
        )

        query_time = time.time() - start_time

        assert user_by_email is not None
        assert query_time < 0.1  # Запит з індексом повинен виконуватися дуже швидко


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
