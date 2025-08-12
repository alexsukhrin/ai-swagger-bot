# AI Swagger Bot - Usage Scenarios

Цей документ містить приклади використання AI Swagger Bot як серверлес сервіса для різних сценаріїв.

## 🏢 Enterprise Deployment

### Сценарій: Велика компанія з багатьма командами

#### Архітектура
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway  │────│   Lambda        │────│   RDS           │
│   (Custom Domain)│   │   Function      │    │   (Multi-AZ)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   ElastiCache   │
                       │   (Cluster)     │
                       └─────────────────┘
```

#### Конфігурація

**serverless.yml:**
```yaml
service: ai-swagger-bot-enterprise

provider:
  name: aws
  runtime: python3.11
  region: us-east-1
  stage: ${opt:stage, 'dev'}
  
  # Enterprise features
  memorySize: 2048
  timeout: 60
  
  # VPC configuration
  vpc:
    securityGroupIds:
      - sg-enterprise-lambda
    subnetIds:
      - subnet-private-1a
      - subnet-private-1b

functions:
  api:
    handler: lambda_handler.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true
          authorizer: aws_iam  # IAM авторизація
    
    # Enterprise settings
    memorySize: 2048
    timeout: 60
    reservedConcurrency: 100
    
    # Environment variables
    environment:
      STAGE: ${self:provider.stage}
      ENVIRONMENT: enterprise
      LOG_LEVEL: INFO
      ENABLE_METRICS: true
      ENABLE_TRACING: true
```

**terraform/main.tf:**
```hcl
# Enterprise VPC
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"
  
  name = "enterprise-vpc"
  cidr = "10.0.0.0/16"
  
  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  
  enable_nat_gateway = true
  single_nat_gateway = false  # Multi-AZ для enterprise
  
  enable_dns_hostnames = true
  enable_dns_support   = true
}

# Enterprise RDS
resource "aws_db_instance" "main" {
  identifier = "enterprise-db"
  
  engine         = "postgres"
  engine_version = "15.7"
  instance_class = "db.r6g.large"  # Enterprise instance
  
  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_type          = "gp3"  # GP3 для кращої продуктивності
  
  multi_az = true  # Multi-AZ для enterprise
  
  backup_retention_period = 30
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  deletion_protection = true  # Захист від випадкового видалення
}
```

#### Розгортання

```bash
# Enterprise розгортання
make -f Makefile.lambda deploy ENVIRONMENT=enterprise

# Terraform розгортання
cd terraform
make quick-deploy ENVIRONMENT=enterprise

# Перевірка
make -f Makefile.lambda info ENVIRONMENT=enterprise
```

## 🚀 Startup Deployment

### Сценарій: Стартап з обмеженим бюджетом

#### Архітектура
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway  │────│   Lambda        │────│   RDS           │
│   (Free Tier)  │    │   Function      │    │   (t3.micro)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   ElastiCache   │
                       │   (t3.micro)    │
                       └─────────────────┘
```

#### Конфігурація

**serverless.yml:**
```yaml
service: ai-swagger-bot-startup

provider:
  name: aws
  runtime: python3.11
  region: us-east-1
  stage: ${opt:stage, 'dev'}
  
  # Startup optimization
  memorySize: 512
  timeout: 30
  
  # Cost optimization
  logRetentionInDays: 7  # Менше логів = менше вартості

functions:
  api:
    handler: lambda_handler.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true
    
    # Startup settings
    memorySize: 512
    timeout: 30
    
    # Environment variables
    environment:
      STAGE: ${self:provider.stage}
      ENVIRONMENT: startup
      LOG_LEVEL: WARNING  # Менше логування
      ENABLE_METRICS: false  # Вимикаємо метрики для економії
```

**terraform/main.tf:**
```hcl
# Startup VPC (мінімальна конфігурація)
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"
  
  name = "startup-vpc"
  cidr = "10.0.0.0/16"
  
  azs             = ["us-east-1a"]  # Тільки одна AZ
  private_subnets = ["10.0.1.0/24"]
  public_subnets  = ["10.0.101.0/24"]
  
  enable_nat_gateway = true
  single_nat_gateway = true  # Одна NAT Gateway для економії
  
  enable_dns_hostnames = true
  enable_dns_support   = true
}

# Startup RDS (Free Tier)
resource "aws_db_instance" "main" {
  identifier = "startup-db"
  
  engine         = "postgres"
  engine_version = "15.7"
  instance_class = "db.t3.micro"  # Free Tier instance
  
  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp2"
  
  multi_az = false  # Single AZ для економії
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  deletion_protection = false  # Дозволяємо видалення для економії
}
```

#### Розгортання

```bash
# Startup розгортання
make -f Makefile.lambda deploy ENVIRONMENT=startup

# Terraform розгортання
cd terraform
make quick-deploy ENVIRONMENT=startup

# Перевірка вартості
make cost ENVIRONMENT=startup
```

## 🧪 Development Environment

### Сценарій: Команда розробників

#### Архітектура
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway  │────│   Lambda        │────│   RDS           │
│   (Local)      │    │   Function      │    │   (Local)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Redis         │
                       │   (Local)       │
                       └─────────────────┘
