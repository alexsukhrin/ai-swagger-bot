# Використовуємо офіційний Python образ
FROM python:3.11-slim

# Встановлюємо системні залежності
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо файли залежностей
COPY requirements.txt .

# Встановлюємо Python залежності
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо код додатку
COPY . .

# Створюємо директорію для логів
RUN mkdir -p logs

# Створюємо директорію для chroma_db якщо не існує
RUN mkdir -p chroma_db

# Відкриваємо порт для Streamlit
EXPOSE 8501

# Встановлюємо змінні середовища за замовчуванням
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

# Команда за замовчуванням
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
