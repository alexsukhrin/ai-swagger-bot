# 🤖 AI Error Handler - Автоматичне виправлення помилок API

## 📋 Опис

AI Error Handler - це інтелектуальна система, яка автоматично аналізує помилки API та пропонує їх виправлення за допомогою штучного інтелекту (GPT-4). Система спілкується з користувачем українською мовою та надає зрозумілі пояснення та конкретні рішення.

## ✨ Основні можливості

### 🔍 **Автоматичний аналіз помилок**
- Аналізує помилки API в реальному часі
- Визначає причину помилки
- Пропонує конкретні виправлення

### 🛠️ **Автоматичне виправлення**
- Виправляє дані відповідно до правил валідації
- Пропонує альтернативні варіанти
- Автоматично повторює запит з виправленими даними

### 💬 **Людська комунікація**
- Пояснення українською мовою
- Конкретні поради та рекомендації
- Зрозумілі приклади виправлень

### 🗂️ **Кешування та оптимізація**
- Кешує помилки для швидшого відгуку
- Статистика оброблених помилок
- Оптимізація повторних запитів

## 🚀 Швидкий старт

### 1. Налаштування змінних середовища

Створіть `.env` файл:

```bash
# OpenAI API ключ
OPENAI_API_KEY=your_openai_api_key_here

# Модель OpenAI (за замовчуванням gpt-4)
OPENAI_MODEL=gpt-4

# JWT токен для Clickone Shop API (опціонально)
CLICKONE_JWT_TOKEN=your_jwt_token_here
```

### 2. Використання в коді

```python
from src.clickone_shop_agent import ClickoneShopAgent
from src.ai_error_handler import get_ai_error_handler

# Створюємо агент
agent = ClickoneShopAgent()

# Встановлюємо JWT токен (якщо потрібно)
agent.set_jwt_token("your_jwt_token")

# Спробуємо створити категорію з помилкою
invalid_data = {
    "name": "Test Category 123",  # Містить числа
    "slug": "test-category-123"
}

response = agent.create_category(invalid_data)

if not response.success:
    print("❌ Помилка API:")
    print(response.error)  # Зрозуміле пояснення українською мовою

    # Автоматично виправляємо та повторюємо
    retry_response = agent.retry_with_ai_fix(response)

    if retry_response.success:
        print("✅ AI успішно виправив помилку!")
        print(f"Результат: {retry_response.data}")
```

### 3. CLI Демо

Запустіть інтерактивне демо:

```bash
python src/ai_error_demo.py
```

## 🔧 API Методи

### ClickoneShopAgent

#### `create_category(data)`
Створює категорію з автоматичною обробкою помилок.

#### `retry_with_ai_fix(response)`
Автоматично виправляє помилку та повторює запит.

#### `get_ai_error_analysis(error_message, input_data)`
Отримує аналіз помилки від AI.

#### `get_validation_rules(entity_type)`
Отримує правила валідації від AI.

### AIErrorHandler

#### `analyze_api_error(error)`
Аналізує помилку API та пропонує виправлення.

#### `get_user_friendly_message(error, fix)`
Створює зрозуміле повідомлення для користувача.

#### `suggest_retry_with_fix(error, fix)`
Пропонує спробувати знову з виправленими даними.

## 📝 Приклади використання

### Приклад 1: Автоматичне виправлення назви категорії

```python
# Неправильні дані
invalid_data = {
    "name": "Test Category 123",  # Містить числа
    "slug": "test-category-123"
}

response = agent.create_category(invalid_data)

# AI автоматично виправить:
# "Test Category 123" → "Test Category"
# "test-category-123" → "test-category"
```

### Приклад 2: Отримання правил валідації

```python
# Отримуємо правила від AI
rules = agent.get_validation_rules("category")
print(rules)

# Вивід:
# 1. Назва категорії: Це поле повинне бути обов'язковим і містити від 2 до 255 символів...
# 2. Slug (URL-підручний ідентифікатор): Slug - це URL-підручний ідентифікатор...
```

