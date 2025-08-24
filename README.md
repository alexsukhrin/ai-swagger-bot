# 🤖 AI Swagger Bot CLI

**AI помічник для роботи з API через людську мову!**

Потужний CLI інструмент, який розуміє ваші запити українською мовою та автоматично створює та виконує API запити на основі Swagger документації.

## 🚀 Особливості

- **Swagger/OpenAPI підтримка**: Завантаження та парсинг Swagger файлів
- **RAG система**: Retrieval Augmented Generation з ChromaDB
- **AI чат**: Інтеграція з OpenAI GPT-4 для розумних відповідей
- **Векторна база даних**: ChromaDB для ефективного зберігання та пошуку
- **CLI інтерфейс**: Зручне управління через командний рядок
- **Інтерактивний режим**: Дружній інтерфейс для легкого використання

## 📋 Вимоги

- Python 3.9+
- OpenAI API ключ
- JWT секретний ключ

## 🛠️ Встановлення

1. **Клонуйте репозиторій:**
```bash
git clone <repository-url>
cd ai-swagger-bot
```

2. **Створіть віртуальне середовище:**
```bash
conda create -n ai-swagger-bot python=3.9
conda activate ai-swagger-bot
```

3. **Встановіть залежності:**
```bash
make install
# або
pip install -r requirements.txt
```

4. **Налаштуйте змінні середовища:**
Створіть файл `.env` з наступним вмістом:
```env
OPENAI_API_KEY=your_openai_api_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
```

## 🎯 Швидкий старт

```bash
# Додати Oneshop API
make quick-start

# Або вручну
python cli.py add-swagger https://api.oneshop.click/docs/ai-json --name oneshop

# Тестувати чат
make chat MESSAGE="Покажи всі доступні ендпоінти"
```

## 📚 Доступні команди

### Основні команди

| Команда | Опис | Приклад |
|---------|------|---------|
| `add-swagger` | Додати новий Swagger API | `python cli.py add-swagger <url> --name <name>` |
| `chat` | Відправити повідомлення боту | `python cli.py chat "Повідомлення"` |
| `list-apis` | Показати список API | `python cli.py list-apis` |
| `remove-api` | Видалити API | `python cli.py remove-api <name>` |

### Інформаційні команди

| Команда | Опис | Приклад |
|---------|------|---------|
| `info` | Інформація про систему або API | `python cli.py info [--name <name>]` |
| `stats` | Статистика системи | `python cli.py stats` |
| `status` | Статус системи | `python cli.py status` |
| `version` | Версія CLI | `python cli.py version` |

### Аналітичні команди

| Команда | Опис | Приклад |
|---------|------|---------|
| `search` | Пошук ендпоінтів | `python cli.py search "запит" [--api <name>]` |
| `test-api` | Тестування API | `python cli.py test-api <name>` |
| `analyze-swagger` | Детальний аналіз API | `python cli.py analyze-swagger <name>` |
| `db-info` | Інформація про базу даних | `python cli.py db-info` |

### Управління API

| Команда | Опис | Приклад |
|---------|------|---------|
| `export-api` | Експорт API | `python cli.py export-api <name> [--output <file>]` |
| `import-api` | Імпорт API з файлу | `python cli.py import-api <file> [--name <name>]` |
| `clear-all` | Очистити всі API | `python cli.py clear-all` |

### Спеціалізовані промпти

| Команда | Опис | Приклад |
|---------|------|---------|
| `show-prompts` | Показати спеціалізовані промпти для API | `python cli.py show-prompts <name>` |
| `export-prompts` | Експорт спеціалізованих промптів у файл | `python cli.py export-prompts <name> [--output <file>]` |

### Інтерактивний режим

| Команда | Опис |
|---------|------|
| `interactive` | Запустити інтерактивний режим |

## 🎮 Інтерактивний режим

Запустіть інтерактивний режим для зручного використання:

```bash
python cli.py interactive
```

