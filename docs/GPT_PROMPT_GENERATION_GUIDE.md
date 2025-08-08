# 🤖 GPT Генерація Промптів - Посібник

## 📋 Огляд

Система автоматичної генерації промптів через GPT на основі Swagger специфікації дозволяє створювати розумні та адаптивні промпти для кожного API endpoint.

## 🎯 Основні можливості

### ✅ Автоматична генерація промптів
- Аналіз Swagger специфікації
- Створення промптів для кожного endpoint
- Генерація загальних промптів для ресурсів
- Адаптація під конкретний API

### ✅ Розумні підказки
- Генерація практичних підказок
- Категорізація за складністю
- Приклади запитів
- Контекстні поради

### ✅ Інтеграція з системою
- Автоматичне збереження промптів
- Прив'язка до користувачів
- API endpoints для управління
- CLI команди для тестування

## 🏗️ Архітектура

### Основні компоненти

```
src/
├── gpt_prompt_generator.py     # GPT генератор промптів
└── swagger_prompt_generator.py # Базовий генератор (запасний)

api/
└── prompts.py                  # API endpoints для генерації

examples/
└── gpt_prompt_generation_example.py # Приклад використання
```

### Процес генерації

1. **Аналіз Swagger** - Парсинг специфікації
2. **Визначення ресурсів** - Пошук endpoints та їх типів
3. **Генерація через GPT** - Створення промптів з контекстом
4. **Збереження** - Інтеграція з системою промптів

## 🚀 Швидкий старт

### 1. Налаштування OpenAI API

```bash
# Встановіть змінну середовища
export OPENAI_API_KEY="your_openai_api_key_here"
```

### 2. Генерація промптів через CLI

```bash
# Генерація промптів з Swagger файлу
python cli_tester.py generate-prompts --file examples/swagger_specs/shop_api.json

# Генерація підказок
python cli_tester.py generate-suggestions --file examples/swagger_specs/shop_api.json

# Автоматична генерація для користувача
python cli_tester.py auto-generate --swagger-spec-id your_spec_id
```

### 3. Використання через Streamlit

```bash
# Запустіть Streamlit фронтенд
streamlit run streamlit_frontend.py

# У веб-інтерфейсі:
# 1. Створіть демо користувача
# 2. Завантажте Swagger файл
# 3. Натисніть "Згенерувати промпти через GPT"
```

### 4. Програмне використання

```python
from src.gpt_prompt_generator import generate_prompts_with_gpt

# Читаємо Swagger файл
with open("swagger.json", "r") as f:
    swagger_data = json.load(f)

# Генеруємо промпти
prompts = generate_prompts_with_gpt(swagger_data, api_key="your_key")

# Використовуємо згенеровані промпти
for prompt in prompts:
    print(f"Промпт: {prompt.name}")
    print(f"Категорія: {prompt.category}")
    print(f"Шаблон: {prompt.template}")
```

## 📊 API Endpoints

### Генерація промптів

```http
POST /prompts/generate-from-swagger
Content-Type: application/json

{
    "swagger_data": {
        "openapi": "3.0.0",
        "paths": {...}
    },
    "api_key": "optional_openai_key"
}
```

**Відповідь:**
```json
{
    "message": "Успішно згенеровано 15 промптів",
    "generated_count": 15,
    "saved_count": 15,
    "prompts": [
        {
            "id": "gpt_products_get",
            "name": "Отримання товарів",
            "category": "data_retrieval",
            "resource_type": "products",
            "endpoint_path": "/products",
            "http_method": "GET"
        }
    ]
}
```

### Генерація підказок

```http
POST /prompts/generate-suggestions
Content-Type: application/json

{
    "swagger_data": {...},
    "api_key": "optional_openai_key"
}
```

**Відповідь:**
```json
{
    "message": "Згенеровано 12 підказок",
    "suggestions_count": 12,
    "suggestions": [
        {
            "category": "Аналіз API",
            "title": "Покажи всі endpoints",
            "description": "Отримати повний список доступних API endpoints",
            "example_query": "Покажи всі доступні endpoints",
            "difficulty": "easy"
        }
    ]
}
```

### Автоматична генерація для користувача

```http
POST /prompts/auto-generate-for-user
Content-Type: application/json

{
    "swagger_spec_id": "user_swagger_spec_id",
    "api_key": "optional_openai_key"
}
```

## 🔧 Налаштування

### Конфігурація GPT

```python
from src.gpt_prompt_generator import GPTPromptGenerator

# Створення генератора з налаштуваннями
generator = GPTPromptGenerator(
    api_key="your_openai_key",
    model="gpt-4"  # або "gpt-3.5-turbo"
)
```

### Кастомізація промптів

Система автоматично генерує промпти для:
- **GET endpoints** - Отримання даних
- **POST endpoints** - Створення даних
- **PUT/PATCH endpoints** - Оновлення даних
- **DELETE endpoints** - Видалення даних

### Типи ресурсів

Автоматично розпізнаються:
- `products` - Товари
- `categories` - Категорії
- `orders` - Замовлення
- `users` - Користувачі
- `brands` - Бренди
- `collections` - Колекції
- `attributes` - Атрибути
- `settings` - Налаштування
- `families` - Сімейства товарів

## 📝 Приклади згенерованих промптів

