# AI Swagger Bot 🤖 - Розширений AI-асистент для веб-сайтів

Інтелектуальний агент, який читає Swagger/OpenAPI специфікації та автоматично формує API-запити. Тепер також повноцінний AI-асистент для веб-сайтів з розширеними функціями для e-commerce.

## 🚀 Можливості

### 🔧 Базові функції Swagger
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

### 🏪 Clickone Shop API Інтеграція
- ✅ **Підтримка Clickone Shop Backend API** - повна інтеграція з e-commerce платформою
- ✅ **Категорії товарів** - створення, оновлення, видалення, пошук
- ✅ **Управління товарами** - CRUD операції, атрибути, варіанти
- ✅ **Система замовлень** - створення, відстеження, статуси
- ✅ **Управління клієнтами** - профілі, адреси, історія
- ✅ **Бренди та колекції** - каталогізація, групування
- ✅ **Складські операції** - надходження, списання, контроль залишків
- ✅ **JWT автентифікація** - безпечний доступ до API
- ✅ **Детальна документація** - 37 схем даних, 5 endpoints

### 🛍️ Розширені E-commerce функції
- ✅ **Розумний пошук товарів** - аналіз наміру, персоналізація, фільтрація
- ✅ **Допомога з замовленнями** - оформлення, відстеження, управління
- ✅ **Створення контенту** - автоматичні описи товарів, SEO-оптимізація
- ✅ **Персоналізовані рекомендації** - на основі історії покупок та вподобань
- ✅ **Підтримка клієнтів** - технічна підтримка, питання про товари
- ✅ **Аналітика та звіти** - статистика продажів, популярні товари
- ✅ **Система сповіщень** - статус замовлень, промо-акції, новинки
- ✅ **Історія розмови** - збереження контексту для персоналізації

### ☁️ Serverless Deployment
- ✅ **AWS Lambda** - розгортання як серверлес функція
- ✅ **Mangum** - адаптер для FastAPI на AWS Lambda
- ✅ **Serverless Framework** - автоматизація розгортання
- ✅ **Terraform** - Infrastructure as Code для AWS
- ✅ **Docker** - контейнеризація для Lambda
- ✅ **CI/CD** - GitHub Actions та GitLab CI
- ✅ **Multi-stage** - dev, staging, production
- ✅ **Auto-scaling** - автоматичне масштабування
- ✅ **Monitoring** - CloudWatch, логування, метрики

## 🛠️ Встановлення

### 1. Клонування репозиторію

```bash
git clone https://github.com/alexandrsukhryn/ai-swagger-bot.git
cd ai-swagger-bot
```

### 2. Завантаження Clickone Shop API специфікації

```bash
# Завантажуємо актуальну Swagger специфікацію
curl "https://api.oneshop.click/docs/ai-json" > examples/swagger_specs/clickone_shop_api.json

# Або використовуємо вже завантажену специфікацію
ls examples/swagger_specs/clickone_shop_api.json
```

### 3. Створення віртуального середовища

```bash
# Python 3.11+
python -m venv venv

# Активація
source venv/bin/activate  # Linux/Mac
# або
venv\Scripts\activate     # Windows
```

### 4. Встановлення залежностей

```bash
# Для використання
pip install -r requirements.txt

# Для розробки (з лінтерами та тестами)
pip install -r requirements-dev.txt

# Або використовуйте Makefile
make install-dev
```

### 5. Налаштування змінних середовища

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

### 6. Встановлення pre-commit hooks (опціонально)

```bash
# Встановлення pre-commit
pip install pre-commit

# Встановлення hooks
pre-commit install

# Або використовуйте Makefile
make pre-commit-install
```

### 7. Serverless Deployment (опціонально)

Для розгортання на AWS Lambda:

```bash
# Налаштування серверлес середовища
./scripts/setup_serverless.sh

# Або вручну
npm install
pip install -r requirements.txt

# Розгортання на dev stage
make -f Makefile.lambda deploy

# Розгортання на production
make -f Makefile.lambda deploy-prod
```

