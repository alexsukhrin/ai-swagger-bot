# AI Swagger Bot CLI Makefile

# Встановлюємо TOKENIZERS_PARALLELISM=false для прибирання попереджень
export TOKENIZERS_PARALLELISM=false

.PHONY: help install test clean run add-swagger chat list-apis remove-api info search export-api import-api clear-all stats test-api interactive status version analyze-swagger db-info clear-database reload-swagger reset-system quick-reload show-prompts export-prompts

# Default target
help:
	@echo "AI Swagger Bot CLI - доступні команди:"
	@echo ""
	@echo "  install        - Встановити залежності"
	@echo "  test           - Запустити тести"
	@echo "  clean          - Очистити проект"
	@echo "  run            - Запустити CLI з інтерактивним меню"
	@echo "  add-swagger    - Додати Swagger API (приклад: make add-swagger URL=https://api.oneshop.click/docs/ai-json NAME=oneshop)"
	@echo "  chat           - Відправити повідомлення боту (приклад: make chat MESSAGE='Покажи всі категорії')"
	@echo "  list-apis      - Показати список доступних API"
	@echo "  remove-api     - Видалити API (приклад: make remove-api NAME=oneshop)"
	@echo "  info           - Інформація про систему або API (приклад: make info NAME=oneshop)"
	@echo "  search         - Пошук ендпоінтів (приклад: make search QUERY='створення категорії')"
	@echo "  export-api     - Експорт API (приклад: make export-api NAME=oneshop)"
	@echo "  import-api     - Імпорт API з файлу (приклад: make import-api FILE=swagger.json NAME=myapi)"
	@echo "  clear-all      - Очистити всі API"
	@echo "  stats          - Статистика системи"
	@echo "  test-api       - Тестування API (приклад: make test-api NAME=oneshop)"
	@echo "  interactive    - Інтерактивний режим"
	@echo "  status         - Статус системи"
	@echo "  version        - Версія CLI"
	@echo "  analyze-swagger - Детальний аналіз API (приклад: make analyze-swagger NAME=oneshop)"
	@echo "  db-info        - Інформація про базу даних"
	@echo "  clear-database - Повністю очистити базу даних ChromaDB"
	@echo "  reload-swagger - Перезавантажити Swagger API (приклад: make reload-swagger URL=https://api.oneshop.click/docs/ai-json NAME=oneshop)"
	@echo "  reset-system   - Повністю скинути систему"
	@echo "  quick-reload   - Швидко перезавантажити API (приклад: make quick-reload URL=https://api.oneshop.click/docs/ai-json NAME=oneshop)"
	@echo "  show-prompts   - Показати спеціалізовані промпти (приклад: make show-prompts NAME=oneshop)"
	@echo "  export-prompts - Експорт спеціалізованих промптів (приклад: make export-prompts NAME=oneshop)"
	@echo ""
	@echo "Приклади використання:"
	@echo "  make add-swagger URL=https://api.oneshop.click/docs/ai-json NAME=oneshop"
	@echo "  make chat MESSAGE='Покажи всі категорії'"
	@echo "  make show-prompts NAME=oneshop"
	@echo "  make export-prompts NAME=oneshop OUTPUT=my_prompts.json"

# Встановлення залежностей
install:
	@echo "📦 Встановлення залежностей..."
	pip install -r requirements.txt
	@echo "✅ Залежності встановлено"

# Запуск тестів
test:
	@echo "🧪 Запуск тестів..."
	python -m pytest tests/ -v
	@echo "✅ Тести завершено"

# Очищення проекту
clean:
	@echo "🧹 Очищення проекту..."
	rm -rf __pycache__/
	rm -rf src/__pycache__/
	rm -rf .pytest_cache/
	rm -rf chroma_db/
	@echo "✅ Проект очищено"

# Запуск CLI
run:
	@echo "🚀 Запуск AI Swagger Bot CLI..."
	python cli.py

# Додавання Swagger API
add-swagger:
	@if [ -z "$(URL)" ]; then \
		echo "❌ Помилка: Вкажіть URL для Swagger API"; \
		echo "Приклад: make add-swagger URL=https://api.oneshop.click/docs/ai-json NAME=oneshop"; \
		exit 1; \
	fi
	@if [ -z "$(NAME)" ]; then \
		python cli.py add-swagger "$(URL)"; \
	else \
		python cli.py add-swagger "$(URL)" --name "$(NAME)"; \
	fi

# Відправка повідомлення боту
chat:
	@if [ -z "$(MESSAGE)" ]; then \
		echo "❌ Помилка: Вкажіть повідомлення для бота"; \
		echo "Приклад: make chat MESSAGE='Покажи всі категорії'"; \
		exit 1; \
	fi
	python cli.py chat "$(MESSAGE)"

