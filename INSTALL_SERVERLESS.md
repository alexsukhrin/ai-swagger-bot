# AI Swagger Bot - Serverless Installation Guide

Цей документ містить детальні інструкції по встановленню та налаштуванню серверлес функціональності AI Swagger Bot.

## 🎯 Передумови

### Системні вимоги

- **OS**: macOS 10.15+, Ubuntu 18.04+, Windows 10+
- **Python**: 3.9+ (рекомендується 3.11)
- **Node.js**: 18+ (рекомендується 18 LTS)
- **Docker**: 20.10+ (для контейнеризації)
- **AWS CLI**: 2.0+ (для розгортання)

### Обов'язкові інструменти

```bash
# Python
python3 --version  # >= 3.9
pip3 --version     # >= 20.0

# Node.js
node --version     # >= 18.0
npm --version      # >= 8.0

# Docker
docker --version   # >= 20.10

# AWS CLI
aws --version      # >= 2.0
```

## 🚀 Швидке встановлення

### 1. Автоматичне встановлення

```bash
# Клонувати репозиторій
git clone https://github.com/your-username/ai-swagger-bot.git
cd ai-swagger-bot

# Запустити автоматичне налаштування
./scripts/setup_serverless.sh
```

### 2. Перевірка встановлення

```bash
# Перевірити версії
python3 --version
node --version
npm --version
aws --version

# Перевірити залежності
pip3 list | grep -E "(fastapi|mangum|uvicorn)"
npm list -g serverless
```

## 📦 Ручне встановлення

### 1. Python залежності

```bash
# Створити віртуальне середовище
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# або
venv\Scripts\activate     # Windows

# Встановити залежності
pip3 install -r requirements.txt

# Перевірити встановлення
python3 -c "import mangum; print('Mangum встановлено')"
```

### 2. Node.js залежності

```bash
# Встановити Serverless Framework глобально
npm install -g serverless

# Встановити локальні залежності
npm install

# Перевірити встановлення
serverless --version
```

### 3. AWS CLI

#### macOS
```bash
# Через Homebrew
brew install awscli

# Або через pip
pip3 install awscli
```

#### Ubuntu/Debian
```bash
# Завантажити та встановити
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
rm -rf aws awscliv2.zip
```

#### Windows
```bash
# Завантажити MSI installer з AWS website
# https://awscli.amazonaws.com/AWSCLIV2.msi
```

### 4. Docker

#### macOS
```bash
# Завантажити Docker Desktop
# https://www.docker.com/products/docker-desktop
```

#### Ubuntu
```bash
# Встановити Docker
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo usermod -aG docker $USER

# Перезапустити сесію
newgrp docker
```

## 🔐 Налаштування AWS

### 1. Створення IAM користувача

```bash
# Створити користувача в AWS Console
# https://console.aws.amazon.com/iam/

# Налаштувати credentials
aws configure

# Ввести дані:
# AWS Access Key ID: [your-access-key]
# AWS Secret Access Key: [your-secret-key]
# Default region name: us-east-1
# Default output format: json
```

### 2. Перевірка налаштувань

```bash
# Перевірити credentials
aws sts get-caller-identity

# Перевірити доступ до Lambda
aws lambda list-functions --max-items 1

# Перевірити доступ до S3
aws s3 ls
```

### 3. Створення S3 bucket для Terraform state

```bash
# Створити bucket
aws s3 mb s3://ai-swagger-bot-terraform-state

# Увімкнути versioning
aws s3api put-bucket-versioning \
    --bucket ai-swagger-bot-terraform-state \
    --versioning-configuration Status=Enabled

# Увімкнути encryption
aws s3api put-bucket-encryption \
    --bucket ai-swagger-bot-terraform-state \
    --server-side-encryption-configuration '{
        "Rules": [
            {
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "AES256"
                }
            }
        ]
    }'
```

## 🏗️ Налаштування проекту

### 1. Environment Variables

```bash
# Скопіювати приклад
cp env.serverless.example .env

# Відредагувати .env файл
nano .env
```

**Обов'язкові змінні:**
```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_PROFILE=default

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-here
```

### 2. Terraform Variables

```bash
# Перейти в terraform директорію
cd terraform

# Скопіювати приклад
cp terraform.tfvars.example terraform.tfvars

# Відредагувати terraform.tfvars
nano terraform.tfvars
```

**Обов'язкові змінні:**
```hcl
# AWS Configuration
aws_region = "us-east-1"
environment = "dev"

# Database Configuration
database_password = "your-secure-password-here"

# Application Configuration
openai_api_key = "your-openai-api-key-here"
jwt_secret_key = "your-jwt-secret-key-here"
```

### 3. Створення директорій

```bash
# Створити необхідні директорії
mkdir -p logs
mkdir -p .serverless
mkdir -p terraform/.terraform
```

## 🧪 Тестування встановлення

### 1. Локальне тестування

