# Contributing to AI Swagger Bot 🤖

Дякуємо за інтерес до проекту AI Swagger Bot! Цей документ містить інструкції для контриб'юторів.

## 🚀 Початок роботи

### 1. Fork та Clone

```bash
# Fork репозиторію на GitHub
# Потім клонуйте ваш fork
git clone https://github.com/YOUR_USERNAME/ai-swagger-bot.git
cd ai-swagger-bot
```

### 2. Налаштування середовища розробки

```bash
# Створення віртуального середовища
python -m venv venv
source venv/bin/activate  # Linux/Mac
# або
venv\Scripts\activate     # Windows

# Встановлення залежностей
pip install -r requirements-dev.txt

# Встановлення pre-commit hooks
make pre-commit-install
```

### 3. Налаштування змінних середовища

```bash
cp env_example.txt .env
# Відредагуйте .env файл з вашими API ключами
```

## 🔧 Розробка

### Структура проекту

```
ai-swagger-bot/
├── src/                    # Основний код
├── tests/                  # Тести
├── examples/               # Приклади використання
├── docs/                   # Документація
├── scripts/                # Скрипти
└── .github/workflows/      # CI/CD workflows
```

### Команди для розробки

```bash
# Перевірка коду
make lint

# Форматування коду
make format

# Запуск тестів
make test

# Запуск тестів з покриттям
make test-coverage

# Перевірка безпеки
make security-check

# Запуск CI/CD локально
make ci

# Pre-commit перевірка
make pre-commit-run
```

### Стандарти коду

- **Python 3.11+** - мінімальна версія
- **Black** - форматування коду
- **isort** - сортування імпортів
- **ruff** - лінтер та форматтер
- **mypy** - типізація
- **pytest** - тестування

### Написання тестів

```python
# tests/test_example.py
import pytest
from src.example import ExampleClass

def test_example_function():
    """Тест для прикладу функції."""
    result = ExampleClass().example_function()
    assert result == "expected_value"

@pytest.mark.integration
def test_integration():
    """Інтеграційний тест."""
    # Тест код
    pass
```

## 📝 Pull Request Process

### 1. Створення feature branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Розробка

- Пишіть код згідно стандартів
- Додавайте тести для нової функціональності
- Оновлюйте документацію якщо потрібно

### 3. Перевірка перед PR

```bash
# Запуск всіх перевірок
make ci

# Або окремо
make lint
make test
make security-check
```

### 4. Створення Pull Request

- Використовуйте шаблон PR
- Додайте опис змін
- Вкажіть пов'язані issues
- Переконайтеся, що всі тести проходять

### 5. Code Review

- Відповідайте на коментарі ревьюера
- Вносьте необхідні зміни
- Перезапускайте тести після змін

## 🐛 Bug Reports

При звітуванні про помилки:

1. Використовуйте шаблон bug report
2. Надайте детальний опис проблеми
3. Включіть кроки для відтворення
4. Додайте логи та скріншоти якщо потрібно

## 💡 Feature Requests

При запиті нових функцій:

1. Використовуйте шаблон feature request
2. Опишіть проблему та рішення
3. Надайте приклади використання
4. Вкажіть acceptance criteria

## 📚 Документація

### Оновлення документації

- Документуйте нові функції
- Оновлюйте README.md якщо потрібно
- Додавайте приклади використання

### Структура документації

```
docs/
├── API_REFERENCE.md
├── DEPLOYMENT.md
├── DEVELOPMENT.md
└── USER_GUIDE.md
```

## 🔒 Security

### Звітування про вразливості

- Не створюйте публічні issues для security проблем
- Надішліть email на security@ai-swagger-bot.com
- Опишіть вразливість детально

## 🏷️ Versioning

Проект використовує [Semantic Versioning](https://semver.org/):

- **MAJOR** - несумісні зміни API
- **MINOR** - нова функціональність (зворотна сумісність)
- **PATCH** - виправлення помилок

## 📄 License

Контриб'ючи до проекту, ви погоджуєтеся, що ваші зміни будуть ліцензовані під MIT License.

## 🤝 Code of Conduct

Будь ласка, дотримуйтесь [Code of Conduct](CODE_OF_CONDUCT.md) при участі в проекті.

## 📞 Підтримка

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: team@ai-swagger-bot.com

Дякуємо за ваші контриб'юції! 🎉
