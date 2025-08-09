# 🎯 YAML Система Промптів для AI Swagger Bot

## 📋 Огляд

Нова система промптів дозволяє організувати всі промпти в YAML файлі та додавати кастомні промпти через API. Це забезпечує:

- **Централізоване управління** - всі базові промпти в одному YAML файлі
- **Динамічні кастомні промпти** - можливість додавати власні промпти через API
- **Гнучкість** - легке редагування та налаштування промптів
- **Масштабованість** - просте додавання нових промптів

## 🏗️ Архітектура

### Структура файлів

```
prompts/
├── base_prompts.yaml          # Базові промпти (завантажуються при старті)
└── custom_prompts.yaml        # Кастомні промпти (опціонально)

src/
├── yaml_prompt_manager.py     # Менеджер YAML промптів
└── enhanced_prompt_manager.py # Покращений менеджер (застарілий)

api/
├── prompts.py                 # API endpoints для промптів
└── main.py                   # Головний API (підключення роутера)
```

### Основні компоненти

#### `YAMLPromptManager`
Центральний менеджер для роботи з YAML промптами.

**Основні функції:**
- Завантаження базових промптів з YAML файлу
- Додавання/оновлення/видалення кастомних промптів
- Пошук та фільтрація промптів
- Форматування промптів з параметрами
- Експорт/імпорт промптів

#### `PromptTemplate`
Клас для представлення промпт-шаблону.

**Поля:**
- `id` - унікальний ідентифікатор
- `name` - назва промпту
- `description` - опис промпту
- `template` - шаблон промпту
- `category` - категорія промпту
- `tags` - теги для пошуку
- `is_active` - чи активний промпт
- `is_public` - чи публічний промпт
- `priority` - пріоритет промпту
- `source` - джерело промпту ("yaml", "api", "database")

## 📝 YAML Структура

### Базовий формат

```yaml
version: "1.0"
created_at: "2025-01-27T00:00:00Z"
description: "Базові промпти для InteractiveSwaggerAgent"

# Налаштування за замовчуванням
settings:
  default_language: "uk"
  default_emoji: true
  default_formatting: "structured"
  auto_suggestions: true

# Категорії промптів
categories:
  system:
    name: "Системні промпти"
    description: "Базові промпти для системи"
    tags: ["core", "system", "base"]

# Базові промпти
prompts:
  system_base:
    name: "Системний промпт"
    description: "Загальний системний промпт для агента"
    category: "system"
    template: |
      Ти - експерт з API та Swagger/OpenAPI специфікаціями...
    tags: ["core", "system", "base"]
    is_active: true
    is_public: true
    priority: 1

# Константи для емодзі
emoji_constants:
  SUCCESS: "✅"
  ERROR: "❌"
  WARNING: "⚠️"
```

### Категорії промптів

1. **system** - Системні промпти
2. **intent_analysis** - Аналіз наміру
3. **error_handling** - Обробка помилок
4. **response_formatting** - Форматування відповідей
5. **data_creation** - Створення даних
6. **data_retrieval** - Отримання даних
7. **validation** - Валідація
8. **debugging** - Налагодження
9. **optimization** - Оптимізація
10. **user_defined** - Кастомні промпти

## 🔧 API Endpoints

### Отримання промптів

```http
GET /prompts/
GET /prompts/?category=system
GET /prompts/?search=створення
GET /prompts/{prompt_id}
```

### Створення кастомного промпту

```http
POST /prompts/
Content-Type: application/json

{
  "name": "Мій кастомний промпт",
  "description": "Опис промпту",
  "template": "Ти експерт з API. {user_query}",
  "category": "user_defined",
  "is_public": false
}
```

### Оновлення промпту

```http
PUT /prompts/{prompt_id}
Content-Type: application/json

{
  "name": "Оновлена назва",
  "description": "Оновлений опис",
  "template": "Оновлений шаблон",
  "category": "system",
  "is_public": true
}
```

### Видалення промпту

```http
DELETE /prompts/{prompt_id}
```

### Пошук та пропозиції

```http
GET /prompts/search?query=створення&category=data_creation
GET /prompts/suggestions?query=Створи нову категорію
```

### Форматування промпту

```http
POST /prompts/format
Content-Type: application/json

{
  "prompt_id": "system_base",
  "parameters": {
    "user_query": "Покажи всі категорії",
    "context": "Попередній контекст"
  }
}
```

### Експорт/імпорт

```http
POST /prompts/export?include_custom=true
POST /prompts/import?file_path=prompts/import.yaml&overwrite=false
POST /prompts/reload
```

## 💻 Використання в коді

### Ініціалізація менеджера

```python
from src.yaml_prompt_manager import YAMLPromptManager

# Створюємо менеджер
manager = YAMLPromptManager("prompts/base_prompts.yaml")

# Отримуємо промпт
prompt = manager.get_prompt("system_base")

# Форматуємо промпт
formatted = manager.format_prompt("intent_analysis_base",
                                user_query="Створи категорію",
                                context="Попередній контекст")
```

### Додавання кастомного промпту

```python
# Дані промпту
prompt_data = {
    "name": "Мій кастомний промпт",
    "description": "Опис промпту",
    "template": "Ти експерт з API. {user_query}",
    "category": "user_defined",
    "tags": ["custom", "api"],
    "is_active": True,
    "is_public": False,
    "priority": 100
}

# Додаємо промпт
prompt_id = manager.add_custom_prompt(prompt_data, user_id="user123")
```

### Пошук промптів

