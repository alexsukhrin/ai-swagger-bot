# ⚙️ Конфігурація

Ця папка містить всі конфігураційні файли для AI Swagger Bot.

## 📁 Файли

### Python конфігурація
- **`.flake8`** - Налаштування Flake8 (лінтер)
- **`.isort.cfg`** - Налаштування isort (сортування імпортів)
- **`mypy.ini`** - Налаштування MyPy (типізація)
- **`pytest.ini`** - Налаштування pytest (тестування)
- **`pyproject.toml`** - Налаштування проекту (Poetry/Pip)
- **`requirements.txt`** - Python залежності
- **`requirements-dev.txt`** - Python залежності для розробки

### AI конфігурація
- **`prompt_config.json`** - Конфігурація AI промптів

## 🔧 Використання

### Встановлення залежностей
```bash
# Основні залежності
pip install -r config/requirements.txt

# Залежності для розробки
pip install -r config/requirements-dev.txt
```

### Лінтування коду
```bash
# Flake8
flake8 --config=config/.flake8

# isort
isort --settings-path=config/.isort.cfg

# MyPy
mypy --config-file=config/mypy.ini
```

### Тестування
```bash
# pytest
pytest --config=config/pytest.ini
```

## 💡 Призначення

Ці файли призначені для:
- Налаштування Python середовища
- Конфігурації інструментів розробки
- Управління залежностями
- Налаштування AI промптів

---

**🎯 Мета**: Централізоване зберігання всіх конфігураційних файлів проекту.
