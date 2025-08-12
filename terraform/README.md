# AI Swagger Bot - Terraform Infrastructure

Цей документ описує як розгорнути AWS інфраструктуру для AI Swagger Bot за допомогою Terraform.

## 🏗️ Архітектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway  │────│   Lambda        │────│   RDS           │
│                 │    │   Function      │    │   PostgreSQL    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   ElastiCache   │
                       │   Redis         │
                       └─────────────────┘
```

## 🚀 Швидкий старт

### 1. Передумови

- [Terraform](https://www.terraform.io/downloads.html) >= 1.0
- [AWS CLI](https://aws.amazon.com/cli/) v2
- [PostgreSQL Client](https://www.postgresql.org/download/) (для backup'ів)

### 2. Налаштування AWS

```bash
# Налаштувати AWS credentials
aws configure

# Перевірити налаштування
aws sts get-caller-identity
```

### 3. Налаштування проекту

```bash
# Перейти в terraform директорію
cd terraform

# Скопіювати та налаштувати змінні
cp terraform.tfvars.example terraform.tfvars

# Відредагувати terraform.tfvars з вашими значеннями
nano terraform.tfvars
```

### 4. Розгортання

```bash
# Показати доступні команди
make help

# Ініціалізувати Terraform
make init

# Планувати зміни
make plan

# Застосувати зміни
make apply

# Або швидке розгортання
make quick-deploy
```

## 📁 Структура файлів

```
terraform/
├── main.tf                 # Основна конфігурація
├── variables.tf            # Змінні
├── terraform.tfvars.example # Приклад змінних
├── Makefile               # Команди для управління
├── README.md              # Ця документація
└── outputs.tf             # Вихідні дані (автогенерується)
```

## 🔧 Основні компоненти

### VPC та Networking

- **VPC**: 10.0.0.0/16
- **Private Subnets**: 10.0.1.0/24, 10.0.2.0/24
- **Public Subnets**: 10.0.101.0/24, 10.0.102.0/24
- **NAT Gateway**: Для доступу приватних ресурсів до інтернету

### База даних

- **RDS PostgreSQL**: 15.7
- **Instance Class**: db.t3.micro (dev) / db.t3.small (prod)
- **Storage**: 20GB (dev) / 50GB (prod) з auto-scaling
- **Backup**: 7 днів (dev) / 30 днів (prod)

### Lambda Function

- **Runtime**: Python 3.11
- **Memory**: 1024MB (dev) / 2048MB (prod)
- **Timeout**: 30 секунд
- **VPC**: Розгорнута в приватних subnet'ах

### ElastiCache Redis

- **Engine**: Redis 7
- **Node Type**: cache.t3.micro (dev) / cache.t3.small (prod)
- **Port**: 6379

### API Gateway

- **Type**: Regional
- **Integration**: Lambda Proxy
- **CORS**: Увімкнено

## 🌍 Середовища

### Dev

```bash
make dev
```

- **Instance Types**: t3.micro
- **Storage**: 20GB
- **Backup**: 7 днів
- **Cost**: ~$15-20/місяць

### Staging

```bash
make staging
```

- **Instance Types**: t3.small
- **Storage**: 30GB
- **Backup**: 14 днів
- **Cost**: ~$30-40/місяць

### Production

```bash
make prod
```

- **Instance Types**: t3.small
- **Storage**: 50GB
- **Backup**: 30 днів
- **Cost**: ~$50-70/місяць

## 🔐 Безпека

### Security Groups

- **Database**: Доступ тільки з Lambda
- **Lambda**: Тільки вихідний трафік
- **Redis**: Доступ тільки з Lambda

### IAM Roles

- **Lambda Execution**: Базова роль + VPC доступ
- **Database Access**: Через security groups

### Encryption

- **RDS**: Увімкнено
- **S3 State**: Увімкнено
- **Lambda**: Увімкнено

## 💰 Вартість

### Оцінка вартості

```bash
# Оцінити вартість для dev
make cost ENVIRONMENT=dev

# Оцінити вартість для prod
make cost ENVIRONMENT=prod
```

### Оптимізація витрат

1. **Dev/Staging**: Автоматичне зупинення в неактивні години
2. **RDS**: Multi-AZ тільки для production
3. **Lambda**: Provisioned Concurrency для критичних endpoint'ів
4. **Storage**: Auto-scaling з мінімальними лімітами

## 📊 Monitoring

### CloudWatch

- **Lambda**: Duration, Errors, Throttles
- **RDS**: CPU, Memory, Connections
- **Redis**: CPU, Memory, Connections
- **API Gateway**: Request Count, Latency

### Logs

```bash
# Показати логи Lambda
make logs

# Показати логи в реальному часі
make dev-logs
```

## 🔄 CI/CD

### GitHub Actions

```yaml
- name: Deploy Infrastructure
  run: |
    cd terraform
    make quick-deploy ENVIRONMENT=${{ github.ref_name == 'main' && 'prod' || 'staging' }}
```

### GitLab CI

```yaml
deploy:infrastructure:
  script:
    - cd terraform
    - make quick-deploy ENVIRONMENT=$CI_COMMIT_REF_NAME
```

## 🚨 Troubleshooting

### Поширені проблеми

1. **State Lock**
   ```bash
   make force-unlock
   ```

2. **Import Existing Resources**
   ```bash
   make import
   ```

3. **State Sync Issues**
   ```bash
   make state-pull
   make state-push
   ```

### Debug Commands

```bash
# Валідація конфігурації
make validate

# Форматування коду
make format

# Pre-flight перевірки
make pre-flight
```

## 📚 Додаткові ресурси

- [Terraform Documentation](https://www.terraform.io/docs)
- [AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [VPC Module Documentation](https://registry.terraform.io/modules/terraform-aws-modules/vpc/aws/latest)
- [Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)

## 🤝 Підтримка

Якщо у вас виникли питання або проблеми:

1. Перевірте [troubleshooting](#-troubleshooting) секцію
2. Подивіться на логи: `make logs`
3. Виконайте pre-flight перевірки: `make pre-flight`
4. Створіть issue з детальним описом проблеми

---

**Примітка**: Завжди перевіряйте план перед застосуванням змін: `make plan` 