Доступні команди в інтерактивному режимі:
- `add <url> [name]` - Додати API
- `chat <message>` - Чат з ботом
- `list/ls/show/apis/api` - Список API
- `remove <name>` - Видалити API
- `info [name]` - Інформація про API або систему
- `search <query> [api]` - Пошук ендпоінтів
- `export <name> [file]` - Експорт API
- `import <file> [name]` - Імпорт API
- `clear` - Очистити всі API
- `stats` - Статистика системи
- `test <name>` - Тестування API
- `status` - Статус системи
- `version` - Версія CLI
- `analyze <name>` - Детальний аналіз API
- `db-info` - Інформація про базу даних
- `exit` - Вихід

## 🔧 Makefile команди

Для зручності використання доступні Makefile команди:

### Основні команди
```bash
make install          # Встановити залежності
make test             # Запустити тести
make clean            # Очистити проект
make run              # Запустити CLI
```

### API команди
```bash
make add-swagger URL=<url> NAME=<name>  # Додати API
make chat MESSAGE="<message>"           # Чат з ботом
make list-apis                          # Список API
make remove-api NAME=<name>             # Видалити API
```

### Інформаційні команди
```bash
make info [NAME=<name>]                 # Інформація про систему або API
make search QUERY="<query>" [API=<name>] # Пошук ендпоінтів
make stats                              # Статистика системи
make status                             # Статус системи
make version                            # Версія CLI
```

### Аналітичні команди
```bash
make test-api NAME=<name>               # Тестування API
make analyze-swagger NAME=<name>        # Детальний аналіз API
make db-info                            # Інформація про базу даних
```

### Управління API
```bash
make export-api NAME=<name> [OUTPUT=<file>] # Експорт API
make import-api FILE=<file> [NAME=<name>]   # Імпорт API
make clear-all                             # Очистити всі API
```

### Спеціальні команди
```bash
make interactive                          # Інтерактивний режим
make quick-start                         # Швидкий старт з Oneshop API
make demo                                # Показати демо команди
make test-all                            # Повний цикл тестування
```

### Аліаси
```bash
make ls                                  # Список API (аліас для list-apis)
make show                                # Список API (аліас для list-apis)
make apis                                # Список API (аліас для list-apis)
make api                                 # Список API (аліас для list-apis)
```

## 📊 Приклади використання

### 1. Додавання API
```bash
# Додати Oneshop API
python cli.py add-swagger https://api.oneshop.click/docs/ai-json --name oneshop

# Або через Makefile
make add-swagger URL=https://api.oneshop.click/docs/ai-json NAME=oneshop
```

### 2. Чат з ботом
```bash
# Запитати про ендпоінти
python cli.py chat "Покажи всі доступні ендпоінти"

# Запитати про створення категорії
python cli.py chat "Як створити нову категорію?"

# Або через Makefile
make chat MESSAGE="Покажи всі доступні ендпоінти"
```

### 3. Пошук та аналіз
```bash
# Пошук ендпоінтів
python cli.py search "створення категорії"

# Детальний аналіз API
python cli.py analyze-swagger oneshop

# Інформація про базу даних
python cli.py db-info
```

### 4. Управління API
```bash
# Переглянути список API
python cli.py list-apis

# Тестувати API
python cli.py test-api oneshop

# Отримати статистику
python cli.py stats

# Очистити всі API
python cli.py clear-all
```

## 🔍 Детальний аналіз API

Команда `analyze-swagger` надає глибокий аналіз Swagger API:

```bash
python cli.py analyze-swagger oneshop
```

Ця команда виконує:
- 📋 Базова інформація про API
- 🔍 Аналіз ендпоінтів через RAG систему
- 📝 Аналіз схем даних
- 🔒 Аналіз безпеки та аутентифікації
- ⚙️ Технічна інформація (розмір, chunks)
- 🧪 Тестування API
- 💡 Рекомендації щодо використання