**Детальна документація**: [README_SERVERLESS.md](README_SERVERLESS.md)

## 🏪 Приклади роботи з Clickone Shop API

### Демонстрація роботи

```bash
# Запуск демонстрації
make docker-demo-clickone

# Або вручну
docker-compose -f docker-compose.test.yml run --rm test python examples/clickone_shop_demo.py
```

### Тестування API

```bash
# Запуск тестів Clickone Shop API
make docker-test-clickone

# Запуск всіх тестів
make docker-test-all
```

### Основні можливості

- **📊 Аналіз структури API** - автоматичне визначення endpoints, схем, методів
- **🔍 Пошук endpoints** - пошук за ключовими словами, тегами, описом
- **📝 Детальна інформація** - повна документація кожного endpoint та схеми
- **🔐 Безпека** - JWT автентифікація, схеми безпеки
- **📋 Валідація** - перевірка структури, обов'язкових полів, типів даних

### Структура API

Clickone Shop Backend API включає:
- **5 endpoints** для управління категоріями
- **37 схем даних** (DTOs) для різних сутностей
- **JWT автентифікація** для безпечного доступу
- **Повна документація** з прикладами та описом

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

# Перевірка безпеки
make security-check

# Запуск CI/CD локально
make ci
```

### Pre-commit hooks

```bash
# Встановлення pre-commit
pip install pre-commit

# Встановлення hooks
pre-commit install

# Запуск на всіх файлах
pre-commit run --all-files

# Або використовуйте Makefile
make pre-commit-install
make pre-commit-run
```

### Docker для розробки

```bash
# Тестування з Docker Compose
make docker-compose-test

