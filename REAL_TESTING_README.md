# 🧪 Реальне Тестування AI Swagger Bot

Цей документ описує, як запускати тести з реальними компонентами: PostgreSQL базою даних, pgvector та OpenAI API.

## 🗄️ Тестування з Реальною PostgreSQL Базою

### Запуск реальної бази даних

```bash
# Запуск PostgreSQL з pgvector
make docker-start-real-db

# Перевірка статусу
docker ps | grep postgres-real

# Логи бази
make docker-logs-real-db
```

### Структура реальної бази

База автоматично створює:
- **Схему**: `test_schema`
- **Таблиці**:
  - `test_embeddings` - для векторних embeddings
  - `test_documents` - для документів
  - `test_swagger_specs` - для Swagger специфікацій
  - `test_api_endpoints` - для API endpoints
  - `test_data_schemas` - для схем даних
- **Індекси**: GIN для тексту, IVFFlat для векторів
- **Функції**: пошук подібності, гібридний пошук

### Тестування RAG функціональності

```bash
# Запуск тестів з реальною базою
make docker-test-with-real-db

# Або вручну
docker-compose -f docker-compose.real-db.yml run --rm test-with-real-db \
  python -m pytest tests/test_rag_real_database.py -v -s
```

## 🤖 Тестування OpenAI Моделі

### Налаштування OpenAI API

```bash
# Встановлення змінних середовища
export OPENAI_API_KEY="your_actual_api_key"
export OPENAI_MODEL="gpt-4"  # або gpt-3.5-turbo

# Перевірка налаштувань
echo "API Key: $OPENAI_API_KEY"
echo "Model: $OPENAI_MODEL"
```

### Запуск тестів OpenAI

```bash
# Тести помилок моделі
make docker-test-openai-errors

# Або вручну
docker-compose -f docker-compose.test.yml run --rm test \
  python -m pytest tests/test_openai_model_errors.py -v -s
```

### Типи тестованих помилок

1. **API Key Validation** - валідація ключа
2. **Model Availability** - доступність моделі
3. **Token Limits** - обмеження токенів
4. **Rate Limiting** - обмеження швидкості
5. **Content Filtering** - фільтрація контенту
6. **Context Window** - обмеження контексту
7. **Function Calling** - помилки функцій
8. **Network Errors** - мережеві помилки

## 🏪 Тестування Clickone Shop API

### Реальні інтеграційні тести

```bash
# Тести з реальним JWT токеном
make docker-test-clickone-real

# Або вручну
docker-compose -f docker-compose.test.yml run --rm test \
  python -m pytest tests/test_clickone_shop_integration_real.py -v -s
```

### JWT Токен для тестування

Тести використовують реальний JWT токен для:
- Створення категорій
- Оновлення категорій
- Видалення категорій
- Тестування автентифікації

## 🔧 Налаштування Тестового Середовища

### Змінні середовища

```bash
# База даних
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=ai_swagger_bot_test
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# OpenAI
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4

# Python
PYTHONPATH=/app
TESTING=true
```

### Docker Compose файли

- `docker-compose.test.yml` - основне тестове середовище
- `docker-compose.real-db.yml` - середовище з реальною базою

## 📊 Аналіз Результатів Тестів

### Перевірка покриття

```bash
# Запуск з покриттям
docker-compose -f docker-compose.test.yml run --rm test \
  python -m pytest --cov=src --cov-report=html tests/

# Відкриття звіту
open htmlcov/index.html
```

### Аналіз помилок

Тести показують:
- **Реальні помилки моделі** - проблеми з OpenAI API
- **Проблеми бази даних** - помилки PostgreSQL/pgvector
- **Мережеві помилки** - проблеми з'єднання
- **Проблеми продуктивності** - повільні запити

## 🚀 Запуск Всіх Тестів

### Послідовність тестування

```bash
# 1. Запуск реальної бази
make docker-start-real-db

# 2. Базові тести
make docker-test-simple

# 3. Тести Clickone Shop API
make docker-test-clickone

# 4. Тести з реальною базою
make docker-test-with-real-db

# 5. Тести OpenAI помилок
make docker-test-openai-errors

# 6. Всі тести
make docker-test-all

# 7. Зупинка бази
make docker-stop-real-db
```

### Команди для розробки

```bash
# Швидке тестування
make docker-test-simple

# Тестування конкретного модуля
docker-compose -f docker-compose.test.yml run --rm test \
  python -m pytest tests/test_specific_module.py -v -s

# Тестування з детальним виводом
docker-compose -f docker-compose.test.yml run --rm test \
  python -m pytest -v -s --tb=long tests/
```

## ⚠️ Важливі Примітки

### Безпека

- **НЕ комітьте** реальні API ключі в Git
- Використовуйте `.env` файли для секретів
- Тестова база ізольована від продакшн

### Продуктивність

- Реальні тести можуть займати більше часу
- OpenAI API має обмеження швидкості
- pgvector індекси створюються автоматично

### Діагностика

```bash
# Перевірка статусу контейнерів
docker ps -a

# Логи конкретного сервісу
docker-compose -f docker-compose.real-db.yml logs postgres-real

# Підключення до бази
docker-compose -f docker-compose.real-db.yml exec postgres-real psql -U postgres -d ai_swagger_bot_test
```

## 🔍 Приклади Тестових Сценаріїв

### Тест RAG пошуку

```python
# Тестування пошуку подібних документів
def test_semantic_search():
    query = "API для створення категорій"
    results = rag_engine.search_similar(query, top_k=5)

    assert len(results) > 0
    assert any("категорій" in doc['text'] for doc in results)
```

### Тест OpenAI помилок

```python
# Тестування обмеження токенів
def test_token_limit():
    long_content = "text " * 10000

    try:
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": long_content}],
            max_tokens=5
        )
        assert False, "Очікувалася помилка обмеження токенів"
    except openai.BadRequestError as e:
        assert "token" in str(e).lower()
```

## 📈 Метрики Якості

### Покриття тестами

- **Unit тести**: ~80%
- **Інтеграційні тести**: ~60%
- **E2E тести**: ~40%
- **Загальне покриття**: ~65%

### Швидкість виконання

- **Базові тести**: 2-5 секунд
- **Тести з базою**: 10-30 секунд
- **OpenAI тести**: 30-120 секунд
- **Всі тести**: 2-5 хвилин

## 🆘 Вирішення Проблем

### Поширені помилки

1. **База не запускається**
   ```bash
   make docker-stop-real-db
   docker system prune -f
   make docker-start-real-db
   ```

2. **OpenAI API помилки**
   ```bash
   echo $OPENAI_API_KEY  # перевірте ключ
   export OPENAI_API_KEY="new_key"
   ```

3. **Проблеми з pgvector**
   ```bash
   docker-compose -f docker-compose.real-db.yml exec postgres-real \
     psql -U postgres -d ai_swagger_bot_test -c "CREATE EXTENSION IF NOT EXISTS vector;"
   ```

### Підтримка

- Перевірте логи: `make docker-logs-real-db`
- Перезапустіть сервіси: `make docker-stop-real-db && make docker-start-real-db`
- Очистіть Docker: `docker system prune -f`

---

**🎯 Мета**: Забезпечити надійне тестування всіх компонентів системи з реальними залежностями та виявлення справжніх помилок моделі.
