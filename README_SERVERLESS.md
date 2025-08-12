# AI Swagger Bot - Serverless Deployment

Цей документ описує як розгорнути AI Swagger Bot API як серверлес сервіс на AWS Lambda з використанням [Mangum](https://pypi.org/project/mangum/) та Serverless Framework.

## 🚀 Швидкий старт

### 1. Встановлення залежностей

```bash
# Встановити Node.js залежності
npm install

# Встановити Python залежності
pip install -r requirements.txt

# Встановити Serverless Framework глобально
npm install -g serverless
```

### 2. Налаштування AWS

```bash
# Налаштувати AWS credentials
aws configure

# Або використовувати AWS_PROFILE
export AWS_PROFILE=your-profile-name
```

### 3. Розгортання

```bash
# Розгорнути на dev stage
make deploy

# Розгорнути на production
make deploy-prod

# Розгорнути на staging
make deploy-staging
```

## 📁 Структура файлів

```
├── lambda_handler.py          # AWS Lambda handler з Mangum
├── serverless.yml            # Конфігурація Serverless Framework
├── package.json              # Node.js залежності
├── Dockerfile.lambda         # Docker image для Lambda
├── docker-compose.lambda.yml # Локальне тестування
├── Makefile.lambda           # Команди для управління
├── test-event.json           # Тестовий event для Lambda
└── README_SERVERLESS.md      # Ця документація
```

## 🔧 Основні компоненти

### Mangum Handler

```python
from mangum import Mangum
from api.main import app

# Створюємо handler для AWS Lambda
handler = Mangum(app, lifespan="off")
```

**Параметри:**
- `lifespan="off"` - вимикає startup/shutdown події (рекомендується для Lambda)
- `lifespan="on"` - включає startup/shutdown події

### Serverless Configuration

Основні налаштування в `serverless.yml`:

```yaml
provider:
  name: aws
  runtime: python3.11
  region: us-east-1
  stage: ${opt:stage, 'dev'}

functions:
  api:
    handler: lambda_handler.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true
```

## 🐳 Docker Deployment

### Локальне тестування

```bash
# Збудувати Docker image
make build-docker

# Тестувати локально
make test-docker

# Або з docker-compose
make test-docker-compose
```

### Розгортання на ECR

```bash
# Створити ECR repository
aws ecr create-repository --repository-name ai-swagger-bot-lambda

# Авторизуватися в ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Збудувати та затегувати image
docker build -f Dockerfile.lambda -t ai-swagger-bot-lambda .
docker tag ai-swagger-bot-lambda:latest $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-swagger-bot-lambda:latest

# Запушити в ECR
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-swagger-bot-lambda:latest
```

## 📊 Monitoring та Logs

### CloudWatch Logs

```bash
# Показати логи в реальному часі
make dev-logs

# Показати логи конкретного stage
make logs-prod
make logs-staging
```

### Metrics

Основні метрики доступні в CloudWatch:
- Duration
- Errors
- Throttles
- Concurrent executions

## 🔒 Security

### IAM Roles

```yaml
iam:
  role:
    statements:
      - Effect: Allow
        Action:
          - logs:CreateLogGroup
          - logs:CreateLogStream
          - logs:PutLogEvents
        Resource: "*"
      - Effect: Allow
        Action:
          - rds:*
          - ec2:*
        Resource: "*"
```

### Environment Variables

```yaml
environment:
  STAGE: ${self:provider.stage}
  PYTHONPATH: /var/task:/var/task/api:/var/task/src
```

## 🧪 Тестування

### Локальне тестування

```bash
# Тестувати з test-event.json
make test-local

# Тестувати з власним event
serverless invoke local -f api --path custom-event.json
```

### Тестування в AWS

```bash
# Викликати розгорнуту функцію
make invoke

# Показати інформацію про deployment
make info
```

## 📈 Scaling

### Конфігурація

```yaml
functions:
  api:
    memorySize: 1024      # Memory в MB
    timeout: 30           # Timeout в секундах
    reservedConcurrency: 100  # Максимальна кількість одночасних виконань
```

### Auto Scaling

Lambda автоматично масштабується на основі:
- Кількості запитів
- Навантаження
- Налаштованих лімітів

## 💰 Cost Optimization

### Рекомендації

1. **Memory**: Оптимізувати memory для кращої продуктивності
2. **Timeout**: Встановити мінімальний необхідний timeout
3. **Provisioned Concurrency**: Для критичних endpoint'ів
4. **Reserved Concurrency**: Обмежити максимальну кількість виконань

### Cost Calculation

```
Cost = (Duration × Memory × Price per GB-second) + (Requests × Price per request)
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
# Показати детальну інформацію
serverless info --verbose

# Логи з деталями
serverless logs -f api --verbose

# Тестувати локально з debug
serverless invoke local -f api --path test-event.json --log
```

## 🔄 CI/CD

### GitHub Actions

```yaml
name: Deploy to AWS Lambda

on:
  push:
    branches: [main, develop]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - uses: actions/setup-node@v3
      
      - name: Install dependencies
        run: |
          npm install
          pip install -r requirements.txt
      
      - name: Deploy to AWS
        run: |
          make ci-deploy STAGE=${{ github.ref_name == 'main' && 'prod' || 'staging' }}
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

### GitLab CI

```yaml
deploy:
  stage: deploy
  script:
    - npm install
    - pip install -r requirements.txt
    - make ci-deploy STAGE=$CI_COMMIT_REF_NAME
  only:
    - main
    - develop
```

## 📚 Додаткові ресурси

- [Mangum Documentation](https://mangum.fastapiexpert.com/)
- [Serverless Framework Documentation](https://www.serverless.com/framework/docs/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🤝 Підтримка

Якщо у вас виникли питання або проблеми:

1. Перевірте [troubleshooting](#-troubleshooting) секцію
2. Подивіться на [issues](https://github.com/your-repo/issues)
3. Створіть нове issue з детальним описом проблеми

---

**Примітка**: Ця документація оновлюється разом з проектом. Завжди перевіряйте останню версію. 