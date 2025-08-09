# AI Swagger Bot API Documentation

## Огляд

AI Swagger Bot API - це FastAPI сервіс для роботи зі Swagger специфікаціями та виконання API запитів з використанням AI.

## Базовий URL

```
http://localhost:8000
```

## Аутентифікація

API використовує JWT токени для аутентифікації. Включіть токен в заголовок:

```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### 1. Health Check

**GET** `/health`

Перевірка стану сервісу.

**Відповідь:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "active_users": 5,
  "swagger_specs_count": 10
}
```

### 2. Завантаження Swagger специфікації

**POST** `/upload-swagger`

Завантаження Swagger специфікації у форматі JSON.

**Параметри:**
- `file`: JSON файл з Swagger специфікацією

**Відповідь:**
```json
{
  "swagger_id": "uuid-string",
  "message": "Swagger специфікація успішно завантажена",
  "endpoints_count": 25
}
```

### 3. Чат з AI агентом

**POST** `/chat`

Надсилання повідомлення до AI агента.

**Тіло запиту:**
```json
{
  "message": "Покажи всі доступні endpoints",
  "user_id": "optional-user-id"
}
```

**Відповідь:**
```json
{
  "response": "Ось список доступних endpoints...",
  "user_id": "user-uuid",
  "timestamp": "2024-01-01T12:00:00",
  "swagger_id": "swagger-uuid"
}
```

### 4. Історія чату

**GET** `/chat-history`

Отримання історії чату користувача.

**Відповідь:**
```json
{
  "user_id": "user-uuid",
  "chat_history": [
    {
      "user_message": "Покажи endpoints",
      "ai_response": "Ось список...",
      "timestamp": "2024-01-01T12:00:00"
    }
  ],
  "swagger_id": "swagger-uuid"
}
```

### 5. Промпт шаблони

**POST** `/prompts`

Створення нового промпт шаблону.

**Тіло запиту:**
```json
{
  "name": "API Analysis",
  "description": "Шаблон для аналізу API",
  "template": "Проаналізуй наступне API: {api_spec}",
  "category": "analysis"
}
```

**GET** `/prompts`

Отримання всіх промпт шаблонів.

### 6. Управління Swagger специфікаціями

**GET** `/swagger-specs`

Отримання списку Swagger специфікацій користувача.

**DELETE** `/swagger/{swagger_id}`

Видалення Swagger специфікації.

## Коди помилок

- `400` - Неправильний запит
- `401` - Неавторизований доступ
- `403` - Немає прав доступу
- `404` - Не знайдено
- `500` - Внутрішня помилка сервера

## Приклади використання

### cURL

```bash
# Завантаження Swagger файлу
curl -X POST "http://localhost:8000/upload-swagger" \
  -H "Authorization: Bearer your-token" \
  -F "file=@swagger.json"

# Чат з AI
curl -X POST "http://localhost:8000/chat" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"message": "Покажи всі GET endpoints"}'

# Health check
curl "http://localhost:8000/health"
```

### Python

```python
import requests

# Налаштування
BASE_URL = "http://localhost:8000"
TOKEN = "your-jwt-token"
headers = {"Authorization": f"Bearer {TOKEN}"}

# Завантаження Swagger
with open("swagger.json", "rb") as f:
    files = {"file": f}
    response = requests.post(f"{BASE_URL}/upload-swagger", headers=headers, files=files)
    print(response.json())

# Чат
chat_data = {"message": "Покажи всі endpoints"}
response = requests.post(f"{BASE_URL}/chat", headers=headers, json=chat_data)
print(response.json())
```

## Розгортання

### Локальний запуск

```bash
# Встановлення залежностей
pip install -r requirements.txt

# Запуск сервісу
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Docker

```bash
# Збірка образу
docker build -f Dockerfile.api -t ai-swagger-bot-api .

# Запуск контейнера
docker run -p 8000:8000 ai-swagger-bot-api
```

### Docker Compose (з PostgreSQL)

```bash
# Запуск повного стеку
docker-compose -f docker-compose.prod.yml up -d
```

## Моніторинг

### Health Check

Регулярно перевіряйте `/health` endpoint для моніторингу стану сервісу.

### Логування

Логи доступні в консолі або через Docker logs:

```bash
docker logs ai-swagger-bot-api
```

## Безпека

1. **JWT токени** - використовуйте безпечні секретні ключі
2. **HTTPS** - завжди використовуйте HTTPS в продакшені
3. **Rate limiting** - налаштуйте обмеження на кількість запитів
4. **Валідація** - всі вхідні дані валідуються
5. **SQL injection** - використовується SQLAlchemy ORM

## Розширення

### Додавання нових endpoints

1. Створіть нову функцію в `api/main.py`
2. Додайте декоратор `@app.post("/your-endpoint")`
3. Додайте валідацію та обробку помилок
4. Оновіть документацію

### Підключення нової бази даних

1. Оновіть `DATABASE_URL` в змінних середовища
2. Створіть міграції (якщо потрібно)
3. Оновіть моделі в `api/models.py`
