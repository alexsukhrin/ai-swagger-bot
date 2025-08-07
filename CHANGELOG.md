# Changelog

Всі важливі зміни в цьому проекті будуть документуватися в цьому файлі.

Формат базується на [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
і цей проект дотримується [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CI/CD pipeline з GitHub Actions
- Лінтери: Black, isort, ruff, mypy
- Security scanning: Bandit, Trivy, CodeQL
- Docker тестування та збірка
- Pre-commit hooks
- Автоматичні releases
- Dependabot для оновлення залежностей
- Issue templates та PR templates
- Code of Conduct та Security Policy
- Contributing guidelines

### Changed
- Оновлено Python версію до 3.11+
- Замінено flake8 на ruff
- Покращено структуру проекту

### Fixed
- Виправлено конфігурацію лінтерів
- Оновлено залежності

## [0.1.0] - 2024-01-XX

### Added
- Базова функціональність AI Swagger Bot
- Підтримка Swagger/OpenAPI специфікацій
- RAG система для обробки API
- CLI інтерфейс
- Streamlit веб-інтерфейс
- Логування та обробка помилок
- Базові тести

### Changed
- Початкова версія проекту

### Fixed
- Початкові виправлення

---

## Типи змін

- **Added** - для нової функціональності
- **Changed** - для змін у існуючій функціональності
- **Deprecated** - для функціональності, яка буде видалена
- **Removed** - для видаленої функціональності
- **Fixed** - для виправлення помилок
- **Security** - для виправлення вразливостей безпеки

## Приклади

```markdown
## [1.0.0] - 2024-01-15

### Added
- Нова функція для обробки API запитів
- Підтримка нових форматів відповідей

### Changed
- Покращено продуктивність обробки запитів
- Оновлено документацію

### Fixed
- Виправлено помилку з кодуванням UTF-8
- Виправлено проблему з кешуванням

### Security
- Виправлено вразливість XSS в веб-інтерфейсі
```
