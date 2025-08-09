# Міграція з хардкоду промптів на YAML

Цей документ описує процес міграції з хардкоду промптів в коді на використання YAML файлів.

## Проблема

Раніше промпти були хардкодовані в файлі `src/prompt_templates.py`, що створювало наступні проблеми:

1. **Дублювання**: Промпти дублювалися в коді та YAML файлах
2. **Складність редагування**: Для зміни промпту потрібно було редагувати код
3. **Відсутність версіонування**: Неможливо було відстежувати зміни промптів
4. **Складність локалізації**: Промпти були зашиті в код

## Рішення

Створено нову систему, яка використовує YAML файли як єдине джерело промптів:

### 1. Новий менеджер промптів

```python
from src.enhanced_prompt_manager import EnhancedPromptManager

# Ініціалізація
prompt_manager = EnhancedPromptManager()

# Використання
prompt = prompt_manager.get_intent_analysis_prompt(
    user_query="Покажи всі товари",
    context="Попередні запити..."
)
```

### 2. Структура YAML файлу

```yaml
# prompts/base_prompts.yaml
version: "1.0"
description: "Базові промпти для AI Swagger Bot"

prompts:
  system_base:
    name: "Системний промпт"
    description: "Базовий системний промпт для агента"
    category: "system"
    template: |
      Ти - експерт з API та Swagger/OpenAPI специфікаціями.
      Твоя задача - допомогти користувачам взаємодіяти з API через природну мову.
    tags: ["core", "system", "base"]
    is_active: true
    is_public: true
    priority: 1

  intent_analysis_base:
    name: "Аналіз наміру"
    description: "Промпт для аналізу наміру користувача"
    category: "intent_analysis"
    template: |
      Ти - експерт з API. Аналізуй запит користувача та визначай:
      1. Тип операції (GET, POST, PUT, DELETE)
      2. Ресурс або endpoint
      3. Параметри та дані
      4. Мета або ціль запиту

      Контекст попередніх взаємодій:
      {context}

      Запит користувача: {user_query}

      Відповідай у форматі JSON:
      {{
          "operation": "GET|POST|PUT|DELETE",
          "resource": "назва ресурсу",
          "parameters": {{"param1": "value1"}},
          "data": {{"field1": "value1"}},
          "intent": "опис мети запиту"
      }}
    tags: ["nlp", "intent", "analysis"]
    is_active: true
    is_public: true
    priority: 2
```

### 3. Переваги нової системи

#### ✅ Централізоване управління
- Всі промпти в одному YAML файлі
- Легко редагувати та версіонувати
- Підтримка Git для відстеження змін

#### ✅ Гнучкість
- Можна додавати нові промпти без зміни коду
- Підтримка різних категорій та тегів
- Можливість активувати/деактивувати промпти

#### ✅ Локалізація
- Легко створювати версії для різних мов
- Підтримка Unicode для української мови
- Можливість експорту/імпорту

#### ✅ Тестування
- Можна тестувати промпти окремо від коду
- A/B тестування різних версій промптів
- Метрики ефективності

## Міграція існуючого коду

### 1. Оновлення імпортів

```python
# Старий код
from .prompt_templates import PromptTemplates

# Новий код
from .enhanced_prompt_manager import EnhancedPromptManager
```

### 2. Оновлення використання

```python
# Старий код
prompt = PromptTemplates.get_intent_analysis_prompt(
    user_query=query,
    context=context
)

# Новий код
prompt_manager = EnhancedPromptManager()
prompt = prompt_manager.get_intent_analysis_prompt(
    user_query=query,
    context=context
)
```

### 3. Оновлення класів

```python
class InteractiveSwaggerAgent:
    def __init__(self, ...):
        # Додаємо менеджер промптів
        self.prompt_manager = EnhancedPromptManager()

    def _analyze_user_intent(self, user_query: str, context: str = ""):
        # Використовуємо новий менеджер
        prompt = self.prompt_manager.get_intent_analysis_prompt(
            user_query=user_query,
            context=context
        )
        # ... решта коду
```

## Структура YAML файлу

### Основні секції:

1. **Метадані**
   ```yaml
   version: "1.0"
   created_at: "2025-01-27T00:00:00Z"
   description: "Базові промпти для InteractiveSwaggerAgent"
   ```

2. **Налаштування**
   ```yaml
   settings:
     default_language: "uk"
     default_emoji: true
     default_formatting: "structured"
     auto_suggestions: true
   ```

