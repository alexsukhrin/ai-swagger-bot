# Makefile для AI Swagger Bot

.PHONY: help install test run clean lint format docs

# Змінні
PYTHON = python
PIP = pip
STREAMLIT = streamlit
VENV = venv

# Команди для різних ОС
ifeq ($(OS),Windows_NT)
	PYTHON_VENV = $(VENV)\Scripts\python
	PIP_VENV = $(VENV)\Scripts\pip
	ACTIVATE = $(VENV)\Scripts\activate
else
	# Перевіряємо чи використовується conda
	PYTHON_VENV = python
	PIP_VENV = pip
	ACTIVATE = conda activate ai-swagger
endif

# CLI Тестер команди
CLI_TESTER = $(PYTHON_VENV) cli_tester.py
INTERACTIVE_CLI = $(PYTHON_VENV) interactive_cli.py
QUICK_TEST = $(PYTHON_VENV) quick_test.py

help: ## Показати довідку
	@echo "AI Swagger Bot - Доступні команди:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Встановити проект
	@echo "🚀 Встановлення AI Swagger Bot..."
	$(PYTHON) setup.py

install-dev: ## Встановити проект з dev залежностями
	@echo "🔧 Встановлення з dev залежностями..."
	$(PIP_VENV) install -r requirements.txt
	$(PIP_VENV) install -r requirements-dev.txt
	cp env_example.txt .env
	@echo "✅ Встановлення завершено!"

test: ## Run all tests
	python -m pytest tests/ -v --tb=short

test-fast: ## Run tests quickly (without slow tests)
	python -m pytest tests/ -v --tb=short -m "not slow"

test-coverage: ## Run tests with coverage
	python -m pytest tests/ -v --tb=short --cov=src --cov-report=html

test-clean: ## Clear pytest cache and run tests
	python -m pytest tests/ -v --tb=short --cache-clear

run: ## Запустити Streamlit додаток
	@echo "🌐 Запуск Streamlit додатку..."
	$(PYTHON_VENV) -m streamlit run app.py

run-api: ## Запустити FastAPI сервіс
	@echo "🚀 Запуск FastAPI сервісу..."
	$(PYTHON_VENV) -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

create-admin: ## Створити адміністратора
	@echo "👤 Створення адміністратора..."
	$(PYTHON_VENV) scripts/create_admin.py

run-cli: ## Запустити CLI інтерфейс
	@echo "💻 Запуск CLI інтерфейсу..."
	$(PYTHON_VENV) cli.py --swagger examples/swagger_specs/shop_api.json

# CLI Тестер команди
cli-test: ## Запустити CLI тестер (командний режим)
	@echo "🔧 Запуск CLI тестера..."
	$(CLI_TESTER) health

cli-interactive: ## Запустити інтерактивний CLI тестер
	@echo "🎮 Запуск інтерактивного CLI тестера..."
	$(INTERACTIVE_CLI)

cli-quick: ## Запустити швидкий тест CLI
	@echo "⚡ Запуск швидкого тесту CLI..."
	$(QUICK_TEST)

cli-health: ## Health check через CLI
	@echo "🏥 Health check через CLI..."
	$(CLI_TESTER) health

cli-demo-user: ## Створити демо користувача через CLI
	@echo "👤 Створення демо користувача через CLI..."
	$(CLI_TESTER) demo-user

cli-upload-swagger: ## Завантажити Swagger через CLI
	@echo "📁 Завантаження Swagger через CLI..."
	$(CLI_TESTER) upload-swagger --file examples/swagger_specs/shop_api.json

cli-chat: ## Чат з AI через CLI
	@echo "💬 Чат з AI через CLI..."
	$(CLI_TESTER) chat --message "Покажи всі доступні endpoints"

cli-prompts: ## Перегляд промптів через CLI
	@echo "📝 Перегляд промптів через CLI..."
	$(CLI_TESTER) prompts

cli-create-prompt: ## Створити кастомний промпт через CLI
	@echo "✨ Створення кастомного промпту через CLI..."
	$(CLI_TESTER) create-prompt --name "Мій промпт" --description "Опис" --template "Ти експерт {user_query}" --category user_defined

cli-search-prompts: ## Пошук промптів через CLI
	@echo "🔍 Пошук промптів через CLI..."
	$(CLI_TESTER) search-prompts --query "створення"

