"""
Базовий тест для перевірки конфігурації
"""

import pytest


def test_basic_import():
    """Тест базового імпорту"""
    assert True


def test_environment_variables():
    """Тест змінних середовища"""
    import os

    assert os.getenv("TESTING") == "true"
    assert os.getenv("DATABASE_URL") == "sqlite:///./test.db"


def test_path_configuration():
    """Тест конфігурації шляхів"""
    import sys
    from pathlib import Path

    project_root = Path(__file__).parent.parent
    assert str(project_root) in sys.path
    assert str(project_root / "src") in sys.path
    assert str(project_root / "api") in sys.path
