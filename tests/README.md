# 🧪 Тести AI Swagger Bot

Ця папка містить всі тести для проекту AI Swagger Bot, організовані за модулями та функціональністю.

## 📁 Структура тестів

### 🔧 Базові тести
- `test_basic.py` - базові тести конфігурації та імпортів
- `test_config.py` - тести конфігурації проекту
- `test_mount.py` - тести монтів додатку

### 🚀 API тести
- `test_main_app.py` - тести основного FastAPI додатку
- `test_admin_filters.py` - тести адмін фільтрів
- `test_admin_ui.py` - тести адмін UI
- `test_database_integration.py` - інтеграційні тести бази даних
- `test_database_queries.py` - тести запитів до бази даних

### 🤖 AI та RAG тести
- `test_rag_simple.py` - прості тести RAG engine
- `test_rag.py` - повні тести RAG функціональності
- `test_embedding_relevance.py` - тести релевантності embedding
- `test_swagger_error_handler_simple.py` - тести обробки помилок

### 📝 Промпт тести
- `test_prompt_integration.py` - тести інтеграції промптів
- `test_prompt_agent_integration.py` - тести агента промптів
- `test_yaml_prompt_manager.py` - тести YAML менеджера промптів
- `test_user_prompt_isolation.py` - тести ізоляції промптів користувачів

### 🔗 Інтеграційні тести
- `test_production.py` - тести продакшн функціональності
- `test_production_jwt.py` - тести JWT авторизації
- `test_langchain.py` - тести LangChain компонентів
- `test_categories.py` - тести роботи з категоріями

### 🐳 Lambda тести
- `test_lambda_handler.py` - тести AWS Lambda handler

## 🚀 Запуск тестів

### Локально
```bash
# Всі тести
python -m pytest tests/ -v

# Конкретний тест
python -m pytest tests/test_basic.py -v

# Тести з маркерами
python -m pytest tests/ -v -m "not integration"
```

### Через Docker
```bash
# Прості тести
make docker-test-simple

# Всі тести
make docker-test-all

# Unit тести
make docker-test-unit

# Інтеграційні тести
make docker-test-integration
```

## 🏷️ Маркери тестів

- `@pytest.mark.integration` - інтеграційні тести
- `@pytest.mark.unit` - unit тести
- `@pytest.mark.slow` - повільні тести

## 📊 Покриття тестами

Для перегляду покриття коду тестами:
```bash
# Локально
python -m pytest tests/ --cov=src --cov-report=html

# Docker
make docker-test-all
```

## 🔧 Налаштування

### conftest.py
Містить загальну конфігурацію для всіх тестів:
- Налаштування Python path
- Змінні середовища для тестів
- Моки та фікстури

### pytest.ini
Конфігурація pytest:
- Мінімальна версія
- Маркери
- Шляхи до тестів

## 📝 Написання нових тестів

### Структура тесту
```python
"""
Опис тесту
"""
import pytest
from unittest.mock import Mock, patch


def test_functionality():
    """Опис тесту"""
    # Arrange
    expected = "expected_value"

    # Act
    result = function_under_test()

    # Assert
    assert result == expected
```

### Фікстури
```python
@pytest.fixture
def mock_dependency():
    """Мок для залежності"""
    with patch('module.dependency') as mock:
        mock.return_value = Mock()
        yield mock
```

### Обробка помилок
```python
def test_error_handling():
    """Тест обробки помилок"""
    try:
        from module import Class
        # Тест
    except ImportError as e:
        pytest.skip(f"Модуль не може бути імпортований: {e}")
```

## 🚨 Відомі проблеми

1. **Відносні імпорти** - деякі модулі мають проблеми з відносними імпортами
2. **База даних** - деякі тести потребують PostgreSQL з pgvector
3. **Залежності** - деякі тести потребують зовнішніх API ключів

## 📈 Статистика

- **Всього тестів:** 155+
- **Покриття:** ~13%
- **Статус:** В розробці

## 🤝 Внесок

При додаванні нових тестів:
1. Дотримуйтесь існуючої структури
2. Використовуйте описові назви
3. Додавайте докстрінги
4. Використовуйте моки для зовнішніх залежностей
5. Оновлюйте цей README
