# 🏗️ Архітектура з ізоляцією користувачів

## 📋 Огляд

Нова архітектура AI Swagger Bot забезпечує повну ізоляцію даних між користувачами та ефективне зберігання векторів в PostgreSQL з pgvector.

## 🎯 Основні принципи

### 1. **Ізоляція користувачів**
- Кожен користувач має свої Swagger файли
- Embeddings прив'язані до конкретного користувача
- Промпти ізольовані між користувачами
- API запити виконуються тільки в контексті користувача

### 2. **Зберігання в БД**
- Всі вектори зберігаються в PostgreSQL
- Використання pgvector для векторних операцій
- ACID транзакції для надійності
- Автоматичне резервне копіювання

### 3. **Уникнення дублювання**
- Унікальні констрейни в БД
- Автоматичне оновлення існуючих embeddings
- Очищення дублікатів

## 🗄️ Структура бази даних

### Таблиці з ізоляцією користувачів

#### `users`
```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### `swagger_specs`
```sql
CREATE TABLE swagger_specs (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    original_data JSONB NOT NULL,
    parsed_data JSONB NOT NULL,
    endpoints_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, filename)
);
```

#### `api_embeddings`
```sql
CREATE TABLE api_embeddings (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    swagger_spec_id VARCHAR(36) NOT NULL,
    endpoint_path VARCHAR(500) NOT NULL,
    method VARCHAR(10) NOT NULL,
    description TEXT NOT NULL,
    embedding TEXT NOT NULL, -- JSON string з вектором
    embedding_metadata JSONB, -- Додаткові метадані
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (swagger_spec_id) REFERENCES swagger_specs(id) ON DELETE CASCADE,
    UNIQUE(user_id, swagger_spec_id, endpoint_path, method)
);
```

#### `prompt_templates`
```sql
CREATE TABLE prompt_templates (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36), -- NULL для системних промптів
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    is_public BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    usage_count INTEGER DEFAULT 0,
    success_rate INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, name, category)
);
```

## 🔐 Ізоляція даних

### 1. **Swagger файли**
```python
# Отримання тільки Swagger файлів користувача
swagger_specs = db.query(SwaggerSpec).filter(
    SwaggerSpec.user_id == current_user.id,
    SwaggerSpec.is_active == True
).all()
```

### 2. **Embeddings**
```python
# Пошук embeddings тільки для конкретного користувача
results = vector_manager.search_similar(
    query_embedding=query_embedding,
    user_id=current_user.id,
    swagger_spec_id=swagger_spec_id,
    limit=5
)
```

### 3. **Промпти**
```python
# Отримання промптів користувача + системних
prompts = db.query(PromptTemplate).filter(
    or_(
        PromptTemplate.user_id == current_user.id,
        PromptTemplate.is_public == True
    ),
    PromptTemplate.is_active == True
).all()
```

## 🔍 Пошук та фільтрація

### Пошук embeddings
```python
def search_similar_endpoints(self, query: str, user_id: str, swagger_spec_id: str = None):
    # Створюємо ембедінг для запиту
    query_embedding = self.embeddings.embed_query(query)

    # Шукаємо тільки в embeddings користувача
    results = self.vector_manager.search_similar(
        query_embedding=query_embedding,
        user_id=user_id,
        swagger_spec_id=swagger_spec_id,
        limit=3
    )

    return results
```

### Фільтрація API запитів
```python
# Виконуємо API запити тільки для endpoints з Swagger файлу користувача
swagger_spec = db.query(SwaggerSpec).filter(
    SwaggerSpec.id == session.swagger_spec_id,
    SwaggerSpec.user_id == current_user.id
).first()

if not swagger_spec:
    raise HTTPException(status_code=404, detail="Swagger специфікація не знайдена")
```

## 🚀 Переваги нової архітектури

### ✅ **Безпека**
- Повна ізоляція даних між користувачами
- JWT токени для аутентифікації
- Валідація доступу до ресурсів

### ✅ **Продуктивність**
- Індекси для швидкого пошуку
- Зберігання векторів в БД
- Оптимізовані запити

### ✅ **Надійність**
- ACID транзакції
- Автоматичне резервне копіювання
- Обробка дублікатів

### ✅ **Масштабованість**
- Горизонтальне масштабування PostgreSQL
- Ефективне використання пам'яті
- Оптимізовані індекси

## 🔧 Міграція даних

### Автоматична міграція
```bash
# Запуск міграції
python scripts/migrate_to_user_embeddings.py

# Очищення дублікатів
python scripts/cleanup_duplicates.py
```

### Структура міграції
1. **Створення резервної копії** старої таблиці
2. **Створення нових таблиць** з констрейнтами
3. **Міграція даних** з прив'язкою до системного користувача
4. **Верифікація** успішності міграції

## 📊 Моніторинг

### Статистика користувача
```python
def get_user_statistics(user_id: str):
    return {
        "swagger_specs_count": len(user_swagger_specs),
        "embeddings_count": len(user_embeddings),
        "prompts_count": len(user_prompts),
        "api_calls_count": len(user_api_calls)
    }
```

### Загальна статистика
```python
def get_system_statistics():
    return {
        "total_users": users_count,
        "total_embeddings": embeddings_count,
        "total_swagger_specs": swagger_count,
        "active_sessions": active_sessions_count
    }
```

## 🛡️ Безпека

### Валідація доступу
```python
def validate_user_access(user_id: str, resource_id: str, resource_type: str):
    """Перевіряє чи має користувач доступ до ресурсу"""
    if resource_type == "swagger_spec":
        return db.query(SwaggerSpec).filter(
            SwaggerSpec.id == resource_id,
            SwaggerSpec.user_id == user_id
        ).first() is not None
    # ... інші типи ресурсів
```

### JWT токени
```python
def create_user_token(user_id: str, user_name: str = None):
    payload = {
        'sub': user_id,
        'name': user_name or f'User {user_id}',
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')
```

## 🔄 Життєвий цикл даних

### 1. **Завантаження Swagger**
```python
# Користувач завантажує Swagger файл
swagger_spec = SwaggerSpec(
    user_id=current_user.id,
    filename=file.filename,
    original_data=swagger_data,
    parsed_data=parsed_data
)
db.add(swagger_spec)
db.commit()

# Створюються embeddings для цього файлу
rag_engine = PostgresRAGEngine(user_id=current_user.id, swagger_spec_id=swagger_spec.id)
rag_engine.create_vectorstore_from_swagger(temp_file_path)
```

### 2. **Чат з AI**
```python
# Отримуємо контекст з embeddings користувача
similar_endpoints = rag_engine.search_similar_endpoints(query, limit=3)

# Виконуємо запит з контекстом
response = agent.process_query(enhanced_message)
```

### 3. **Видалення даних**
```python
# При видаленні Swagger файлу автоматично видаляються embeddings
# завдяки CASCADE в БД
db.delete(swagger_spec)
db.commit()
```

## 📈 Масштабування

### Горизонтальне масштабування
- Реплікація PostgreSQL для читання
- Шардинг по користувачах
- Кешування результатів

### Вертикальне масштабування
- Збільшення ресурсів сервера
- Оптимізація індексів
- Налаштування пулів з'єднань

## 🎯 Висновки

Нова архітектура забезпечує:

1. **Повну ізоляцію** даних між користувачами
2. **Ефективне зберігання** векторів в БД
3. **Уникнення дублювання** через констрейни
4. **Високу продуктивність** завдяки індексам
5. **Надійність** через ACID транзакції
6. **Масштабованість** для зростання користувачів
