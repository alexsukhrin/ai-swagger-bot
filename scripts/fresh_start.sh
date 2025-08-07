#!/bin/bash

# Скрипт для швидкого очищення та переіндексації бази даних

echo "🔄 ШВИДКИЙ СТАРТ - ОЧИЩЕННЯ ТА ПЕРЕІНДЕКСАЦІЯ"
echo "=" * 60

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
echo "🐍 Версія Python: $(python --version)"

# Очищуємо базу даних
echo "🧹 Очищення Chroma бази даних..."
python scripts/clear_chroma_db.py --auto

# Переіндексуємо Swagger файли
echo "🔄 Переіндексація Swagger файлів..."
python scripts/reindex_swagger.py

echo ""
echo "✅ ШВИДКИЙ СТАРТ ЗАВЕРШЕНО!"
echo "💡 Тепер можна запускати чат-інтерфейс: ./run_enhanced_chat.sh"
echo "🌐 Або відкрити в браузері: http://localhost:8501"