### Діагностика парсингу Swagger

Якщо система знаходить менше ендпоінтів, ніж очікувалося:

1. **Перевірте розмір chunks**: Використовуйте `CHUNK_SIZE=200` замість 1000
2. **Перевірте кількість chunks**: Команда `db-info` показує реальну кількість документів
3. **Перевірте оригінальний Swagger**: Використайте `curl` для перегляду оригінального файлу

```bash
# Перевірка оригінального Swagger
curl -s https://api.oneshop.click/docs/ai-json | python -c "import json, sys; data=json.load(sys.stdin); print('Paths:', len(data['paths'])); [print(f'  {method.upper()} {path}') for path, methods in data['paths'].items() for method in methods.keys() if method.upper() in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']]"

# Перевірка кількості chunks
python cli.py db-info

# Аналіз конкретного API
python cli.py analyze-swagger <api_name>
```

## 🗄️ Інформація про базу даних

Команда `db-info` показує детальну інформацію про ChromaDB:

```bash
python cli.py db-info
```

Включає:
- 📁 Структуру папок
- 📊 Статистику файлів
- 📚 Інформацію про колекції
- 🏥 Здоров'я бази даних
- ⚠️ Попередження про розмір та кількість файлів

## 📈 Статистика системи

Команда `stats` надає комплексну статистику:

```bash
python cli.py stats
```

Включає:
- 📊 Статистику API
- 🗄️ ChromaDB статистику
- 📚 Статистику колекцій
- ⚙️ Конфігурацію
- 💻 Системну статистику (RAM, диск, CPU)

## 🧪 Тестування

### Запуск тестів
```bash
make test
# або
python -m pytest tests/ -v
```

### Повний цикл тестування
```bash
make test-all
```

Ця команда виконує:
1. Перевірка статусу
2. Додавання API
3. Тестування основних функцій
4. Тестування пошуку
5. Тестування чату
6. Тестування нових команд

## 🚀 Демо

Подивитися всі доступні демо команди:

```bash
make demo
```

## 📁 Структура проекту

```
ai-swagger-bot/
├── cli.py                 # Основний CLI файл
├── src/                   # Вихідний код
│   ├── config.py         # Конфігурація
│   ├── rag_engine.py     # RAG двигун
│   ├── enhanced_swagger_parser.py  # Парсер Swagger
│   └── token_manager.py  # Управління токенами
├── chroma_db/            # ChromaDB база даних
├── requirements.txt       # Залежності Python
├── Makefile              # Makefile команди
└── README.md             # Документація
```

## ⚙️ Конфігурація

Основні налаштування в `src/config.py`:

- `OPENAI_MODEL`: Модель OpenAI (за замовчуванням: "gpt-4")
- `CHROMA_DB_PATH`: Шлях до ChromaDB (за замовчуванням: "./chroma_db")
- `CHROMA_COLLECTION_NAME`: Назва колекції (за замовчуванням: "swagger_specs")
- `CHUNK_SIZE`: Розмір chunks для RAG (за замовчуванням: 200)
- `CHUNK_OVERLAP`: Перекриття між chunks (за замовчуванням: 200)
- `SEARCH_K_RESULTS`: Кількість результатів пошуку (за замовчуванням: 5)

### Налаштування chunks

Важливо правильно налаштувати `CHUNK_SIZE` для ефективної роботи RAG системи:

- **CHUNK_SIZE = 1000** (за замовчуванням): Може призвести до об'єднання коротких ендпоінтів в один chunk
- **CHUNK_SIZE = 200** (рекомендовано): Забезпечує окремі chunks для кожного ендпоінту
- **CHUNK_SIZE = 100**: Створює дуже детальні chunks, але може збільшити кількість документів

Для налаштування додайте до `.env` файлу:
```env
CHUNK_SIZE=200
CHUNK_OVERLAP=50
```

## 🔧 Розробка

### Додавання нових команд

