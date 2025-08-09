# Інтеграційні тести бази даних

Цей документ описує інтеграційні тести для перевірки запитів з базою даних в AI Swagger Bot.

## Огляд

Інтеграційні тести перевіряють:
- Створення та модифікацію записів в базі даних
- Зв'язки між таблицями (relationships)
- Складні запити з JOIN, GROUP BY, агрегатними функціями
- Продуктивність запитів
- API інтеграцію з базою даних
- Цілісність даних та обмеження

## Структура тестів

### 1. Основні інтеграційні тести (`test_database_integration.py`)

#### Тести створення записів:
- `test_create_user` - створення користувача
- `test_create_swagger_spec` - створення Swagger специфікації
- `test_create_chat_session` - створення чат сесії
- `test_create_chat_message` - створення повідомлення чату
- `test_create_prompt_template` - створення шаблону промпту
- `test_create_api_token` - створення API токена
- `test_create_api_embedding` - створення API embedding

#### Тести зв'язків:
- `test_user_relationships` - перевірка всіх зв'язків користувача
- `test_swagger_spec_relationships` - перевірка зв'язків Swagger специфікації
- `test_chat_session_messages` - перевірка повідомлень чат сесії

#### Тести продуктивності:
- `test_query_performance` - тест швидкості запитів
- `test_data_integrity` - тест цілісності даних
- `test_cascade_delete` - тест каскадного видалення

#### API тести:
- `test_health_check` - перевірка health check endpoint
- `test_create_user_api` - створення користувача через API
- `test_get_user_api` - отримання користувача через API
- `test_create_swagger_spec_api` - створення Swagger специфікації через API
- `test_get_swagger_specs_api` - отримання Swagger специфікацій через API

### 2. Тести складних запитів (`test_database_queries.py`)

#### Складні запити:
- `test_user_with_most_swagger_specs` - користувач з найбільшою кількістю специфікацій
- `test_active_swagger_specs_by_user` - активні специфікації користувача
- `test_chat_sessions_with_message_count` - сесії з кількістю повідомлень
- `test_recent_chat_messages` - нещодавні повідомлення
- `test_user_activity_summary` - зведення активності користувача
- `test_search_swagger_specs_by_content` - пошук специфікацій за вмістом
- `test_chat_sessions_by_date_range` - сесії за діапазоном дат
- `test_user_with_most_chat_activity` - користувач з найбільшою активністю
- `test_swagger_specs_with_endpoint_count` - специфікації з кількістю endpoint'ів
- `test_inactive_users` - неактивні користувачі
- `test_swagger_specs_by_user_and_date` - специфікації по користувачу та даті

#### Тести продуктивності:
- `test_large_dataset_query_performance` - продуктивність на великому наборі даних
- `test_complex_join_performance` - продуктивність складних JOIN запитів
- `test_index_usage` - використання індексів

## Запуск тестів

### 1. Локальний запуск

```bash
# Всі тести бази даних
make test-db-all

# Тільки інтеграційні тести
make test-db-integration

# Тільки тести запитів
make test-db-queries
```

### 2. Запуск в Docker

```bash
# Всі інтеграційні тести
make test-integration

# Повні інтеграційні тести
make test-integration-full

# Тести продуктивності
make test-performance

# API інтеграційні тести
make test-api-integration
```

### 3. Використання скрипта

```bash
# Всі тести
./scripts/run_integration_tests.sh

# Окремі типи тестів
./scripts/run_integration_tests.sh integration
./scripts/run_integration_tests.sh performance
./scripts/run_integration_tests.sh api
./scripts/run_integration_tests.sh full

# Довідка
./scripts/run_integration_tests.sh help
```

### 4. Docker Compose команди

```bash
# Запуск тестової бази даних
docker-compose -f docker-compose.integration.yml up test-db -d

# Запуск всіх тестів
docker-compose -f docker-compose.integration.yml up --build

# Очищення
docker-compose -f docker-compose.integration.yml down -v
```

## Конфігурація

### Тестова база даних

Для локальних тестів використовується SQLite:
```python
TEST_DATABASE_URL = "sqlite:///./test.db"
```

Для Docker тестів використовується PostgreSQL:
```yaml
DATABASE_URL=postgresql://postgres:postgres@test-db:5432/ai_swagger_bot_test
```

### Змінні середовища

- `TESTING=true` - режим тестування
- `DATABASE_URL` - URL тестової бази даних
- `OPENAI_API_KEY` - API ключ для тестів (може бути тестовий)
- `USE_PGVECTOR=true` - використання pgvector

