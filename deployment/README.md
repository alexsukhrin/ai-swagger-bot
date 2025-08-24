# 🚀 Розгортання

Ця папка містить всі файли для розгортання AI Swagger Bot на різних платформах.

## 📁 Файли

### Serverless (AWS Lambda)
- **`serverless.yml`** - Конфігурація Serverless Framework
- **`lambda_handler.py`** - AWS Lambda обробник
- **`test-event.json`** - Тестові дані для Lambda

### Docker
- **`nginx.conf`** - Конфігурація Nginx
- **`package.json`** - Node.js залежності

### Змінні середовища
- **`env_example.txt`** - Приклад змінних середовища
- **`env.serverless.example`** - Приклад змінних для Serverless

## 🔧 Використання

### Serverless розгортання
```bash
# Встановлення Serverless Framework
npm install -g serverless

# Розгортання
cd deployment
serverless deploy

# Тестування
serverless invoke -f hello -p test-event.json
```

### Docker розгортання
```bash
# Запуск з Nginx
docker-compose up -d

# Перевірка конфігурації
nginx -t -c deployment/nginx.conf
```

### Змінні середовища
```bash
# Копіювання прикладу
cp deployment/env_example.txt .env

# Редагування
nano .env
```

## 🌐 Платформи

### AWS Lambda
- Автоматичне масштабування
- Pay-per-use модель
- Інтеграція з AWS сервісами

### Docker
- Контейнеризація
- Легке розгортання
- Крос-платформність

### Nginx
- Веб-сервер
- Reverse proxy
- Load balancing

## 💡 Призначення

Ці файли призначені для:
- Автоматизації розгортання
- Конфігурації серверів
- Управління змінними середовища
- Тестування розгортання

---

**🎯 Мета**: Спростити та автоматизувати процес розгортання AI Swagger Bot на різних платформах.
