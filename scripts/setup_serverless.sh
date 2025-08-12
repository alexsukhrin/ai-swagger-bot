#!/bin/bash

# Скрипт для налаштування серверлес середовища для AI Swagger Bot

set -e

echo "🚀 Налаштування серверлес середовища для AI Swagger Bot..."

# Перевіряємо чи встановлений Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js не встановлений. Будь ласка, встановіть Node.js 18+"
    exit 1
fi

# Перевіряємо версію Node.js
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Потрібна Node.js версія 18+. Поточна версія: $(node --version)"
    exit 1
fi

echo "✅ Node.js версія: $(node --version)"

# Перевіряємо чи встановлений Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не встановлений. Будь ласка, встановіть Python 3.9+"
    exit 1
fi

echo "✅ Python версія: $(python3 --version)"

# Перевіряємо чи встановлений pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 не встановлений. Будь ласка, встановіть pip3"
    exit 1
fi

echo "✅ pip3 встановлений"

# Перевіряємо чи встановлений AWS CLI
if ! command -v aws &> /dev/null; then
    echo "⚠️ AWS CLI не встановлений. Встановлюємо..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install awscli
        else
            echo "❌ Homebrew не встановлений. Будь ласка, встановіть AWS CLI вручну"
            echo "   https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        unzip awscliv2.zip
        sudo ./aws/install
        rm -rf aws awscliv2.zip
    else
        echo "❌ Непідтримувана операційна система. Будь ласка, встановіть AWS CLI вручну"
        exit 1
    fi
fi

echo "✅ AWS CLI версія: $(aws --version)"

# Встановлюємо Serverless Framework глобально
echo "📦 Встановлюю Serverless Framework..."
npm install -g serverless

echo "✅ Serverless Framework версія: $(serverless --version)"

# Встановлюємо Node.js залежності
echo "📦 Встановлюю Node.js залежності..."
npm install

# Встановлюємо Python залежності
echo "📦 Встановлюю Python залежності..."
pip3 install -r requirements.txt

# Перевіряємо чи налаштовані AWS credentials
echo "🔐 Перевіряю AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo "⚠️ AWS credentials не налаштовані. Налаштуйте їх:"
    echo "   aws configure"
    echo "   або"
    echo "   export AWS_ACCESS_KEY_ID=your-key"
    echo "   export AWS_SECRET_ACCESS_KEY=your-secret"
    echo "   export AWS_DEFAULT_REGION=us-east-1"
else
    echo "✅ AWS credentials налаштовані"
    aws sts get-caller-identity
fi

# Створюємо .env файл якщо його немає
if [ ! -f .env ]; then
    echo "📝 Створюю .env файл..."
    cp env_example.txt .env
    echo "⚠️ Будь ласка, налаштуйте змінні середовища в .env файлі"
else
    echo "✅ .env файл вже існує"
fi

# Створюємо директорію для логів
mkdir -p logs

echo ""
echo "🎉 Налаштування завершено!"
echo ""
echo "📚 Доступні команди:"
echo "   make help                    - Показати всі команди"
echo "   make deploy                  - Розгорнути на dev stage"
echo "   make deploy-prod             - Розгорнути на production"
echo "   make test-local              - Тестувати локально"
echo "   make logs                    - Показати логи"
echo ""
echo "🚀 Для розгортання виконайте:"
echo "   make deploy"
echo ""
echo "📖 Детальна документація: README_SERVERLESS.md" 