```bash
# Тестувати Lambda handler
python3 test_lambda.py --health

# Тестувати всі endpoints
python3 test_lambda.py --all

# Тестувати приклади
python3 examples/serverless_example.py --usage
```

### 2. Docker тестування

```bash
# Збудувати Docker image
make -f Makefile.lambda build-docker

# Тестувати локально
make -f Makefile.lambda test-docker

# Тестувати з docker-compose
make -f Makefile.lambda test-docker-compose
```

### 3. Serverless тестування

```bash
# Тестувати локально
make -f Makefile.lambda test-local

# Тестувати з test-event.json
make -f Makefile.lambda test-local
```

## 🚀 Перше розгортання

### 1. Serverless Framework

```bash
# Розгорнути на dev stage
make -f Makefile.lambda deploy

# Перевірити статус
make -f Makefile.lambda info

# Показати логи
make -f Makefile.lambda logs
```

### 2. Terraform

```bash
# Перейти в terraform директорію
cd terraform

# Ініціалізувати Terraform
make init

# Планувати розгортання
make plan ENVIRONMENT=dev

# Розгорнути інфраструктуру
make quick-deploy ENVIRONMENT=dev

# Показати вихідні дані
make output
```

### 3. Перевірка розгортання

```bash
# Отримати URL API
cd terraform
make output | grep api_gateway_url

# Тестувати health endpoint
curl https://your-api-id.execute-api.us-east-1.amazonaws.com/dev/health

# Перевірити Lambda функцію
aws lambda get-function --function-name ai-swagger-bot-api-dev
```

## 🔧 Налаштування CI/CD

### 1. GitHub Actions

```bash
# Додати secrets в GitHub repository
# Settings -> Secrets and variables -> Actions

# Обов'язкові secrets:
# AWS_ACCESS_KEY_ID
# AWS_SECRET_ACCESS_KEY
```

### 2. GitLab CI

```bash
# Додати variables в GitLab project
# Settings -> CI/CD -> Variables

# Обов'язкові variables:
# AWS_ACCESS_KEY_ID
# AWS_SECRET_ACCESS_KEY
# AWS_REGION
```

## 🚨 Troubleshooting

### Поширені проблеми

#### 1. Import Errors
```bash
# Перевірити PYTHONPATH
echo $PYTHONPATH

# Встановити PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/ai-swagger-bot"
```

#### 2. AWS Credentials
```bash
# Перевірити credentials
aws sts get-caller-identity

# Якщо помилка, перевірити:
# - AWS_ACCESS_KEY_ID та AWS_SECRET_ACCESS_KEY
# - AWS_PROFILE
# - ~/.aws/credentials
```

#### 3. Terraform State
```bash
# Перевірити S3 bucket
aws s3 ls s3://ai-swagger-bot-terraform-state

# Якщо bucket не існує, створити
aws s3 mb s3://ai-swagger-bot-terraform-state
```

#### 4. Docker Issues
```bash
# Перевірити Docker daemon
docker info

# Перезапустити Docker
sudo systemctl restart docker  # Linux
# Або перезапустити Docker Desktop на macOS/Windows
```

### Debug Commands

```bash
# Детальна інформація про deployment
serverless info --verbose

# Логи з деталями
serverless logs -f api --verbose

# Terraform state
cd terraform
terraform show
terraform state list
```

## 📚 Додаткові ресурси

### Документація

- [README_SERVERLESS.md](README_SERVERLESS.md) - Основна документація
- [SERVERLESS_OVERVIEW.md](SERVERLESS_OVERVIEW.md) - Загальний огляд
- [terraform/README.md](terraform/README.md) - Terraform документація

### Корисні команди

```bash
# Показати всі доступні команди
make -f Makefile.lambda help
cd terraform && make help

# Очистити тимчасові файли
make -f Makefile.lambda clean
cd terraform && make clean

# Оновити залежності
pip3 install -r requirements.txt --upgrade
npm update
```

## 🤝 Підтримка

### Якщо у вас виникли проблеми

1. **Перевірте логи:**
   ```bash
   make -f Makefile.lambda logs
   cd terraform && make logs
   ```

2. **Запустіть тести:**
   ```bash
   python3 test_lambda.py --all
   ```

3. **Перевірте налаштування:**
   ```bash
   aws sts get-caller-identity
   serverless info
   ```

4. **Створіть issue** з детальним описом проблеми та логами

### Корисні посилання

- [Mangum Documentation](https://mangum.fastapiexpert.com/)
- [Serverless Framework](https://www.serverless.com/framework/docs/)
- [AWS Lambda](https://docs.aws.amazon.com/lambda/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

---

**🎉 Вітаємо!** Ви успішно встановили серверлес функціональність AI Swagger Bot.

**🚀 Наступні кроки:**
1. Протестувати локальне розгортання
2. Розгорнути на AWS
3. Налаштувати CI/CD
4. Моніторити та оптимізувати

**📖 Детальна документація:** [README_SERVERLESS.md](README_SERVERLESS.md) 