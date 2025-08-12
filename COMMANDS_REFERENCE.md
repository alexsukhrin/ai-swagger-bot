# AI Swagger Bot - Commands Reference

Цей документ містить всі доступні команди для управління серверлес функціональністю AI Swagger Bot.

## 🚀 Швидкий старт

### 1. Налаштування середовища

```bash
# Автоматичне налаштування
./scripts/setup_serverless.sh

# Перевірка встановлення
python3 --version
node --version
npm --version
aws --version
```

### 2. Перше розгортання

```bash
# Розгорнути на dev stage
make -f Makefile.lambda deploy

# Перевірити статус
make -f Makefile.lambda info

# Показати логи
make -f Makefile.lambda logs
```

## 📋 Serverless Framework Commands

### Основні команди

```bash
# Розгортання
serverless deploy                    # Розгорнути на dev stage
serverless deploy --stage prod      # Розгорнути на production
serverless deploy --stage staging   # Розгорнути на staging

# Видалення
serverless remove                    # Видалити dev deployment
serverless remove --stage prod      # Видалити production deployment
serverless remove --stage staging   # Видалити staging deployment

# Інформація
serverless info                      # Показати інформацію про dev
serverless info --stage prod        # Показати інформацію про production
serverless info --stage staging     # Показати інформацію про staging

# Логи
serverless logs -f api              # Показати логи API функції
serverless logs -f api --stage prod # Показати логи production
serverless logs -f api -t           # Логи в реальному часі

# Локальне тестування
serverless invoke local -f api      # Викликати функцію локально
serverless invoke local -f api --path test-event.json  # З event файлу

# Package
serverless package                   # Створити deployment package
```

### Розширені команди

```bash
# Версіонування
serverless deploy --stage v1.0.0    # Розгорнути конкретну версію

# Регіони
serverless deploy --region eu-west-1 # Розгорнути в іншому регіоні

# Verbose режим
serverless deploy --verbose          # Детальне логування

# Dry run
serverless deploy --dryrun           # Показати що буде розгорнуто

# Конфігурація
serverless config credentials        # Налаштувати AWS credentials
serverless config tabcompletion install  # Встановити автодоповнення
```

## 🔧 Makefile Commands

### Основні команди

```bash
# Показати всі команди
make -f Makefile.lambda help

# Розгортання
make -f Makefile.lambda deploy              # Розгорнути на dev
make -f Makefile.lambda deploy-prod         # Розгорнути на production
make -f Makefile.lambda deploy-staging      # Розгорнути на staging

# Видалення
make -f Makefile.lambda remove              # Видалити dev
make -f Makefile.lambda remove-prod         # Видалити production
make -f Makefile.lambda remove-staging      # Видалити staging

# Тестування
make -f Makefile.lambda test-local          # Тестувати локально
make -f Makefile.lambda test-docker         # Тестувати Docker
make -f Makefile.lambda test-docker-compose # Тестувати docker-compose

# Логи
make -f Makefile.lambda logs                # Показати логи dev
make -f Makefile.lambda logs-prod           # Показати логи production
make -f Makefile.lambda logs-staging        # Показати логи staging
make -f Makefile.lambda dev-logs            # Логи в реальному часі

# Інформація
make -f Makefile.lambda info                # Інформація про dev
make -f Makefile.lambda info-prod           # Інформація про production
make -f Makefile.lambda info-staging        # Інформація про staging

# Очищення
make -f Makefile.lambda clean               # Очистити тимчасові файли
```

### Docker команди

```bash
# Docker
make -f Makefile.lambda build-docker        # Збудувати Docker image
make -f Makefile.lambda test-docker         # Тестувати Docker image
make -f Makefile.lambda test-docker-compose # Тестувати з docker-compose
```

### CI/CD команди

```bash
# CI/CD
make -f Makefile.lambda ci-deploy           # CI/CD deployment
make -f Makefile.lambda ci-remove           # CI/CD removal
```

## 🏗️ Terraform Commands

### Основні команди

```bash
# Перейти в terraform директорію
cd terraform

# Показати всі команди
make help

# Ініціалізація
make init                                # Ініціалізувати Terraform

# Планування
make plan ENVIRONMENT=dev               # Планувати зміни для dev
make plan ENVIRONMENT=staging           # Планувати зміни для staging
make plan ENVIRONMENT=prod              # Планувати зміни для production

# Розгортання
make apply ENVIRONMENT=dev              # Застосувати зміни для dev
make apply-auto ENVIRONMENT=dev         # Автоматично застосувати для dev
make quick-deploy ENVIRONMENT=dev       # Швидке розгортання для dev

# Видалення
make destroy ENVIRONMENT=dev            # Видалити dev інфраструктуру
make destroy ENVIRONMENT=staging        # Видалити staging інфраструктуру
make destroy ENVIRONMENT=prod           # Видалити production інфраструктуру

# Вихідні дані
make output                             # Показати вихідні дані
```

