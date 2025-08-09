#!/bin/bash

# Скрипт для запуску інтеграційних тестів бази даних

set -e

echo "🚀 Запуск інтеграційних тестів бази даних..."

# Кольори для виводу
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функція для виводу повідомлень
print_message() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Перевірка наявності Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker не знайдено. Будь ласка, встановіть Docker."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose не знайдено. Будь ласка, встановіть Docker Compose."
    exit 1
fi

# Функція очищення
cleanup() {
    print_message "Очищення тестових контейнерів..."
    docker-compose -f docker-compose.integration.yml down -v 2>/dev/null || true
    docker-compose -f docker-compose.test.yml down -v 2>/dev/null || true
}

# Встановлення trap для очищення при виході
trap cleanup EXIT

# Функція для запуску тестів
run_tests() {
    local test_type=$1
    local description=$2

    print_message "Запуск $description..."

    if docker-compose -f docker-compose.integration.yml up --build $test_type --exit-code-from $test_type; then
        print_success "$description завершено успішно!"
        return 0
    else
        print_error "$description завершено з помилками!"
        return 1
    fi
}

# Основна логіка
main() {
    print_message "Початок інтеграційного тестування..."

    # Очищення попередніх тестів
    cleanup

    # Масив для зберігання результатів
    declare -a test_results

    # 1. Тести інтеграції бази даних
    print_message "=== Тести інтеграції бази даних ==="
    if run_tests "integration-tests" "тестів інтеграції бази даних"; then
        test_results+=("integration-tests: PASS")
    else
        test_results+=("integration-tests: FAIL")
    fi

    # 2. Тести продуктивності
    print_message "=== Тести продуктивності ==="
    if run_tests "performance-tests" "тестів продуктивності"; then
        test_results+=("performance-tests: PASS")
    else
        test_results+=("performance-tests: FAIL")
    fi

    # 3. Тести API інтеграції
    print_message "=== Тести API інтеграції ==="
    if run_tests "api-integration-tests" "тестів API інтеграції"; then
        test_results+=("api-integration-tests: PASS")
    else
        test_results+=("api-integration-tests: FAIL")
    fi

    # 4. Повні інтеграційні тести
    print_message "=== Повні інтеграційні тести ==="
    if run_tests "full-integration-tests" "повних інтеграційних тестів"; then
        test_results+=("full-integration-tests: PASS")
    else
        test_results+=("full-integration-tests: FAIL")
    fi

    # Виведення результатів
    print_message "=== Результати тестування ==="
    local passed=0
    local failed=0

    for result in "${test_results[@]}"; do
        if [[ $result == *": PASS" ]]; then
            print_success "$result"
            ((passed++))
        else
            print_error "$result"
            ((failed++))
        fi
    done

    print_message "Підсумок: $passed успішних, $failed невдалих тестів"

    if [ $failed -eq 0 ]; then
        print_success "Всі інтеграційні тести пройшли успішно!"
        exit 0
    else
        print_error "Деякі тести завершилися з помилками."
        exit 1
    fi
}

# Функція для запуску окремих тестів
run_specific_test() {
    local test_name=$1

    case $test_name in
        "integration")
            run_tests "integration-tests" "тестів інтеграції бази даних"
            ;;
        "performance")
            run_tests "performance-tests" "тестів продуктивності"
            ;;
        "api")
            run_tests "api-integration-tests" "тестів API інтеграції"
            ;;
        "full")
            run_tests "full-integration-tests" "повних інтеграційних тестів"
            ;;
        *)
            print_error "Невідомий тип тесту: $test_name"
            print_message "Доступні типи: integration, performance, api, full"
            exit 1
            ;;
    esac
}

# Обробка аргументів командного рядка
case "${1:-}" in
    "integration")
        run_specific_test "integration"
        ;;
    "performance")
        run_specific_test "performance"
        ;;
    "api")
        run_specific_test "api"
        ;;
    "full")
        run_specific_test "full"
        ;;
    "help"|"-h"|"--help")
        echo "Використання: $0 [тип_тесту]"
        echo ""
        echo "Типи тестів:"
        echo "  integration  - Тести інтеграції бази даних"
        echo "  performance  - Тести продуктивності"
        echo "  api          - Тести API інтеграції"
        echo "  full         - Повні інтеграційні тести"
        echo "  (без аргументів) - Запуск всіх тестів"
        echo ""
        echo "Приклади:"
        echo "  $0                    # Запуск всіх тестів"
        echo "  $0 integration        # Тільки тести інтеграції"
        echo "  $0 performance        # Тільки тести продуктивності"
        ;;
    "")
        main
        ;;
    *)
        print_error "Невідомий аргумент: $1"
        print_message "Використайте '$0 help' для довідки"
        exit 1
        ;;
esac