```

#### Конфігурація

**docker-compose.lambda.yml:**
```yaml
version: '3.8'

services:
  lambda-local:
    build:
      context: .
      dockerfile: Dockerfile.lambda
    ports:
      - "9000:8080"
    environment:
      - AWS_LAMBDA_RUNTIME_API=host.docker.internal:9000
      - STAGE=local
      - ENVIRONMENT=development
      - DEBUG=true
      - LOG_LEVEL=DEBUG
    volumes:
      - ./logs:/tmp/logs
      - ./.env:/var/task/.env:ro
    command: ["lambda_handler.handler"]

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ai_swagger_bot_dev
      POSTGRES_USER: developer
      POSTGRES_PASSWORD: dev123
    ports:
      - "5432:5432"
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_dev_data:/data

volumes:
  postgres_dev_data:
  redis_dev_data:
```

#### Розгортання

```bash
# Локальне розгортання
make -f Makefile.lambda test-docker-compose

# Тестування
python3 test_lambda.py --all

# Приклади
python3 examples/serverless_example.py --all
```

## 🌍 Multi-Region Deployment

### Сценарій: Глобальна компанія

#### Архітектура
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Route 53      │────│   CloudFront    │────│   API Gateway   │
│   (Global DNS)  │    │   (CDN)         │    │   (US-East-1)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Lambda        │
                       │   (US-East-1)   │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   RDS Global    │
                       │   Database      │
                       └─────────────────┘
```

#### Конфігурація

**serverless.yml:**
```yaml
service: ai-swagger-bot-global

provider:
  name: aws
  runtime: python3.11
  region: us-east-1
  stage: ${opt:stage, 'prod'}

functions:
  api:
    handler: lambda_handler.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true
    
    # Global settings
    memorySize: 1024
    timeout: 30
    
    environment:
      STAGE: ${self:provider.stage}
      ENVIRONMENT: global
      REGION: ${self:provider.region}
      ENABLE_GLOBAL_FEATURES: true
```

**terraform/global.tf:**
```hcl
# Global Route 53
resource "aws_route53_zone" "main" {
  name = "api.yourcompany.com"
}

# CloudFront Distribution
resource "aws_cloudfront_distribution" "main" {
  origin {
    domain_name = aws_api_gateway_deployment.main.invoke_url
    origin_id   = "api-gateway"
    
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }
  
  enabled             = true
  is_ipv6_enabled    = true
  default_root_object = "index.html"
  
  default_cache_behavior {
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "api-gateway"
    
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
    
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }
  
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  
  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

# Global RDS
resource "aws_rds_global_cluster" "main" {
  global_cluster_identifier = "ai-swagger-bot-global"
  engine                    = "aurora-postgresql"
  engine_version           = "15.7"
  database_name            = "ai_swagger_bot"
}
```

#### Розгортання

```bash
# Глобальне розгортання
make -f Makefile.lambda deploy ENVIRONMENT=global

# Terraform розгортання
cd terraform
make quick-deploy ENVIRONMENT=global

# Перевірка глобальної доступності
curl -I https://api.yourcompany.com/health
```

## 🔒 Secure Deployment

### Сценарій: Фінансова компанія

#### Архітектура
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   WAF           │────│   API Gateway   │────│   Lambda        │
│   (Security)    │    │   (Private)      │    │   (VPC)         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   RDS           │
                       │   (Encrypted)   │
                       └─────────────────┘
```

#### Конфігурація

**serverless.yml:**
```yaml
service: ai-swagger-bot-secure

provider:
  name: aws
  runtime: python3.11
  region: us-east-1
  stage: ${opt:stage, 'prod'}
  
  # Security settings
  memorySize: 1024
  timeout: 30
  
  # VPC configuration
  vpc:
    securityGroupIds:
      - sg-secure-lambda
    subnetIds:
      - subnet-private-1a
      - subnet-private-1b

functions:
  api:
    handler: lambda_handler.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true
          authorizer: aws_iam  # IAM авторизація
    
    # Security settings
    memorySize: 1024
    timeout: 30
    
    environment:
      STAGE: ${self:provider.stage}
      ENVIRONMENT: secure
      ENABLE_SECURITY_FEATURES: true
      LOG_LEVEL: INFO
```

**terraform/security.tf:**
```hcl
# WAF Web ACL
resource "aws_wafv2_web_acl" "main" {
  name        = "secure-web-acl"
  description = "WAF Web ACL for secure API"
  scope       = "REGIONAL"
  
  default_action {
    allow {}
  }
  
  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 1
    
    override_action {
      none {}
    }
    
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }
    
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesCommonRuleSetMetric"
      sampled_requests_enabled   = true
    }
  }
  
  rule {
    name     = "RateLimitRule"
    priority = 2
    
    action {
      block {}
    }
    
    statement {
      rate_based_statement {
        limit              = 2000
        aggregate_key_type = "IP"
      }
    }
    
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimitRuleMetric"
      sampled_requests_enabled   = true
    }
  }
  
  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "SecureWebACLMetric"
    sampled_requests_enabled   = true
  }
}