## Структура тестової бази даних

### Таблиці:
- `users` - користувачі
- `swagger_specs` - Swagger специфікації
- `chat_sessions` - чат сесії
- `chat_messages` - повідомлення чату
- `prompt_templates` - шаблони промптів
- `api_tokens` - API токени
- `api_embeddings` - API embeddings

### Зв'язки:
- User ↔ SwaggerSpec (1:N)
- User ↔ ChatSession (1:N)
- User ↔ PromptTemplate (1:N)
- User ↔ ApiToken (1:N)
- User ↔ ApiEmbedding (1:N)
- SwaggerSpec ↔ ChatSession (1:N)
- SwaggerSpec ↔ ApiToken (1:N)
- SwaggerSpec ↔ ApiEmbedding (1:N)
- ChatSession ↔ ChatMessage (1:N)

## Фікстури

### Основні фікстури:
- `test_db` - створення тестової бази даних
- `db_session` - сесія бази даних з транзакцією
- `client` - тестовий FastAPI клієнт
- `test_user` - тестовий користувач
- `test_swagger_spec` - тестова Swagger специфікація

### Фікстури для складних тестів:
- `test_users` - набір тестових користувачів
- `test_swagger_specs` - набір Swagger специфікацій
- `test_chat_sessions` - набір чат сесій
- `test_chat_messages` - набір повідомлень чату

## Приклади тестів

### Простий тест створення:

```python
def test_create_user(self, db_session):
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("password"),
        is_active=True
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id == user_id
    assert user.email == "test@example.com"
```

### Складний запит:

```python
def test_user_with_most_swagger_specs(self, db_session, test_users, test_swagger_specs):
    result = db_session.query(
        User,
        func.count(SwaggerSpec.id).label('spec_count')
    ).join(SwaggerSpec).group_by(User.id).order_by(
        func.count(SwaggerSpec.id).desc()
    ).first()

    assert result is not None
    assert result.spec_count == 3
```

### API тест:

```python
def test_create_user_api(self, client, db_session):
    user_data = {
        "email": "api@example.com",
        "username": "apiuser",
        "password": "testpassword"
    }

    response = client.post("/users/", json=user_data)
    assert response.status_code == 201

    data = response.json()
    assert data["email"] == user_data["email"]
```

## Моніторинг та логування

### Логи тестів:
- Тести виводять детальну інформацію про виконання
- Покриття коду (coverage) генерується автоматично
- Результати зберігаються в `logs/` директорії

### Метрики продуктивності:
- Час виконання запитів
- Кількість запитів до бази даних
- Використання пам'яті

## Troubleshooting

### Поширені проблеми:

1. **Помилка підключення до бази даних**
   ```bash
   # Перевірте що PostgreSQL запущений
   docker-compose -f docker-compose.integration.yml up test-db -d
   ```

2. **Помилки імпорту**
   ```bash
   # Перевірте PYTHONPATH
   export PYTHONPATH=/app
   ```

3. **Помилки транзакцій**
   ```bash
   # Очистіть тестові файли
   rm -f test.db test_queries.db
   ```

4. **Повільні тести**
   ```bash
   # Використовуйте тільки необхідні тести
   make test-db-integration
   ```

### Діагностика:

```bash
# Перевірка статусу контейнерів
docker-compose -f docker-compose.integration.yml ps

# Логи тестів
docker-compose -f docker-compose.integration.yml logs integration-tests

# Підключення до тестової бази даних
docker exec -it ai-swagger-bot-test-db psql -U postgres -d ai_swagger_bot_test
```

## Розширення тестів

### Додавання нових тестів:

1. Створіть новий тестовий клас
2. Додайте необхідні фікстури
3. Напишіть тести з використанням `db_session`
4. Додайте команди в Makefile

### Приклад нового тесту:

```python
class TestNewFeature:
    def test_new_database_operation(self, db_session, test_user):
        # Ваш тест тут
        pass
```

## CI/CD інтеграція

### GitHub Actions:

```yaml
- name: Run Integration Tests
  run: |
    make test-integration
```

### GitLab CI:

```yaml
integration_tests:
  script:
    - make test-integration
```

## Висновок

Інтеграційні тести забезпечують надійну перевірку роботи з базою даних та допомагають виявити проблеми на ранніх етапах розробки. Регулярний запуск цих тестів гарантує стабільність системи.
