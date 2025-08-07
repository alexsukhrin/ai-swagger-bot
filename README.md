# AI Swagger Bot 🤖

Інтелектуальний агент, який читає Swagger/OpenAPI специфікації та автоматично формує API-запити.

## 🚀 Можливості

- ✅ Читає API з Swagger/OpenAPI (структура, методи, схеми)
- ✅ Розуміє, які поля потрібні для створення ресурсів
- ✅ Дістає потрібні параметри з запиту користувача
- ✅ Автоматично формує правильний API-запит (JSON + метод)
- ✅ Викликає API (опціонально)
- ✅ Повертає відповідь у зручному вигляді
- ✅ Підтримує два типи агентів: з LangChain та без
- ✅ CLI інтерфейс для командного рядка
- ✅ Streamlit веб-інтерфейс
- ✅ Логування та обробка помилок
- ✅ Тести та валідація

## 🛠️ Встановлення

### 1. Клонування репозиторію

```bash
git clone <repository-url>
cd ai-swagger-bot
```

### 2. Створення віртуального середовища

```bash
# Python 3.11+
python -m venv venv

# Активація
source venv/bin/activate  # Linux/Mac
# або
venv\Scripts\activate     # Windows
```

### 3. Встановлення залежностей

```bash
# Для використання
pip install -r requirements.txt

# Для розробки (з лінтерами та тестами)
pip install -r requirements-dev.txt
```

### 4. Налаштування змінних середовища

```bash
# Копіюємо приклад
cp env_example.txt .env

# Редагуємо .env файл
nano .env  # або відкриваємо в редакторі
```

Додайте ваш OpenAI API ключ:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

## 🔧 Розробка

### Лінтери та форматування

```bash
# Перевірка коду
make lint

# Форматування коду
make format

# Запуск тестів
make test

# Запуск тестів з покриттям
make test-coverage
```

### Pre-commit hooks

```bash
# Встановлення pre-commit
pip install pre-commit

# Встановлення hooks
pre-commit install

# Запуск на всіх файлах
pre-commit run --all-files
```

## 🚀 CI/CD

Проект налаштований з повним CI/CD pipeline:

- ✅ **Лінтери**: Black, isort, ruff, mypy
- ✅ **Тести**: pytest з покриттям
- ✅ **Security**: Bandit, Trivy, CodeQL
- ✅ **Docker**: Збірка та тестування образів
- ✅ **Deployment**: Автоматичний деплой на main branch

### GitHub Actions Workflows

- `ci-cd.yml` - Повний CI/CD pipeline
- `quick-check.yml` - Швидкі перевірки
- `codeql.yml` - Security scanning
- `release.yml` - Автоматичні releases

### Badges

