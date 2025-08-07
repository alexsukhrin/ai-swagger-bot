# AI Swagger Bot - Гід по Адмінці

## Огляд

AI Swagger Bot має дві адмін панелі:

1. **SQLAdmin** - автоматично згенерована адмінка на `/admin/`
2. **Веб-інтерфейс** - кастомна адмінка на `/admin/`

## Швидкий старт

### 1. Створення адміністратора

```bash
# Створити адміністратора
make create-admin

# Або безпосередньо
python scripts/create_admin.py
```

### 2. Запуск API з адмінкою

```bash
# Запустити FastAPI сервіс
make run-api

# Або безпосередньо
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Доступ до адмінки

- **SQLAdmin**: http://localhost:8000/admin/
- **Веб-інтерфейс**: http://localhost:8000/admin/
- **API документація**: http://localhost:8000/docs

## SQLAdmin Панель

### Функції

- **Користувачі** - управління користувачами
- **Swagger Специфікації** - перегляд та редагування специфікацій
- **Сесії Чату** - управління сесіями чату
- **Повідомлення** - перегляд повідомлень
- **Промпт Шаблони** - управління промпт шаблонами
- **API Виклики** - логування API викликів

### Можливості

- ✅ Створення нових записів
- ✅ Редагування існуючих записів
- ✅ Видалення записів
- ✅ Пошук та фільтрація
- ✅ Сортування по колонках
- ✅ Експорт даних

## Веб-інтерфейс Адмінки

### Дашборд

- **Статистика** - кількість користувачів, специфікацій, повідомлень
- **Останні користувачі** - список нещодавно зареєстрованих
- **Останні специфікації** - список нещодавно завантажених
- **Оновлення в реальному часі** - кнопка "Оновити"

### Сторінки

1. **Користувачі** (`/admin/users`)
   - Список всіх користувачів
   - Статус активності
   - Дата реєстрації

2. **Swagger Специфікації** (`/admin/swagger-specs`)
   - Список всіх специфікацій
   - Кількість endpoints
   - Статус активності

3. **Сесії Чату** (`/admin/chat-sessions`)
   - Список сесій чату
   - Прив'язка до користувача та специфікації

4. **Повідомлення** (`/admin/messages`)
   - Останні 100 повідомлень
   - Тип повідомлення (користувач/асистент)
   - Обмежений перегляд контенту

5. **Промпт Шаблони** (`/admin/prompts`)
   - Список промпт шаблонів
   - Категорії та статус

6. **API Виклики** (`/admin/api-calls`)
   - Логування API викликів
   - Статус коди та час виконання

## API Endpoints для Адмінки

### Статистика

```bash
GET /admin/api/stats
```

**Відповідь:**
```json
{
  "users_count": 5,
  "swagger_specs_count": 10,
  "chat_sessions_count": 25,
  "messages_count": 150,
  "prompts_count": 8,
  "api_calls_count": 300
}
```

### Управління користувачами

```bash
DELETE /admin/api/users/{user_id}
```

### Управління специфікаціями

```bash
DELETE /admin/api/swagger-specs/{spec_id}
```

## Безпека

### Аутентифікація

Адмінка зараз не має окремої аутентифікації. В продакшені додайте:

1. **Middleware для перевірки ролей**
2. **Окрему таблицю для адміністраторів**
3. **JWT токени з ролями**

### Приклад middleware

```python
from fastapi import HTTPException, Depends
from .auth import get_current_user
from .models import User

def require_admin(user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
```

## Розширення

### Додавання нових моделей

1. Створіть модель в `api/models.py`
2. Додайте адмін клас в `api/admin.py`
3. Додайте в `setup_admin()` функцію

### Приклад

```python
# api/admin.py
class NewModelAdmin(ModelView, model=NewModel):
    name = "Нова Модель"
    column_list = [NewModel.id, NewModel.name]
    # ... інші налаштування

# В setup_admin()
admin.add_view(NewModelAdmin)
```

### Кастомні дії

```python
class UserAdmin(ModelView, model=User):
    def on_model_change(self, model, is_created):
        # Логування змін
        print(f"User {'created' if is_created else 'updated'}: {model.email}")

    def on_model_delete(self, model):
        # Додаткова логіка при видаленні
        print(f"User deleted: {model.email}")
```

## Моніторинг

### Логи

```bash
# Перегляд логів
docker logs ai-swagger-bot-api

# Фільтрація адмін дій
docker logs ai-swagger-bot-api | grep "admin"
```

### Метрики

- **Кількість користувачів** - активні/неактивні
- **Кількість специфікацій** - завантажених/видалених
- **Активність чату** - повідомлень за день
- **API виклики** - успішні/невдалі

## Troubleshooting

### Проблеми з базою даних

```bash
# Перевірка підключення
python -c "from api.database import engine; print(engine.execute('SELECT 1').fetchone())"

# Створення таблиць
python -c "from api.database import create_tables; create_tables()"
```

### Проблеми з адмінкою

```bash
# Перевірка залежностей
pip install sqladmin jinja2

# Очищення кешу
rm -rf __pycache__/
```

### Проблеми з аутентифікацією

```bash
# Створення нового адміністратора
python scripts/create_admin.py

# Перевірка токена
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/health
```

## Продакшен

### Налаштування

1. **Змініть SECRET_KEY** в `api/auth.py`
2. **Налаштуйте HTTPS** в `nginx.conf`
3. **Додайте аутентифікацію** для адмінки
4. **Налаштуйте логування** в файл
5. **Додайте моніторинг** (Prometheus, Grafana)

### Docker

```bash
# Запуск з адмінкою
docker-compose -f docker-compose.prod.yml up -d

# Доступ до адмінки
https://your-domain.com/admin/
```

### Безпека

- ✅ HTTPS тільки
- ✅ Rate limiting
- ✅ Валідація вхідних даних
- ✅ Логування адмін дій
- ✅ Резервне копіювання БД