cli-export-prompts: ## Експорт промптів через CLI
	@echo "📤 Експорт промптів через CLI..."
	$(CLI_TESTER) export-prompts --include-custom

cli-full-test: ## Повний цикл тестування через CLI
	@echo "🚀 Повний цикл тестування через CLI..."
	$(MAKE) cli-health
	$(MAKE) cli-demo-user
	$(MAKE) cli-upload-swagger
	$(MAKE) cli-chat
	$(MAKE) cli-prompts
	$(MAKE) cli-create-prompt
	$(MAKE) cli-search-prompts
	$(MAKE) cli-export-prompts
	@echo "✅ Повний цикл тестування завершено!"

cli-help: ## Довідка по CLI командам
	@echo "🔧 CLI Тестер - Доступні команди:"
	@echo ""
	@echo "🏥 Health Check:"
	@echo "  make cli-health"
	@echo ""
	@echo "👤 Демо користувач:"
	@echo "  make cli-demo-user"
	@echo ""
	@echo "📁 Завантаження Swagger:"
	@echo "  make cli-upload-swagger"
	@echo ""
	@echo "💬 Чат з AI:"
	@echo "  make cli-chat"
	@echo ""
	@echo "📝 Промпти:"
	@echo "  make cli-prompts"
	@echo ""
	@echo "✨ Створення промпту:"
	@echo "  make cli-create-prompt"
	@echo ""
	@echo "🔍 Пошук промптів:"
	@echo "  make cli-search-prompts"
	@echo ""
	@echo "📤 Експорт промптів:"
	@echo "  make cli-export-prompts"
	@echo ""
	@echo "🎮 Інтерактивний режим:"
	@echo "  make cli-interactive"
	@echo ""
	@echo "⚡ Швидкий тест:"
	@echo "  make cli-quick"
	@echo ""
	@echo "🚀 Повний цикл:"
	@echo "  make cli-full-test"

run-examples: ## Запустити приклади
	@echo "📝 Запуск прикладів..."
	$(PYTHON_VENV) examples/basic_usage.py

lint: ## Перевірити код
	@echo "🔍 Перевірка коду..."
	$(PYTHON_VENV) -m black --check src/ tests/ examples/
	$(PYTHON_VENV) -m isort --check-only src/ tests/ examples/

format: ## Форматувати код
	@echo "🎨 Форматування коду..."
	$(PYTHON_VENV) -m black src/ tests/ examples/
	$(PYTHON_VENV) -m isort src/ tests/ examples/

clean: ## Очистити проект
	@echo "🧹 Очищення проекту..."
	rm -rf __pycache__/
	rm -rf src/__pycache__/
	rm -rf tests/__pycache__/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf chroma_db/
	rm -rf logs/
	@echo "✅ Очищення завершено!"

clean-venv: ## Видалити віртуальне середовище
	@echo "🗑️ Видалення віртуального середовища..."
	rm -rf $(VENV)
	@echo "✅ Віртуальне середовище видалено!"

docs: ## Створити документацію
	@echo "📚 Створення документації..."
	$(PIP_VENV) install pdoc3
	$(PYTHON_VENV) -m pdoc --html --output-dir docs src/
	@echo "✅ Документація створена в docs/"

check: ## Перевірити проект
	@echo "🔍 Перевірка проекту..."
	$(MAKE) lint
	$(MAKE) test

ci: ## Запустити CI/CD локально
	@echo "🚀 Запуск CI/CD локально..."
	$(MAKE) lint
	$(MAKE) test-coverage
	$(MAKE) security-check
	$(MAKE) docker-test

security-check: ## Перевірити безпеку
	@echo "🔒 Перевірка безпеки..."
	$(PYTHON_VENV) -m bandit -r src/ -f json -o bandit-report.json || true

docker-test: ## Тестувати Docker образ
	@echo "🐳 Тестування Docker образу..."
	docker build -t ai-swagger-bot:test .
	docker run --rm ai-swagger-bot:test python -c "import sys; print('Python version:', sys.version)"
	docker run --rm ai-swagger-bot:test python -m pytest tests/ -v

docker-compose-test: ## Тестувати з Docker Compose
	@echo "🐳 Тестування з Docker Compose..."
	docker-compose -f docker-compose.test.yml run --rm test
	docker-compose -f docker-compose.test.yml run --rm lint

docker-up: ## Запустити проект з Docker Compose
	@echo "🚀 Запуск проекту з Docker Compose..."
	docker-compose up -d