# Тестування Docker образу
make docker-test
```

## 🚀 CI/CD

Проект налаштований з повним CI/CD pipeline:

- ✅ **Лінтери**: Black, isort, ruff, mypy
- ✅ **Тести**: pytest з покриттям
- ✅ **Security**: Bandit, Trivy, CodeQL
- ✅ **Docker**: Збірка та тестування образів
- ✅ **Deployment**: Автоматичний деплой на main branch
- ✅ **Pre-commit hooks**: Автоматична перевірка перед комітами
- ✅ **Dependabot**: Автоматичне оновлення залежностей
- ✅ **Issue templates**: Структуровані шаблони для issues
- ✅ **PR templates**: Шаблони для pull requests

### GitHub Actions Workflows

- `ci-cd.yml` - Повний CI/CD pipeline
- `quick-check.yml` - Швидкі перевірки
- `codeql.yml` - Security scanning
- `release.yml` - Автоматичні releases
- `badges.yml` - Генерація badges

### Badges

[![CI/CD Pipeline](https://github.com/alexandrsukhryn/ai-swagger-bot/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/alexandrsukhryn/ai-swagger-bot/actions)
[![Quick Check](https://github.com/alexandrsukhryn/ai-swagger-bot/workflows/Quick%20Check/badge.svg)](https://github.com/alexandrsukhryn/ai-swagger-bot/actions)
[![CodeQL](https://github.com/alexandrsukhryn/ai-swagger-bot/workflows/CodeQL/badge.svg)](https://github.com/alexandrsukhryn/ai-swagger-bot/actions)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Ruff](https://img.shields.io/badge/ruff-A00034?style=flat&logo=ruff&logoColor=white)](https://github.com/astral-sh/ruff)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

### Автоматизація

- 🔄 **Автоматичні тести** при кожному push/PR
- 🔒 **Security scanning** з CodeQL та Trivy
- 📦 **Docker збірка** та тестування
- 🚀 **Автоматичні releases** при тегах
- 📈 **Coverage reports** з Codecov
- 🔧 **Dependabot** для оновлення залежностей

## 📁 Структура проекту

```
ai-swagger-bot/
├── src/                       # Основний код
│   ├── __init__.py
│   ├── interactive_api_agent.py
│   ├── enhanced_swagger_parser.py
│   ├── rag_engine.py
│   ├── enhanced_prompt_manager.py
│   ├── dynamic_prompt_manager.py
│   ├── swagger_error_handler.py
│   ├── swagger_validation_prompt.py
│   ├── config.py
│   ├── prompt_descriptions.py
│   └── prompt_templates.py
├── tests/                     # Тести
│   ├── test_*.py
│   └── __pycache__/
├── examples/                  # Приклади
│   ├── swagger_specs/
│   ├── basic_usage.py
│   ├── enhanced_prompt_usage.py
│   ├── object_creation_example.py
│   └── api_response_processing_example.py
├── docs/                      # Документація
│   ├── README_AGENTS.md
│   ├── QUERY_GUIDE.md
│   ├── OBJECT_CREATION_GUIDE.md
│   ├── ENHANCED_PROMPTS_GUIDE.md
│   ├── API_RESPONSE_PROCESSING.md
│   ├── RAG_SYSTEM_ANALYSIS.md
│   ├── RAG_ANSWERS_SUMMARY.md
│   ├── GPT_PROMPTS_SUMMARY.md
│   ├── DYNAMIC_PROMPTS_README.md
│   ├── DOCKER_GUIDE.md
│   ├── DEMO_EXAMPLES.md
│   ├── QUICK_REFERENCE.md
│   ├── ALGORITHM_FLOWCHART.md
│   ├── AI_SWAGGER_BOT_ALGORITHM.md
│   ├── SECURITY_REPORT.md
│   └── SECURITY_SETUP.md
├── scripts/                   # Скрипти
│   ├── analyze_chroma_db.py
│   ├── clear_chroma_db.py
│   ├── fresh_start.sh
│   ├── quick_start.py
│   ├── run_enhanced_chat.sh
│   ├── reindex_swagger.py
│   ├── view_vectors.py
│   └── README_DB_MANAGEMENT.md
├── .github/                   # GitHub конфігурація
│   ├── workflows/             # CI/CD workflows
│   │   ├── ci-cd.yml
│   │   ├── quick-check.yml
│   │   ├── codeql.yml
│   │   ├── release.yml
│   │   └── badges.yml
│   ├── ISSUE_TEMPLATE/        # Шаблони issues
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   │   ├── question.md
│   │   ├── documentation.md
│   │   ├── performance.md
│   │   ├── accessibility.md
│   │   ├── translation.md
│   │   ├── regression.md
│   │   ├── duplicate.md
│   │   ├── invalid.md
│   │   ├── wontfix.md
│   │   ├── help_wanted.md
│   │   ├── good_first_issue.md
│   │   ├── enhancement.md
│   │   ├── breaking_change.md
│   │   ├── discussion.md
│   │   ├── idea.md
│   │   ├── feedback.md
│   │   ├── thanks.md
│   │   ├── spam.md
│   │   ├── off_topic.md
│   │   ├── not_reproducible.md
│   │   ├── works_for_me.md
│   │   ├── confirmed.md
│   │   ├── blocked.md
│   │   ├── priority_*.md
│   │   └── config.yml
│   ├── dependabot.yml         # Автооновлення залежностей
│   ├── FUNDING.yml           # Фінансування
│   └── pull_request_template.md
├── enhanced_chat_app.py      # Streamlit додаток
├── demo_client.html          # Демо клієнт
├── docker-compose.yml        # Docker Compose
├── docker-compose.test.yml   # Docker Compose для тестів
├── Dockerfile               # Docker образ
├── .dockerignore           # Docker ignore
├── requirements.txt        # Залежності
├── requirements-dev.txt    # Dev залежності
├── setup.py              # Python пакет
├── pyproject.toml        # Конфігурація проекту
├── ruff.toml            # Ruff конфігурація
├── .coveragerc          # Coverage конфігурація
├── pytest.ini          # Pytest конфігурація
├── mypy.ini           # MyPy конфігурація
├── .bandit            # Bandit конфігурація
├── .isort.cfg         # isort конфігурація
├── .flake8           # flake8 конфігурація
├── .pre-commit-config.yaml # Pre-commit hooks
├── Makefile          # Команди для розробки
├── LICENSE          # MIT License
├── CONTRIBUTING.md  # Інструкції для контриб'юторів
├── CODE_OF_CONDUCT.md # Code of Conduct
├── SECURITY.md      # Security Policy
├── CHANGELOG.md     # Історія змін
└── README.md        # Головний README
```

## 🎯 Приклади використання

### 1. Базовий використання (Python)

```python
from src.interactive_api_agent import InteractiveAPIAgent

