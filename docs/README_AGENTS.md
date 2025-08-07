# AI Swagger Bot - Архітектура агентів

## 🤖 InteractiveSwaggerAgent (Основний агент)

**Файл:** `src/interactive_api_agent.py`

### Особливості:
- ✅ **Зберігає історію взаємодій** - зберігає всі запити та відповіді
- ✅ **Аналізує помилки сервера** - розуміє коли API повертає помилки
- ✅ **Генерує запити на додаткову інформацію** - якщо не вистачає даних
- ✅ **Підтримує діалог для виправлення помилок** - може повторно виконувати запити
- ✅ **Інтерактивний режим** - підтримує follow-up запити

### Основні методи:
```python
# Ініціалізація
agent = InteractiveSwaggerAgent(
    swagger_spec_path="examples/swagger_specs/shop_api.json",
    enable_api_calls=True,
    openai_api_key="your_key",
    jwt_token="your_token"
)

# Обробка запиту
response = agent.process_interactive_query("Створи категорію")
print(response['response'])  # Відповідь
print(response['status'])    # Статус (success, error, needs_followup)

# Додатковий запит (якщо потрібно)
if response['needs_followup']:
    followup = agent.process_followup_query("Назва: Електроніка")
```

### Використання в додатках:
- `enhanced_chat_app.py` - основний Streamlit інтерфейс
- `examples/basic_usage.py` - приклади використання
- `scripts/quick_start.py` - демонстрація функціональності

## 📁 Структура файлів

### Основні компоненти:
- `src/interactive_api_agent.py` - **InteractiveSwaggerAgent** (основний)
- `src/enhanced_swagger_parser.py` - парсер Swagger файлів
- `src/rag_engine.py` - RAG двигун для пошуку endpoints
- `src/dynamic_prompt_manager.py` - управління промптами
- `src/swagger_error_handler.py` - обробка помилок Swagger
- `src/swagger_validation_prompt.py` - валідація Swagger
- `src/prompt_templates.py` - шаблони промптів

### Допоміжні файли:
- `src/config.py` - конфігурація
- `src/__init__.py` - ініціалізація пакету

## 🗑️ Видалені агенти

### EnhancedSwaggerAgent (видалено)
- **Було в:** `src/enhanced_api_agent.py`
- **Причина видалення:** застарілий, менш функціональний
- **Замінений на:** InteractiveSwaggerAgent

### SimpleSwaggerAgent (видалено)
- **Було в:** тестах (не існував як окремий файл)
- **Причина видалення:** застарілий, простий функціонал
- **Замінений на:** InteractiveSwaggerAgent

## 🔄 Міграція зі старих агентів

### Було:
```python
from src.enhanced_api_agent import EnhancedSwaggerAgent
agent = EnhancedSwaggerAgent("swagger.json")
response = agent.process_query("запит")
```

### Стало:
```python
from src.interactive_api_agent import InteractiveSwaggerAgent
agent = InteractiveSwaggerAgent("swagger.json")
response = agent.process_interactive_query("запит")
print(response['response'])  # Відповідь
print(response['status'])    # Статус
```

## 🧪 Тестування

### Запуск тестів:
```bash
# Тест основного агента
python tests/test_agents_comparison.py

# Тест з продакшн сервером
python tests/test_production.py

# Тест з JWT автентифікацією
python tests/test_production_jwt.py
```

### Приклади використання:
```bash
# Базовий приклад
python examples/basic_usage.py

# Швидкий старт
python scripts/quick_start.py

# Streamlit інтерфейс
streamlit run enhanced_chat_app.py
```

## 📊 Порівняння функціональності

| Функція | InteractiveSwaggerAgent |
|---------|------------------------|
| Збереження історії | ✅ |
| Аналіз помилок сервера | ✅ |
| Діалог для виправлення | ✅ |
| Follow-up запити | ✅ |
| Валідація даних | ✅ |
| RAG пошук endpoints | ✅ |
| JWT автентифікація | ✅ |

## 🎯 Рекомендації

1. **Використовуйте InteractiveSwaggerAgent** для всіх нових проектів
2. **Оновіть існуючі коди** з `process_query()` на `process_interactive_query()`
3. **Перевіряйте статус відповіді** через `response['status']`
4. **Використовуйте follow-up запити** для покращення результатів

## 🔧 Налаштування

### Змінні середовища:
```bash
export OPENAI_API_KEY="your_openai_key"
export JWT_TOKEN="your_jwt_token"
```

### Конфігурація:
```python
# В src/config.py
Config.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
Config.JWT_TOKEN = os.getenv('JWT_TOKEN')
Config.CHROMA_DB_PATH = "./temp_chroma_db"
```
