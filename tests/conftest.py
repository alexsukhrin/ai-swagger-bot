"""
Pytest configuration file for tests
"""

import os
import sys
from pathlib import Path

# Додаємо src та api до Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
api_path = project_root / "api"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(api_path))
sys.path.insert(0, str(project_root))

# Налаштування тестового середовища
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from unittest.mock import patch

# Мокаємо створення таблиць при імпорті
import pytest

# Мокаємо create_tables перед імпортом api модулів
with patch("api.database.create_tables"):
    pass
