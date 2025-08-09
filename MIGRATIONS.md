# Database Migrations with Alembic

## Обзор

Проект использует Alembic для управления миграциями базы данных. Все изменения схемы БД должны выполняться через миграции.

## Структура

```
alembic/
├── env.py                 # Конфигурация Alembic
├── script.py.mako        # Шаблон для новых миграций
└── versions/             # Файлы миграций
    └── f175caf04ca9_initial_migration_create_all_tables.py
alembic.ini               # Конфигурация Alembic
```

## Основные команды

### Просмотр статуса миграций
```bash
alembic current          # Текущая миграция
alembic history          # История миграций
alembic show f175caf04ca9  # Детали конкретной миграции
```

### Создание новой миграции
```bash
# Автогенерация на основе изменений в моделях
alembic revision --autogenerate -m "Описание изменения"

# Пустая миграция для ручного написания
alembic revision -m "Описание изменения"
```

### Применение миграций
```bash
alembic upgrade head      # Применить все новые миграции
alembic upgrade +1        # Применить следующую миграцию
alembic upgrade f175caf04ca9  # Применить до конкретной миграции
```

### Откат миграций
```bash
alembic downgrade -1      # Откатить одну миграцию
alembic downgrade base    # Откатить все миграции
alembic downgrade f175caf04ca9  # Откатить до конкретной миграции
```

## Текущие таблицы

После применения начальной миграции создаются следующие таблицы:

- **users** - Пользователи системы
- **swagger_specs** - Swagger спецификации (включает поле `jwt_token`)
- **prompt_templates** - Шаблоны промптов
- **api_embeddings** - Векторные представления API
- **chat_sessions** - Сессии чата
- **chat_messages** - Сообщения чата
- **api_calls** - Логи API вызовов
- **alembic_version** - Служебная таблица Alembic

## Важные изменения

### Миграция от api_tokens к jwt_token

В рамках рефакторинга:
1. **Удалена таблица `api_tokens`** - больше не используется
2. **Добавлено поле `jwt_token`** в таблицу `swagger_specs`
3. JWT токены теперь хранятся прямо в спецификациях

## Workflow разработки

1. **Изменяем модели** в `api/models.py`
2. **Создаем миграцию**: `alembic revision --autogenerate -m "Описание"`
3. **Проверяем миграцию** в созданном файле
4. **Применяем**: `alembic upgrade head`
5. **Тестируем изменения**

## Настройка

Конфигурация в `alembic.ini`:
```ini
sqlalchemy.url = postgresql://postgres:postgres@localhost:5432/ai_swagger_bot
```

Для Docker окружения URL автоматически берется из переменных окружения.

## Troubleshooting

### Ошибка подключения к БД
Убедитесь, что контейнер PostgreSQL запущен:
```bash
docker-compose up -d db
```

### Конфликт миграций
Если есть конфликт, создайте merge миграцию:
```bash
alembic merge -m "Merge migrations" revision1 revision2
```

### Откат к чистому состоянию
```bash
alembic downgrade base    # Удалить все таблицы
alembic upgrade head      # Пересоздать все заново
```
