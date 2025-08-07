# Покращена система динамічних промптів

## 🎯 Огляд

Покращена система промптів додає нові можливості до базової системи:

- **Метадані промптів** - детальна інформація про кожен промпт
- **Реєстр промптів** - централізоване управління описів
- **Шаблони промптів** - створення промптів з готових шаблонів
- **Пропозиції промптів** - автоматичний підбір найкращих промптів
- **Експорт/імпорт** - збереження та відновлення конфігурації
- **Статистика** - детальна аналітика використання

## 🏗️ Архітектура

### Основні компоненти

```
src/
├── enhanced_prompt_manager.py    # Покращений менеджер промптів
├── prompt_descriptions.py        # Описи та метадані промптів
├── dynamic_prompt_manager.py     # Базовий менеджер (SQLite)
└── prompt_templates.py           # Статичні промпт-шаблони
```

### Класи та інтерфейси

#### `EnhancedPromptManager`
Розширений менеджер промптів з додатковими можливостями.

**Основні методи:**
- `add_enhanced_prompt()` - додавання промпту з метаданими
- `get_prompt_with_metadata()` - отримання промпту з метаданими
- `create_prompt_from_template()` - створення з шаблону
- `get_prompt_suggestions()` - пропозиції промптів
- `export_prompts_to_file()` - експорт в файл
- `import_prompts_from_file()` - імпорт з файлу

#### `PromptDescriptions`
Колекція описів промптів з метаданими.

**Основні методи:**
- `get_system_prompt_description()` - опис системного промпту
- `get_intent_analysis_description()` - опис аналізу наміру
- `get_error_handling_description()` - опис обробки помилок
- `get_all_descriptions()` - всі описи

#### `PromptRegistry`
Реєстр промптів з метаданими.

**Основні методи:**
- `register_custom_prompt()` - реєстрація кастомного промпту
- `get_prompt_description()` - отримання опису
- `get_prompt_metadata()` - метадані промпту

## 🚀 Швидкий старт

### 1. Базове використання

```python
from src.enhanced_prompt_manager import EnhancedPromptManager

# Створюємо менеджер
manager = EnhancedPromptManager()

# Додаємо промпт з метаданими
from src.prompt_descriptions import PromptDescriptions

desc = PromptDescriptions.get_system_prompt_description()
prompt = EnhancedPromptTemplate(
    name="My System Prompt",
    description=desc.description,
    prompt_text="Ти експерт API...",
    category=desc.category.value,
    tags=desc.tags
)

prompt_id = manager.add_enhanced_prompt(prompt)
```

### 2. Створення з шаблону

```python
# Створюємо промпт з готового шаблону
template_id = manager.create_prompt_from_template(
    "intent_analysis",
    name="Custom Intent Analysis",
    prompt_text="Ти експерт API. Аналізуй запит: {user_query}",
    tags=["custom", "intent"]
)
```

### 3. Отримання пропозицій

```python
# Отримуємо пропозиції промптів для запиту
suggestions = manager.get_prompt_suggestions("Покажи всі товари")

for suggestion in suggestions:
    print(f"Промпт: {suggestion['name']}")
    print(f"Релевантність: {suggestion['relevance_score']:.2f}")
```

## 📊 Метадані промптів

### Структура метаданих

```python
{
    "usage_count": 15,           # Кількість використань
    "success_rate": 0.85,        # Успішність (0-1)
    "created_at": "2024-01-01T12:00:00",
    "updated_at": "2024-01-15T14:30:00",
    "category": "data_retrieval",
    "tags": ["custom", "data"],
    "version": "1.0",
    "author": "system"
}
```

### Отримання метаданих

```python
# Отримуємо промпт з метаданими
enhanced_prompt = manager.get_prompt_with_metadata(prompt_id)
print(f"Метадані: {enhanced_prompt.metadata}")

# Отримуємо промпти за категорією з метаданими
prompts = manager.get_prompts_by_category_with_metadata("system")
for prompt in prompts:
    print(f"{prompt.name}: {prompt.metadata['usage_count']} використань")
```

## 🎯 Категорії промптів

### Система категорій

