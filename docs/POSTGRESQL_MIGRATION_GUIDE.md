# 🐘 Міграція на PostgreSQL - Гід

## 📋 Огляд

Цей гід описує процес міграції системи з SQLite на PostgreSQL для зберігання промптів та користувацьких даних.

## 🎯 Переваги PostgreSQL

### ✅ Підтримка конкурентного доступу
- Множество користувачів можуть працювати одночасно
- Транзакційна цілісність даних
- Блокування на рівні рядків

### ✅ Масштабованість
- Обробка великих обсягів даних
- Індекси для швидкого пошуку
- Підтримка складних запитів

### ✅ Надійність
- ACID транзакції
- Автоматичне резервне копіювання
- Відновлення після збоїв

## 🚀 Швидкий старт

### 1. Запуск PostgreSQL

```bash
# Запускаємо базу даних
./scripts/start_postgres.sh

# Або вручну
docker-compose up -d db
```

### 2. Міграція даних

```bash
# Мігруємо промпти з SQLite в PostgreSQL
python scripts/migrate_to_postgres.py

# Або через CLI
python cli_tester.py migrate-prompts
```

### 3. Тестування

```bash
# Тестуємо PostgreSQL промпти
python cli_tester.py test-postgres-prompts

# Переглядаємо список промптів
python cli_tester.py list-postgres-prompts
```

## 📊 Структура бази даних

### Таблиці промптів

#### `prompt_templates`
```sql
CREATE TABLE prompt_templates (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    is_public BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    usage_count INTEGER DEFAULT 0,
    success_rate REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `prompt_usage_history`
```sql
CREATE TABLE prompt_usage_history (
    id VARCHAR(36) PRIMARY KEY,
    prompt_template_id VARCHAR(36) NOT NULL,
    user_query TEXT,
    context TEXT,
    result TEXT,
    success BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prompt_template_id) REFERENCES prompt_templates (id)
);
```

#### `prompt_settings`
```sql
CREATE TABLE prompt_settings (
    key VARCHAR(255) PRIMARY KEY,
    value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Таблиці користувачів

#### `users`
```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `chat_sessions`
```sql
CREATE TABLE chat_sessions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    swagger_spec_id VARCHAR(36),
    session_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (swagger_spec_id) REFERENCES swagger_specs (id)
);
```

## 🔧 Налаштування

### Змінні середовища

```bash
# PostgreSQL налаштування
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_swagger_bot

# Для розробки
DATABASE_URL=postgresql://postgres:postgres@db:5432/ai_swagger_bot

# Для продакшену
DATABASE_URL=postgresql://username:password@host:5432/database
```

### Конфігурація в коді

```python
from src.postgres_prompt_manager import PostgresPromptManager

# Використання PostgreSQL менеджера
manager = PostgresPromptManager()

# Додавання промпту
prompt = PromptTemplate(
    name="Мій промпт",
    description="Опис промпту",
    template="Шаблон промпту",
    category="custom"
)

prompt_id = manager.add_prompt(prompt)
```

## 📈 Моніторинг

### Перевірка статусу

```bash
# Статус контейнерів
docker-compose ps

# Логи бази даних
docker-compose logs db

# Підключення до бази
docker-compose exec db psql -U postgres -d ai_swagger_bot
```

### Статистика промптів

```python
from src.postgres_prompt_manager import PostgresPromptManager

manager = PostgresPromptManager()
stats = manager.get_statistics()

print(f"Загальна кількість: {stats['total_prompts']}")
print(f"Активних: {stats['active_prompts']}")
print(f"Середній успіх: {stats['avg_success_rate']:.2%}")
```

## 🔄 Міграція даних

### Автоматична міграція

```python
from src.postgres_prompt_manager import PostgresPromptManager

manager = PostgresPromptManager()
manager.migrate_from_sqlite("prompts.db")
```

### Ручна міграція

```sql
-- Експорт з SQLite
sqlite3 prompts.db ".dump" > prompts_backup.sql

-- Імпорт в PostgreSQL
psql -U postgres -d ai_swagger_bot -f prompts_backup.sql
```

## 🛠️ Розробка

### Створення таблиць

```python
from api.database import create_tables

# Створюємо всі таблиці
create_tables()
```

### Тестування

```bash
# Тестування підключення
python cli_tester.py test-postgres-prompts

# Тестування міграції
python cli_tester.py migrate-prompts

# Перегляд даних
python cli_tester.py list-postgres-prompts
```

## 🔒 Безпека

### Налаштування безпеки

```sql
-- Створення користувача з обмеженими правами
CREATE USER ai_swagger_user WITH PASSWORD 'secure_password';

-- Надання прав
GRANT CONNECT ON DATABASE ai_swagger_bot TO ai_swagger_user;
GRANT USAGE ON SCHEMA public TO ai_swagger_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ai_swagger_user;
```

### Резервне копіювання

```bash
# Створення резервної копії
docker-compose exec db pg_dump -U postgres ai_swagger_bot > backup.sql

# Відновлення з резервної копії
docker-compose exec -T db psql -U postgres ai_swagger_bot < backup.sql
```

## 🚨 Вирішення проблем

### Проблема: Не вдається підключитися до бази

```bash
# Перевірка статусу контейнера
docker-compose ps

# Перезапуск бази даних
docker-compose restart db

# Перевірка логів
docker-compose logs db
```

### Проблема: Помилка міграції

```bash
# Очищення таблиць
python cli_tester.py list-postgres-prompts

# Повторна міграція
python cli_tester.py migrate-prompts
```

### Проблема: Повільні запити

```sql
-- Створення індексів
CREATE INDEX idx_prompt_templates_category ON prompt_templates(category);
CREATE INDEX idx_prompt_templates_user_id ON prompt_templates(user_id);
CREATE INDEX idx_prompt_usage_history_prompt_id ON prompt_usage_history(prompt_template_id);
```

## 📚 Додаткові ресурси

- [PostgreSQL документація](https://www.postgresql.org/docs/)
- [SQLAlchemy документація](https://docs.sqlalchemy.org/)
- [Docker Compose документація](https://docs.docker.com/compose/)

## 🤝 Підтримка

Якщо у вас виникли проблеми:

1. Перевірте логи: `docker-compose logs db`
2. Перевірте статус: `docker-compose ps`
3. Створіть issue в репозиторії
4. Зверніться до документації PostgreSQL
