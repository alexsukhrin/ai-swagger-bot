#!/bin/bash

# Скрипт для запуску покращеного Streamlit чат-додатку

echo "💬 AI Swagger Bot - Запуск покращеного чат-інтерфейсу"
echo "="*60

# Перевіряємо наявність conda
if ! command -v conda &> /dev/null; then
    echo "❌ Помилка: conda не знайдено"
    echo "💡 Встановіть Miniconda або Anaconda"
    exit 1
fi

# Активуємо conda середовище
echo "🔧 Активуємо conda середовище..."
source $HOME/miniconda3/etc/profile.d/conda.sh
conda activate ai-swagger

# Перевіряємо версію Python
echo "🐍 Перевіряємо версію Python..."
python --version

# Перевіряємо API ключ
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY не встановлено"
    echo "💡 Встановіть змінну середовища OPENAI_API_KEY"
    echo "   export OPENAI_API_KEY=your_api_key_here"
    exit 1
else
    echo "✅ OpenAI API ключ знайдено"
fi

# Перевіряємо JWT токен
if [ -z "$JWT_TOKEN" ]; then
    echo "⚠️  JWT_TOKEN не встановлено"
    echo "💡 Встановіть змінну середовища JWT_TOKEN"
    echo "   export JWT_TOKEN=your_jwt_token_here"
else
    echo "✅ JWT токен знайдено"
fi

# Очищуємо базу даних для свіжих даних
echo "🧹 Очищення Chroma бази даних для свіжих даних..."
python scripts/clear_chroma_db.py --auto

# Переіндексуємо Swagger файли
echo "🔄 Переіндексація Swagger файлів..."
python scripts/reindex_swagger.py

# Зупиняємо попередні процеси Streamlit
echo "🛑 Зупиняємо попередні процеси Streamlit..."
pkill -f streamlit 2>/dev/null || true

# Запускаємо покращений Streamlit чат-додаток
echo "🚀 Запускаємо покращений Streamlit чат-додаток..."
echo "📱 URL: http://localhost:8501"
echo "🌐 Network URL: http://192.168.0.110:8501"
echo ""
echo "💬 Це покращений чат-інтерфейс для InteractiveSwaggerAgent"
echo "🤖 Підтримує повноцінний діалог для виправлення помилок"
echo "🎨 Має покращений UI зі статистикою та експортом"
echo ""
echo "✨ Особливості покращеного інтерфейсу:"
echo "   • Красивий градієнтний заголовок"
echo "   • Статистика чату в реальному часі"
echo "   • Експорт історії розмови"
echo "   • Покращені стилі та анімації"
echo "   • Підказки для користувача"
echo "   • Автоматичне очищення БД при старті"
echo "   • Автоматична переіндексація Swagger файлів"
echo ""
echo "⏹️  Для зупинки натисніть Ctrl+C"

streamlit run enhanced_chat_app.py --server.port 8501