### Environment-specific команди

```bash
# Dev
make dev                                # Розгорнути dev середовище

# Staging
make staging                            # Розгорнути staging середовище

# Production
make prod                               # Розгорнути production середовище
```

### Допоміжні команди

```bash
# Валідація
make validate                           # Валідувати конфігурацію

# Форматування
make format                             # Форматувати код

# Очищення
make clean                              # Очистити тимчасові файли

# Pre-flight перевірки
make pre-flight                         # Виконати pre-flight перевірки

# Повний workflow
make deploy                             # Повний workflow розгортання
```

### Database команди

```bash
# Backup
make db-backup ENVIRONMENT=dev          # Створити backup бази даних
```

### Security команди

```bash
# Security scan
make security-scan ENVIRONMENT=dev      # Сканувати безпеку
```

### Cost команди

```bash
# Cost estimation
make cost ENVIRONMENT=dev               # Оцінити вартість
```

### Workspace команди

```bash
# Workspace management
make workspace-new ENVIRONMENT=dev      # Створити новий workspace
make workspace-select ENVIRONMENT=dev   # Вибрати workspace
make workspace-list                     # Показати список workspace'ів
```

### State команди

```bash
# State management
make state-pull                         # Завантажити стан з S3
make state-push                         # Завантажити стан в S3
make force-unlock                       # Примусово розблокувати state
```

## 🧪 Testing Commands

### Lambda тестування

```bash
# Основні тести
python3 test_lambda.py --all            # Запустити всі тести
python3 test_lambda.py --health         # Тестувати health endpoint
python3 test_lambda.py --chat           # Тестувати chat endpoint
python3 test_lambda.py --upload         # Тестувати upload endpoint

# Тестування з файлу
python3 test_lambda.py --event-file test-event.json  # З event файлу
```

### Приклади використання

```bash
# Основні приклади
python3 examples/serverless_example.py --all          # Запустити всі приклади
python3 examples/serverless_example.py --health       # Приклад health check
python3 examples/serverless_example.py --chat         # Приклад chat запиту
python3 examples/serverless_example.py --upload       # Приклад завантаження
python3 examples/serverless_example.py --error        # Приклад обробки помилок
python3 examples/serverless_example.py --usage        # Показати інструкції
```

## 🐳 Docker Commands

### Основні команди

```bash
# Збірка
docker build -f Dockerfile.lambda -t ai-swagger-bot-lambda .

# Запуск
docker run -p 9000:8080 ai-swagger-bot-lambda

# Тестування
docker run --rm -p 9000:8080 ai-swagger-bot-lambda

# Логи
docker logs <container_id>

# Вхід в контейнер
docker exec -it <container_id> /bin/bash
```

### Docker Compose

```bash
# Запуск
docker-compose -f docker-compose.lambda.yml up

# Запуск в фоновому режимі
docker-compose -f docker-compose.lambda.yml up -d

# Збірка та запуск
docker-compose -f docker-compose.lambda.yml up --build

# Зупинка
docker-compose -f docker-compose.lambda.yml down

# Логи
docker-compose -f docker-compose.lambda.yml logs

# Логи конкретного сервісу
docker-compose -f docker-compose.lambda.yml logs lambda-local
```

## 🔍 Debug Commands

### Serverless Debug

```bash
# Verbose режим
serverless deploy --verbose
serverless info --verbose
serverless logs --verbose

# Debug режим
serverless invoke local -f api --log
```

### Terraform Debug

```bash
# Детальна інформація
terraform show
terraform state list
terraform state show <resource_name>

# Plan детально
terraform plan -detailed-exitcode
```

### AWS Debug

```bash
# Перевірка credentials
aws sts get-caller-identity

# Перевірка Lambda
aws lambda list-functions --max-items 10

# Перевірка API Gateway
aws apigateway get-rest-apis --limit 10

# Перевірка RDS
aws rds describe-db-instances --max-items 10
```

## 📊 Monitoring Commands

### CloudWatch

```bash
# Логи
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda"

# Метрики
aws cloudwatch list-metrics --namespace "AWS/Lambda"

# Алерти
aws cloudwatch describe-alarms --alarm-name-prefix "ai-swagger-bot"
```

### Lambda Metrics

```bash
# Duration
aws cloudwatch get-metric-statistics \
  --namespace "AWS/Lambda" \
  --metric-name "Duration" \
  --dimensions Name=FunctionName,Value=ai-swagger-bot-api-dev \
  --start-time $(date -d '1 hour ago' --iso-8601) \
  --end-time $(date --iso-8601) \
  --period 300 \
  --statistics Average

# Errors
aws cloudwatch get-metric-statistics \
  --namespace "AWS/Lambda" \
  --metric-name "Errors" \
  --dimensions Name=FunctionName,Value=ai-swagger-bot-api-dev \
  --start-time $(date -d '1 hour ago' --iso-8601) \
  --end-time $(date --iso-8601) \
  --period 300 \
  --statistics Sum
```