# Список API
list-apis:
	@echo "📚 Список доступних API:"
	python cli.py list-apis

# Видалення API
remove-api:
	@if [ -z "$(NAME)" ]; then \
		echo "❌ Помилка: Вкажіть назву API для видалення"; \
		echo "Приклад: make remove-api NAME=oneshop"; \
		exit 1; \
	fi
	python cli.py remove-api "$(NAME)"

# Інформація про систему або API
info:
	@if [ -z "$(NAME)" ]; then \
		python cli.py info; \
	else \
		python cli.py info --name "$(NAME)"; \
	fi

# Пошук ендпоінтів
search:
	@if [ -z "$(QUERY)" ]; then \
		echo "❌ Помилка: Вкажіть пошуковий запит"; \
		echo "Приклад: make search QUERY='створення категорії'"; \
		exit 1; \
	fi
	@if [ -z "$(API)" ]; then \
		python cli.py search "$(QUERY)"; \
	else \
		python cli.py search "$(QUERY)" --api "$(API)"; \
	fi

# Експорт API
export-api:
	@if [ -z "$(NAME)" ]; then \
		echo "❌ Помилка: Вкажіть назву API для експорту"; \
		echo "Приклад: make export-api NAME=oneshop"; \
		exit 1; \
	fi
	@if [ -z "$(OUTPUT)" ]; then \
		python cli.py export-api "$(NAME)"; \
	else \
		python cli.py export-api "$(NAME)" --output "$(OUTPUT)"; \
	fi

# Імпорт API з файлу
import-api:
	@if [ -z "$(FILE)" ]; then \
		echo "❌ Помилка: Вкажіть шлях до файлу"; \
		echo "Приклад: make import-api FILE=swagger.json NAME=myapi"; \
		exit 1; \
	fi
	@if [ -z "$(NAME)" ]; then \
		python cli.py import-api "$(FILE)"; \
	else \
		python cli.py import-api "$(FILE)" --name "$(NAME)"; \
	fi

# Очищення всіх API
clear-all:
	@echo "🧹 Очищення всіх API..."
	python cli.py clear-all

# Статистика системи
stats:
	@echo "📊 Статистика системи:"
	python cli.py stats

# Тестування API
test-api:
	@if [ -z "$(NAME)" ]; then \
		echo "❌ Помилка: Вкажіть назву API для тестування"; \
		echo "Приклад: make test-api NAME=oneshop"; \
		exit 1; \
	fi
	python cli.py test-api "$(NAME)"

# Інтерактивний режим
interactive:
	@echo "🎮 Запуск інтерактивного режиму..."
	python cli.py interactive

# Статус системи
status:
	@echo "📊 Статус системи:"
	python cli.py status

# Версія CLI
version:
	@echo "🚀 Версія CLI:"
	python cli.py version

# Детальний аналіз Swagger API
analyze-swagger:
	@if [ -z "$(NAME)" ]; then \
		echo "❌ Помилка: Вкажіть назву API для аналізу"; \
		echo "Приклад: make analyze-swagger NAME=oneshop"; \
		exit 1; \
	fi
	@echo "🔍 Детальний аналіз API: $(NAME)"
	python cli.py analyze-swagger "$(NAME)"

# Інформація про базу даних
db-info:
	@echo "🗄️  Інформація про базу даних:"
	python cli.py db-info

# Очищення бази даних
clear-database:
	@echo "🗄️  Очищення бази даних:"
	python cli.py clear-database

# Перезавантаження Swagger API
reload-swagger:
	@if [ -z "$(URL)" ]; then \
		echo "❌ Помилка: Вкажіть URL для Swagger API"; \
		echo "Приклад: make reload-swagger URL=https://api.oneshop.click/docs/ai-json NAME=oneshop"; \
		exit 1; \
	fi
	@echo "🔄 Перезавантаження Swagger API: $(URL)"
	@if [ -z "$(NAME)" ]; then \
		python cli.py reload-swagger "$(URL)"; \
	else \
		python cli.py reload-swagger "$(URL)" --name "$(NAME)"; \
	fi

# Скидання системи
reset-system:
	@echo "🔄 Скидання системи:"
	python cli.py reset-system

# Швидке перезавантаження API
quick-reload:
	@if [ -z "$(URL)" ]; then \
		echo "❌ Помилка: Вкажіть URL для Swagger API"; \
		echo "Приклад: make quick-reload URL=https://api.oneshop.click/docs/ai-json NAME=oneshop"; \
		exit 1; \
	fi
	@echo "⚡ Швидке перезавантаження API: $(URL)"
	@if [ -z "$(NAME)" ]; then \
		python cli.py quick-reload "$(URL)"; \
	else \
		python cli.py quick-reload "$(URL)" --name "$(NAME)"; \
	fi

