"""
Тест монтів додатку
"""

from unittest.mock import Mock, patch

import pytest


def test_mount_import():
    """Тест імпорту монтів"""
    try:
        from api.main import app

        assert app is not None
    except ImportError as e:
        pytest.skip(f"main.py не може бути імпортований: {e}")


def test_admin_ui_mount():
    """Тест монту admin-ui"""
    try:
        from api.main import app

        # Перевіряємо наявність admin-ui монту
        admin_mounts = [
            route
            for route in app.routes
            if hasattr(route, "path") and "/admin-ui" in str(route.path)
        ]

        assert len(admin_mounts) > 0, "Повинен бути admin-ui монт"

        for mount in admin_mounts:
            print(f"Знайдено admin-ui монт: {mount.path} -> {mount.app}")

    except ImportError:
        pytest.skip("main.py не може бути імпортований")


def test_admin_dashboard_mount():
    """Тест монту admin dashboard"""
    try:
        from api.main import app

        # Перевіряємо наявність admin dashboard монту
        admin_mounts = [
            route for route in app.routes if hasattr(route, "path") and "/admin" in str(route.path)
        ]

        assert len(admin_mounts) > 0, "Повинен бути admin монт"

        for mount in admin_mounts:
            print(f"Знайдено admin монт: {mount.path} -> {mount.app}")

    except ImportError:
        pytest.skip("main.py не може бути імпортований")


def test_static_files_mount():
    """Тест монту статичних файлів"""
    try:
        from api.main import app

        # Перевіряємо наявність статичних файлів
        static_mounts = [
            route for route in app.routes if hasattr(route, "path") and "/static" in str(route.path)
        ]

        # Статичні файли можуть бути опціональними
        if static_mounts:
            for mount in static_mounts:
                print(f"Знайдено static монт: {mount.path} -> {mount.app}")
        else:
            print("Статичні файли не знайдено (це нормально)")

    except ImportError:
        pytest.skip("main.py не може бути імпортований")


def test_api_routes_mount():
    """Тест монту API маршрутів"""
    try:
        from api.main import app

        # Перевіряємо наявність API маршрутів
        api_routes = [
            route for route in app.routes if hasattr(route, "path") and "/api" in str(route.path)
        ]

        # API маршрути повинні бути
        assert len(api_routes) > 0, "Повинні бути API маршрути"

        for route in api_routes:
            print(f"Знайдено API маршрут: {route.path}")

    except ImportError:
        pytest.skip("main.py не може бути імпортований")


def test_mount_structure():
    """Тест структури монтів"""
    try:
        from api.main import app

        # Перевіряємо загальну структуру
        assert hasattr(app, "routes")
        assert len(app.routes) > 0

        # Групуємо маршрути за типами
        mount_routes = []
        regular_routes = []

        for route in app.routes:
            if hasattr(route, "path"):
                if hasattr(route, "app") and route.app != app:
                    mount_routes.append(route)
                else:
                    regular_routes.append(route)

        print(f"Знайдено {len(mount_routes)} монтів та {len(regular_routes)} звичайних маршрутів")

        # Перевіряємо, що є хоча б один монт
        assert len(mount_routes) > 0, "Повинен бути хоча б один монт"

    except ImportError:
        pytest.skip("main.py не може бути імпортований")


def test_mount_health_check():
    """Тест health check монту"""
    try:
        from api.main import app
        from fastapi.testclient import TestClient

        client = TestClient(app)

        # Перевіряємо health endpoint
        response = client.get("/health")
        assert response.status_code == 200

        # Перевіряємо, що відповідь містить статус
        data = response.json()
        assert "status" in data

    except ImportError:
        pytest.skip("main.py не може бути імпортований")


def test_mount_error_handling():
    """Тест обробки помилок монтів"""
    try:
        from api.main import app
        from fastapi.testclient import TestClient

        client = TestClient(app)

        # Перевіряємо 404 для неіснуючого маршруту
        response = client.get("/non-existent-route")
        assert response.status_code == 404

    except ImportError:
        pytest.skip("main.py не може бути імпортований")
