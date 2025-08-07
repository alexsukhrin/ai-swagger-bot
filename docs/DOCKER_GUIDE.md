# 🐳 Docker Guide для AI Swagger Bot

## 📋 Огляд

AI Swagger Bot може бути запущений в Docker контейнері з Streamlit веб-інтерфейсом або CLI інтерфейсом.

---

## 🚀 Швидкий старт

### 1. Встановлення змінних середовища

```bash
# Обов'язковий OpenAI API ключ
export OPENAI_API_KEY="sk-your-openai-key"

# Опціональний JWT токен для продакшну
export JWT_TOKEN="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 2. Запуск через скрипт (рекомендовано)

```bash
# Зробити скрипт виконуваним
chmod +x run_docker.sh

# Інтерактивний запуск
./run_docker.sh

# Або пряма команда
./run_docker.sh streamlit
```

### 3. Запуск через docker-compose

```bash
# Запуск Streamlit
docker-compose up -d

# Запуск CLI
docker-compose run --rm ai-swagger-bot python cli.py

# Запуск тесту
docker-compose run --rm ai-swagger-bot python test_full_functionality.py
```

---

## 🔧 Доступні команди

### Скрипт run_docker.sh:

```bash
./run_docker.sh streamlit  # Запустити Streamlit веб-інтерфейс
./run_docker.sh cli        # Запустити CLI інтерфейс
./run_docker.sh test       # Запустити тест функціональності
./run_docker.sh build      # Збудувати образ та запустити
./run_docker.sh stop       # Зупинити контейнер
./run_docker.sh logs       # Показати логи
./run_docker.sh            # Інтерактивний режим
```

### Docker Compose команди:

```bash
# Збірка образу
docker-compose build

# Запуск в фоновому режимі
docker-compose up -d

# Запуск з логами
docker-compose up

# Зупинка
docker-compose down

# Перегляд логів
docker-compose logs -f

# Перегляд статусу
docker-compose ps
```

---

## 🌐 Доступ до додатку

### Streamlit веб-інтерфейс:
- **URL**: http://localhost:8501
- **Порт**: 8501
- **Функції**: Повний веб-інтерфейс з налаштуваннями

### CLI інтерфейс:
```bash
docker-compose run --rm ai-swagger-bot python cli.py
```

---

## ⚙️ Налаштування

### Змінні середовища:

```bash
# Обов'язкові
OPENAI_API_KEY=sk-your-openai-key

# Опціональні
JWT_TOKEN=your-jwt-token
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0
REQUEST_TIMEOUT=30
LOG_LEVEL=INFO
```

### Volumes (збереження даних):

```yaml
volumes:
  - ./chroma_db:/app/chroma_db      # Векторна база даних
  - ./logs:/app/logs                 # Логи
  - ./examples/swagger_specs:/app/examples/swagger_specs  # Swagger файли
```

---

## 🏗️ Структура Docker

### Dockerfile:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

### docker-compose.yml:
```yaml
version: '3.8'
services:
  ai-swagger-bot:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - JWT_TOKEN=${JWT_TOKEN}
    volumes:
      - ./chroma_db:/app/chroma_db
      - ./logs:/app/logs
```

---

## 🧪 Тестування в Docker

### 1. Тест функціональності:
```bash
docker-compose run --rm ai-swagger-bot python test_full_functionality.py
```

### 2. Тест JWT авторизації:
```bash
docker-compose run --rm ai-swagger-bot python test_ngrok_jwt.py
```

### 3. Тест RAG системи:
```bash
docker-compose run --rm ai-swagger-bot python check_rag_status.py
```

---

## 🔍 Діагностика

### Перевірка статусу:
```bash
# Статус контейнерів
docker-compose ps

# Логи контейнера
docker-compose logs ai-swagger-bot

# Логи в реальному часі
docker-compose logs -f ai-swagger-bot
```

### Перевірка змінних середовища:
```bash
# В контейнері
docker-compose exec ai-swagger-bot env | grep OPENAI
docker-compose exec ai-swagger-bot env | grep JWT
```

### Перевірка файлів:
```bash
# Структура директорій
docker-compose exec ai-swagger-bot ls -la

# Перевірка chroma_db
docker-compose exec ai-swagger-bot ls -la chroma_db/
```

---

## 🛠️ Розробка в Docker

### Запуск з відладкою:
```bash
# Запуск з логами
docker-compose up

# Або в інтерактивному режимі
docker-compose run --rm -it ai-swagger-bot bash
```

### Внесення змін:
```bash
# Перебудувати образ після змін
docker-compose build --no-cache
docker-compose up -d
```

---

## 📊 Моніторинг

### Health Check:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### Логи:
- **Streamlit логи**: В контейнері
- **Додаток логи**: В контейнері
- **Системні логи**: Docker logs

---

## 🚨 Вирішення проблем

### Проблема: Контейнер не запускається
```bash
# Перевірити логи
docker-compose logs ai-swagger-bot

# Перевірити змінні середовища
echo $OPENAI_API_KEY
```

### Проблема: Порт 8501 зайнятий
```bash
# Змінити порт в docker-compose.yml
ports:
  - "8502:8501"  # Зовнішній:внутрішній
```

### Проблема: Немає доступу до chroma_db
```bash
# Перевірити права доступу
ls -la chroma_db/

# Створити директорію
mkdir -p chroma_db
```

---

## 📈 Продуктивність

### Оптимізація образу:
- Використовується python:3.11-slim
- .dockerignore виключає непотрібні файли
- Багатоетапна збірка для кешування

### Ресурси:
- **CPU**: Мінімум 1 ядро
- **RAM**: Мінімум 2GB
- **Диск**: 1GB для образу + chroma_db

---

## 🔐 Безпека

### Рекомендації:
- ✅ Використовуйте змінні середовища для секретів
- ✅ Не комітьте API ключі в код
- ✅ Регулярно оновлюйте базовий образ
- ✅ Використовуйте .dockerignore

### Змінні середовища:
```bash
# Безпечно в .env файлі
OPENAI_API_KEY=sk-your-key
JWT_TOKEN=your-jwt-token

# Завантаження
source .env
```

---

## 📝 Приклади використання

### Приклад 1: Локальна розробка
```bash
export OPENAI_API_KEY="sk-your-key"
./run_docker.sh streamlit
```

### Приклад 2: Продакшн з JWT
```bash
export OPENAI_API_KEY="sk-your-key"
export JWT_TOKEN="your-jwt-token"
./run_docker.sh streamlit
```

### Приклад 3: CLI режим
```bash
export OPENAI_API_KEY="sk-your-key"
docker-compose run --rm ai-swagger-bot python cli.py
```

---

## 🎯 Висновок

Docker конфігурація AI Swagger Bot:
- ✅ **Готовий до продакшну**
- ✅ **Підтримує Streamlit та CLI**
- ✅ **Зберігає дані між перезапусками**
- ✅ **Безпечне управління секретами**
- ✅ **Легкий моніторинг та діагностика**

**Готово до використання!** 🚀
