# 🔐 AI Swagger Bot - Архітектура з ізоляцією користувачів

## 🎯 Проблема, яку вирішуємо

**Раніше:** Всі користувачі мали доступ до спільних embeddings та Swagger файлів, що призводило до:
- ❌ Порушення приватності даних
- ❌ Змішування контексту між користувачами
- ❌ Неможливість масштабування
- ❌ Складність управління даними

**Тепер:** Повна ізоляція даних з ефективним зберіганням в PostgreSQL:
- ✅ Кожен користувач має свої дані
- ✅ Embeddings зберігаються в БД (не в пам'яті)
- ✅ Унікальні констрейни запобігають дублюванню
- ✅ Високі індекси для швидкого пошуку

## 🏗️ Нова архітектура

### 📊 Структура даних

```
Користувач A:
├── Swagger файли (A)
├── Embeddings (A)
├── Промпти (A)
└── API запити (A)

Користувач B:
├── Swagger файли (B)
├── Embeddings (B)
├── Промпти (B)
└── API запити (B)
```

### 🔗 Зв'язки в БД

```sql
users (1) ←→ (N) swagger_specs
swagger_specs (1) ←→ (N) api_embeddings
users (1) ←→ (N) prompt_templates
users (1) ←→ (N) chat_sessions
```

## 🚀 Швидкий старт

### 1. Запуск міграції
```bash
# Міграція до нової структури
python scripts/migrate_to_user_embeddings.py

# Очищення дублікатів
python scripts/cleanup_duplicates.py
```

### 2. Створення таблиць
```bash
# Створення всіх таблиць з констрейнтами
python scripts/create_tables.py
```

### 3. Запуск API
```bash
# Запуск FastAPI сервісу
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## 🔐 Безпека та ізоляція

### JWT Аутентифікація
```python
# Створення токена для користувача
token = create_user_token(user_id="user123", user_name="John")

# Перевірка токена в API
@app.post("/chat")
async def chat(request: UserRequest, current_user: User = Depends(get_current_user)):
    # current_user.id - ID користувача з токена
    pass
```

### Ізоляція даних
```python
# Отримання тільки Swagger файлів користувача
swagger_specs = db.query(SwaggerSpec).filter(
    SwaggerSpec.user_id == current_user.id,
    SwaggerSpec.is_active == True
).all()

# Пошук embeddings тільки для користувача
results = rag_engine.search_similar_endpoints(
    query=user_query,
    user_id=current_user.id,
    swagger_spec_id=session.swagger_spec_id
)
```

## 📊 API Endpoints

### Завантаження Swagger
```http
POST /upload-swagger
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data

file: swagger.json
```

### Чат з AI
```http
POST /chat
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "message": "Покажи всі endpoints для користувачів"
}
```

### Статистика користувача
```http
GET /statistics
Authorization: Bearer <jwt_token>
```

## 🗄️ База даних

### Основні таблиці

#### `users`
- Унікальні користувачі системи
- JWT токени для аутентифікації

#### `swagger_specs`
- Swagger файли користувачів
- Унікальний констрейнт: `(user_id, filename)`

#### `api_embeddings`
- Вектори для пошуку
- Унікальний констрейнт: `(user_id, swagger_spec_id, endpoint_path, method)`
- CASCADE видалення при видаленні користувача/Swagger файлу

#### `prompt_templates`
- Промпти користувачів + системні
- Унікальний констрейнт: `(user_id, name, category)`

### Індекси для продуктивності
```sql
-- Швидкий пошук по користувачу
CREATE INDEX idx_embedding_user_swagger ON api_embeddings(user_id, swagger_spec_id);

-- Швидкий пошук по endpoint
CREATE INDEX idx_embedding_method_path ON api_embeddings(method, endpoint_path);

-- Сортування по даті
CREATE INDEX idx_embedding_created ON api_embeddings(created_at);
```

## 🔍 Пошук та RAG

### Створення embeddings
```python
# При завантаженні Swagger файлу
rag_engine = PostgresRAGEngine(
    user_id=current_user.id,
    swagger_spec_id=swagger_spec.id
)

