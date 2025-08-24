FROM python:3.13-slim

# Встановлюємо системні залежності
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо файли залежностей
COPY requirements.txt ./

# Встановлюємо Python залежності
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо код програми
COPY . .

# Створюємо директорію для логів
RUN mkdir -p logs

# Відкриваємо порт для Streamlit
EXPOSE 8501

# Встановлюємо змінні середовища
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true

# Створюємо точку входу
CMD ["streamlit", "run", "streamlit_demo.py", "--server.port=8501", "--server.address=0.0.0.0"]
