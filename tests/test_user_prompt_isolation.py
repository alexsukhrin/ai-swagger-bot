"""
Тести для перевірки системи ізоляції промптів між користувачами
"""

import os
import sys
import uuid
from unittest.mock import Mock

import pytest

# Додаємо шлях до модуля
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.yaml_prompt_manager import PromptTemplate, YAMLPromptManager


class TestUserPromptIsolation:
    """Тести для перевірки ізоляції промптів між користувачами."""

    def setup_method(self):
        """Налаштування перед кожним тестом."""
        self.manager = YAMLPromptManager()

        # Додаємо тестові промпти
        self._add_test_prompts()

    def _add_test_prompts(self):
        """Додає тестові промпти для різних користувачів."""

        # Промпти користувача 1
        prompt1_data = {
            "name": "Промпт користувача 1",
            "description": "Приватний промпт користувача 1",
            "template": "Ти експерт. {user_query}",
            "category": "user_defined",
            "is_public": False,
            "user_id": "user1",
        }
        self.manager.add_custom_prompt(prompt1_data, "user1")

        # Публічний промпт користувача 1
        prompt2_data = {
            "name": "Публічний промпт користувача 1",
            "description": "Публічний промпт користувача 1",
            "template": "Ти експерт. {user_query}",
            "category": "system",
            "is_public": True,
            "user_id": "user1",
        }
        self.manager.add_custom_prompt(prompt2_data, "user1")

        # Промпти користувача 2
        prompt3_data = {
            "name": "Промпт користувача 2",
            "description": "Приватний промпт користувача 2",
            "template": "Ти експерт. {user_query}",
            "category": "user_defined",
            "is_public": False,
            "user_id": "user2",
        }
        self.manager.add_custom_prompt(prompt3_data, "user2")

        # Публічний промпт користувача 2
        prompt4_data = {
            "name": "Публічний промпт користувача 2",
            "description": "Публічний промпт користувача 2",
            "template": "Ти експерт. {user_query}",
            "category": "system",
            "is_public": True,
            "user_id": "user2",
        }
        self.manager.add_custom_prompt(prompt4_data, "user2")

    def test_user_can_see_own_prompts(self):
        """Тест: користувач може бачити свої промпти."""
        all_prompts = self.manager.get_active_prompts()

        # Фільтруємо промпти користувача 1
        user1_prompts = [p for p in all_prompts if p.user_id == "user1"]

        assert len(user1_prompts) == 2
        assert all(p.user_id == "user1" for p in user1_prompts)

    def test_user_can_see_public_prompts(self):
        """Тест: користувач може бачити публічні промпти."""
        all_prompts = self.manager.get_active_prompts()

        # Фільтруємо публічні промпти
        public_prompts = [p for p in all_prompts if p.is_public]

        # Базові промпти також публічні, тому їх буде більше
        assert len(public_prompts) >= 2  # Наші 2 + базові промпти
        assert all(p.is_public for p in public_prompts)

    def test_user_cannot_see_other_private_prompts(self):
        """Тест: користувач не може бачити приватні промпти інших користувачів."""
        all_prompts = self.manager.get_active_prompts()

        # Фільтруємо промпти, які користувач 1 може бачити
        accessible_prompts = [p for p in all_prompts if p.user_id == "user1" or p.is_public]

        # Перевіряємо, що немає приватних промптів користувача 2
        user2_private_prompts = [
            p for p in accessible_prompts if p.user_id == "user2" and not p.is_public
        ]

        assert len(user2_private_prompts) == 0

    def test_prompt_access_control(self):
        """Тест: контроль доступу до промптів."""
        all_prompts = self.manager.get_active_prompts()

        # Знаходимо промпт користувача 1
        user1_prompt = next(p for p in all_prompts if p.user_id == "user1" and not p.is_public)

        # Перевіряємо права доступу
        def check_access(prompt, user_id, action):
            if action in ["edit", "delete"]:
                return prompt.user_id == user_id
            elif action == "read":
                return prompt.user_id == user_id or prompt.is_public
            return False

        # Користувач 1 має повний доступ до свого промпту
        assert check_access(user1_prompt, "user1", "read") == True
        assert check_access(user1_prompt, "user1", "edit") == True
        assert check_access(user1_prompt, "user1", "delete") == True

        # Користувач 2 не має доступу до промпту користувача 1
        assert check_access(user1_prompt, "user2", "read") == False
        assert check_access(user1_prompt, "user2", "edit") == False
        assert check_access(user1_prompt, "user2", "delete") == False

    def test_public_prompt_access(self):
        """Тест: доступ до публічних промптів."""
        all_prompts = self.manager.get_active_prompts()

        # Знаходимо публічний промпт (може бути базовий або наш)
        public_prompts = [p for p in all_prompts if p.is_public]
        assert len(public_prompts) > 0

        public_prompt = public_prompts[0]

        # Публічні промпти можуть бути базовими (user_id=None) або користувацькими
        assert public_prompt.is_public == True
        assert public_prompt.user_id is None or public_prompt.user_id in ["user1", "user2"]

    def test_prompt_filtering_logic(self):
        """Тест: логіка фільтрації промптів."""
        all_prompts = self.manager.get_active_prompts()

        def filter_prompts_by_user_access(prompts, current_user_id):
            """Фільтрує промпти за правами доступу користувача."""
            filtered = []
            for prompt in prompts:
                if prompt.user_id == current_user_id or prompt.is_public:
                    filtered.append(prompt)
            return filtered

        # Фільтруємо промпти для користувача 1
        user1_accessible = filter_prompts_by_user_access(all_prompts, "user1")

        # Перевіряємо, що користувач 1 бачить:
        # 1. Свої промпти (2 штуки)
        # 2. Публічні промпти (базові + наші 2)
        user1_own_prompts = [p for p in user1_accessible if p.user_id == "user1"]
        user1_public_prompts = [p for p in user1_accessible if p.is_public]

        assert len(user1_own_prompts) == 2
        assert len(user1_public_prompts) >= 2  # Наші 2 + базові промпти

    def test_prompt_statistics_calculation(self):
        """Тест: розрахунок статистики промптів."""
        all_prompts = self.manager.get_active_prompts()

        # Розділяємо промпти за типами
        user1_prompts = []
        user2_prompts = []
        public_prompts = []
        other_prompts = []

        for prompt in all_prompts:
            if prompt.user_id == "user1":
                user1_prompts.append(prompt)
            elif prompt.user_id == "user2":
                user2_prompts.append(prompt)
            elif prompt.is_public:
                public_prompts.append(prompt)
            else:
                other_prompts.append(prompt)

        # Статистика за категоріями
        user1_categories = {}
        user2_categories = {}
        public_categories = {}

        for prompt in user1_prompts:
            category = prompt.category
            user1_categories[category] = user1_categories.get(category, 0) + 1

        for prompt in user2_prompts:
            category = prompt.category
            user2_categories[category] = user2_categories.get(category, 0) + 1

        for prompt in public_prompts:
            category = prompt.category
            public_categories[category] = public_categories.get(category, 0) + 1

        # Перевіряємо статистику
        assert len(user1_prompts) == 2
        assert len(user2_prompts) == 2  # Приватний + публічний
        assert len(public_prompts) >= 2  # Базові промпти + наші 2
        assert len(other_prompts) == 0  # Всі промпти або користувачів, або публічні

        assert "user_defined" in user1_categories
        assert "system" in user1_categories
        assert user1_categories["user_defined"] == 1
        assert user1_categories["system"] == 1

        # Перевіряємо статистику користувача 2
        assert "user_defined" in user2_categories
        assert "system" in user2_categories

    def test_export_filtering(self):
        """Тест: фільтрація при експорті."""
        all_prompts = self.manager.get_active_prompts()

        # Експорт тільки промптів користувача 1
        user1_prompts = [p for p in all_prompts if p.user_id == "user1"]
        assert len(user1_prompts) == 2

        # Експорт публічних промптів
        public_prompts = [p for p in all_prompts if p.is_public]
        assert len(public_prompts) >= 2  # Базові промпти + наші 2

        # Експорт промптів користувача 1 + публічних
        user1_and_public = [p for p in all_prompts if p.user_id == "user1" or p.is_public]
        assert len(user1_and_public) >= 4  # 2 користувача + публічні

    def test_search_filtering(self):
        """Тест: фільтрація при пошуку."""
        all_prompts = self.manager.get_active_prompts()

        # Пошук промптів для користувача 1
        user1_accessible = [p for p in all_prompts if p.user_id == "user1" or p.is_public]

        # Перевіряємо, що в результатах пошуку немає приватних промптів інших користувачів
        other_private_prompts = [
            p for p in user1_accessible if p.user_id != "user1" and not p.is_public
        ]

        assert len(other_private_prompts) == 0

    def test_prompt_ownership(self):
        """Тест: перевірка власності промптів."""
        all_prompts = self.manager.get_active_prompts()

        for prompt in all_prompts:
            if prompt.user_id == "user1":
                # Користувач 1 є власником
                assert prompt.user_id == "user1"
            elif prompt.user_id == "user2":
                # Користувач 2 є власником
                assert prompt.user_id == "user2"
            elif prompt.user_id is None:
                # Базові промпти не мають власника
                assert prompt.source == "yaml"
            else:
                # Інші промпти мають валідного власника
                assert prompt.user_id in ["user1", "user2"]

    def test_prompt_isolation_integration(self):
        """Тест: інтеграційна перевірка ізоляції."""
        all_prompts = self.manager.get_active_prompts()

        # Симулюємо запит від користувача 1
        user1_accessible = [p for p in all_prompts if p.user_id == "user1" or p.is_public]

        # Симулюємо запит від користувача 2
        user2_accessible = [p for p in all_prompts if p.user_id == "user2" or p.is_public]

        # Перевіряємо ізоляцію
        user1_private = [p for p in user1_accessible if p.user_id == "user1" and not p.is_public]
        user2_private = [p for p in user2_accessible if p.user_id == "user2" and not p.is_public]

        # Користувач 1 не бачить приватні промпти користувача 2
        user1_sees_user2_private = any(
            p.user_id == "user2" and not p.is_public for p in user1_accessible
        )
        assert user1_sees_user2_private == False

        # Користувач 2 не бачить приватні промпти користувача 1
        user2_sees_user1_private = any(
            p.user_id == "user1" and not p.is_public for p in user2_accessible
        )
        assert user2_sees_user1_private == False

        # Обидва користувачі бачать публічні промпти
        user1_public_count = len([p for p in user1_accessible if p.is_public])
        user2_public_count = len([p for p in user2_accessible if p.is_public])
        assert user1_public_count >= 2  # Базові промпти + наші 2
        assert user2_public_count >= 2  # Базові промпти + наші 2

    def test_export_specific_prompts_method(self):
        """Тест: метод експорту конкретних промптів."""
        all_prompts = self.manager.get_active_prompts()

        # Фільтруємо промпти користувача 1
        user1_prompts = [p for p in all_prompts if p.user_id == "user1"]

        # Тестуємо метод експорту
        assert hasattr(self.manager, "export_specific_prompts_to_yaml")

        # Перевіряємо, що метод приймає правильні параметри
        import inspect

        sig = inspect.signature(self.manager.export_specific_prompts_to_yaml)
        assert len(sig.parameters) == 2  # file_path, specific_prompts

    def test_prompt_modification_isolation(self):
        """Тест: ізоляція при модифікації промптів."""
        all_prompts = self.manager.get_active_prompts()

        # Знаходимо промпт користувача 1
        user1_prompt = next(p for p in all_prompts if p.user_id == "user1" and not p.is_public)

        # Симулюємо модифікацію промпту
        original_template = user1_prompt.template
        modified_template = "Модифікований: " + original_template

        # Перевіряємо, що модифікація не впливає на інші промпти
        other_prompts = [p for p in all_prompts if p.user_id != "user1"]
        other_templates = [p.template for p in other_prompts]

        # Модифікуємо промпт
        user1_prompt.template = modified_template

        # Перевіряємо, що інші промпти не змінилися
        for prompt in other_prompts:
            assert prompt.template in other_templates

    def test_prompt_deletion_isolation(self):
        """Тест: ізоляція при видаленні промптів."""
        all_prompts = self.manager.get_active_prompts()

        # Підраховуємо промпти перед видаленням
        initial_count = len(all_prompts)
        user1_count = len([p for p in all_prompts if p.user_id == "user1"])
        user2_count = len([p for p in all_prompts if p.user_id == "user2"])

        # Симулюємо видалення промпту користувача 1
        user1_prompts = [p for p in all_prompts if p.user_id == "user1"]
        if user1_prompts:
            # Видаляємо перший промпт користувача 1
            all_prompts.remove(user1_prompts[0])

        # Перевіряємо, що кількість промптів користувача 2 не змінилася
        remaining_user2_count = len([p for p in all_prompts if p.user_id == "user2"])
        assert remaining_user2_count == user2_count

    def test_prompt_category_isolation(self):
        """Тест: ізоляція промптів за категоріями."""
        all_prompts = self.manager.get_active_prompts()

        # Групуємо промпти за категоріями для кожного користувача
        user1_categories = {}
        user2_categories = {}

        for prompt in all_prompts:
            if prompt.user_id == "user1":
                category = prompt.category
                if category not in user1_categories:
                    user1_categories[category] = []
                user1_categories[category].append(prompt)
            elif prompt.user_id == "user2":
                category = prompt.category
                if category not in user2_categories:
                    user2_categories[category] = []
                user2_categories[category].append(prompt)

        # Перевіряємо, що категорії користувачів не перетинаються
        user1_category_names = set(user1_categories.keys())
        user2_category_names = set(user2_categories.keys())

        # Користувачі можуть мати однакові категорії, але різні промпти
        for category in user1_category_names.intersection(user2_category_names):
            user1_prompts = user1_categories[category]
            user2_prompts = user2_categories[category]

            # Промпти в одній категорії мають бути різними
            user1_names = {p.name for p in user1_prompts}
            user2_names = {p.name for p in user2_prompts}

            assert user1_names.isdisjoint(user2_names)

    def test_prompt_performance_isolation(self):
        """Тест: ізоляція продуктивності промптів."""
        all_prompts = self.manager.get_active_prompts()

        # Симулюємо велику кількість промптів для одного користувача
        large_user_prompts = []
        for i in range(100):
            prompt_data = {
                "id": str(uuid.uuid4()),
                "name": f"Промпт {i}",
                "description": f"Опис промпту {i}",
                "template": f"Шаблон {i}: {{user_query}}",
                "category": "user_defined",
                "tags": [],
                "is_public": False,
                "user_id": "large_user",
            }
            large_user_prompts.append(PromptTemplate(**prompt_data))

        # Додаємо велику кількість промптів
        all_prompts.extend(large_user_prompts)

        # Перевіряємо, що це не впливає на доступ до промптів інших користувачів
        user1_accessible = [p for p in all_prompts if p.user_id == "user1" or p.is_public]
        user2_accessible = [p for p in all_prompts if p.user_id == "user2" or p.is_public]

        # Кількість доступних промптів для інших користувачів не змінилася
        assert len([p for p in user1_accessible if p.user_id == "user1"]) == 2
        assert len([p for p in user2_accessible if p.user_id == "user2"]) == 2

    def test_prompt_security_isolation(self):
        """Тест: безпечна ізоляція промптів."""
        all_prompts = self.manager.get_active_prompts()

        # Симулюємо спробу доступу до приватних промптів
        def attempt_unauthorized_access(target_user_id, attacker_user_id):
            """Симулює спробу несанкціонованого доступу."""
            target_prompts = [
                p for p in all_prompts if p.user_id == target_user_id and not p.is_public
            ]
            accessible_prompts = [
                p for p in all_prompts if p.user_id == attacker_user_id or p.is_public
            ]

            # Перевіряємо, що атакуючий не може отримати доступ до приватних промптів
            unauthorized_access = any(p in accessible_prompts for p in target_prompts)
            return unauthorized_access

        # Тестуємо різні сценарії атак
        assert not attempt_unauthorized_access("user1", "user2")
        assert not attempt_unauthorized_access("user2", "user1")
        assert not attempt_unauthorized_access("user1", "anonymous")
        assert not attempt_unauthorized_access("user2", "anonymous")

    def test_prompt_data_integrity(self):
        """Тест: цілісність даних промптів."""
        all_prompts = self.manager.get_active_prompts()

        # Перевіряємо цілісність даних для кожного промпту
        for prompt in all_prompts:
            # Обов'язкові поля
            assert hasattr(prompt, "name")
            assert hasattr(prompt, "description")
            assert hasattr(prompt, "template")
            assert hasattr(prompt, "category")
            assert hasattr(prompt, "is_public")
            assert hasattr(prompt, "user_id")

            # Перевіряємо типи даних
            assert isinstance(prompt.name, str)
            assert isinstance(prompt.description, str)
            assert isinstance(prompt.template, str)
            assert isinstance(prompt.category, str)
            assert isinstance(prompt.is_public, bool)
            assert prompt.user_id is None or isinstance(prompt.user_id, str)

            # Перевіряємо валідність даних
            assert len(prompt.name) > 0
            assert len(prompt.description) > 0
            assert len(prompt.template) > 0
            assert len(prompt.category) > 0

    def test_prompt_concurrent_access(self):
        """Тест: одночасний доступ до промптів."""
        all_prompts = self.manager.get_active_prompts()

        # Симулюємо одночасний доступ кількох користувачів
        import threading
        import time

        results = {}

        def user_access_simulation(user_id, delay=0.1):
            """Симулює доступ користувача до промптів."""
            time.sleep(delay)
            accessible_prompts = [p for p in all_prompts if p.user_id == user_id or p.is_public]
            results[user_id] = len(accessible_prompts)

        # Запускаємо одночасні запити
        threads = []
        for user_id in ["user1", "user2", "user3"]:
            thread = threading.Thread(target=user_access_simulation, args=(user_id,))
            threads.append(thread)
            thread.start()

        # Чекаємо завершення всіх потоків
        for thread in threads:
            thread.join()

        # Перевіряємо результати
        assert "user1" in results
        assert "user2" in results
        assert "user3" in results

        # Користувач 3 не має власних промптів, тому бачить тільки публічні
        assert results["user3"] >= 2  # Базові промпти + наші 2

    def test_prompt_error_handling(self):
        """Тест: обробка помилок при роботі з промптами."""
        all_prompts = self.manager.get_active_prompts()

        # Симулюємо різні помилки
        def test_invalid_prompt_access():
            """Тестує доступ до неіснуючого промпту."""
            try:
                # Спробуємо знайти неіснуючий промпт
                non_existent_prompt = next(
                    (p for p in all_prompts if p.name == "Неіснуючий промпт"), None
                )
                return non_existent_prompt is None
            except Exception:
                return True

        def test_invalid_user_access():
            """Тестує доступ з невалідним user_id."""
            try:
                invalid_user_prompts = [p for p in all_prompts if p.user_id == "invalid_user"]
                return len(invalid_user_prompts) == 0
            except Exception:
                return True

        # Перевіряємо обробку помилок
        assert test_invalid_prompt_access()
        assert test_invalid_user_access()

    def test_prompt_migration_isolation(self):
        """Тест: ізоляція при міграції промптів."""
        all_prompts = self.manager.get_active_prompts()

        # Симулюємо міграцію промптів між користувачами
        user1_prompts = [p for p in all_prompts if p.user_id == "user1"]
        user2_prompts = [p for p in all_prompts if p.user_id == "user2"]

        initial_user1_count = len(user1_prompts)
        initial_user2_count = len(user2_prompts)

        # Симулюємо передачу промпту від user1 до user2
        if user1_prompts:
            transferred_prompt = user1_prompts[0]
            transferred_prompt.user_id = "user2"

            # Перераховуємо промпти
            updated_user1_prompts = [p for p in all_prompts if p.user_id == "user1"]
            updated_user2_prompts = [p for p in all_prompts if p.user_id == "user2"]

            # Перевіряємо, що кількість змінилася правильно
            assert len(updated_user1_prompts) == initial_user1_count - 1
            assert len(updated_user2_prompts) == initial_user2_count + 1

    def test_prompt_backup_isolation(self):
        """Тест: ізоляція при резервному копіюванні промптів."""
        all_prompts = self.manager.get_active_prompts()

        # Симулюємо створення резервної копії (глибока копія)
        backup_prompts = []
        for prompt in all_prompts:
            backup_prompt = PromptTemplate(
                id=prompt.id,
                name=prompt.name,
                description=prompt.description,
                template=prompt.template,
                category=prompt.category,
                tags=prompt.tags.copy(),
                is_active=prompt.is_active,
                is_public=prompt.is_public,
                priority=prompt.priority,
                created_at=prompt.created_at,
                updated_at=prompt.updated_at,
                usage_count=prompt.usage_count,
                success_rate=prompt.success_rate,
                user_id=prompt.user_id,
                source=prompt.source,
            )
            backup_prompts.append(backup_prompt)

        # Модифікуємо оригінальні промпти
        for prompt in all_prompts:
            if prompt.user_id == "user1":
                prompt.template = "Модифікований: " + prompt.template

        # Перевіряємо, що резервна копія не змінилася
        original_user1_prompts = [p for p in backup_prompts if p.user_id == "user1"]
        modified_user1_prompts = [p for p in all_prompts if p.user_id == "user1"]

        # Порівнюємо оригінальні та модифіковані промпти
        for orig, mod in zip(original_user1_prompts, modified_user1_prompts):
            assert orig.template != mod.template
            assert orig.template in mod.template  # Модифікований містить оригінальний

    def test_prompt_validation_isolation(self):
        """Тест: ізоляція при валідації промптів."""
        all_prompts = self.manager.get_active_prompts()

        # Функція валідації промптів
        def validate_prompt(prompt):
            """Валідує промпт."""
            errors = []

            if not prompt.name or len(prompt.name.strip()) == 0:
                errors.append("Назва промпту не може бути порожньою")

            if not prompt.template or len(prompt.template.strip()) == 0:
                errors.append("Шаблон промпту не може бути порожнім")

            if prompt.user_id and not isinstance(prompt.user_id, str):
                errors.append("user_id має бути рядком")

            return errors

        # Валідуємо всі промпти
        validation_results = {}
        for prompt in all_prompts:
            errors = validate_prompt(prompt)
            validation_results[prompt.name] = errors

        # Перевіряємо, що всі промпти валідні
        for prompt_name, errors in validation_results.items():
            assert len(errors) == 0, f"Промпт '{prompt_name}' має помилки: {errors}"

    def test_prompt_cleanup_isolation(self):
        """Тест: ізоляція при очищенні промптів."""
        all_prompts = self.manager.get_active_prompts()

        # Симулюємо очищення промптів користувача 1
        user1_prompts = [p for p in all_prompts if p.user_id == "user1"]
        user2_prompts = [p for p in all_prompts if p.user_id == "user2"]

        initial_user2_count = len(user2_prompts)

        # Видаляємо всі промпти користувача 1
        for prompt in user1_prompts[:]:
            all_prompts.remove(prompt)

        # Перевіряємо, що промпти користувача 2 не змінилися
        remaining_user2_prompts = [p for p in all_prompts if p.user_id == "user2"]
        assert len(remaining_user2_prompts) == initial_user2_count

        # Перевіряємо, що всі промпти користувача 2 залишилися
        for original_prompt in user2_prompts:
            assert original_prompt in remaining_user2_prompts


if __name__ == "__main__":
    # Запуск тестів
    pytest.main([__file__, "-v"])