docker-down: ## Зупинити проект
	@echo "🛑 Зупинка проекту..."
	docker-compose down

docker-logs: ## Показати логи
	@echo "📋 Логи проекту..."
	docker-compose logs -f

docker-rebuild: ## Перебудувати та запустити проект
	@echo "🔨 Перебудування та запуск проекту..."
	docker-compose down
	docker-compose up --build -d

docker-status: ## Статус сервісів
	@echo "📊 Статус сервісів..."
	docker-compose ps

pre-commit-install: ## Встановити pre-commit hooks
	@echo "🔧 Встановлення pre-commit hooks..."
	$(PIP_VENV) install pre-commit
	$(PYTHON_VENV) -m pre_commit install

pre-commit-run: ## Запустити pre-commit на всіх файлах
	@echo "🔧 Запуск pre-commit..."
	$(PYTHON_VENV) -m pre_commit run --all-files
	@echo "✅ Pre-commit перевірка завершена!"

dev-setup: ## Налаштування для розробки
	@echo "⚙️ Налаштування для розробки..."
	$(MAKE) install-dev
	$(MAKE) format
	$(MAKE) check
	@echo "✅ Налаштування завершено!"

# Команди для роботи з агентами
test-simple-agent: ## Тестувати простий агент
	@echo "🤖 Тестування простого агента..."
	$(PYTHON_VENV) -c "from src.simple_agent import SimpleSwaggerAgent; print('✅ SimpleSwaggerAgent імпортовано')"

test-api-agent: ## Тестувати API агент
	@echo "🤖 Тестування API агента..."
	$(PYTHON_VENV) -c "from src.api_agent import SwaggerAgent; print('✅ SwaggerAgent імпортовано')"

# Команди для роботи з Swagger файлами
list-specs: ## Показати доступні Swagger специфікації
	@echo "📋 Доступні Swagger специфікації:"
	@ls -la examples/swagger_specs/

validate-specs: ## Валідувати Swagger специфікації
	@echo "✅ Валідація Swagger специфікацій..."
	@for file in examples/swagger_specs/*.json; do \
		echo "Перевірка $$file..."; \
		$(PYTHON_VENV) -c "import json; json.load(open('$$file')); print('✅ $$file - валідний')"; \
	done

# Команди для моніторингу
logs: ## Показати логи
	@echo "📋 Логи:"
	@if [ -d "logs" ]; then ls -la logs/; else echo "Директорія logs не існує"; fi

monitor: ## Моніторинг системи
	@echo "📊 Моніторинг системи:"
	@echo "Python версія: $$(python --version)"
	@echo "Віртуальне середовище: $$(if [ -d "venv" ]; then echo "Активне"; else echo "Не активне"; fi)"
	@echo "OpenAI API ключ: $$(if [ -n "$$OPENAI_API_KEY" ]; then echo "Встановлено"; else echo "Не встановлено"; fi)"

# Команди для розгортання
build: ## Зібрати проект
	@echo "🔨 Збірка проекту..."
	$(MAKE) clean
	$(MAKE) install
	$(MAKE) test
	@echo "✅ Збірка завершена!"

package: ## Створити пакет
	@echo "📦 Створення пакету..."
	$(PYTHON_VENV) setup.py sdist bdist_wheel
	@echo "✅ Пакет створено!"

# Допоміжні команди
status: ## Показати статус проекту
	@echo "📊 Статус проекту:"
	@echo "Python: $$(python --version)"
	@echo "Віртуальне середовище: $$(if [ -d "venv" ]; then echo "✅"; else echo "❌"; fi)"
	@echo "Залежності: $$(if [ -f "requirements.txt" ]; then echo "✅"; else echo "❌"; fi)"
	@echo "Тести: $$(if [ -d "tests" ]; then echo "✅"; else echo "❌"; fi)"
	@echo "Swagger файли: $$(ls examples/swagger_specs/*.json 2>/dev/null | wc -l) файлів"

help-dev: ## Довідка для розробників
	@echo "🔧 Команди для розробки:"
	@echo "  make install-dev    - Встановити з dev залежностями"
	@echo "  make format         - Форматувати код"
	@echo "  make lint           - Перевірити код"
	@echo "  make test           - Запустити тести"
	@echo "  make test-coverage  - Тести з покриттям"
	@echo "  make check          - Повна перевірка"
	@echo "  make clean          - Очистити проект"
	@echo "  make docs           - Створити документацію"