1. Додайте метод до класу `SwaggerBotCLI`
2. Додайте парсер аргументів у функції `main()`
3. Додайте обробку команди
4. Оновіть інтерактивний режим
5. Додайте Makefile команду
6. Оновіть документацію

### Тестування

```bash
# Запуск всіх тестів
make test

# Запуск конкретного тесту
python -m pytest tests/test_specific.py -v

# Запуск з покриттям
python -m pytest tests/ --cov=src --cov-report=html
```

## 🐛 Вирішення проблем

### Помилка "No module named 'langchain'"
```bash
pip install langchain langchain-openai
```

### Помилка "No module named 'psutil'"
```bash
pip install psutil
```

### Проблеми з ChromaDB
```bash
# Очистити базу даних
make clean

# Перезапустити
make run
```

## 📄 Ліцензія

Цей проект розповсюджується під ліцензією MIT.

## 🤝 Внесок

Вітаються внески! Будь ласка:

1. Форкніть репозиторій
2. Створіть гілку для нової функції
3. Зробіть коміт змін
4. Відправте pull request

## 📞 Підтримка

Якщо у вас виникли питання або проблеми:

1. Перевірте документацію
2. Запустіть `make demo` для прикладів
3. Використайте `make test-all` для діагностики
4. Створіть issue у репозиторії

## 🧠 RAG система та промпти

### Як працює RAG система

RAG (Retrieval Augmented Generation) система автоматично створюється на основі парсингу Swagger специфікацій:

1. **Парсинг Swagger**: Система аналізує Swagger файл та витягує:
   - Ендпоінти з їх методами (GET, POST, PUT, PATCH, DELETE)
   - Параметри запитів та відповідей
   - Схеми даних та типи
   - Опис та документацію

2. **Створення chunks**: Кожен ендпоінт розбивається на логічні частини:
   - Основна інформація (шлях, метод, опис)
   - Параметри та їх типи
   - Request/Response схеми
   - Приклади використання
   - Інструкції та рекомендації

3. **Збереження в SQLite**: Створені дані зберігаються у SQLite базі даних з:
   - Таблицею API
   - Таблицею ендпоінтів
   - Таблицею промптів
   - Таблицею embeddings (векторів)

4. **Генерація відповідей**: При запиті користувача:
   - Система шукає релевантні ендпоінти за допомогою векторного пошуку
   - Формує контекст на основі знайдених даних
   - Генерує детальну відповідь за допомогою GPT-4

### 🗄️ SQLite замість ChromaDB

**Проблема**: ChromaDB мав проблеми з відображенням всіх ендпоінтів та створенням дублікатів chunks.

**Рішення**: Перехід на SQLite RAG двигун з наступними перевагами:

✅ **Надійність**: SQLite - стабільна та перевірена база даних  
✅ **Простота**: Один файл бази даних замість складних структур  
✅ **Швидкість**: Швидкий пошук та доступ до даних  
✅ **Контроль**: Повний контроль над структурою даних  
✅ **Розмір**: Менший розмір (0.21 MB замість 16.4 MB)  
✅ **Точність**: Всі 5 ендпоінтів відображаються правильно  

### Структура SQLite бази даних

```
📊 Таблиці:
├── apis - інформація про API
├── endpoints - всі ендпоінти з деталями
├── prompts - спеціалізовані промпти
└── embeddings - векторні представлення для пошуку
```

### Спеціалізовані промпти

Система автоматично створює 5 типів промптів для кожного API:

#### 🎯 Data Retrieval (Отримання даних)
- Список GET ендпоінтів
- Параметри запитів
- Формати відповідей
- Приклади використання

#### 🆕 Data Creation (Створення даних)
- Список POST ендпоінтів
- Структура request body
- Необхідні поля
- Приклади JSON

#### 🔄 Data Update (Оновлення даних)
- Список PUT/PATCH ендпоінтів
- Параметри оновлення
- Часткове vs повне оновлення