3. **Категорії**
   ```yaml
   categories:
     system:
       name: "Системні промпти"
       description: "Базові промпти для системи"
       tags: ["core", "system", "base"]
   ```

4. **Промпти**
   ```yaml
   prompts:
     prompt_id:
       name: "Назва промпту"
       description: "Опис промпту"
       category: "category_name"
       template: |
         Шаблон промпту з {placeholders}
       tags: ["tag1", "tag2"]
       is_active: true
       is_public: true
       priority: 1
   ```

## Доступні методи

### Базові промпти:
- `get_system_prompt()` - системний промпт
- `get_intent_analysis_prompt()` - аналіз наміру
- `get_error_analysis_prompt()` - аналіз помилок
- `get_response_formatting_prompt()` - форматування відповіді

### Спеціалізовані промпти:
- `get_endpoint_search_prompt()` - пошук endpoints
- `get_request_formation_prompt()` - формування запиту
- `get_object_creation_prompt()` - створення об'єктів
- `get_optimization_prompt()` - оптимізація

### E-commerce промпти:
- `get_ecommerce_search_prompt()` - пошук товарів
- `get_content_creation_prompt()` - створення контенту
- `get_customer_support_prompt()` - підтримка клієнтів
- `get_order_management_prompt()` - управління замовленнями

### Універсальні методи:
- `get_prompt_by_name(prompt_name, **kwargs)` - отримання за назвою
- `get_available_prompts()` - список доступних промптів
- `reload_prompts()` - перезавантаження з файлу
- `get_prompt_statistics()` - статистика

## Приклади використання

### 1. Базове використання

```python
from src.enhanced_prompt_manager import EnhancedPromptManager

# Ініціалізація
prompt_manager = EnhancedPromptManager()

# Отримання промпту
prompt = prompt_manager.get_intent_analysis_prompt(
    user_query="Покажи всі товари",
    context="Попередні запити..."
)

print(prompt)
```

### 2. Динамічне отримання промпту

```python
# Отримання за назвою
prompt = prompt_manager.get_prompt_by_name(
    "custom_prompt",
    user_query="Запит",
    parameter="значення"
)
```

### 3. Статистика та моніторинг

```python
# Отримання статистики
stats = prompt_manager.get_prompt_statistics()
print(f"Всього промптів: {stats['total_prompts']}")
print(f"Активних промптів: {stats['active_prompts']}")

# Список доступних промптів
available = prompt_manager.get_available_prompts()
print(f"Доступні промпти: {available}")
```

## Тестування

### 1. Тестування промптів

```python
def test_prompt_formatting():
    prompt_manager = EnhancedPromptManager()

    prompt = prompt_manager.get_intent_analysis_prompt(
        user_query="Тестовий запит",
        context="Тестовий контекст"
    )

    assert "Тестовий запит" in prompt
    assert "Тестовий контекст" in prompt
```

### 2. Тестування YAML файлу

```python
import yaml

def test_yaml_structure():
    with open("prompts/base_prompts.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert "prompts" in data
    assert "categories" in data
    assert "settings" in data
```

## Міграційний план

### Етап 1: Підготовка
1. Створити YAML файл з існуючими промптами
2. Протестувати новий менеджер промптів
3. Оновити документацію

### Етап 2: Поступова міграція
1. Оновити один клас за раз
2. Замінити використання PromptTemplates
3. Протестувати функціональність

### Етап 3: Очищення
1. Видалити старий prompt_templates.py
2. Оновити всі імпорти
3. Фінальне тестування

### Етап 4: Оптимізація
1. Додати нові промпти в YAML
2. Налаштувати метрики
3. Оптимізувати продуктивність

## Переваги після міграції

### ✅ Для розробників:
- Легше редагувати промпти
- Кращий контроль версій
- Можливість A/B тестування

### ✅ Для користувачів:
- Більш точні відповіді
- Кращий користувацький досвід
- Швидші оновлення

### ✅ Для системи:
- Централізоване управління
- Краща масштабованість
- Легше тестування

## Висновок

Міграція з хардкоду промптів на YAML файли значно покращує:
- Гнучкість системи
- Зручність розробки
- Можливості тестування
- Масштабованість

Нова система дозволяє легко додавати, редагувати та тестувати промпти без зміни коду, що робить систему більш гнучкою та зручною для розробки.