# Створення векторів для endpoints
rag_engine.create_vectorstore_from_swagger(swagger_file_path)
```

### Пошук подібних endpoints
```python
# Пошук в контексті користувача
similar_endpoints = rag_engine.search_similar_endpoints(
    query="знайти endpoint для створення користувача",
    user_id=current_user.id,
    swagger_spec_id=session.swagger_spec_id,
    limit=3
)
```

## 🛠️ Утиліти

### Очищення дублікатів
```bash
python scripts/cleanup_duplicates.py
```

### Перегляд статистики
```bash
python scripts/view_vectors.py
```

### Міграція даних
```bash
python scripts/migrate_to_user_embeddings.py
```

## 📈 Моніторинг

### Статистика користувача
```python
{
    "user_id": "user123",
    "swagger_specs_count": 2,
    "embeddings_count": 45,
    "messages_count": 128
}
```

### Загальна статистика
```python
{
    "total_users": 15,
    "total_embeddings": 1250,
    "total_swagger_specs": 23,
    "active_sessions": 8
}
```

## 🔧 Налаштування

### Змінні середовища
```bash
# База даних
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_swagger_bot

# OpenAI
OPENAI_API_KEY=your_openai_key

# JWT
JWT_SECRET_KEY=your_secret_key

# Очищення дублікатів при старті
CLEANUP_DUPLICATES_ON_STARTUP=true
```

### Docker Compose
```yaml
version: '3.8'
services:
  db:
    image: pgvector/pgvector:pg15
    environment:
      POSTGRES_DB: ai_swagger_bot
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:postgres@db:5432/ai_swagger_bot
    depends_on:
      - db
```

## 🚀 Переваги нової архітектури

### ✅ **Безпека**
- Повна ізоляція даних між користувачами
- JWT токени для аутентифікації
- Валідація доступу до ресурсів

### ✅ **Продуктивність**
- Вектори зберігаються в БД (не в пам'яті)
- Індекси для швидкого пошуку
- Оптимізовані запити

### ✅ **Надійність**
- ACID транзакції PostgreSQL
- Автоматичне резервне копіювання
- Обробка дублікатів

### ✅ **Масштабованість**
- Горизонтальне масштабування PostgreSQL
- Ефективне використання пам'яті
- Оптимізовані індекси

## 🔄 Міграція з старої архітектури

### Автоматична міграція
1. **Резервна копія** - стару таблицю перейменовуємо
2. **Нові таблиці** - створюємо з констрейнтами
3. **Міграція даних** - переносимо з прив'язкою до системного користувача
4. **Верифікація** - перевіряємо успішність

### Ручна міграція
```sql
-- Створення резервної копії
ALTER TABLE api_embeddings RENAME TO api_embeddings_old;

-- Створення нової таблиці
CREATE TABLE api_embeddings (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    swagger_spec_id VARCHAR(36) NOT NULL,
    endpoint_path VARCHAR(500) NOT NULL,
    method VARCHAR(10) NOT NULL,
    description TEXT NOT NULL,
    embedding TEXT NOT NULL,
    embedding_metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (swagger_spec_id) REFERENCES swagger_specs(id) ON DELETE CASCADE,
    UNIQUE(user_id, swagger_spec_id, endpoint_path, method)
);

-- Міграція даних
INSERT INTO api_embeddings (id, user_id, swagger_spec_id, endpoint_path, method, description, embedding, metadata, created_at)
SELECT id, 'system', 'system-swagger', endpoint_path, method, description, embedding, metadata, created_at
FROM api_embeddings_old;
```

## 🎯 Висновки

Нова архітектура забезпечує:

1. **Повну ізоляцію** даних між користувачами
2. **Ефективне зберігання** векторів в БД
3. **Уникнення дублювання** через констрейни
4. **Високу продуктивність** завдяки індексам
5. **Надійність** через ACID транзакції
6. **Масштабованість** для зростання користувачів

---

**AI Swagger Bot** - Робіть API простішими з повною ізоляцією користувачів! 🚀