#### 🗑️ Data Deletion (Видалення даних)
- Список DELETE ендпоінтів
- Параметри видалення
- Підтвердження операцій

#### 📋 General (Загальний огляд)
- Повний список всіх ендпоінтів
- Групування за методами
- Загальна інформація про API

### Перегляд та експорт промптів

```bash
# Показати всі типи промптів для API
python cli.py show-prompts oneshop

# Експортувати промпти у JSON файл
python cli.py export-prompts oneshop

# Експорт з власною назвою файлу
python cli.py export-prompts oneshop --output my_prompts.json
```

### Приклад створеного промпту

```
=== oneshop - Отримання даних ===
Цей API надає наступні можливості для отримання даних:

• GET /api/categories
  Опис: Get all categories (Public)

• GET /api/categories/{id}
  Опис: Get a category by ID (Public)

Використання: Використовуйте ці ендпоінти для отримання інформації з системи.
```

### Переваги SQLite RAG системи

✅ **Автоматичне створення**: Промпти генеруються автоматично з Swagger  
✅ **Актуальність**: Завжди відповідають поточній версії API  
✅ **Деталізація**: Включають всі необхідні деталі для роботи  
✅ **Структурованість**: Розділені за типами операцій  
✅ **Експорт**: Можна зберегти та використовувати окремо  
✅ **Інтеграція**: Повністю інтегровані з чат-системою  
✅ **Надійність**: SQLite забезпечує стабільну роботу  
✅ **Ефективність**: Швидкий пошук та доступ до даних

## 🔑 JWT токени та авторизація

### Автоматичне налаштування з .env файлу

Система автоматично налаштовує JWT токени та базові URL з `.env` файлу:

```bash
# Створіть .env файл на основі env_example.txt
cp env_example.txt .env

# Відредагуйте .env файл, вставивши ваші реальні ключі
nano .env
```

#### Обов'язкові змінні:

```env
# OpenAI API ключ
OPENAI_API_KEY=your_openai_api_key_here

# JWT токен (загальний або специфічний для API)
JWT_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your.token
JWT_SECRET_KEY=your_jwt_secret_key_here

# Базовий URL для API
API_BASE_URL=https://api.oneshop.click
```

#### Специфічні налаштування для API:

```env
# Специфічний JWT токен для конкретного API
JWT_TOKEN_ONESHOP=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.oneshop.token

# Специфічний базовий URL для API
API_BASE_URL_ONESHOP=https://api.oneshop.click

# Час життя токена (в секундах)
JWT_EXPIRES_IN=3600
```

### Перевірка налаштувань

```bash
# Перевірити статус системи та JWT токени
python cli.py status

# Показати детальну інформацію про токени
python cli.py info
```

### Ручне встановлення JWT токена

```bash
# Встановити JWT токен для конкретного API
python cli.py set-jwt-token oneshop "your.jwt.token"

# Встановити токен з часом життя
python cli.py set-jwt-token oneshop "your.jwt.token" 7200
```

### Виконання API запитів

```bash
# Виконати GET запит
python cli.py execute-request oneshop GET "/api/categories" "{}"

# Виконати POST запит з даними
python cli.py execute-request oneshop POST "/api/categories" '{"name": "Test", "slug": "test"}'

# Тестувати ендпоінт
python cli.py test-endpoint oneshop GET "/api/categories" "{}"
```

### Інтерактивне тестування API

```bash
# Запустити інтерактивне тестування
python cli.py api-testing

# Доступні команди в інтерактивному режимі:
# test <method> <path> [data] - тестувати ендпоінт
# set-token <api_name> <token> - встановити JWT токен
# history [api_name] - показати історію запитів
# endpoints [api_name] - показати доступні ендпоінти
# quit - вийти
```

### Історія запитів

```bash
# Показати історію всіх запитів
python cli.py request-history

# Показати історію для конкретного API
python cli.py request-history oneshop
```