```python
from src.prompt_descriptions import PromptCategory

# Доступні категорії
categories = [
    PromptCategory.SYSTEM,              # Системні промпти
    PromptCategory.INTENT_ANALYSIS,     # Аналіз наміру
    PromptCategory.ERROR_HANDLING,      # Обробка помилок
    PromptCategory.RESPONSE_FORMATTING, # Форматування відповідей
    PromptCategory.DATA_RETRIEVAL,      # Отримання даних
    PromptCategory.DATA_CREATION,       # Створення даних
    PromptCategory.DATA_UPDATE,         # Оновлення даних
    PromptCategory.DATA_DELETION,       # Видалення даних
    PromptCategory.VALIDATION,          # Валідація
    PromptCategory.DEBUGGING,           # Налагодження
    PromptCategory.USER_DEFINED         # Користувацькі
]
```

### Автоматична класифікація

Система автоматично визначає категорію на основі запиту:

```python
# Приклади автоматичної класифікації
"Покажи всі товари" → DATA_RETRIEVAL
"Створи новий товар" → DATA_CREATION
"Онови товар з ID 123" → DATA_UPDATE
"Видали товар з ID 456" → DATA_DELETION
"Помилка при створенні" → ERROR_HANDLING
```

## 📈 Статистика та аналітика

### Детальна статистика

```python
stats = manager.get_prompt_statistics()

print(f"Загальна статистика:")
print(f"  • Всього промптів: {stats['total_prompts']}")
print(f"  • Активних промптів: {stats['active_prompts']}")
print(f"  • Середня успішність: {stats['avg_success_rate']:.2%}")

print(f"Статистика по категоріях:")
for category, cat_stats in stats['category_details'].items():
    if cat_stats['count'] > 0:
        print(f"  • {category}: {cat_stats['count']} промптів")
```

### Релевантність промптів

Система розраховує релевантність на основі:

1. **Успішність** (40%) - відсоток успішних використань
2. **Використання** (30%) - кількість використань (нормалізована)
3. **Схожість тексту** (30%) - семантична схожість з запитом

```python
# Приклад розрахунку релевантності
relevance_score = (
    prompt.success_rate * 0.4 +
    min(prompt.usage_count / 100.0, 1.0) * 0.3 +
    text_similarity * 0.3
)
```

## 💾 Експорт та імпорт

### Збереження конфігурації

```python
# Автоматичне збереження
manager.save_prompt_config()

# Експорт в JSON
manager.export_prompts_to_file("my_prompts.json", "json")

# Експорт в YAML
manager.export_prompts_to_file("my_prompts.yaml", "yaml")
```

### Відновлення конфігурації

```python
# Імпорт з JSON
manager.import_prompts_from_file("my_prompts.json", "json")

# Імпорт з YAML
manager.import_prompts_from_file("my_prompts.yaml", "yaml")
```

### Формат конфігурації

```json
{
  "prompts": [
    {
      "name": "Custom Prompt",
      "description": "Опис промпту",
      "prompt_text": "Текст промпту...",
      "category": "data_retrieval",
      "tags": ["custom", "data"],
      "metadata": {
        "usage_count": 10,
        "success_rate": 0.85,
        "created_at": "2024-01-01T12:00:00",
        "updated_at": "2024-01-15T14:30:00"
      }
    }
  ],
  "categories": {
    "data_retrieval": {
      "name": "data_retrieval",
      "description": "Промпти для data_retrieval",
      "prompt_count": 5,
      "tags": ["data", "retrieval"]
    }
  },
  "settings": {
    "default_category": {
      "value": "user_defined",
      "description": "Категорія за замовчуванням"
    }
  },
  "last_updated": "2024-01-15T15:00:00"
}
```

## 🔧 Інтеграція з існуючою системою

### Заміна базового менеджера

```python
# Було
from src.dynamic_prompt_manager import DynamicPromptManager
manager = DynamicPromptManager()

# Стало
from src.enhanced_prompt_manager import EnhancedPromptManager
manager = EnhancedPromptManager()
```

### Зворотна сумісність

Покращений менеджер повністю сумісний з базовим:

```python
# Всі методи базового менеджера працюють
prompt_id = manager.add_prompt(prompt)
prompt = manager.get_prompt(prompt_id)
prompts = manager.get_prompts_by_category("system")
```

### Додаткові можливості

```python
# Нові методи покращеного менеджера
enhanced_prompt = manager.get_prompt_with_metadata(prompt_id)
suggestions = manager.get_prompt_suggestions(user_query)
stats = manager.get_prompt_statistics()
manager.save_prompt_config()
```

## 🎯 Приклади використання

### Приклад 1: Створення кастомного промпту

