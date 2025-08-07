# Налаштування середовища для AI Swagger Bot

## 🔧 Налаштування змінних середовища

### 1. Створення .env файлу

Скопіюйте файл `.env.example` як `.env`:

```bash
cp .env.example .env
```

### 2. Заповнення .env файлу

Відредагуйте файл `.env` та додайте свої ключі:

```bash
# OpenAI API ключ (обов'язково)
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# JWT токен для авторизації (опціонально)
JWT_TOKEN=your-jwt-token-here

# Налаштування бази даних
CHROMA_DB_PATH=./temp_chroma_db

# Налаштування сервера
API_BASE_URL=http://localhost:3030/api

# Налаштування логування
LOG_LEVEL=INFO
```

### 3. Отримання OpenAI API ключа

1. Перейдіть на [OpenAI Platform](https://platform.openai.com/)
2. Увійдіть або створіть акаунт
3. Перейдіть в розділ "API Keys"
4. Створіть новий ключ
5. Скопіюйте ключ та додайте в `.env` файл

### 4. Отримання JWT токена (опціонально)

Якщо ваш API потребує авторизації:

1. Отримайте JWT токен від вашого API сервера
2. Додайте токен в `.env` файл

## 🚀 Запуск додатків

### Перевірка налаштувань

```bash
# Перевірка середовища
python scripts/quick_start.py

# Тест основного агента
python tests/test_agents_comparison.py
```

### Запуск Streamlit додатку

```bash
# Основний чат-інтерфейс
streamlit run enhanced_chat_app.py

# Або через скрипт
./run_enhanced_chat.sh
```

### Приклади використання

```bash
# Базовий приклад
python examples/basic_usage.py

# Тест з продакшн сервером
python tests/test_production.py
```

## 🔒 Безпека

### ⚠️ Важливо:

1. **Ніколи не комітьте .env файл** в Git
2. **Не додавайте API ключі** в код
3. **Використовуйте .env файл** для зберігання секретів
4. **Додайте .env в .gitignore** (вже додано)

### Перевірка безпеки

```bash
# Перевірка наявності хардкодованих ключів
grep -r "sk-" . --exclude-dir=.git --exclude-dir=__pycache__

# Перевірка наявності JWT токенів
grep -r "eyJ" . --exclude-dir=.git --exclude-dir=__pycache__
```

## 📁 Структура файлів

```
ai-swagger-bot/
├── .env.example          # Приклад налаштувань
├── .env                  # Ваші налаштування (не комітиться)
├── enhanced_chat_app.py  # Основний додаток
├── examples/
│   └── basic_usage.py   # Приклад використання
├── scripts/
│   └── quick_start.py   # Швидкий старт
└── tests/
    └── test_agents_comparison.py  # Тести
```

## 🔧 Вирішення проблем

### Проблема: "OPENAI_API_KEY не знайдено"

**Рішення:**
1. Перевірте, чи існує файл `.env`
2. Перевірте, чи правильно заповнений API ключ
3. Перезапустіть додаток

```bash
# Перевірка змінних середовища
echo $OPENAI_API_KEY

# Перевірка .env файлу
cat .env
```

### Проблема: "ModuleNotFoundError: No module named 'dotenv'"

**Рішення:**
```bash
pip install python-dotenv
```

### Проблема: "ImportError: No module named 'langchain'"

**Рішення:**
```bash
conda activate ai-swagger
pip install langchain langchain-openai
```

## 📋 Перевірка готовності

```bash
# 1. Перевірка Python
python --version

# 2. Перевірка conda середовища
conda info --envs

# 3. Перевірка залежностей
python scripts/check_dependencies.py

# 4. Перевірка налаштувань
python examples/basic_usage.py
```

## 🎯 Готово!

Після налаштування ви можете:

- ✅ Запускати чат-інтерфейс
- ✅ Використовувати InteractiveSwaggerAgent
- ✅ Тестувати з різними Swagger файлами
- ✅ Працювати з API через діалог