# Ініціалізація агента
agent = InteractiveAPIAgent("examples/swagger_specs/shop_api.json")

# Запит користувача
user_query = "Додай товар: синя сукня, розмір 22, кількість 10"

# Отримання відповіді
response = agent.process_query(user_query)
print(response)
# Вивід: "📋 Сформований API запит: POST /products"
```

### 2. Використання з Docker

```bash
# Збірка Docker образу
docker build -t ai-swagger-bot .

# Запуск контейнера
docker run -p 8501:8501 ai-swagger-bot

# Або з Docker Compose
docker-compose up
```

### 3. Використання з Makefile

```bash
# Встановлення залежностей
make install-dev

# Запуск тестів
make test

# Перевірка коду
make lint

# Форматування коду
make format

# Запуск CI/CD локально
make ci
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

### 🔧 Базові Swagger запити

#### Товари
```
Додай товар: синя сукня, розмір 22, кількість 10
Створи новий товар - червона сукня, розмір 44, 5 штук
Додай товар з назвою 'Чорні кросівки', ціна 1500 грн, категорія 'Взуття'
Покажи всі товари
Отримай товар з ID 123
Онови товар 456 - зміни ціну на 2000 грн
Видали товар 789
```

#### Замовлення
```
Створи замовлення для користувача 1 з товаром 123, кількість 2
Покажи всі замовлення
Отримай замовлення з ID 456
```

#### Користувачі
```
Створи користувача: Іван Петренко, email ivan@example.com
Отримай користувача з ID 1
Онови користувача 2 - зміни email на new@example.com
```

### 🛍️ Розширені E-commerce запити

#### Розумний пошук товарів
```
Знайди теплу куртку для зими
Потрібен подарунок для дівчини
Шукаю телефон в діапазоні 5000-15000 грн
Щось для активного відпочинку
Потрібна елегантна сукня для вечірки
```

#### Допомога з замовленнями
```
Відстежи моє замовлення #12345
Як оформити замовлення?
Хочу скасувати замовлення
Коли прибуде моє замовлення?
Як змінити адресу доставки?
```

#### Створення контенту
```
Створи опис для товару Смартфон Samsung Galaxy
Напиши опис для куртки зимової
Створи опис для подарункового набору
Напиши рекламний текст для нової колекції
```

#### Персоналізовані рекомендації
```
Що порекомендуєш для подарунка?
Покажи рекомендації на основі моїх покупок
Що популярне зараз?
Що підійде до мого телефону?
```

#### Підтримка клієнтів
```
Проблема з оплатою замовлення
Коли прибуде моє замовлення?
Як повернути товар?
Які способи доставки доступні?
```

#### Аналітика та звіти
```
Покажи статистику продажів
Які товари найпопулярніші?
Звіт по користувачах
Аналіз категорій товарів
```

#### Система сповіщень
```
Створи сповіщення про акцію
Надішли повідомлення про статус замовлення
Оголоси про новинки
Сповісти про знижки
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

## 🎯 Демонстрація нових функцій

### Запуск демонстрації розширеного AI-асистента
```bash
python examples/enhanced_ai_assistant_example.py
```

### Приклад використання
```python
from src.enhanced_ai_assistant import EnhancedAIAssistant
from src.enhanced_prompt_manager import EnhancedPromptManager
from src.rag_engine import RAGEngine

# Ініціалізація
prompt_manager = EnhancedPromptManager()
rag_engine = RAGEngine()
assistant = EnhancedAIAssistant(prompt_manager, rag_engine)