# Показати спеціалізовані промпти
show-prompts:
	@if [ -z "$(NAME)" ]; then \
		echo "❌ Помилка: Вкажіть назву API"; \
		echo "Приклад: make show-prompts NAME=oneshop"; \
		exit 1; \
	fi
	@echo "📝 Спеціалізовані промпти для API: $(NAME)"
	python cli.py show-prompts "$(NAME)"

# Експорт спеціалізованих промптів
export-prompts:
	@if [ -z "$(NAME)" ]; then \
		echo "❌ Помилка: Вкажіть назву API"; \
		echo "Приклад: make export-prompts NAME=oneshop"; \
		exit 1; \
	fi
	@echo "📤 Експорт промптів для API: $(NAME)"
	@if [ -z "$(OUTPUT)" ]; then \
		python cli.py export-prompts "$(NAME)"; \
	else \
		python cli.py export-prompts "$(NAME)" --output "$(OUTPUT)"; \
	fi

# Швидкий старт з Oneshop API
quick-start:
	@echo "🚀 Швидкий старт з Oneshop API..."
	python cli.py add-swagger https://api.oneshop.click/docs/ai-json --name oneshop
	@echo "✅ Oneshop API додано! Тепер можете тестувати:"
	@echo "  make chat MESSAGE='Покажи всі доступні ендпоінти'"

# Перевірка статусу (застаріла, використовуйте make status)
check-status:
	@echo "⚠️  Команда 'check-status' застаріла. Використовуйте 'make status'"
	@$(MAKE) status

# Демо запити
demo:
	@echo "🎯 Демо запити:"
	@echo "1. Додавання Oneshop API:"
	@echo "   make add-swagger URL=https://api.oneshop.click/docs/ai-json NAME=oneshop"
	@echo ""
	@echo "2. Тестування чату:"
	@echo "   make chat MESSAGE='Покажи всі доступні ендпоінти'"
	@echo "   make chat MESSAGE='Як створити нову категорію?'"
	@echo "   make chat MESSAGE='Опиши ендпоінт для створення продукту'"
	@echo ""
	@echo "3. Управління API:"
	@echo "   make list-apis"
	@echo "   make remove-api NAME=oneshop"
	@echo ""
	@echo "4. Нова функціональність:"
	@echo "   make info"
	@echo "   make search QUERY='створення категорії'"
	@echo "   make stats"
	@echo "   make test-api NAME=oneshop"
	@echo "   make interactive"
	@echo "   make status"
	@echo "   make version"
	@echo "   make analyze-swagger NAME=oneshop"
	@echo "   make db-info"
	@echo ""
	@echo "5. Управління базою даних:"
	@echo "   make clear-database"
	@echo "   make reload-swagger URL=https://api.oneshop.click/docs/ai-json NAME=oneshop"
	@echo "   make reset-system"
	@echo "   make quick-reload URL=https://api.oneshop.click/docs/ai-json NAME=oneshop"
	@echo ""
	@echo "6. Спеціалізовані промпти:"
	@echo "   make show-prompts NAME=oneshop"
	@echo "   make export-prompts NAME=oneshop"

# Повний цикл тестування
test-all:
	@echo "🚀 Повний цикл тестування CLI..."
	@echo "1. Перевірка статусу..."
	@$(MAKE) status
	@echo ""
	@echo "2. Додавання API..."
	@$(MAKE) add-swagger URL=https://api.oneshop.click/docs/ai-json NAME=oneshop
	@echo ""
	@echo "3. Тестування основних функцій..."
	@$(MAKE) list-apis
	@$(MAKE) info
	@$(MAKE) stats
	@$(MAKE) test-api NAME=oneshop
	@echo ""
	@echo "4. Тестування пошуку..."
	@$(MAKE) search QUERY="Покажи всі доступні ендпоінти"
	@echo ""
	@echo "5. Тестування чату..."
	@$(MAKE) chat MESSAGE="Опиши як створити нову категорію"
	@echo ""
	@echo "6. Тестування нових команд..."
	@$(MAKE) status
	@$(MAKE) version
	@$(MAKE) analyze-swagger NAME=oneshop
	@$(MAKE) db-info
	@echo ""
	@echo "7. Тестування управління базою даних..."
	@$(MAKE) quick-reload URL=https://api.oneshop.click/docs/ai-json NAME=oneshop
	@$(MAKE) db-info
	@echo ""
	@echo "8. Тестування спеціалізованих промптів..."
	@$(MAKE) show-prompts NAME=oneshop
	@$(MAKE) export-prompts NAME=oneshop
	@echo ""
	@echo "✅ Повний цикл тестування завершено!"

# Швидкі команди (аліаси)
ls: list-apis
show: list-apis
apis: list-apis
api: list-apis
