"""
AI Error Handler для обробки помилок API через GPT модель.
"""

import json
import logging
from typing import Any, Dict, Optional

from src.config import Config

logger = logging.getLogger(__name__)


class AIErrorHandler:
    """AI Error Handler для аналізу та обробки помилок API."""

    def __init__(self):
        """Ініціалізація AI Error Handler."""
        self.config = Config()
        logger.info("AI Error Handler ініціалізовано")
    
    def analyze_error(self, error_context: Dict[str, Any]) -> str:
        """
        Аналізує помилку API через AI модель.
        
        Args:
            error_context: Контекст помилки з деталями
            
        Returns:
            Аналіз помилки та рекомендації
        """
        try:
            logger.info(f"AI аналіз помилки для API: {error_context.get('api_name', 'N/A')}")
            
            # Формуємо детальний контекст для GPT
            analysis_prompt = self._create_analysis_prompt(error_context)
            
            # Аналізуємо помилку через GPT
            error_analysis = self._analyze_with_gpt(analysis_prompt)
            
            return error_analysis
            
        except Exception as e:
            logger.error(f"Помилка AI аналізу помилки: {e}")
            return self._fallback_error_analysis(error_context)
    
    def _create_analysis_prompt(self, error_context: Dict[str, Any]) -> str:
        """Створює промпт для аналізу помилки."""
        api_name = error_context.get('api_name', 'N/A')
        method = error_context.get('method', 'N/A')
        path = error_context.get('path', 'N/A')
        status_code = error_context.get('status_code', 'N/A')
        response_text = error_context.get('response_text', 'N/A')
        headers = error_context.get('headers', {})
        
        prompt = f"""
        Ти - експерт з API та обробки помилок. Проаналізуй помилку та надай детальні рекомендації.
        
        Контекст помилки:
        - API: {api_name}
        - Метод: {method}
        - Шлях: {path}
        - Код статусу: {status_code}
        - Відповідь сервера: {response_text}
        - Заголовки: {json.dumps(headers, indent=2)}
        
        Завдання:
        1. Визначити тип помилки
        2. Пояснити можливі причини
        3. Надати конкретні кроки для вирішення
        4. Запропонувати альтернативні рішення
        5. Надати приклади правильного використання
        
        Відповідь має бути структурованою та практичною, українською мовою.
        """
        
        return prompt
    
    def _analyze_with_gpt(self, prompt: str) -> str:
        """Аналізує помилку через GPT модель."""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.config.OPENAI_API_KEY)
            
            system_prompt = """
            Ти - експерт з API та обробки помилок. Твоя задача - надавати детальні, практичні аналізи помилок
            з конкретними рекомендаціями та рішеннями.
            
            Ключові принципи:
            1. Аналізуй помилку системно та детально
            2. Надавай практичні кроки для вирішення
            3. Пояснюй причини та контекст помилки
            4. Запропонуй альтернативні рішення
            5. Відповідай українською мовою
            6. Структуруй відповідь для легкого розуміння
            """
            
            response = client.chat.completions.create(
                model=self.config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Низька температура для більш точних відповідей
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Помилка GPT аналізу: {e}")
            return f"Не вдалося проаналізувати помилку через AI: {str(e)}"
    
    def _fallback_error_analysis(self, error_context: Dict[str, Any]) -> str:
        """Fallback аналіз помилки без AI."""
        try:
            status_code = error_context.get('status_code', 0)
            method = error_context.get('method', 'N/A')
            path = error_context.get('path', 'N/A')
            
            # Базовий аналіз на основі HTTP статус кодів
            if status_code == 400:
                return f"""
                🔍 Аналіз помилки 400 (Bad Request):
                
                📍 Деталі:
                - Метод: {method}
                - Шлях: {path}
                - Тип: Помилка запиту
                
                💡 Можливі причини:
                - Неправильний формат даних
                - Відсутні обов'язкові поля
                - Невалідні значення параметрів
                
                🛠️ Рекомендації:
                1. Перевірте формат даних запиту
                2. Переконайтеся, що всі обов'язкові поля присутні
                3. Валідуйте значення параметрів
                4. Перевірте документацію API
                
                📚 Приклад правильного запиту:
                ```json
                {{
                    "name": "Назва категорії",
                    "slug": "nazva-kategorii"
                }}
                ```
                """
            
            elif status_code == 401:
                return f"""
                🔍 Аналіз помилки 401 (Unauthorized):
                
                📍 Деталі:
                - Метод: {method}
                - Шлях: {path}
                - Тип: Помилка авторизації
                
                💡 Можливі причини:
                - Відсутній або невалідний JWT токен
                - Застарілий токен
                - Неправильні права доступу
                
                🛠️ Рекомендації:
                1. Перевірте наявність JWT токена
                2. Оновіть токен, якщо він застарів
                3. Переконайтеся у правильності прав доступу
                4. Виконайте повторну авторизацію
                
                🔑 Приклад заголовка:
                ```
                Authorization: Bearer <your-jwt-token>
                ```
                """
            
            elif status_code == 403:
                return f"""
                🔍 Аналіз помилки 403 (Forbidden):
                
                📍 Деталі:
                - Метод: {method}
                - Шлях: {path}
                - Тип: Доступ заборонено
                
                💡 Можливі причини:
                - Недостатні права доступу
                - Обмеження для ролі користувача
                - Блокування IP адреси
                
                🛠️ Рекомендації:
                1. Перевірте права доступу користувача
                2. Зверніться до адміністратора для надання прав
                3. Переконайтеся у правильності ролі
                4. Перевірте налаштування безпеки
                """
            
            elif status_code == 404:
                return f"""
                🔍 Аналіз помилки 404 (Not Found):
                
                📍 Деталі:
                - Метод: {method}
                - Шлях: {path}
                - Тип: Ресурс не знайдено
                
                💡 Можливі причини:
                - Неправильний шлях ендпоінту
                - Ресурс не існує
                - Неправильний ID ресурсу
                
                🛠️ Рекомендації:
                1. Перевірте правильність шляху
                2. Переконайтеся, що ресурс існує
                3. Валідуйте ID ресурсу
                4. Перевірте документацію API
                
                📚 Доступні ендпоінти:
                - GET /api/categories - отримати всі категорії
                - GET /api/categories/{id} - отримати категорію за ID
                """
            
            elif status_code == 422:
                return f"""
                🔍 Аналіз помилки 422 (Unprocessable Entity):
                
                📍 Деталі:
                - Метод: {method}
                - Шлях: {path}
                - Тип: Помилка валідації
                
                💡 Можливі причини:
                - Невалідні дані запиту
                - Порушення бізнес-правил
                - Конфлікт з існуючими даними
                
                🛠️ Рекомендації:
                1. Перевірте формат та валідність даних
                2. Переконайтеся у відповідності бізнес-правилам
                3. Перевірте унікальність значень
                4. Використовуйте правильні типи даних
                
                📋 Приклад валідних даних:
                ```json
                {{
                    "name": "Назва категорії",
                    "slug": "nazva-kategorii",
                    "status": "active"
                }}
                ```
                """
            
            elif status_code == 500:
                return f"""
                🔍 Аналіз помилки 500 (Internal Server Error):
                
                📍 Деталі:
                - Метод: {method}
                - Шлях: {path}
                - Тип: Внутрішня помилка сервера
                
                💡 Можливі причини:
                - Помилка на стороні сервера
                - Проблеми з базою даних
                - Неочікувана помилка в коді
                
                🛠️ Рекомендації:
                1. Спробуйте повторити запит через деякий час
                2. Перевірте статус сервера
                3. Зверніться до технічної підтримки
                4. Перевірте логи сервера
                
                ⏰ Повторна спроба:
                - Зачекайте 1-2 хвилини
                - Виконайте запит ще раз
                - Якщо помилка повторюється - зверніться до підтримки
                """
            
            else:
                return f"""
                🔍 Аналіз помилки {status_code}:
                
                📍 Деталі:
                - Метод: {method}
                - Шлях: {path}
                - Тип: Невідома помилка
                
                💡 Рекомендації:
                1. Перевірте документацію API
                2. Зверніться до технічної підтримки
                3. Перевірте логи сервера
                4. Спробуйте повторити запит
                
                📚 Корисні посилання:
                - Документація API
                - Статус сервера
                - Технічна підтримка
                """
                
        except Exception as e:
            logger.error(f"Помилка fallback аналізу: {e}")
            return f"Не вдалося проаналізувати помилку: {str(e)}"
    
    def get_error_suggestions(self, error_type: str) -> str:
        """
        Отримує загальні рекомендації для типу помилки.
        
        Args:
            error_type: Тип помилки
            
        Returns:
            Рекомендації для вирішення
        """
        suggestions = {
            "authentication": """
                🔐 Проблеми з авторизацією:
                
                ✅ Перевірте:
                1. Наявність JWT токена
                2. Валідність токена
                3. Права доступу користувача
                4. Термін дії токена
                
                🔄 Рішення:
                1. Оновіть JWT токен
                2. Перевірте права доступу
                3. Зверніться до адміністратора
                4. Виконайте повторну авторизацію
                """,
            
            "validation": """
                ✅ Проблеми з валідацією:
                
                🔍 Перевірте:
                1. Формат даних запиту
                2. Обов'язкові поля
                3. Типи даних
                4. Бізнес-правила
                
                🛠️ Рішення:
                1. Використовуйте правильний формат JSON
                2. Заповніть всі обов'язкові поля
                3. Перевірте типи даних
                4. Дотримуйтесь бізнес-правил
                """,
            
            "network": """
                🌐 Проблеми з мережею:
                
                📡 Перевірте:
                1. Підключення до інтернету
                2. Доступність сервера
                3. Таймаути запитів
                4. Firewall налаштування
                
                🔄 Рішення:
                1. Перевірте підключення
                2. Спробуйте повторити запит
                3. Зменшіть розмір даних
                4. Перевірте мережеві налаштування
                """,
            
            "server": """
                🖥️ Проблеми з сервером:
                
                ⚠️ Симптоми:
                1. Помилки 5xx
                2. Повільна робота
                3. Таймаути
                4. Нестабільність
                
                🛠️ Рішення:
                1. Зачекайте та повторите запит
                2. Зверніться до технічної підтримки
                3. Перевірте статус сервера
                4. Використовуйте retry логіку
                """
        }
        
        return suggestions.get(error_type, "Тип помилки не розпізнано")
    
    def format_error_response(self, error_context: Dict[str, Any], 
                            include_suggestions: bool = True) -> str:
        """
        Форматує відповідь з помилкою.
        
        Args:
            error_context: Контекст помилки
            include_suggestions: Чи включати рекомендації
            
        Returns:
            Форматована відповідь з помилкою
        """
        try:
            # Аналізуємо помилку
            error_analysis = self.analyze_error(error_context)
            
            # Форматуємо відповідь
            response_parts = [
                "❌ Помилка API",
                "=" * 50,
                error_analysis
            ]
            
            if include_suggestions:
                # Визначаємо тип помилки для рекомендацій
                status_code = error_context.get('status_code', 0)
                if status_code in [401, 403]:
                    error_type = "authentication"
                elif status_code in [400, 422]:
                    error_type = "validation"
                elif status_code >= 500:
                    error_type = "server"
                else:
                    error_type = "general"
                
                suggestions = self.get_error_suggestions(error_type)
                response_parts.extend([
                    "",
                    "💡 Загальні рекомендації:",
                    suggestions
                ])
            
            return "\n".join(response_parts)
            
        except Exception as e:
            logger.error(f"Помилка форматування відповіді з помилкою: {e}")
            return f"❌ Помилка: {str(e)}"
    
    def create_fix_plan(self, error_context: Dict[str, Any], original_request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Створює план автоматичного виправлення помилки через GPT.
        
        Args:
            error_context: Контекст помилки
            original_request: Оригінальний запит, який викликав помилку
            
        Returns:
            План виправлення або None якщо виправлення неможливе
        """
        try:
            logger.info(f"Створення плану виправлення для API: {error_context.get('api_name', 'N/A')}")
            
            # Формуємо промпт для створення плану виправлення
            fix_prompt = self._create_fix_plan_prompt(error_context, original_request)
            
            # Отримуємо план виправлення через GPT
            fix_plan = self._get_fix_plan_from_gpt(fix_prompt)
            
            return fix_plan
            
        except Exception as e:
            logger.error(f"Помилка створення плану виправлення: {e}")
            return None
    
    def _create_fix_plan_prompt(self, error_context: Dict[str, Any], original_request: Dict[str, Any]) -> str:
        """Створює промпт для створення плану виправлення."""
        prompt = f"""
        Ти - AI помічник, який може автоматично виправляти помилки API. Проаналізуй помилку та створи план виправлення.
        
        Контекст помилки:
        - API: {error_context.get('api_name', 'N/A')}
        - Метод: {error_context.get('method', 'N/A')}
        - Шлях: {error_context.get('path', 'N/A')}
        - Код статусу: {error_context.get('status_code', 'N/A')}
        - Відповідь сервера: {error_context.get('response_text', 'N/A')}
        
        Оригінальний запит:
        - Дані: {json.dumps(original_request.get('data', {}), ensure_ascii=False)}
        - Параметри: {json.dumps(original_request.get('params', {}), ensure_ascii=False)}
        
        Завдання:
        1. Визначити, чи можна автоматично виправити помилку
        2. Якщо так - створити план виправлення
        3. Якщо ні - пояснити чому та що потрібно зробити вручну
        
        Створи JSON план виправлення:
        {{
            "can_fix": true/false,
            "fix_type": "data_correction|parameter_adjustment|retry|manual_intervention",
            "fix_description": "опис що буде виправлено",
            "corrected_request": {{
                "method": "HTTP метод",
                "path": "шлях",
                "data": {{}} // виправлені дані
                "params": {{}} // виправлені параметри
            }},
            "explanation": "пояснення що було виправлено та чому"
        }}
        
        Відповідь має бути тільки JSON без додаткового тексту.
        """
        
        return prompt
    
    def _get_fix_plan_from_gpt(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Отримує план виправлення від GPT."""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.config.OPENAI_API_KEY)
            
            system_prompt = """
            Ти - AI помічник для автоматичного виправлення помилок API. Твоя задача - створювати точні плани виправлення
            у форматі JSON. Відповідай тільки JSON без додаткового тексту.
            """
            
            response = client.chat.completions.create(
                model=self.config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Парсимо JSON відповідь
            gpt_response = response.choices[0].message.content.strip()
            
            # Спробуємо знайти JSON у відповіді
            import re
            json_match = re.search(r'\{.*\}', gpt_response, re.DOTALL)
            
            if json_match:
                try:
                    fix_plan = json.loads(json_match.group())
                    logger.info(f"GPT створив план виправлення: {fix_plan}")
                    return fix_plan
                except json.JSONDecodeError:
                    logger.warning(f"Не вдалося розпарсити JSON план виправлення: {gpt_response}")
            
            return None
            
        except Exception as e:
            logger.error(f"Помилка отримання плану виправлення від GPT: {e}")
            return None
