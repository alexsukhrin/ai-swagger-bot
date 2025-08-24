# 🛍️ AI Swagger Bot - Clickone Shop API

AI-powered bot для роботи з Clickone Shop API через Swagger документацію та RAG (Retrieval Augmented Generation).

## 📋 Зміст

- [🚀 Швидкий старт](#-швидкий-старт)
- [📋 Основна функціональність](#-основна-функціональність)
- [🏗️ Архітектура](#️-архітектура)
- [🛠️ Технології](#️-технології)
- [📁 Структура проекту](#-структура-проекту)
- [🔑 Налаштування](#-налаштування)
- [🎯 Використання](#-використання)
- [🐳 Docker](#-docker)
- [🧪 Тестування](#-тестування)
- [🔧 Розробка](#-розробка)
- [📚 Детальні гіді](#-детальні-гіді)
- [⚡ Швидкий довідник запитів](#-швидкий-довідник-запитів)
- [🤝 Внесок](#-внесок)
- [📄 Ліцензія](#-ліцензія)

## 🚀 Швидкий старт

### Streamlit Demo (рекомендовано для початківців)

```bash
# Запуск Streamlit демо
make streamlit-up

# Перевірка статусу
make streamlit-status

# Тестування
make streamlit-demo

# Перегляд логів
make streamlit-logs

# Зупинка
make streamlit-down
```

**🌐 Відкрийте**: http://localhost:8502

### CLI Interface

```bash
# Запуск CLI через Docker
make cli-up

# Або локально
python clickone_cli.py
```

### Docker (рекомендовано для продакшну)

```bash
# Основна конфігурація (всі сервіси)
docker-compose up -d

# Тільки Streamlit
docker-compose up streamlit -d

# Тільки CLI
docker-compose up cli -d

# Спеціалізовані конфігурації
docker-compose -f docker-compose.streamlit-only.yml up -d
docker-compose -f docker-compose.cli-only.yml up -d
docker-compose -f docker-compose.testing.yml up -d
```

## 📋 Основна функціональність

### 🔍 Swagger Integration
- Автоматичне завантаження Swagger специфікації
- Парсинг та аналіз API документації
- Створення векторних embeddings для RAG

### 🤖 AI-Powered Operations
- Створення, оновлення, видалення ресурсів через AI
- Автоматичне виправлення помилок API
- Людська мова відповідей (українська)
- Розумний пошук товарів та рекомендації

### 🗄️ Database Integration
- PostgreSQL з pgvector для векторного пошуку
- RAG engine для інтелектуального пошуку
- Кешування AI-аналізованих помилок
- Ізоляція користувачів та їх даних

### 🛍️ E-commerce Features
- Розумний пошук товарів з аналізом наміру
- Персоналізовані рекомендації
- Допомога з замовленнями
- Автоматичне створення описів товарів
- Аналітика продажів та користувачів

## 🏗️ Архітектура

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │   Clickone CLI   │    │   AI Agent      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌──────────────────┐
                    │ Clickone Service │
                    └──────────────────┘
                                 │
                    ┌──────────────────┐
                    │  RAG Engine      │
                    │  (PostgreSQL)    │
                    └──────────────────┘
```

### Компоненти системи

- **Frontend**: Streamlit веб-інтерфейс та CLI
- **AI Layer**: OpenAI GPT-4, RAG engine, prompt management
- **API Layer**: Clickone Shop API integration
- **Database**: PostgreSQL + pgvector для векторного пошуку
- **Security**: JWT токени, ізоляція користувачів

## 🛠️ Технології

- **Backend**: Python 3.9+, FastAPI, SQLAlchemy
- **AI**: OpenAI GPT-4, RAG, vector embeddings
- **Database**: PostgreSQL + pgvector
- **Frontend**: Streamlit, HTML/CSS/JS
- **Containerization**: Docker, Docker Compose
- **Testing**: pytest, unittest.mock
- **Deployment**: Serverless (AWS Lambda), Docker

## 📁 Структура проекту

```
├── src/                           # Основний код
│   ├── clickone_swagger_service.py # Сервіс для роботи з API
│   ├── enhanced_ai_assistant.py   # Розширений AI асистент
│   ├── rag_engine.py              # RAG двигун
│   ├── config.py                  # Конфігурація
│   └── ...
├── demos/                         # Демо файли
│   ├── demo_ai_bot.py            # AI бот демо
│   ├── demo_ai_interactive.py    # Інтерактивне демо
│   └── ...
├── tools/                         # Утиліти та інструменти
│   ├── cli_tester.py             # CLI тестер
│   ├── check_prompts.py          # Перевірка промптів
│   └── ...
├── config/                        # Конфігураційні файли
│   ├── requirements.txt           # Python залежності
│   ├── prompt_config.json        # AI конфігурація
│   └── ...
├── deployment/                    # Файли розгортання
│   ├── serverless.yml            # Serverless конфігурація
│   ├── lambda_handler.py         # AWS Lambda
│   └── ...
├── frontend/                      # Фронтенд файли
│   └── demo_client.html          # Демо клієнт
├── database/                      # База даних
│   └── init-real-db.sql          # SQL скрипти
├── api/                           # FastAPI сервер
├── tests/                         # Тести
├── streamlit_demo.py              # Streamlit додаток
├── clickone_cli.py                # CLI інтерфейс
├── docker-compose.yml             # Docker конфігурація
└── Makefile                       # Команди управління
```

## 🔑 Налаштування

### Змінні середовища (.env)

```bash
# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Clickone Shop API
JWT_SECRET_KEY=your_jwt_secret
JWT_TOKEN=your_jwt_token

# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Server
HOST=0.0.0.0
PORT=8000
```

### API URLs

```python
CLICKONE_SHOP_API_URL = "https://api.oneshop.click"
CLICKONE_SHOP_SWAGGER_URL = "https://api.oneshop.click/docs/ai-json"
```

### Docker Environment

```bash
# Обов'язковий OpenAI API ключ
export OPENAI_API_KEY="sk-your-openai-key"

# Опціональний JWT токен для продакшну
export JWT_TOKEN="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## 🎯 Використання

### 1. Streamlit Demo
- Відкрийте http://localhost:8502
- Використовуйте бічну панель для навігації
- Аналізуйте завантажену Swagger специфікацію
- Тестуйте доступні ендпоінти API

### 2. CLI Interface
```bash
python clickone_cli.py
# Виберіть опцію з меню
```

### 3. AI Agent
- Автоматичне створення ресурсів
- Виправлення помилок API
- Людська мова відповідей
- Розумні рекомендації

## 🐳 Docker

### Основна конфігурація (рекомендовано)

```bash
# Всі сервіси
docker-compose up -d

# Тільки Streamlit
docker-compose up streamlit -d

# Тільки CLI
docker-compose up cli -d

# Тільки база даних
docker-compose up postgres -d
```

### Запуск окремих сервісів

```bash
# Тільки Streamlit
docker-compose up streamlit -d

# Тільки CLI
docker-compose up cli -d

# Тільки база даних
docker-compose up postgres -d
```

### Доступні команди

```bash
# Збірка образів
docker-compose build

# Запуск в фоновому режимі
docker-compose up -d

# Запуск з логами
docker-compose up

# Зупинка
docker-compose down

# Перегляд логів
docker-compose logs -f

# Перегляд статусу
docker-compose ps
```



## 🧪 Тестування

### Unit Tests
```bash
make test
```

### Integration Tests
```bash
make test-integration
```

### Streamlit Tests
```bash
make streamlit-test
```

### Docker Tests
```bash
make docker-test
```

## 🔧 Розробка

### Додавання нових ендпоінтів
1. Оновіть `test_api_endpoints()` в Streamlit
2. Додайте нову сторінку в навігацію
3. Створіть відповідні функції

### Кастомізація AI промптів
1. Редагуйте YAML файли в `src/prompts/`
2. Оновіть `ClickonePromptManager`
3. Протестуйте через CLI або Streamlit

### Розширення AI асистента
1. Додайте нові функції в `EnhancedAIAssistant`
2. Створіть відповідні промпти
3. Додайте тести

## 📚 Детальні гіді

### AI Swagger Bot Algorithm
- **Парсинг Swagger**: Автоматичне завантаження та аналіз API документації
- **Vector Embeddings**: Створення векторних представлень для RAG
- **AI Processing**: Обробка запитів через GPT-4 з контекстом API
- **Error Handling**: Автоматичне виправлення помилок API

### RAG System
- **Retrieval**: Пошук релевантної інформації в векторній базі
- **Generation**: Створення відповідей на основі знайденої інформації
- **Context**: Збереження контексту розмови та історії

### User Isolation
- **Multi-tenancy**: Ізоляція даних між користувачами
- **Security**: JWT токени та безпечне зберігання
- **Privacy**: Кожен користувач бачить тільки свої дані

### Enhanced AI Assistant
- **E-commerce**: Розумний пошук, рекомендації, аналітика
- **Content Creation**: Автоматичне створення описів товарів
- **Customer Support**: Підтримка клієнтів та вирішення проблем
- **Personalization**: Адаптація під кожного користувача

## ⚡ Швидкий довідник запитів

### 📖 ЧИТАННЯ (GET)
```
"Покажи всі категорії"
"Знайди категорію з назвою Електроніка"
"Покажи продукт з ID 123"
"Знайди бренд Apple"
```

### ➕ СТВОРЕННЯ (POST)
```
"Створи категорію: Електроніка, опис: Електронні пристрої"
"Створи бренд: Apple, опис: Американська компанія з електроніки"
"Створи продукт: iPhone 15 Pro, ціна: 999.99, опис: Новий iPhone"
```

### ✏️ ОНОВЛЕННЯ (PUT/PATCH)
```
"Онови ціну продукту 123 на 1500 грн"
"Зміни назву категорії 456 на 'Нова назва'"
"Онови опис бренду Apple на 'Оновлений опис'"
```

### 🗑️ ВИДАЛЕННЯ (DELETE)
```
"Видали категорію з ID 123"
"Видали бренд Apple"
"Видали продукт з ID 456"
```

### 🛍️ E-commerce запити
```
"Знайди теплу куртку для зими"
"Потрібен подарунок для дівчини"
"Шукаю телефон в діапазоні 5000-15000 грн"
"Відстежи моє замовлення #12345"
"Створи опис для товару Смартфон Samsung Galaxy"
"Що порекомендуєш для подарунка?"
"Покажи статистику продажів"
```

## 🐛 Відладка

### Логи
```bash
# Streamlit
make streamlit-logs

# CLI
make cli-logs

# Всі сервіси
make logs

# Docker
docker-compose logs -f
```

### Статус
```bash
make status
docker-compose ps
```

### Перезапуск
```bash
make restart
docker-compose restart
```

## 📈 Моніторинг

- **API Health**: Автоматичне тестування ендпоінтів
- **AI Performance**: Кешування помилок та відповідей
- **Database**: Векторний пошук та RAG статистика
- **User Activity**: Активні користувачі та їх запити

## 🔒 Безпека

- **JWT Authentication**: Безпечна автентифікація користувачів
- **User Isolation**: Повна ізоляція даних між користувачами
- **API Security**: Безпечне з'єднання з Clickone Shop API
- **Environment Variables**: Безпечне зберігання секретів

## 🚀 Deployment

### Docker
```bash
# Production build
docker build -t ai-swagger-bot:latest .

# Run
docker run -d -p 8502:8502 --env-file .env ai-swagger-bot:latest
```

### Serverless (AWS Lambda)
```bash
# Deploy
make deploy-lambda

# Test
make test-lambda
```

### Traditional Server
```bash
# Install dependencies
pip install -r requirements.txt

# Run
python streamlit_demo.py
```

## 🤝 Внесок

1. Fork проекту
2. Створіть feature branch
3. Додайте тести
4. Створіть Pull Request

### Guidelines
- Дотримуйтесь PEP 8 для Python коду
- Додавайте тести для нових функцій
- Оновлюйте документацію при змінах
- Використовуйте українську мову в коментарях

## 📄 Ліцензія

MIT License

## 🆘 Підтримка

- **Issues**: GitHub Issues
- **Documentation**: README файли
- **Examples**: Streamlit demo та CLI
- **Community**: Обговорення та питання

---

**🎯 Мета**: Створити інтелектуальний інтерфейс для роботи з Clickone Shop API через AI та RAG технології.

**💡 Особливість**: Автоматичне виправлення помилок API, розумні рекомендації та людська мова відповідей.

**🚀 Статус**: Активно розвивається з підтримкою Docker, Serverless та традиційного розгортання.