[![CI/CD Pipeline](https://github.com/alexandrsukhryn/ai-swagger-bot/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/alexandrsukhryn/ai-swagger-bot/actions)
[![Quick Check](https://github.com/alexandrsukhryn/ai-swagger-bot/workflows/Quick%20Check/badge.svg)](https://github.com/alexandrsukhryn/ai-swagger-bot/actions)
[![CodeQL](https://github.com/alexandrsukhryn/ai-swagger-bot/workflows/CodeQL/badge.svg)](https://github.com/alexandrsukhryn/ai-swagger-bot/actions)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

## 📁 Структура проекту

```
ai-swagger-bot/
├── src/
│   ├── __init__.py
│   ├── swagger_parser.py      # Парсер Swagger/OpenAPI
│   ├── rag_engine.py          # RAG система
│   ├── api_agent.py           # Основний агент (з LangChain)
│   ├── simple_agent.py        # Спрощений агент (без LangChain)
│   └── utils.py               # Допоміжні функції
├── examples/
│   ├── swagger_specs/         # Приклади Swagger файлів
│   ├── basic_usage.py         # Базовий приклад
│   └── test_queries.py        # Тестові запити
├── tests/
│   └── test_agent.py          # Тести
├── app.py                     # Streamlit інтерфейс
├── cli.py                     # CLI інтерфейс
├── requirements.txt
└── README.md
```

## 🎯 Приклади використання

### 1. Базовий використання (Python)

```python
from src.api_agent import SwaggerAgent

# Ініціалізація агента
agent = SwaggerAgent("examples/swagger_specs/shop_api.json")

# Запит користувача
user_query = "Додай товар: синя сукня, розмір 22, кількість 10"

# Отримання відповіді
response = agent.process_query(user_query)
print(response)
# Вивід: "📋 Сформований API запит: POST /products"
```

### 2. CLI інтерфейс

```bash
# Інтерактивний режим
python cli.py --swagger examples/swagger_specs/shop_api.json

# Одиночний запит
python cli.py --swagger examples/swagger_specs/shop_api.json --query "Додай товар: тест"

# З API викликами
python cli.py --swagger examples/swagger_specs/shop_api.json --enable-api --query "Створи товар"

# Спрощений агент
python cli.py --swagger examples/swagger_specs/shop_api.json --simple --query "Покажи товари"

# Перегляд endpoints
python cli.py --swagger examples/swagger_specs/shop_api.json --list-endpoints
```

### 3. Streamlit веб-інтерфейс

```bash
streamlit run app.py
```

Відкрийте браузер на http://localhost:8501

### 4. Запуск тестів

```bash
# Запуск всіх тестів
python -m unittest tests/test_agent.py

# Запуск з детальним виводом
python -m unittest tests/test_agent.py -v
```

## 🔧 Як це працює

### 1. Парсинг Swagger
- Читає JSON/YAML файл з описом API
- Витягує endpoints, методи, параметри, схеми
- Створює структуровані об'єкти для подальшої обробки

### 2. RAG система
- Зберігає endpoints у векторній базі (ChromaDB)
- Індексує для швидкого пошуку
- Знаходить найбільш відповідні endpoints для запиту

### 3. Обробка запиту
- GPT аналізує намір користувача
- Визначає тип операції (GET, POST, PUT, DELETE)
- Витягує параметри з тексту

### 4. Формування запиту
- Створює правильний HTTP запит
- Формує JSON дані згідно зі схемою
- Додає необхідні заголовки

### 5. Виклик API
- Виконує HTTP запит
- Обробляє відповідь
- Форматує результат

## 🎛️ Налаштування

### Змінні середовища (.env)

```env
# OpenAI API Key (обов'язково)
OPENAI_API_KEY=your_openai_api_key_here

# Налаштування моделі
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0

# Налаштування RAG
CHROMA_PERSIST_DIRECTORY=./chroma_db

# Налаштування API викликів
ENABLE_API_CALLS=false

# Налаштування логування
LOG_LEVEL=INFO

# Налаштування безпеки
MAX_REQUEST_SIZE=10485760
REQUEST_TIMEOUT=30
```

### Типи агентів

1. **SwaggerAgent** (з LangChain)
   - Використовує LangChain компоненти
   - Більш гнучкий та розширюваний
   - Підтримує промпти та ланцюги

2. **SimpleSwaggerAgent** (без LangChain)
   - Прямий виклик OpenAI API
   - Простіший та швидший
   - Менше залежностей

## 📊 Приклади запитів

### Товари
```
Додай товар: синя сукня, розмір 22, кількість 10
Створи новий товар - червона сукня, розмір 44, 5 штук
Додай товар з назвою 'Чорні кросівки', ціна 1500 грн, категорія 'Взуття'
Покажи всі товари
Отримай товар з ID 123
Онови товар 456 - зміни ціну на 2000 грн
Видали товар 789
```

### Замовлення
```
Створи замовлення для користувача 1 з товаром 123, кількість 2
Покажи всі замовлення
Отримай замовлення з ID 456
```

### Користувачі
```
Створи користувача: Іван Петренко, email ivan@example.com
Отримай користувача з ID 1
Онови користувача 2 - зміни email на new@example.com
```

## 🧪 Тестування

### Запуск тестів
```bash
# Всі тести
python -m unittest discover tests

# Конкретний тест
python -m unittest tests.test_agent.TestSimpleSwaggerAgent

# З покриттям
coverage run -m unittest discover tests
coverage report
```

### Тестові запити
```bash
python examples/test_queries.py
```

## 🔍 Діагностика

### Логування
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Перевірка налаштувань
```bash
python cli.py --swagger examples/swagger_specs/shop_api.json --agent-info --verbose
```

### Перегляд endpoints
```bash
python cli.py --swagger examples/swagger_specs/shop_api.json --list-endpoints
```

## 🚨 Обробка помилок

### Поширені помилки

1. **Не знайдено OPENAI_API_KEY**
   ```
   ❌ Помилка: Не знайдено OPENAI_API_KEY в змінних середовища
   ```
   **Рішення:** Додайте API ключ в .env файл

2. **Файл Swagger не знайдено**
   ```
   ❌ Помилка: Файл examples/swagger_specs/shop_api.json не знайдено
   ```
   **Рішення:** Перевірте шлях до файлу

3. **Таймаут при виклику API**
   ```
   ❌ Помилка при виклику API: Таймаут при виклику API
   ```
   **Рішення:** Перевірте мережу або збільшіть REQUEST_TIMEOUT

4. **Не знайдено endpoints**
   ```
   Вибачте, не знайшов відповідного API endpoint для вашого запиту.
   ```
   **Рішення:** Перевірте Swagger специфікацію або змініть запит

## 🤝 Внесок

1. Форкніть репозиторій
2. Створіть гілку для нової функції (`git checkout -b feature/amazing-feature`)
3. Зробіть коміт змін (`git commit -m 'Add amazing feature'`)
4. Відправте в гілку (`git push origin feature/amazing-feature`)
5. Відкрийте Pull Request

## 📝 Ліцензія

Цей проект розповсюджується під ліцензією MIT. Дивіться файл `LICENSE` для деталей.

## 🙏 Подяки

- OpenAI за GPT моделі
- LangChain за фреймворк
- ChromaDB за векторну базу даних
- Streamlit за веб-інтерфейс

## 📞 Підтримка

Якщо у вас є питання або проблеми:

1. Перевірте [Issues](https://github.com/your-repo/issues)
2. Створіть нове Issue з детальним описом проблеми
3. Додайте логи та приклади запитів

---

**AI Swagger Bot** - Робіть API простішими! 🚀