```python
# Пошук за запитом
results = manager.search_prompts("створення", category="data_creation")

# Пропозиції для запиту
suggestions = manager.get_prompt_suggestions("Створи нову категорію")
```

### Статистика

```python
# Отримуємо статистику
stats = manager.get_statistics()
print(f"Всього промптів: {stats['total_prompts']}")
print(f"Активних промптів: {stats['active_prompts']}")
print(f"Категорії: {stats['categories']}")
```

## 🔄 Міграція з старої системи

### Крок 1: Створення YAML файлу

```bash
# Створюємо директорію для промптів
mkdir -p prompts

# Копіюємо базові промпти
cp prompts/base_prompts.yaml prompts/
```

### Крок 2: Оновлення коду

```python
# Замість старого менеджера
# from src.enhanced_prompt_manager import EnhancedPromptManager
# manager = EnhancedPromptManager()

# Використовуємо новий менеджер
from src.yaml_prompt_manager import YAMLPromptManager
manager = YAMLPromptManager("prompts/base_prompts.yaml")
```

### Крок 3: Оновлення API

```python
# В api/main.py додаємо
from .prompts import router as prompts_router
app.include_router(prompts_router)
```

## 📊 Переваги нової системи

### ✅ Покращення

1. **Централізоване управління** - всі промпти в одному YAML файлі
2. **Легке редагування** - можна редагувати YAML файл без перезапуску
3. **Версіонування** - YAML файли можна версіонувати в Git
4. **API для кастомних промптів** - користувачі можуть додавати свої промпти
5. **Пошук та фільтрація** - зручний пошук промптів
6. **Експорт/імпорт** - можна експортувати та імпортувати промпти
7. **Статистика** - детальна статистика використання промптів

### 🔧 Технічні переваги

1. **Типізація** - використання dataclass для типізації
2. **Валідація** - автоматична валідація YAML структури
3. **Помилки** - детальні повідомлення про помилки
4. **Логування** - детальне логування операцій
5. **Тестування** - легке тестування промптів

## 🚀 Швидкий старт

### 1. Створення базового YAML файлу

```yaml
# prompts/base_prompts.yaml
version: "1.0"
description: "Базові промпти"

categories:
  system:
    name: "Системні промпти"
    description: "Базові промпти для системи"
    tags: ["core", "system"]

prompts:
  system_base:
    name: "Системний промпт"
    description: "Загальний системний промпт"
    category: "system"
    template: |
      Ти - експерт з API. {user_query}
    tags: ["core", "system"]
    is_active: true
    is_public: true
    priority: 1
```

### 2. Ініціалізація в коді

```python
from src.yaml_prompt_manager import YAMLPromptManager

# Створюємо менеджер
manager = YAMLPromptManager("prompts/base_prompts.yaml")

# Використовуємо промпт
formatted = manager.format_prompt("system_base", user_query="Покажи категорії")
```

### 3. Додавання API endpoints

```python
# В api/main.py
from .prompts import router as prompts_router
app.include_router(prompts_router)
```

## 📝 Приклади використання

### Створення промпту для створення об'єктів

```yaml
object_creation_custom:
  name: "Створення об'єктів (кастомний)"
  description: "Промпт для створення об'єктів з автоматичним заповненням"
  category: "data_creation"
  template: |
    Ти - експерт з створення об'єктів через API.

    Запит користувача: {user_query}
    Тип створення: {creation_type}

    Правила:
    1. Автоматично заповнюй обов'язкові поля
    2. Використовуй контекст для кращого розуміння
    3. Генеруй реалістичні значення

    Створи дружелюбну відповідь українською мовою.
  tags: ["creation", "objects", "auto_fill"]
  is_active: true
  is_public: true
  priority: 5
```

### Створення промпту для обробки помилок

```yaml
error_handling_custom:
  name: "Обробка помилок (кастомний)"
  description: "Промпт для детального аналізу помилок"
  category: "error_handling"
  template: |
    Проаналізуй помилку та надай корисну інформацію.

    Помилка: {error_message}
    Запит: {user_query}
    API запит: {api_request}

    Типи помилок:
    - Валідація: потрібні додаткові поля
    - Авторизація: проблеми з токеном
    - Не знайдено: неправильний ID
    - Конфлікт: запис вже існує

    Створи зрозуміле пояснення українською мовою.
  tags: ["error", "debugging", "user_friendly"]
  is_active: true
  is_public: true
  priority: 3
```

## 🔍 Діагностика

### Перевірка завантаження промптів

```python
# Перевіряємо статистику
stats = manager.get_statistics()
print(f"Завантажено промптів: {stats['total_prompts']}")

# Перевіряємо категорії
for category, count in stats['categories'].items():
    print(f"{category}: {count} промптів")
```

### Перевірка форматування

```python
# Тестуємо форматування
try:
    formatted = manager.format_prompt("system_base", user_query="тест")
    print("✅ Форматування працює")
except Exception as e:
    print(f"❌ Помилка форматування: {e}")
```

### Перевірка API

```bash
# Тестуємо API endpoints
curl -X GET "http://localhost:8000/prompts/"
curl -X GET "http://localhost:8000/prompts/statistics"
curl -X GET "http://localhost:8000/prompts/categories"
```

## 🎯 Висновок

Нова YAML система промптів забезпечує:

1. **Централізоване управління** - всі промпти в одному місці
2. **Гнучкість** - легке додавання та редагування промптів
3. **API інтеграція** - можливість додавати кастомні промпти
4. **Масштабованість** - просте розширення системи
5. **Зручність** - інтуїтивний інтерфейс для роботи з промптами

Це значно покращує організацію та управління промптами в AI Swagger Bot проекті.
