# 🤖 CLI Тестер для AI Swagger Bot API

CLI інтерфейс для тестування всіх функцій AI Swagger Bot API без авторизації через Swagger UI.

## 📋 Зміст

- [Встановлення](#-встановлення)
- [Швидкий старт](#-швидкий-старт)
- [Команди CLI](#-команди-cli)
- [Інтерактивний режим](#-інтерактивний-режим)
- [Приклади використання](#-приклади-використання)
- [Тroubleshooting](#-troubleshooting)

## 🚀 Встановлення

### Залежності

```bash
pip install requests
```

### Запуск API сервера

```bash
# Запуск API сервера
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## ⚡ Швидкий старт

### 1. Інтерактивний режим (рекомендовано)

```bash
python interactive_cli.py
```

### 2. Командний режим

```bash
# Перевірка стану сервісу
python cli_tester.py health

# Створення демо користувача
python cli_tester.py demo-user

# Завантаження Swagger файлу
python cli_tester.py upload-swagger --file examples/swagger_specs/shop_api.json

# Чат з AI
python cli_tester.py chat --message "Покажи всі доступні endpoints"
```

## 📝 Команди CLI

### 🏥 Health Check

```bash
python cli_tester.py health
```

**Відповідь:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "database": "healthy",
  "active_users": 5,
  "swagger_specs_count": 10
}
```

### 👤 Демо користувач

```bash
python cli_tester.py demo-user
```

**Відповідь:**
```json
{
  "user": {
    "id": "uuid",
    "email": "demo@example.com",
    "username": "demo_user"
  },
  "token": "jwt_token_here"
}
```

### 📁 Завантаження Swagger

```bash
python cli_tester.py upload-swagger --file path/to/swagger.json
```

**Відповідь:**
```json
{
  "swagger_id": "uuid",
  "message": "Swagger специфікація успішно завантажена",
  "endpoints_count": 25
}
```

### 💬 Чат з AI

```bash
python cli_tester.py chat --message "Покажи всі доступні endpoints"
```

**Відповідь:**
```json
{
  "response": "Ось список доступних endpoints...",
  "user_id": "user-uuid",
  "timestamp": "2024-01-01T12:00:00",
  "swagger_id": "swagger-uuid"
}
```

### 📜 Історія чату

```bash
python cli_tester.py chat-history
```

### 📝 Промпти

```bash
# Всі промпти
python cli_tester.py prompts

# Промпти за категорією
python cli_tester.py prompts --category system

# Пошук промптів
python cli_tester.py prompts --search "створення"
```

### 📂 Категорії промптів

```bash
python cli_tester.py prompt-categories
```

### 📊 Статистика промптів

```bash
python cli_tester.py prompt-statistics
```

### 📋 Swagger специфікації

```bash
python cli_tester.py swagger-specs
```

### 👤 Інформація про користувача

```bash
python cli_tester.py user-info
```

### ✨ Створення кастомного промпту

```bash
python cli_tester.py create-prompt \
  --name "Мій промпт" \
  --description "Опис промпту" \
  --template "Ти експерт з API. {user_query}" \
  --category user_defined
```

### 🔍 Пошук промптів

```bash
python cli_tester.py search-prompts --query "створення"
```

### 💡 Пропозиції промптів

```bash
python cli_tester.py prompt-suggestions --query "Створи нову категорію"
```

### 🔧 Форматування промпту

```bash
python cli_tester.py format-prompt \
  --prompt-id "system_base" \
  --parameters '{"user_query": "Покажи endpoints"}'
```

### 📤 Експорт промптів

```bash
python cli_tester.py export-prompts --include-custom
```

### 🔄 Перезавантаження промптів

```bash
python cli_tester.py reload-prompts
```

### 📊 Статус

```bash
python cli_tester.py status
```

## 🎮 Інтерактивний режим

### Запуск

```bash
python interactive_cli.py
```

### Меню

```
📋 ГОЛОВНЕ МЕНЮ:
1.  🏥 Health Check
2.  👤 Створити демо користувача
3.  📁 Завантажити Swagger файл
4.  💬 Чат з AI
5.  📜 Історія чату
6.  📝 Промпти
7.  📂 Категорії промптів
8.  📊 Статистика промптів
9.  📋 Swagger специфікації
10. 👤 Інформація про користувача
11. ✨ Створити кастомний промпт
12. 🔍 Пошук промптів
13. 💡 Пропозиції промптів
14. 🔧 Форматування промпту
15. 📤 Експорт промптів
16. 🔄 Перезавантажити промпти
17. 📊 Статус
0.  🚪 Вихід
```

## 💡 Приклади використання

### Повний цикл тестування

```bash
# 1. Перевірка стану
python cli_tester.py health

# 2. Створення демо користувача
python cli_tester.py demo-user

# 3. Завантаження Swagger
python cli_tester.py upload-swagger --file examples/swagger_specs/shop_api.json

# 4. Перегляд промптів
python cli_tester.py prompts

# 5. Чат з AI
python cli_tester.py chat --message "Покажи всі доступні endpoints"

# 6. Створення кастомного промпту
python cli_tester.py create-prompt \
  --name "Мій тестовий промпт" \
  --description "Тестовий опис" \
  --template "Ти експерт з API. {user_query}" \
  --category user_defined

# 7. Пошук промптів
python cli_tester.py search-prompts --query "тестовий"

# 8. Експорт промптів
python cli_tester.py export-prompts --include-custom
```

### Тестування чату

```bash
# Базові запити
python cli_tester.py chat --message "Покажи всі доступні endpoints"
python cli_tester.py chat --message "Створи товар з назвою Телефон"
python cli_tester.py chat --message "Покажи категорії товарів"
python cli_tester.py chat --message "Як створити нову категорію?"

# Складні запити
python cli_tester.py chat --message "Створи категорію Електроніка з описом 'Електронні пристрої'"
python cli_tester.py chat --message "Покажи товари в категорії Одяг"
python cli_tester.py chat --message "Онови товар з ID 1, зміни ціну на 1500"
```

### Тестування промптів

```bash
# Перегляд всіх промптів
python cli_tester.py prompts

# Промпти за категорією
python cli_tester.py prompts --category system
python cli_tester.py prompts --category data_creation
python cli_tester.py prompts --category error_handling

# Пошук промптів
python cli_tester.py search-prompts --query "створення"
python cli_tester.py search-prompts --query "помилка"
python cli_tester.py search-prompts --query "форматування"

# Пропозиції промптів
python cli_tester.py prompt-suggestions --query "Створи нову категорію"
python cli_tester.py prompt-suggestions --query "Покажи товари"
```

## 🔧 Налаштування

### Зміна URL API

```bash
# Командний режим
python cli_tester.py health --url http://localhost:8000

# Інтерактивний режим
python interactive_cli.py --url http://localhost:8000
```

### Показ заголовків відповіді

В коді `cli_tester.py` можна змінити параметр `show_headers=True` в методі `print_response()`:

```python
self.print_response(response, show_headers=True)
```

## 🐛 Troubleshooting

### Помилка підключення

```
❌ Не вдалося підключитися до http://localhost:8000
Перевірте, чи запущений API сервер
```

**Рішення:**
```bash
# Запустіть API сервер
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Помилка авторизації

```
❌ Спочатку створіть демо користувача!
```

**Рішення:**
```bash
python cli_tester.py demo-user
```

### Файл не знайдено

```
❌ Файл не знайдено: path/to/file.json
```

**Рішення:**
```bash
# Перевірте шлях до файлу
ls examples/swagger_specs/

# Використайте правильний шлях
python cli_tester.py upload-swagger --file examples/swagger_specs/shop_api.json
```

### Помилка JSON

```
❌ Неправильний формат JSON для параметрів
```

**Рішення:**
```bash
# Використовуйте правильний JSON формат
python cli_tester.py format-prompt \
  --prompt-id "system_base" \
  --parameters '{"user_query": "тест", "context": "контекст"}'
```

## 📊 Логування

Всі запити та відповіді логуються в консоль з детальною інформацією:

```
============================================================
📡 POST http://localhost:8000/chat
📊 Статус: 200 OK
📦 Дані відповіді:
{
  "response": "Ось список доступних endpoints...",
  "user_id": "user-uuid",
  "timestamp": "2024-01-01T12:00:00",
  "swagger_id": "swagger-uuid"
}
============================================================
```

## 🎯 Переваги CLI тестера

1. **Швидкість** - без необхідності відкривати браузер
2. **Автоматизація** - можна використовувати в скриптах
3. **Детальне логування** - всі запити та відповіді
4. **Зручність** - інтерактивне меню
5. **Без авторизації** - автоматичне створення демо користувача
6. **Повний функціонал** - всі API endpoints

## 🔗 Корисні посилання

- [API Документація](API_DOCUMENTATION.md)
- [Swagger UI](http://localhost:8000/docs)
- [Адмін панель](http://localhost:8000/admin)
- [Приклади Swagger файлів](examples/swagger_specs/)
