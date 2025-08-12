# AI Swagger Bot - Serverless Overview

Цей документ надає загальний огляд серверлес функціональності AI Swagger Bot, яка дозволяє розгортати API як серверлес сервіс на AWS Lambda з використанням [Mangum](https://pypi.org/project/mangum/).

## 🎯 Що додано

### 1. AWS Lambda Integration з Mangum

```python
# lambda_handler.py
from mangum import Mangum
from api.main import app

# Створюємо handler для AWS Lambda
handler = Mangum(app, lifespan="off")
```

**Переваги:**
- ✅ Повна сумісність з FastAPI
- ✅ Автоматичне масштабування
- ✅ Pay-per-use модель
- ✅ Вбудована безпека AWS

### 2. Serverless Framework Configuration

```yaml
# serverless.yml
service: ai-swagger-bot
provider:
  name: aws
  runtime: python3.11
  region: us-east-1

functions:
  api:
    handler: lambda_handler.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true
```

**Можливості:**
- 🌍 Multi-stage deployment (dev, staging, prod)
- 🔒 IAM roles та security groups
- 📊 CloudWatch monitoring
- 🚀 Auto-scaling

### 3. Infrastructure as Code з Terraform

```hcl
# terraform/main.tf
resource "aws_lambda_function" "main" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "${var.project_name}-api-${var.environment}"
  role            = aws_iam_role.lambda_exec.arn
  handler         = "lambda_handler.handler"
  runtime         = "python3.11"
  timeout         = var.lambda_timeout
  memory_size     = var.lambda_memory_size
}
```

**Компоненти:**
- 🏗️ VPC з private/public subnets
- 🗄️ RDS PostgreSQL
- 🔴 ElastiCache Redis
- 🌐 API Gateway
- 📊 CloudWatch Logs

### 4. Docker Containerization

```dockerfile
# Dockerfile.lambda
FROM public.ecr.aws/lambda/python:3.11

# Встановлюємо системні залежності
RUN yum update -y && \
    yum install -y gcc gcc-c++ libffi-devel postgresql-devel

# Копіюємо код та встановлюємо залежності
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Копіюємо код додатку
COPY api/ ${LAMBDA_TASK_ROOT}/api/
COPY src/ ${LAMBDA_TASK_ROOT}/src/
COPY lambda_handler.py ${LAMBDA_TASK_ROOT}

CMD ["lambda_handler.handler"]
```

### 5. CI/CD Pipelines

#### GitHub Actions
```yaml
# .github/workflows/deploy-lambda.yml
name: Deploy to AWS Lambda

on:
  push:
    branches: [main, develop]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to AWS Lambda
        run: |
          make -f Makefile.lambda deploy STAGE=${{ github.ref_name == 'main' && 'prod' || 'staging' }}
```

#### GitLab CI
```yaml
# .gitlab-ci.yml
deploy:production:
  stage: deploy
  script:
    - make -f Makefile.lambda deploy-prod
  only:
    - main
```

### 6. Comprehensive Testing

```bash
# Локальне тестування
python test_lambda.py --all

# Docker тестування
make -f Makefile.lambda test-docker

# Serverless тестування
make -f Makefile.lambda test-local
```

## 🚀 Швидкий старт

### 1. Налаштування середовища

```bash
# Автоматичне налаштування
./scripts/setup_serverless.sh

# Або вручну
npm install
pip install -r requirements.txt
npm install -g serverless
```

### 2. Розгортання

```bash
# Dev stage
make -f Makefile.lambda deploy

# Production
make -f Makefile.lambda deploy-prod

# Terraform
cd terraform
make quick-deploy ENVIRONMENT=prod
```

### 3. Тестування

```bash
# Локальне тестування
python test_lambda.py --health

# Приклади використання
python examples/serverless_example.py --all
```

## 📁 Структура файлів

```
├── lambda_handler.py              # AWS Lambda handler
├── serverless.yml                 # Serverless Framework config
├── package.json                   # Node.js dependencies
├── Dockerfile.lambda              # Docker image
├── docker-compose.lambda.yml      # Local testing
├── Makefile.lambda                # Lambda commands
├── test-event.json                # Test event
├── test_lambda.py                 # Lambda testing
├── examples/serverless_example.py # Usage examples
├── terraform/                     # Infrastructure as Code
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── README.md
├── .github/workflows/             # GitHub Actions
├── .gitlab-ci.yml                 # GitLab CI
├── README_SERVERLESS.md           # Serverless docs
├── env.serverless.example         # Environment variables
└── .gitignore.serverless          # Git ignore
```

## 🔧 Основні команди

### Serverless Framework

```bash
# Розгортання
serverless deploy
serverless deploy --stage prod

# Видалення
serverless remove
serverless remove --stage prod

# Логи
serverless logs -f api
serverless logs -f api --stage prod -t

# Локальне тестування
serverless invoke local -f api --path test-event.json
```

### Makefile Commands

```bash
# Показати всі команди
make -f Makefile.lambda help

# Розгортання
make -f Makefile.lambda deploy
make -f Makefile.lambda deploy-prod

# Тестування
make -f Makefile.lambda test-local
make -f Makefile.lambda test-docker

# Очищення
make -f Makefile.lambda clean
```

### Terraform Commands

```bash
# Показати всі команди
cd terraform && make help

# Розгортання
make quick-deploy ENVIRONMENT=dev
make quick-deploy ENVIRONMENT=prod

# Планування
make plan ENVIRONMENT=staging

# Видалення
make destroy ENVIRONMENT=dev
```

## 💰 Вартість

### Приблизна вартість на місяць

| Environment | Lambda | RDS | Redis | API Gateway | Total |
|-------------|--------|-----|-------|-------------|-------|
| Dev         | $1.20  | $15 | $10   | $3.50       | $29.70 |
| Staging     | $1.20  | $20 | $12   | $3.50       | $36.70 |
| Production  | $1.20  | $25 | $15   | $3.50       | $44.70 |

**Примітки:**
- Вартість залежить від кількості запитів
- RDS вартість залежить від instance class та storage
- Redis вартість залежить від node type
- API Gateway вартість залежить від кількості запитів

## 🔒 Безпека

### Security Groups

- **Lambda**: Тільки вихідний трафік
- **Database**: Доступ тільки з Lambda
- **Redis**: Доступ тільки з Lambda

### IAM Roles

- **Lambda Execution**: Базова роль + VPC доступ
- **Database Access**: Через security groups
- **CloudWatch**: Логування та метрики

### Encryption

- **RDS**: Увімкнено за замовчуванням
- **S3 State**: Увімкнено за замовчуванням
- **Lambda**: Увімкнено за замовчуванням

## 📊 Monitoring

### CloudWatch Metrics

- **Lambda**: Duration, Errors, Throttles
- **RDS**: CPU, Memory, Connections
- **Redis**: CPU, Memory, Connections
- **API Gateway**: Request Count, Latency

### Logs

```bash
# Lambda логи
make -f Makefile.lambda logs

# Логи в реальному часі
make -f Makefile.lambda dev-logs

# Логи конкретного stage
make -f Makefile.lambda logs-prod
```

## 🚨 Troubleshooting

### Поширені проблеми

1. **Import Errors**
   - Перевірити PYTHONPATH
   - Переконатися що всі залежності включені

2. **Timeout Errors**
   - Збільшити timeout в serverless.yml
   - Оптимізувати код

3. **Memory Errors**
   - Збільшити memorySize
   - Оптимізувати використання пам'яті

4. **Cold Start**
   - Використовувати Provisioned Concurrency
   - Оптимізувати розмір package

### Debug Commands

```bash
# Детальна інформація
serverless info --verbose

# Логи з деталями
serverless logs -f api --verbose

# Локальне тестування з debug
serverless invoke local -f api --path test-event.json --log
```

## 🌟 Переваги

### Технічні переваги

- 🚀 **Auto-scaling** - автоматичне масштабування
- 💰 **Pay-per-use** - плата тільки за використання
- 🔒 **Security** - вбудована безпека AWS
- 📊 **Monitoring** - CloudWatch, логування, метрики
- 🌍 **Multi-stage** - dev, staging, production
- 🐳 **Docker** - контейнеризація та портабельність

### Бізнес переваги

- 💸 **Cost-effective** - низька вартість для малого навантаження
- ⚡ **Fast deployment** - швидке розгортання та оновлення
- 🔄 **CI/CD** - автоматизація процесів розробки
- 📈 **Scalability** - легко масштабувати при зростанні
- 🛡️ **Reliability** - висока доступність AWS

## 🔮 Майбутні покращення

### Планувані функції

- [ ] **Multi-region deployment** - розгортання в кількох регіонах
- [ ] **Custom domains** - власні домени для API
- [ ] **Rate limiting** - обмеження швидкості запитів
- [ ] **API versioning** - версіонування API
- [ ] **GraphQL support** - підтримка GraphQL
- [ ] **WebSocket support** - real-time комунікація

### Технічні покращення

- [ ] **Layer optimization** - оптимізація Lambda layers
- [ ] **Cold start reduction** - зменшення cold start
- [ ] **Performance monitoring** - детальний моніторинг продуктивності
- [ ] **Automated testing** - автоматизоване тестування
- [ ] **Disaster recovery** - план відновлення після аварій

## 📚 Додаткові ресурси

### Документація

- [README_SERVERLESS.md](README_SERVERLESS.md) - Детальна документація
- [terraform/README.md](terraform/README.md) - Terraform документація
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API документація

### Зовнішні ресурси

- [Mangum Documentation](https://mangum.fastapiexpert.com/)
- [Serverless Framework](https://www.serverless.com/framework/docs/)
- [AWS Lambda](https://docs.aws.amazon.com/lambda/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

## 🤝 Підтримка

### Якщо у вас виникли питання

1. Перевірте [troubleshooting](#-troubleshooting) секцію
2. Подивіться на [examples](examples/) директорію
3. Запустіть тести: `python test_lambda.py --all`
4. Створіть issue з детальним описом проблеми

### Контриб'юція

1. Форкніть репозиторій
2. Створіть feature branch
3. Додайте тести для нової функціональності
4. Створіть Pull Request

---

**AI Swagger Bot Serverless** - Робіть API простішими та масштабованими! 🚀☁️ 