# Налаштування профілю користувача
assistant.update_user_profile("user123", {
    "name": "Іван Петренко",
    "preferences": {
        "categories": ["Електроніка", "Одяг"],
        "price_range": {"min": 100, "max": 5000}
    },
    "purchase_history": [
        {"product": "Смартфон", "category": "Електроніка", "price": 8000}
    ]
})

# Обробка запитів
response = assistant.process_user_query("user123", "Знайди теплу куртку для зими")
print(response)

response = assistant.process_user_query("user123", "Створи опис для товару Смартфон iPhone 15")
print(response)

response = assistant.process_user_query("user123", "Що порекомендуєш для подарунка?")
print(response)
```

### Документація нових функцій
- [Enhanced AI Assistant Guide](docs/ENHANCED_AI_ASSISTANT_GUIDE.md) - повний опис нових функцій
- [E-commerce Features](docs/ECOMMERCE_FEATURES.md) - детальний опис e-commerce функцій
- [Content Creation Guide](docs/CONTENT_CREATION_GUIDE.md) - створення контенту
- [Recommendations System](docs/RECOMMENDATIONS_SYSTEM.md) - система рекомендацій

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

Цей проект ліцензований під MIT License - дивіться файл [LICENSE](LICENSE) для деталей.

## 🤝 Контриб'юція

Дивіться [CONTRIBUTING.md](CONTRIBUTING.md) для деталей про те, як контриб'ютити до проекту.

## 📚 Документація

- [API Reference](docs/API_REFERENCE.md)
- [Query Guide](docs/QUERY_GUIDE.md)
- [Object Creation Guide](docs/OBJECT_CREATION_GUIDE.md)
- [Enhanced Prompts Guide](docs/ENHANCED_PROMPTS_GUIDE.md)
- [Docker Guide](docs/DOCKER_GUIDE.md)
- [Quick Reference](docs/QUICK_REFERENCE.md)

## 🔒 Безпека

Дивіться [SECURITY.md](SECURITY.md) для інформації про безпеку та звітування про вразливості.

## 📋 Changelog

Дивіться [CHANGELOG.md](CHANGELOG.md) для історії змін проекту.

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

## ☁️ Serverless Deployment

### AWS Lambda з Mangum

Проект підтримує розгортання як серверлес функція на AWS Lambda з використанням [Mangum](https://pypi.org/project/mangum/):

```python
from mangum import Mangum
from api.main import app

# Створюємо handler для AWS Lambda
handler = Mangum(app, lifespan="off")
```

### Швидкий старт

```bash
# Налаштування
./scripts/setup_serverless.sh

# Розгортання
make -f Makefile.lambda deploy

# Тестування
make -f Makefile.lambda test-local
```

### Компоненти

- **`lambda_handler.py`** - AWS Lambda handler з Mangum
- **`serverless.yml`** - Serverless Framework конфігурація
- **`Dockerfile.lambda`** - Docker image для Lambda
- **`terraform/`** - Infrastructure as Code
- **CI/CD** - GitHub Actions та GitLab CI

### Переваги

- 🚀 **Auto-scaling** - автоматичне масштабування
- 💰 **Pay-per-use** - плата тільки за використання
- 🔒 **Security** - VPC, security groups, IAM roles
- 📊 **Monitoring** - CloudWatch, логування, метрики
- 🌍 **Multi-stage** - dev, staging, production

**Детальна документація**: [README_SERVERLESS.md](README_SERVERLESS.md)

## 🗄️ Бази даних

### PostgreSQL (основна база)
- **Призначення**: Користувачі, сесії чату, промпти, Swagger специфікації
- **Статус**: ✅ Активна
- **URL**: `postgresql://postgres:postgres@localhost:5432/ai_swagger_bot`

### ChromaDB (векторна база)
- **Призначення**: Векторні ембедінги для RAG
- **Статус**: ✅ Активна
- **Розташування**: `./temp_chroma_db/`