# Secure RDS
resource "aws_db_instance" "main" {
  identifier = "secure-db"
  
  engine         = "postgres"
  engine_version = "15.7"
  instance_class = "db.t3.medium"
  
  allocated_storage     = 50
  max_allocated_storage = 200
  storage_type          = "gp3"
  storage_encrypted     = true
  
  # Security settings
  publicly_accessible = false
  deletion_protection = true
  
  backup_retention_period = 30
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  # Encryption
  kms_key_id = aws_kms_key.rds.arn
}

# KMS Key for RDS encryption
resource "aws_kms_key" "rds" {
  description             = "KMS key for RDS encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true
  
  tags = {
    Environment = "secure"
    Purpose     = "RDS encryption"
  }
}
```

#### Розгортання

```bash
# Безпечне розгортання
make -f Makefile.lambda deploy ENVIRONMENT=secure

# Terraform розгортання
cd terraform
make quick-deploy ENVIRONMENT=secure

# Перевірка безпеки
make security-scan ENVIRONMENT=secure
```

## 📊 Monitoring & Analytics

### Сценарій: Компанія з високими вимогами до моніторингу

#### Архітектура
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CloudWatch    │────│   Lambda        │────│   X-Ray         │
│   (Metrics)     │    │   Function      │    │   (Tracing)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   SNS           │
                       │   (Alerts)      │
                       └─────────────────┘
```

#### Конфігурація

**serverless.yml:**
```yaml
service: ai-swagger-bot-monitored

provider:
  name: aws
  runtime: python3.11
  region: us-east-1
  stage: ${opt:stage, 'prod'}
  
  # Monitoring settings
  memorySize: 1024
  timeout: 30
  
  # CloudWatch settings
  logRetentionInDays: 30
  
  # X-Ray tracing
  tracing:
    lambda: true
    apiGateway: true

functions:
  api:
    handler: lambda_handler.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true
    
    # Monitoring settings
    memorySize: 1024
    timeout: 30
    
    environment:
      STAGE: ${self:provider.stage}
      ENVIRONMENT: monitored
      ENABLE_MONITORING: true
      ENABLE_TRACING: true
      LOG_LEVEL: INFO
```

**terraform/monitoring.tf:**
```hcl
# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "ai-swagger-bot-dashboard"
  
  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        
        properties = {
          metrics = [
            ["AWS/Lambda", "Duration", "FunctionName", "ai-swagger-bot-api-prod"],
            [".", "Errors", ".", "."],
            [".", "Throttles", ".", "."]
          ]
          period = 300
          stat   = "Average"
          region = "us-east-1"
          title  = "Lambda Metrics"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        
        properties = {
          metrics = [
            ["AWS/ApiGateway", "Count", "ApiName", "ai-swagger-bot-api-prod"],
            [".", "Latency", ".", "."],
            [".", "4XXError", ".", "."],
            [".", "5XXError", ".", "."]
          ]
          period = 300
          stat   = "Sum"
          region = "us-east-1"
          title  = "API Gateway Metrics"
        }
      }
    ]
  })
}

# SNS Topic for Alerts
resource "aws_sns_topic" "alerts" {
  name = "ai-swagger-bot-alerts"
}

# CloudWatch Alarm for Lambda Errors
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "lambda-errors-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "Lambda function errors"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    FunctionName = "ai-swagger-bot-api-prod"
  }
}

# CloudWatch Alarm for API Gateway 5XX Errors
resource "aws_cloudwatch_metric_alarm" "api_5xx_errors" {
  alarm_name          = "api-5xx-errors-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "5XXError"
  namespace           = "AWS/ApiGateway"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "API Gateway 5XX errors"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    ApiName = "ai-swagger-bot-api-prod"
  }
}
```

#### Розгортання

```bash
# Моніторинг розгортання
make -f Makefile.lambda deploy ENVIRONMENT=monitored

# Terraform розгортання
cd terraform
make quick-deploy ENVIRONMENT=monitored

# Перевірка моніторингу
aws cloudwatch describe-dashboards --dashboard-name-prefix "ai-swagger-bot"
```

## 🎯 Вибір сценарію

### Критерії вибору

| Сценарій | Бюджет | Безпека | Масштабованість | Моніторинг |
|----------|--------|---------|------------------|------------|
| Startup  | Низький | Базова   | Обмежена         | Мінімальний |
| Enterprise | Високий | Висока  | Висока           | Розширений  |
| Development | Середній | Базова  | Середня          | Базовий     |
| Global   | Високий | Висока  | Дуже висока      | Розширений  |
| Secure   | Високий | Максимальна | Висока       | Розширений  |
| Monitored | Високий | Висока  | Висока           | Максимальний |

### Рекомендації

1. **Startup**: Почати з цього сценарію для швидкого запуску
2. **Development**: Використовувати для команди розробників
3. **Enterprise**: Перейти коли проект зросте
4. **Global**: Розглянути при міжнародному розширенні
5. **Secure**: Використовувати для фінансових або медичних проектів
6. **Monitored**: Додати коли потрібен детальний моніторинг

---

**💡 Порада**: Почніть з простого сценарію та поступово ускладнюйте архітектуру за потреби. 