### Приклад 3: Аналіз конкретної помилки

```python
error_message = "Slug must be unique"
input_data = {"name": "Test", "slug": "existing-slug"}

analysis = agent.get_ai_error_analysis(error_message, input_data)
print(analysis)

# Вивід:
# 🚨 **Помилка API**
# **Ендпоінт:** POST /api/categories
# **Код помилки:** 400
#
# **Що сталося:**
# Slug 'existing-slug' вже існує в системі...
```

## 🧪 Тестування

### Запуск тестів

```bash
# Всі тести
docker-compose -f docker-compose.real-db.yml run --rm test-with-real-db python -m pytest tests/ -v

# Тільки AI Error Handler тести
docker-compose -f docker-compose.real-db.yml run --rm test-with-real-db python -m pytest tests/test_ai_error_handler_integration.py -v -s

# Тести з реальним API
docker-compose -f docker-compose.real-db.yml run --rm test-with-real-db python -m pytest tests/test_ai_error_handler_integration.py::TestRealAPIErrorHandling -v -s
```

### Тестування з реальним API

Для тестування з реальним API потрібно:

1. Встановити `OPENAI_API_KEY` в `.env`
2. Встановити `CLICKONE_JWT_TOKEN` в `.env`
3. Запустити тести з маркером `@pytest.mark.integration`

## 🔍 Як це працює

### 1. **Перехоплення помилки**
Коли API повертає помилку, система автоматично створює об'єкт `APIError`.

### 2. **AI аналіз**
Помилка відправляється в GPT-4 для аналізу та отримання виправлення.

### 3. **Створення відповіді**
AI створює зрозуміле пояснення українською мовою та пропонує виправлення.

### 4. **Автоматичне виправлення**
Система може автоматично виправити дані та повторити запит.

### 5. **Кешування**
Результати аналізу зберігаються в кеші для швидшого відгуку.

## 📊 Статистика та моніторинг

### Кеш помилок

```python
# Отримати статистику
stats = agent.ai_error_handler.get_cache_stats()
print(f"Загальна кількість помилок: {stats['total_errors']}")
print(f"Розмір кешу: {stats['cache_size']} символів")
print(f"Модель AI: {stats['model']}")

# Очистити кеш
agent.ai_error_handler.clear_cache()
```

### Логування

Система автоматично логує:
- Аналізовані помилки
- AI відповіді
- Успішні виправлення
- Статистику кешу

## 🚨 Обмеження та вимоги

### Вимоги
- Python 3.9+
- OpenAI API ключ
- Інтернет з'єднання для OpenAI API

### Обмеження
- Залежність від OpenAI API
- Можливі затримки при аналізі помилок
- Обмежена точність для складних помилок

## 🔮 Майбутні покращення

### Заплановані функції
- [ ] Підтримка інших AI моделей
- [ ] Локальне кешування виправлень
- [ ] Машинне навчання на основі історії помилок
- [ ] Інтеграція з системами моніторингу
- [ ] Автоматичне створення тестів на основі помилок

### Розширення
- [ ] Підтримка інших типів API
- [ ] Багатомовна підтримка
- [ ] Інтеграція з CI/CD пайплайнами
- [ ] Веб-інтерфейс для моніторингу

## 🤝 Внесок

Для внесення змін:

1. Форкніть репозиторій
2. Створіть feature branch
3. Внесіть зміни
4. Додайте тести
5. Створіть Pull Request

## 📄 Ліцензія

Цей проект розповсюджується під MIT ліцензією.

## 📞 Підтримка

Якщо у вас є питання або проблеми:

1. Перевірте документацію
2. Запустіть тести
3. Створіть Issue в репозиторії
4. Зверніться до команди розробки

---

**AI Error Handler** - робимо API помилки зрозумілими та автоматично виправленими! 🚀
