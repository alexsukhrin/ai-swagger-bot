#!/usr/bin/env python3

import requests


def check_prompts():
    """Перевіряє промпт шаблони в SQLAdmin"""

    # Перевіряємо головну сторінку SQLAdmin
    response = requests.get("http://localhost:8000/admin/")
    if response.status_code == 200:
        print("✅ SQLAdmin працює")
    else:
        print(f"❌ SQLAdmin не працює: {response.status_code}")
        return

    # Перевіряємо промпт шаблони
    response = requests.get("http://localhost:8000/admin/prompt-template/list")
    if response.status_code == 200:
        print("✅ Промпт шаблони доступні")

        # Перевіряємо, чи є дані
        if "prompttemplate" in response.text.lower():
            print("✅ Сторінка промпт шаблонів завантажена")
        else:
            print("❌ Дані не знайдено")

        # Перевіряємо, чи є user_id
        if "user_id" in response.text.lower():
            print("✅ Поле user_id відображається")
        else:
            print("❌ Поле user_id не відображається")

        # Перевіряємо наявність фільтрів
        if "filter" in response.text.lower():
            print("✅ Фільтри присутні")
        else:
            print("❌ Фільтри не знайдено")

    else:
        print(f"❌ Промпт шаблони недоступні: {response.status_code}")


if __name__ == "__main__":
    check_prompts()
