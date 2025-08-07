"""
Pytest configuration file
"""

import os
import sys
from pathlib import Path

# Додаємо src до Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))