## 🚨 Troubleshooting Commands

### Перевірка стану

```bash
# Перевірка всіх сервісів
make -f Makefile.lambda info
cd terraform && make output

# Перевірка логів
make -f Makefile.lambda logs
cd terraform && make logs

# Перевірка помилок
aws logs filter-log-events \
  --log-group-name "/aws/lambda/ai-swagger-bot-api-dev" \
  --filter-pattern "ERROR"
```

### Відновлення

```bash
# Перезапуск Lambda
aws lambda update-function-configuration \
  --function-name ai-swagger-bot-api-dev \
  --timeout 30

# Очищення кешу
make -f Makefile.lambda clean
cd terraform && make clean

# Перезапуск з нуля
make -f Makefile.lambda remove
make -f Makefile.lambda deploy
```

## 🔄 CI/CD Commands

### GitHub Actions

```bash
# Локальне тестування workflow
act -j deploy

# Перевірка workflow
act --list
```

### GitLab CI

```bash
# Локальне тестування
gitlab-runner exec docker deploy:staging

# Перевірка конфігурації
gitlab-runner verify
```

## 📚 Utility Commands

### Перевірка залежностей

```bash
# Python
pip3 list | grep -E "(fastapi|mangum|uvicorn)"
python3 -c "import mangum; print('Mangum OK')"

# Node.js
npm list -g serverless
npm list

# AWS
aws --version
aws sts get-caller-identity
```

### Оновлення

```bash
# Python
pip3 install -r requirements.txt --upgrade

# Node.js
npm update
npm install -g serverless@latest

# AWS CLI
pip3 install awscli --upgrade
```

### Очищення

```bash
# Python
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Node.js
rm -rf node_modules package-lock.json

# Terraform
cd terraform && make clean

# Serverless
make -f Makefile.lambda clean
```

## 🎯 Команди за сценаріями

### Startup

```bash
# Мінімальне розгортання
make -f Makefile.lambda deploy ENVIRONMENT=startup
cd terraform && make quick-deploy ENVIRONMENT=startup

# Перевірка вартості
cd terraform && make cost ENVIRONMENT=startup
```

### Enterprise

```bash
# Enterprise розгортання
make -f Makefile.lambda deploy ENVIRONMENT=enterprise
cd terraform && make quick-deploy ENVIRONMENT=enterprise

# Перевірка
make -f Makefile.lambda info ENVIRONMENT=enterprise
```

### Development

```bash
# Локальне розгортання
make -f Makefile.lambda test-docker-compose

# Тестування
python3 test_lambda.py --all
python3 examples/serverless_example.py --all
```

### Global

```bash
# Глобальне розгортання
make -f Makefile.lambda deploy ENVIRONMENT=global
cd terraform && make quick-deploy ENVIRONMENT=global

# Перевірка глобальної доступності
curl -I https://api.yourcompany.com/health
```

### Secure

```bash
# Безпечне розгортання
make -f Makefile.lambda deploy ENVIRONMENT=secure
cd terraform && make quick-deploy ENVIRONMENT=secure

# Перевірка безпеки
cd terraform && make security-scan ENVIRONMENT=secure
```

### Monitored

```bash
# Моніторинг розгортання
make -f Makefile.lambda deploy ENVIRONMENT=monitored
cd terraform && make quick-deploy ENVIRONMENT=monitored

# Перевірка моніторингу
aws cloudwatch describe-dashboards --dashboard-name-prefix "ai-swagger-bot"
```

## 💡 Корисні комбінації

### Повний workflow

```bash
# 1. Налаштування
./scripts/setup_serverless.sh

# 2. Розгортання
make -f Makefile.lambda deploy
cd terraform && make quick-deploy ENVIRONMENT=dev

# 3. Тестування
python3 test_lambda.py --all
make -f Makefile.lambda test-local

# 4. Перевірка
make -f Makefile.lambda info
cd terraform && make output

# 5. Моніторинг
make -f Makefile.lambda logs
```

### Production deployment

```bash
# 1. Планування
cd terraform && make plan ENVIRONMENT=prod

# 2. Розгортання
make -f Makefile.lambda deploy-prod
cd terraform && make quick-deploy ENVIRONMENT=prod

# 3. Перевірка
make -f Makefile.lambda info-prod
cd terraform && make output

# 4. Тестування
curl -I https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/health
```

### Troubleshooting workflow

```bash
# 1. Перевірка стану
make -f Makefile.lambda info
cd terraform && make output

# 2. Перевірка логів
make -f Makefile.lambda logs
cd terraform && make logs

# 3. Тестування
python3 test_lambda.py --all

# 4. Перезапуск
make -f Makefile.lambda remove
make -f Makefile.lambda deploy
```

---

**💡 Порада**: Використовуйте `make -f Makefile.lambda help` та `cd terraform && make help` для перегляду всіх доступних команд. 