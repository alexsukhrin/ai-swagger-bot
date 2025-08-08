"""
Розширений AI-асистент для веб-сайтів
Покращена версія Swagger бота з додатковими функціями для e-commerce
"""

import json
import logging
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .enhanced_prompt_manager import EnhancedPromptManager
from .rag_engine import RAGEngine
from .swagger_validation_prompt import SwaggerValidationPrompt

logger = logging.getLogger(__name__)


class EnhancedAIAssistant:
    """
    Розширений AI-асистент з додатковими функціями для веб-сайтів
    """

    def __init__(self, prompt_manager: EnhancedPromptManager, rag_engine: RAGEngine):
        self.prompt_manager = prompt_manager
        self.rag_engine = rag_engine
        self.user_profiles = {}
        self.conversation_history = {}
        self.product_database = {}
        self.order_database = {}

    def process_user_query(self, user_id: str, query: str, context: Dict = None) -> str:
        """
        Обробка запиту користувача з розширеними функціями
        """
        try:
            # Аналіз наміру користувача
            intent = self._analyze_user_intent(query)

            # Визначення типу допомоги
            assistance_type = self._determine_assistance_type(intent, query)

            # Обробка в залежності від типу
            if assistance_type == "product_search":
                return self._handle_product_search(user_id, query, context)
            elif assistance_type == "order_assistance":
                return self._handle_order_assistance(user_id, query, context)
            elif assistance_type == "content_creation":
                return self._handle_content_creation(user_id, query, context)
            elif assistance_type == "customer_support":
                return self._handle_customer_support(user_id, query, context)
            elif assistance_type == "recommendations":
                return self._handle_recommendations(user_id, query, context)
            elif assistance_type == "analytics":
                return self._handle_analytics(user_id, query, context)
            elif assistance_type == "notifications":
                return self._handle_notifications(user_id, query, context)
            else:
                # Стандартна обробка через Swagger
                return self._handle_swagger_query(user_id, query, context)

        except Exception as e:
            logger.error(f"Помилка обробки запиту: {e}")
            return "❌ Вибачте, сталася помилка при обробці вашого запиту. Спробуйте ще раз."

    def _analyze_user_intent(self, query: str) -> Dict:
        """
        Аналіз наміру користувача
        """
        intent_keywords = {
            "product_search": ["знайти", "шукаю", "потрібен", "купити", "товар", "продукт"],
            "order_assistance": ["замовлення", "заказ", "відстежити", "статус", "доставка"],
            "content_creation": ["опис", "створити", "написати", "контент", "текст"],
            "customer_support": ["допомога", "проблема", "питання", "підтримка", "зв'язатися"],
            "recommendations": ["рекомендації", "поради", "що купити", "подарунок"],
            "analytics": ["статистика", "звіт", "аналіз", "продажі", "популярні"],
            "notifications": ["сповіщення", "оновлення", "новини", "акції"],
        }

        query_lower = query.lower()
        detected_intents = []

        for intent, keywords in intent_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_intents.append(intent)

        return {
            "primary_intent": detected_intents[0] if detected_intents else "general",
            "all_intents": detected_intents,
            "confidence": len(detected_intents) / len(intent_keywords),
        }

    def _determine_assistance_type(self, intent: Dict, query: str) -> str:
        """
        Визначення типу допомоги
        """
        primary_intent = intent.get("primary_intent", "general")

        # Спеціальні правила для визначення типу
        if "swagger" in query.lower() or "api" in query.lower():
            return "swagger"
        elif "опис" in query.lower() and ("товар" in query.lower() or "продукт" in query.lower()):
            return "content_creation"
        elif any(word in query.lower() for word in ["замовлення", "заказ", "відстежити"]):
            return "order_assistance"
        elif any(word in query.lower() for word in ["рекомендації", "поради", "що купити"]):
            return "recommendations"
        else:
            return primary_intent

    def _handle_product_search(self, user_id: str, query: str, context: Dict = None) -> str:
        """
        Обробка пошуку товарів
        """
        try:
            # Отримання промпту для розумного пошуку
            prompt = self.prompt_manager.get_prompt("smart_product_search")

            # Підготовка контексту
            search_context = {
                "user_query": query,
                "available_products": self._get_available_products(),
                "categories": self._get_categories(),
                "filters": self._get_search_filters(),
                "user_profile": self._get_user_profile(user_id),
            }

            # Генерація відповіді
            response = self._generate_response(prompt, search_context)

            # Оновлення історії
            self._update_conversation_history(user_id, query, response, "product_search")

            return response

        except Exception as e:
            logger.error(f"Помилка пошуку товарів: {e}")
            return "❌ Вибачте, не вдалося виконати пошук. Спробуйте ще раз."

    def _handle_order_assistance(self, user_id: str, query: str, context: Dict = None) -> str:
        """
        Обробка допомоги з замовленнями
        """
        try:
            prompt = self.prompt_manager.get_prompt("order_assistance")

            order_context = {
                "user_query": query,
                "assistance_type": self._determine_order_assistance_type(query),
                "order_data": self._get_user_orders(user_id),
                "order_status": self._get_order_status(user_id),
            }

            response = self._generate_response(prompt, order_context)
            self._update_conversation_history(user_id, query, response, "order_assistance")

            return response

        except Exception as e:
            logger.error(f"Помилка допомоги з замовленнями: {e}")
            return "❌ Вибачте, не вдалося надати допомогу з замовленням. Спробуйте ще раз."

    def _handle_content_creation(self, user_id: str, query: str, context: Dict = None) -> str:
        """
        Обробка створення контенту
        """
        try:
            prompt = self.prompt_manager.get_prompt("product_description_creation")

            # Витягування інформації про товар з запиту
            product_info = self._extract_product_info(query)

            content_context = {
                "product_name": product_info.get("name", "Товар"),
                "category": product_info.get("category", "Загальна"),
                "features": product_info.get("features", []),
                "price": product_info.get("price", "Ціна не вказана"),
            }

            response = self._generate_response(prompt, content_context)
            self._update_conversation_history(user_id, query, response, "content_creation")

            return response

        except Exception as e:
            logger.error(f"Помилка створення контенту: {e}")
            return "❌ Вибачте, не вдалося створити контент. Спробуйте ще раз."

    def _handle_customer_support(self, user_id: str, query: str, context: Dict = None) -> str:
        """
        Обробка підтримки клієнтів
        """
        try:
            prompt = self.prompt_manager.get_prompt("customer_support_assistant")

            support_context = {
                "user_query": query,
                "issue_type": self._determine_issue_type(query),
                "product_service": self._get_relevant_product_service(query),
                "user_profile": self._get_user_profile(user_id),
            }

            response = self._generate_response(prompt, support_context)
            self._update_conversation_history(user_id, query, response, "customer_support")

            return response

        except Exception as e:
            logger.error(f"Помилка підтримки клієнтів: {e}")
            return "❌ Вибачте, не вдалося надати підтримку. Спробуйте ще раз."

    def _handle_recommendations(self, user_id: str, query: str, context: Dict = None) -> str:
        """
        Обробка рекомендацій
        """
        try:
            prompt = self.prompt_manager.get_prompt("personalized_recommendations")

            recommendation_context = {
                "user_profile": self._get_user_profile(user_id),
                "purchase_history": self._get_purchase_history(user_id),
                "viewed_products": self._get_viewed_products(user_id),
                "cart_items": self._get_cart_items(user_id),
                "current_query": query,
            }

            response = self._generate_response(prompt, recommendation_context)
            self._update_conversation_history(user_id, query, response, "recommendations")

            return response

        except Exception as e:
            logger.error(f"Помилка генерації рекомендацій: {e}")
            return "❌ Вибачте, не вдалося згенерувати рекомендації. Спробуйте ще раз."

    def _handle_analytics(self, user_id: str, query: str, context: Dict = None) -> str:
        """
        Обробка аналітики
        """
        try:
            prompt = self.prompt_manager.get_prompt("analytics_insights")

            analytics_context = {
                "analysis_type": self._determine_analysis_type(query),
                "data": self._get_analytics_data(),
                "period": self._extract_period(query),
                "metrics": self._extract_metrics(query),
            }

            response = self._generate_response(prompt, analytics_context)
            self._update_conversation_history(user_id, query, response, "analytics")

            return response

        except Exception as e:
            logger.error(f"Помилка аналітики: {e}")
            return "❌ Вибачте, не вдалося створити звіт. Спробуйте ще раз."

    def _handle_notifications(self, user_id: str, query: str, context: Dict = None) -> str:
        """
        Обробка сповіщень
        """
        try:
            prompt = self.prompt_manager.get_prompt("notification_system")

            notification_context = {
                "notification_type": self._determine_notification_type(query),
                "context": self._get_notification_context(user_id),
                "target_audience": self._get_target_audience(query),
                "priority": self._determine_priority(query),
            }

            response = self._generate_response(prompt, notification_context)
            self._update_conversation_history(user_id, query, response, "notifications")

            return response

        except Exception as e:
            logger.error(f"Помилка сповіщень: {e}")
            return "❌ Вибачте, не вдалося створити сповіщення. Спробуйте ще раз."

    def _handle_swagger_query(self, user_id: str, query: str, context: Dict = None) -> str:
        """
        Стандартна обробка через Swagger
        """
        # Використання існуючої логіки Swagger
        return "🔄 Обробка через Swagger API..."

    def _generate_response(self, prompt: str, context: Dict) -> str:
        """
        Генерація відповіді через RAG або LLM
        """
        try:
            # Використання RAG для генерації відповіді
            response = self.rag_engine.generate_response(prompt, context)
            return response
        except Exception as e:
            logger.error(f"Помилка генерації відповіді: {e}")
            return "❌ Помилка генерації відповіді"

    # Допоміжні методи для роботи з даними
    def _get_available_products(self) -> List[Dict]:
        """Отримання доступних товарів"""
        return self.product_database.get("products", [])

    def _get_categories(self) -> List[str]:
        """Отримання категорій"""
        return self.product_database.get("categories", [])

    def _get_search_filters(self) -> Dict:
        """Отримання фільтрів пошуку"""
        return {
            "price_range": {"min": 0, "max": 100000},
            "categories": self._get_categories(),
            "availability": ["in_stock", "out_of_stock"],
            "sort_options": ["price", "popularity", "newest", "rating"],
        }

    def _get_user_profile(self, user_id: str) -> Dict:
        """Отримання профілю користувача"""
        return self.user_profiles.get(user_id, {})

    def _get_user_orders(self, user_id: str) -> List[Dict]:
        """Отримання замовлень користувача"""
        return self.order_database.get(user_id, [])

    def _get_order_status(self, user_id: str) -> Dict:
        """Отримання статусу замовлень"""
        orders = self._get_user_orders(user_id)
        return {
            "total_orders": len(orders),
            "active_orders": len([o for o in orders if o.get("status") == "active"]),
            "completed_orders": len([o for o in orders if o.get("status") == "completed"]),
        }

    def _extract_product_info(self, query: str) -> Dict:
        """Витягування інформації про товар з запиту"""
        # Простий парсинг для прикладу
        product_info = {
            "name": "Товар",
            "category": "Загальна",
            "features": [],
            "price": "Ціна не вказана",
        }

        # Пошук назви товару
        name_pattern = r"товар[а]?\s+([а-яА-Я\s]+)"
        match = re.search(name_pattern, query.lower())
        if match:
            product_info["name"] = match.group(1).strip()

        return product_info

    def _determine_order_assistance_type(self, query: str) -> str:
        """Визначення типу допомоги з замовленнями"""
        query_lower = query.lower()

        if any(word in query_lower for word in ["оформити", "створити", "новий"]):
            return "creation"
        elif any(word in query_lower for word in ["відстежити", "статус", "де"]):
            return "tracking"
        elif any(word in query_lower for word in ["змінити", "редагувати"]):
            return "modification"
        elif any(word in query_lower for word in ["скасувати", "видалити"]):
            return "cancellation"
        else:
            return "general"

    def _determine_issue_type(self, query: str) -> str:
        """Визначення типу проблеми"""
        query_lower = query.lower()

        if any(word in query_lower for word in ["технічн", "помилка", "не працює"]):
            return "technical"
        elif any(word in query_lower for word in ["оплата", "гроші", "кошти"]):
            return "payment"
        elif any(word in query_lower for word in ["доставка", "відправка"]):
            return "delivery"
        elif any(word in query_lower for word in ["повернення", "обмін"]):
            return "return"
        else:
            return "general"

    def _get_relevant_product_service(self, query: str) -> str:
        """Отримання релевантного продукту/сервісу"""
        # Простий аналіз для прикладу
        return "Загальний сервіс"

    def _get_purchase_history(self, user_id: str) -> List[Dict]:
        """Отримання історії покупок"""
        return self.user_profiles.get(user_id, {}).get("purchase_history", [])

    def _get_viewed_products(self, user_id: str) -> List[Dict]:
        """Отримання переглянутих товарів"""
        return self.user_profiles.get(user_id, {}).get("viewed_products", [])

    def _get_cart_items(self, user_id: str) -> List[Dict]:
        """Отримання товарів у кошику"""
        return self.user_profiles.get(user_id, {}).get("cart_items", [])

    def _determine_analysis_type(self, query: str) -> str:
        """Визначення типу аналізу"""
        query_lower = query.lower()

        if any(word in query_lower for word in ["продажі", "продаж"]):
            return "sales"
        elif any(word in query_lower for word in ["користувачі", "клієнти"]):
            return "users"
        elif any(word in query_lower for word in ["товари", "продукти"]):
            return "products"
        elif any(word in query_lower for word in ["маркетинг", "реклама"]):
            return "marketing"
        else:
            return "general"

    def _get_analytics_data(self) -> Dict:
        """Отримання даних для аналітики"""
        return {
            "sales": {"total": 1000000, "growth": 15},
            "users": {"total": 5000, "new": 500},
            "products": {"total": 1000, "popular": 50},
        }

    def _extract_period(self, query: str) -> str:
        """Витягування періоду з запиту"""
        # Простий аналіз для прикладу
        return "останній місяць"

    def _extract_metrics(self, query: str) -> List[str]:
        """Витягування метрик з запиту"""
        return ["sales", "users", "products"]

    def _determine_notification_type(self, query: str) -> str:
        """Визначення типу сповіщення"""
        query_lower = query.lower()

        if any(word in query_lower for word in ["замовлення", "статус"]):
            return "order_status"
        elif any(word in query_lower for word in ["акція", "знижка", "пропозиція"]):
            return "promo"
        elif any(word in query_lower for word in ["система", "технічн"]):
            return "system"
        else:
            return "general"

    def _get_notification_context(self, user_id: str) -> Dict:
        """Отримання контексту для сповіщень"""
        return {
            "user_id": user_id,
            "last_activity": datetime.now().isoformat(),
            "preferences": self._get_user_profile(user_id).get("notification_preferences", {}),
        }

    def _get_target_audience(self, query: str) -> str:
        """Визначення цільової аудиторії"""
        return "all_users"

    def _determine_priority(self, query: str) -> str:
        """Визначення пріоритету"""
        query_lower = query.lower()

        if any(word in query_lower for word in ["терміново", "важливо", "критично"]):
            return "high"
        elif any(word in query_lower for word in ["звичайно", "стандартно"]):
            return "normal"
        else:
            return "low"

    def _update_conversation_history(self, user_id: str, query: str, response: str, category: str):
        """Оновлення історії розмови"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []

        self.conversation_history[user_id].append(
            {
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "response": response,
                "category": category,
            }
        )

        # Обмеження історії до останніх 50 повідомлень
        if len(self.conversation_history[user_id]) > 50:
            self.conversation_history[user_id] = self.conversation_history[user_id][-50:]

    def get_conversation_history(self, user_id: str) -> List[Dict]:
        """Отримання історії розмови"""
        return self.conversation_history.get(user_id, [])

    def clear_conversation_history(self, user_id: str):
        """Очищення історії розмови"""
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]

    def update_user_profile(self, user_id: str, profile_data: Dict):
        """Оновлення профілю користувача"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {}

        self.user_profiles[user_id].update(profile_data)

    def add_product_to_database(self, product_data: Dict):
        """Додавання товару до бази даних"""
        if "products" not in self.product_database:
            self.product_database["products"] = []

        self.product_database["products"].append(product_data)

    def add_order_to_database(self, user_id: str, order_data: Dict):
        """Додавання замовлення до бази даних"""
        if user_id not in self.order_database:
            self.order_database[user_id] = []

        self.order_database[user_id].append(order_data)
