# API Proxy Architecture - Реалізація

## Проблема

Користувач запитав: *"чи може бот розуміти та як це зробити? щоб коли питання стосовно API виконувався пошук по нашому бекенду який зараз на порту 8000 а вже бекенд при створенні чи видалені чи оновлені робив виклик іншого API на порту який зараз 3030 але цей сервіс правда зараз теж в докері то може 0.0.0.0:3030 потрібно вказати"*

## Рішення

Реалізовано **API Proxy Architecture** з наступною структурою:

### 🏗️ Архітектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Bot API       │    │   API Service   │
│   (Port 8501)   │───▶│   (Port 8000)   │───▶│   (Port 3031)   │
│   Streamlit     │    │   FastAPI       │    │   Express.js    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 📋 Компоненти

1. **Frontend (Streamlit)** - інтерфейс користувача
2. **Bot API (FastAPI)** - обробка запитів користувача та проксі
3. **API Service (Express.js)** - реальні операції з даними

## Технічна реалізація

### 1. Модифікація InteractiveSwaggerAgent

**Додано можливість перевизначення base_url:**

```python
def __init__(
    self,
    swagger_spec_path: str,
    enable_api_calls: bool = False,
    openai_api_key: Optional[str] = None,
    jwt_token: Optional[str] = None,
    base_url_override: Optional[str] = None,  # ← Новий параметр
):
    # ...
    self.base_url = base_url_override or self.parser.get_base_url()
```

### 2. Оновлення API endpoint

**Додано конфігурацію для API сервісу:**

```python
# Отримуємо URL API сервісу з змінних середовища
api_service_url = os.getenv("API_SERVICE_URL", "http://0.0.0.0:3031")

agent = InteractiveSwaggerAgent(
    swagger_spec_path=temp_file_path,
    enable_api_calls=True,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    jwt_token=os.getenv("JWT_TOKEN"),
    base_url_override=api_service_url  # ← Перевизначаємо URL
)
```

### 3. Docker Compose конфігурація

**Додано API сервіс:**

```yaml
# API Service (External API that bot will call)
api-service:
  build: ./api-service
  container_name: ai-swagger-bot-api-service
  ports:
    - "3031:3030"
  environment:
    - NODE_ENV=development
    - PORT=3030
  restart: unless-stopped
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:3030/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s
```

**Додано змінну середовища для API:**

```yaml
environment:
  - API_SERVICE_URL=${API_SERVICE_URL:-http://0.0.0.0:3031}
```

### 4. API Service (Express.js)

**Створено простий API сервіс з endpoints:**

```javascript
// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// Users endpoints
app.get('/users', (req, res) => {
  res.json(users);
});

app.post('/users', (req, res) => {
  // Логіка створення користувача
});

// Products endpoints
app.get('/products', (req, res) => {
  res.json(products);
});

// Orders endpoints
app.get('/orders', (req, res) => {
  res.json(orders);
});
```

## Процес роботи

### 🔄 Flow запиту

1. **Користувач** задає питання через Streamlit
2. **Bot API** аналізує запит та формує API запит
3. **Bot API** виконує запит до **API Service**
4. **API Service** обробляє запит та повертає відповідь
5. **Bot API** форматує відповідь через GPT
6. **Користувач** отримує дружелюбну відповідь

### 📊 Приклад запиту

**Користувач:** "Покажи всі користувачів"

**Bot API:**
```python
# Формує запит
api_request = {
    "url": "http://0.0.0.0:3031/users",
    "method": "GET",
    "headers": {...}
}

# Виконує запит
response = requests.get("http://0.0.0.0:3031/users")

# Форматує відповідь через GPT
formatted_response = gpt_process(response.json())
```

**API Service:**
```javascript
// Повертає дані
[
  { "id": 1, "name": "John Doe", "email": "john@example.com" },
  { "id": 2, "name": "Jane Smith", "email": "jane@example.com" }
]
```

**Результат:** "Ось список всіх користувачів: John Doe (john@example.com) та Jane Smith (jane@example.com)"

## Переваги архітектури

### ✅ Розділення відповідальності
- **Bot API** - обробка запитів користувача та AI
- **API Service** - бізнес-логіка та дані
- **Frontend** - інтерфейс користувача

### ✅ Гнучкість
- Можна легко змінити API Service
- Bot працює з будь-яким API
- Незалежне масштабування компонентів

### ✅ Безпека
- Bot API як проксі/фасад
- Контроль доступу через Bot API
- Ізоляція API Service

### ✅ Тестування
- Легко тестувати кожен компонент окремо
- Можна мокати API Service для тестів
- Незалежне розгортання

## Конфігурація

### Змінні середовища

```bash
# .env файл
API_SERVICE_URL=http://0.0.0.0:3031
OPENAI_API_KEY=your_openai_key
JWT_TOKEN=your_jwt_token
```

### Docker Compose

```bash
# Запуск всіх сервісів
docker-compose up -d

# Тільки API сервіс
docker-compose up -d api-service

# Перебудування
docker-compose up -d --build
```

## Тестування

### Health Check
```bash
curl http://localhost:3031/health
# {"status":"healthy","timestamp":"2025-08-08T11:11:18.908Z"}
```

### API Endpoints
```bash
# Користувачі
curl http://localhost:3031/users

# Товари
curl http://localhost:3031/products

# Замовлення
curl http://localhost:3031/orders
```

### Через Bot
```bash
# Через Streamlit
# Запит: "Покажи всі користувачів"
# Результат: Форматується через GPT
```

## Структура файлів

```
ai-swagger-bot/
├── api/
│   └── main.py                    # Bot API (FastAPI)
├── api-service/
│   ├── Dockerfile                 # API Service контейнер
│   ├── package.json              # Node.js залежності
│   └── server.js                 # API Service (Express.js)
├── streamlit_frontend.py         # Frontend (Streamlit)
├── docker-compose.yml            # Docker Compose конфігурація
└── src/
    └── interactive_api_agent.py  # InteractiveSwaggerAgent
```

## Висновок

Реалізовано повноцінну **API Proxy Architecture**, де:

1. ✅ **Bot API** обробляє запити користувача та виконує виклики до API Service
2. ✅ **API Service** виконує реальні операції з даними
3. ✅ **Frontend** надає зручний інтерфейс
4. ✅ **Docker** забезпечує ізоляцію та легке розгортання
5. ✅ **Конфігурація** через змінні середовища

Тепер бот може розуміти запити користувача та виконувати реальні API виклики до окремого сервісу! 🚀
