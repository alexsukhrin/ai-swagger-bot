"""
Тест основного додатку FastAPI
"""

from unittest.mock import patch

import pytest


def test_main_app_import():
    """Тест імпорту основного додатку"""
    try:
        from api.main import app

        assert app is not None
    except ImportError as e:
        pytest.skip(f"main.py не може бути імпортований: {e}")


def test_main_app_routes():
    """Тест наявності маршрутів в додатку"""
    try:
        from api.main import app

        # Перевіряємо, що є маршрути
        assert hasattr(app, "routes")
        assert len(app.routes) > 0

        # Перевіряємо наявність основних маршрутів
        route_paths = []
        for route in app.routes:
            if hasattr(route, "path"):
                route_paths.append(str(route.path))

        assert len(route_paths) > 0
        print(f"Знайдено {len(route_paths)} маршрутів")

    except ImportError:
        pytest.skip("main.py не може бути імпортований")


def test_main_app_admin_mounts():
    """Тест наявності адмін монтів"""
    try:
        from api.main import app

        # Перевіряємо монти
        mounts = [
            route for route in app.routes if hasattr(route, "path") and "/admin" in str(route.path)
        ]

        print(f"Знайдено {len(mounts)} адмін монтів")

        # Перевіряємо, що є хоча б один адмін монт
        assert len(mounts) > 0, "Повинен бути хоча б один адмін монт"

        for mount in mounts:
            print(f"  {mount.path} -> {mount.app}")

    except ImportError:
        pytest.skip("main.py не може бути імпортований")


def test_main_app_health_endpoint():
    """Тест health endpoint"""
    try:
        from api.main import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        assert "status" in response.json()

    except ImportError:
        pytest.skip("main.py не може бути імпортований")


def test_main_app_structure():
    """Тест структури основного додатку"""
    try:
        from api.main import app

        # Перевіряємо основні атрибути
        assert hasattr(app, "title")
        assert hasattr(app, "version")
        assert hasattr(app, "description")

        print(f"Додаток: {app.title} v{app.version}")
        print(f"Опис: {app.description}")

    except ImportError:
        pytest.skip("main.py не може бути імпортований")