### Промпт для GET /products

```yaml
id: gpt_products_get
name: "Отримання товарів"
description: "Промпт для отримання списку товарів через API"
template: |
  Ти - експерт з API для роботи з товарами.

  ENDPOINT: GET /products

  Твоя задача - допомогти користувачу взаємодіяти з цим endpoint через природну мову.

  ІНФОРМАЦІЯ ПРО ENDPOINT:
  - Метод: GET
  - Шлях: /products
  - Ресурс: products

  ПАРАМЕТРИ:
  - page (query, опціональний): Номер сторінки
  - limit (query, опціональний): Кількість елементів на сторінці
  - sortBy (query, опціональний): Поле для сортування
  - sortOrder (query, опціональний): Порядок сортування
  - filters (query, опціональний): Фільтри у форматі JSON

  ПРАВИЛА ВІДПОВІДІ:
  1. Завжди відповідай українською мовою
  2. Використовуй емодзі для кращого сприйняття
  3. Надавай практичні приклади
  4. Пояснюй параметри та їх призначення
  5. Допомагай з валідацією даних

  КОРИСТУВАЧ ЗАПИТУЄ: {user_query}

  Твоя відповідь:
category: data_retrieval
tags: ["gpt_generated", "products", "get", "api", "endpoint"]
```

### Промпт для POST /products

```yaml
id: gpt_products_post
name: "Створення товару"
description: "Промпт для створення нового товару"
template: |
  Ти - експерт з API для роботи з товарами.

  ENDPOINT: POST /products

  Твоя задача - допомогти користувачу створити новий товар через API.

  СХЕМА ЗАПИТУ:
  {
    "name": "string",
    "price": "number",
    "description": "string",
    "sku": "string",
    "categoryId": "string",
    "stock": "boolean",
    "status": "string"
  }

  ОБОВ'ЯЗКОВІ ПОЛЯ:
  - name: Назва товару
  - price: Ціна товару
  - description: Опис товару
  - sku: Унікальний ідентифікатор
  - categoryId: ID категорії
  - stock: Наявність на складі
  - status: Статус товару

  ПРАВИЛА ВІДПОВІДІ:
  1. Завжди відповідай українською мовою
  2. Допомагай з валідацією обов'язкових полів
  3. Надавай приклади правильного заповнення
  4. Пояснюй призначення кожного поля

  КОРИСТУВАЧ ЗАПИТУЄ: {user_query}

  Твоя відповідь:
category: data_creation
tags: ["gpt_generated", "products", "post", "api", "endpoint"]
```

## 🎯 Розумні підказки

### Приклади згенерованих підказок

```json
{
    "suggestions": [
        {
            "category": "Аналіз API",
            "title": "Покажи всі endpoints",
            "description": "Отримати повний список доступних API endpoints",
            "example_query": "Покажи всі доступні endpoints",
            "difficulty": "easy"
        },
        {
            "category": "Робота з товарами",
            "title": "Створи новий товар",
            "description": "Додати новий товар до каталогу",
            "example_query": "Створи товар з назвою iPhone 15 Pro",
            "difficulty": "medium"
        },
        {
            "category": "Фільтрація та пошук",
            "title": "Знайти товари за ціною",
            "description": "Пошук товарів у вказаному діапазоні цін",
            "example_query": "Покажи товари з ціною від 1000 до 5000",
            "difficulty": "medium"
        }
    ]
}
```

## 🔍 Troubleshooting

### Помилки та рішення

#### ❌ OpenAI API ключ не знайдено
```bash
# Рішення: Встановіть змінну середовища
export OPENAI_API_KEY="your_api_key_here"
```

#### ❌ Помилка підключення до OpenAI
```bash
# Перевірте:
# 1. Інтернет-з'єднання
# 2. Правильність API ключа
# 3. Ліміти OpenAI API
```

#### ❌ Файл Swagger не знайдено
```bash
# Перевірте шлях до файлу
ls examples/swagger_specs/
python cli_tester.py generate-prompts --file examples/swagger_specs/shop_api.json
```

#### ❌ Помилка парсингу JSON
```bash
# Перевірте валідність Swagger файлу
python -m json.tool examples/swagger_specs/shop_api.json
```

## 📈 Оптимізація

### Налаштування температури GPT

```python
# Для більш креативних промптів
generator = GPTPromptGenerator(model="gpt-4", temperature=0.8)

# Для більш консистентних промптів
generator = GPTPromptGenerator(model="gpt-4", temperature=0.3)
```

### Кешування результатів

```python
# Зберігайте згенеровані промпти для повторного використання
import pickle

# Збереження
with open("generated_prompts.pkl", "wb") as f:
    pickle.dump(generated_prompts, f)

# Завантаження
with open("generated_prompts.pkl", "rb") as f:
    prompts = pickle.load(f)
```

## 🎉 Висновок

GPT генерація промптів надає:

1. **Автоматизацію** - Не потрібно створювати промпти вручну
2. **Адаптивність** - Промпти генеруються під конкретний API
3. **Розумність** - GPT розуміє контекст та створює корисні промпти
4. **Масштабованість** - Легко генерувати промпти для великих API
5. **Інтеграцію** - Повна інтеграція з існуючою системою

Система значно покращує користувацький досвід та зменшує час на налаштування промптів для нових API.
