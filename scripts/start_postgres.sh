#!/bin/bash

# Скрипт для запуску PostgreSQL бази даних

echo "🚀 Запуск PostgreSQL бази даних..."

# Перевіряємо чи встановлений Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не встановлений. Будь ласка, встановіть Docker."
    exit 1
fi

# Перевіряємо чи запущений Docker
if ! docker info &> /dev/null; then
    echo "❌ Docker не запущений. Будь ласка, запустіть Docker."
    exit 1
fi

# Зупиняємо існуючі контейнери
echo "🛑 Зупиняємо існуючі контейнери..."
docker-compose down 2>/dev/null || true

# Запускаємо тільки базу даних
echo "🐘 Запускаємо PostgreSQL..."
docker-compose up -d db

# Чекаємо поки база даних буде готова
echo "⏳ Чекаємо готовності бази даних..."
sleep 10

# Перевіряємо статус
echo "🔍 Перевіряємо статус бази даних..."
docker-compose ps

echo "✅ PostgreSQL база даних запущена!"
echo "📊 URL: postgresql://postgres:postgres@localhost:5432/ai_swagger_bot"
echo ""
echo "💡 Для міграції промптів виконайте:"
echo "   python scripts/migrate_to_postgres.py"
echo ""
echo "💡 Для тестування виконайте:"
echo "   python cli_tester.py test-postgres-prompts"
