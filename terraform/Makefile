# Makefile для Terraform інфраструктури AI Swagger Bot

.PHONY: help init plan apply apply-auto destroy output validate format clean

# Variables
ENVIRONMENT ?= dev
AWS_REGION ?= us-east-1
TF_VARS_FILE = terraform.tfvars

help: ## Показати довідку
	@echo "🚀 Terraform команди для AI Swagger Bot:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "📝 Змінні:"
	@echo "  ENVIRONMENT=$(ENVIRONMENT)"
	@echo "  AWS_REGION=$(AWS_REGION)"
	@echo "  TF_VARS_FILE=$(TF_VARS_FILE)"
	@echo ""
	@echo "💡 Приклади:"
	@echo "  make plan ENVIRONMENT=prod"
	@echo "  make apply ENVIRONMENT=staging"

init: ## Ініціалізувати Terraform
	@echo "🔧 Ініціалізую Terraform..."
	terraform init
	@echo "✅ Terraform ініціалізовано"

plan: ## Планувати зміни
	@echo "📋 Планую зміни для $(ENVIRONMENT) середовища..."
	terraform plan \
		-var-file="$(TF_VARS_FILE)" \
		-var="environment=$(ENVIRONMENT)" \
		-var="aws_region=$(AWS_REGION)" \
		-out="terraform.plan"
	@echo "✅ План створено: terraform.plan"

apply: ## Застосувати зміни (з підтвердженням)
	@echo "🚀 Застосовую зміни для $(ENVIRONMENT) середовища..."
	terraform apply "terraform.plan"
	@echo "✅ Зміни застосовано"

apply-auto: ## Застосувати зміни автоматично
	@echo "🚀 Автоматично застосовую зміни для $(ENVIRONMENT) середовища..."
	terraform apply \
		-var-file="$(TF_VARS_FILE)" \
		-var="environment=$(ENVIRONMENT)" \
		-var="aws_region=$(AWS_REGION)" \
		-auto-approve
	@echo "✅ Зміни застосовано автоматично"

destroy: ## Видалити інфраструктуру
	@echo "🗑️ Видаляю інфраструктуру для $(ENVIRONMENT) середовища..."
	terraform destroy \
		-var-file="$(TF_VARS_FILE)" \
		-var="environment=$(ENVIRONMENT)" \
		-var="aws_region=$(AWS_REGION)"
	@echo "✅ Інфраструктуру видалено"

output: ## Показати вихідні дані
	@echo "📤 Вихідні дані Terraform:"
	terraform output

validate: ## Валідувати конфігурацію
	@echo "✅ Валідую Terraform конфігурацію..."
	terraform validate
	@echo "✅ Конфігурація валідна"

format: ## Форматувати код
	@echo "🎨 Форматую Terraform код..."
	terraform fmt -recursive
	@echo "✅ Код відформатовано"

clean: ## Очистити тимчасові файли
	@echo "🧹 Очищаю тимчасові файли..."
	rm -f terraform.plan
	rm -f *.tfstate
	rm -f *.tfstate.backup
	rm -f .terraform.lock.hcl
	rm -rf .terraform/
	@echo "✅ Файли очищено"

# Environment-specific commands
dev: ## Розгорнути dev середовище
	@$(MAKE) apply-auto ENVIRONMENT=dev

staging: ## Розгорнути staging середовище
	@$(MAKE) apply-auto ENVIRONMENT=staging

prod: ## Розгорнути production середовище
	@$(MAKE) apply-auto ENVIRONMENT=prod

# Database commands
db-backup: ## Створити backup бази даних
	@echo "💾 Створюю backup бази даних..."
	@DB_ENDPOINT=$$(terraform output -raw database_endpoint) && \
	DB_NAME=$$(terraform output -raw database_name) && \
	pg_dump -h $$DB_ENDPOINT -U postgres $$DB_NAME > backup_$(ENVIRONMENT)_$$(date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup створено"

# Security commands
security-scan: ## Сканувати безпеку
	@echo "🔒 Сканую безпеку..."
	terraform plan \
		-var-file="$(TF_VARS_FILE)" \
		-var="environment=$(ENVIRONMENT)" \
		-var="aws_region=$(AWS_REGION)" \
		-out="security-scan.tfplan"
	@echo "✅ Сканування безпеки завершено"

# Cost estimation
cost: ## Оцінити вартість
	@echo "💰 Оцінюю вартість інфраструктури..."
	terraform plan \
		-var-file="$(TF_VARS_FILE)" \
		-var="environment=$(ENVIRONMENT)" \
		-var="aws_region=$(AWS_REGION)" \
		-out="cost-estimate.tfplan"
	@echo "✅ Оцінка вартості завершена"

# Import existing resources
import: ## Імпортувати існуючі ресурси
	@echo "📥 Імпортую існуючі ресурси..."
	@echo "💡 Використовуйте: terraform import <resource_type>.<resource_name> <resource_id>"
	@echo "📚 Приклад: terraform import aws_lambda_function.main arn:aws:lambda:us-east-1:123456789012:function:ai-swagger-bot-api-dev"

# Workspace management
workspace-new: ## Створити новий workspace
	@echo "🆕 Створюю новий workspace: $(ENVIRONMENT)"
	terraform workspace new $(ENVIRONMENT) || true
	@echo "✅ Workspace створено"

workspace-select: ## Вибрати workspace
	@echo "🔍 Вибираю workspace: $(ENVIRONMENT)"
	terraform workspace select $(ENVIRONMENT)
	@echo "✅ Workspace вибрано"

workspace-list: ## Показати список workspace'ів
	@echo "📋 Список workspace'ів:"
	terraform workspace list

# State management
state-pull: ## Завантажити стан з S3
	@echo "📥 Завантажую стан з S3..."
	terraform state pull
	@echo "✅ Стан завантажено"

state-push: ## Завантажити стан в S3
	@echo "📤 Завантажую стан в S3..."
	terraform state push
	@echo "✅ Стан завантажено"

# Lock management
force-unlock: ## Примусово розблокувати state
	@echo "🔓 Примусово розблоковую state..."
	@echo "⚠️ Увага! Це може призвести до втрати даних!"
	@read -p "Введіть lock ID: " lock_id; \
	terraform force-unlock $$lock_id
	@echo "✅ State розблоковано"

# Helpers
check-vars: ## Перевірити змінні
	@echo "🔍 Перевіряю змінні..."
	@if [ ! -f "$(TF_VARS_FILE)" ]; then \
		echo "❌ Файл $(TF_VARS_FILE) не знайдено!"; \
		echo "💡 Скопіюйте terraform.tfvars.example в terraform.tfvars"; \
		exit 1; \
	fi
	@echo "✅ Змінні перевірено"

check-aws: ## Перевірити AWS credentials
	@echo "🔐 Перевіряю AWS credentials..."
	@aws sts get-caller-identity > /dev/null 2>&1 || { \
		echo "❌ AWS credentials не налаштовані!"; \
		echo "💡 Виконайте: aws configure"; \
		exit 1; \
	}
	@echo "✅ AWS credentials налаштовані"

# Pre-flight checks
pre-flight: check-vars check-aws ## Виконати pre-flight перевірки
	@echo "✅ Pre-flight перевірки пройдені"

# Full deployment workflow
deploy: pre-flight init plan apply ## Повний workflow розгортання
	@echo "🎉 Розгортання завершено!"

# Quick deployment (without plan)
quick-deploy: pre-flight init apply-auto ## Швидке розгортання без плану
	@echo "🚀 Швидке розгортання завершено!" 