```python
from src.enhanced_prompt_manager import EnhancedPromptManager, EnhancedPromptTemplate

manager = EnhancedPromptManager()

# Створюємо кастомний промпт
custom_prompt = EnhancedPromptTemplate(
    name="Custom Data Retrieval",
    description="Кастомний промпт для отримання даних",
    prompt_text="""
Ти експерт API. Користувач хоче отримати дані.

ЗАПИТ: {user_query}

ЗАВДАННЯ:
1. Знайди відповідний GET endpoint
2. Перевір параметри
3. Виконай запит
4. Поверни результат

ВІДПОВІДЬ:
{{
    "endpoint": "URL endpoint",
    "method": "GET",
    "parameters": {{}},
    "result": "результат запиту"
}}
    """,
    category="data_retrieval",
    tags=["custom", "data", "retrieval"]
)

prompt_id = manager.add_enhanced_prompt(custom_prompt)
print(f"✅ Додано промпт з ID: {prompt_id}")
```

### Приклад 2: Отримання пропозицій

```python
# Отримуємо пропозиції для різних запитів
queries = [
    "Покажи всі товари",
    "Створи новий товар",
    "Онови товар з ID 123",
    "Видали товар з ID 456"
]

for query in queries:
    suggestions = manager.get_prompt_suggestions(query)
    print(f"\n📝 Запит: {query}")
    print(f"🎯 Знайдено {len(suggestions)} пропозицій:")

    for i, suggestion in enumerate(suggestions[:3], 1):
        print(f"  {i}. {suggestion['name']}")
        print(f"     Релевантність: {suggestion['relevance_score']:.2f}")
        print(f"     Успішність: {suggestion['success_rate']:.2%}")
```

### Приклад 3: Робота з метаданими

```python
# Отримуємо промпт з метаданими
enhanced_prompt = manager.get_prompt_with_metadata(prompt_id)

if enhanced_prompt:
    print(f"📋 Промпт: {enhanced_prompt.name}")
    print(f"📊 Метадані:")
    print(f"  • Використання: {enhanced_prompt.metadata.get('usage_count', 0)}")
    print(f"  • Успішність: {enhanced_prompt.metadata.get('success_rate', 0):.2%}")
    print(f"  • Створено: {enhanced_prompt.metadata.get('created_at', 'Невідомо')}")
    print(f"  • Оновлено: {enhanced_prompt.metadata.get('updated_at', 'Невідомо')}")

# Отримуємо промпти за категорією з метаданими
system_prompts = manager.get_prompts_by_category_with_metadata("system")
print(f"\n🔧 Системних промптів: {len(system_prompts)}")

for prompt in system_prompts:
    usage = prompt.metadata.get('usage_count', 0)
    success = prompt.metadata.get('success_rate', 0)
    print(f"  • {prompt.name}: {usage} використань, {success:.2%} успішність")
```

### Приклад 4: Експорт та імпорт

```python
# Експортуємо поточну конфігурацію
manager.save_prompt_config()
manager.export_prompts_to_file("backup_prompts.json", "json")

# Створюємо новий менеджер
new_manager = EnhancedPromptManager("new_prompts.db")

# Імпортуємо конфігурацію
new_manager.import_prompts_from_file("backup_prompts.json", "json")

print("✅ Конфігурація експортована та імпортована")
```

## 🔮 Майбутні покращення

### Заплановані функції

1. **Машинне навчання**
   - Автоматичне покращення промптів
   - Кластеризація схожих запитів
   - A/B тестування промптів

2. **Розширена аналітика**
   - Графіки використання
   - Тренди успішності
   - Прогнозування ефективності

3. **Колaborative фільтрація**
   - Рекомендації на основі схожих користувачів
   - Спільне використання промптів
   - Рейтингова система

4. **Версіонування**
   - Відстеження змін промптів
   - Відкат до попередніх версій
   - Історія модифікацій

5. **API для зовнішніх систем**
   - REST API для управління промптами
   - Webhook для сповіщень
   - Інтеграція з зовнішніми системами

## 📝 Висновки

Покращена система промптів надає:

- **Кращу організацію** - метадані та категорії
- **Автоматизацію** - пропозиції та шаблони
- **Аналітику** - детальна статистика
- **Гнучкість** - експорт/імпорт конфігурації
- **Сумісність** - зворотна сумісність з базовою системою

Система готова для використання та подальшого розвитку.

---

**Автор:** AI Assistant
**Дата:** 2024
**Версія:** 2.0
**Статус:** ✅ Готово до використання
