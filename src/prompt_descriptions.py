"""
Описи та метадані промптів для системи AI Swagger Bot.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

class PromptCategory(Enum):
    """Категорії промптів."""
    SYSTEM = "system"
    INTENT_ANALYSIS = "intent_analysis"
    ERROR_HANDLING = "error_handling"
    RESPONSE_FORMATTING = "response_formatting"
    DATA_RETRIEVAL = "data_retrieval"
    DATA_CREATION = "data_creation"
    DATA_UPDATE = "data_update"
    DATA_DELETION = "data_deletion"
    VALIDATION = "validation"
    DEBUGGING = "debugging"
    USER_DEFINED = "user_defined"

@dataclass
class PromptDescription:
    """Опис промпту з метаданими."""
    name: str
    description: str
    category: PromptCategory
    tags: List[str]
    usage_examples: List[str]
    success_criteria: List[str]
    version: str = "1.0"
    author: str = "system"
    is_deprecated: bool = False

class PromptDescriptions:
    """Колекція описів промптів."""
    
    @staticmethod
    def get_system_prompt_description() -> PromptDescription:
        """Опис системного промпту."""
        return PromptDescription(
            name="System Prompt",
            description="Загальний системний промпт для агента API",
            category=PromptCategory.SYSTEM,
            tags=["core", "system", "api"],
            usage_examples=[
                "Використовується при ініціалізації агента",
                "Визначає базову поведінку агента"
            ],
            success_criteria=[
                "Агент розуміє свою роль",
                "Відповідає українською мовою",
                "Використовує емодзі для кращого UX"
            ]
        )
    
    @staticmethod
    def get_intent_analysis_description() -> PromptDescription:
        """Опис промпту для аналізу наміру."""
        return PromptDescription(
            name="Intent Analysis Prompt",
            description="Аналізує запит користувача та визначає намір",
            category=PromptCategory.INTENT_ANALYSIS,
            tags=["analysis", "intent", "nlp"],
            usage_examples=[
                "Покажи всі товари",
                "Створи новий товар",
                "Онови товар з ID 123"
            ],
            success_criteria=[
                "Визначає правильний HTTP метод",
                "Ідентифікує ресурс",
                "Витягує параметри та дані",
                "Повертає структурований JSON"
            ]
        )
    
    @staticmethod
    def get_error_handling_description() -> PromptDescription:
        """Опис промпту для обробки помилок."""
        return PromptDescription(
            name="Error Handling Prompt",
            description="Аналізує помилки сервера та генерує корисні відповіді",
            category=PromptCategory.ERROR_HANDLING,
            tags=["error", "debugging", "user_friendly"],
            usage_examples=[
                "Помилка валідації",
                "Проблеми з авторизацією",
                "Ресурс не знайдено"
            ],
            success_criteria=[
                "Класифікує тип помилки",
                "Генерує зрозуміле пояснення",
                "Запитує додаткову інформацію",
                "Пропонує рішення"
            ]
        )
    
    @staticmethod
    def get_response_formatting_description() -> PromptDescription:
        """Опис промпту для форматування відповідей."""
        return PromptDescription(
            name="Response Formatting Prompt",
            description="Форматує відповідь користувачу про API запит",
            category=PromptCategory.RESPONSE_FORMATTING,
            tags=["formatting", "ux", "presentation"],
            usage_examples=[
                "Успішний API виклик",
                "Помилка при виконанні",
                "Попередній перегляд запиту"
            ],
            success_criteria=[
                "Використовує емодзі для кращого UX",
                "Показує URL, метод, параметри",
                "Структурована відповідь",
                "Дружелюбний тон"
            ]
        )
    
    @staticmethod
    def get_api_response_processing_description() -> PromptDescription:
        """Опис промпту для обробки відповідей API сервера."""
        return PromptDescription(
            name="API Response Processing Prompt",
            description="Обробляє JSON відповідь від API сервера та перетворює її в дружелюбний текст",
            category=PromptCategory.RESPONSE_FORMATTING,
            tags=["api_response", "json_processing", "user_friendly", "customization"],
            usage_examples=[
                "Покажи тільки назви товарів",
                "Виведи список категорій",
                "Покажи ID та назву",
                "Фільтруй за певними полями"
            ],
            success_criteria=[
                "Розуміє запит користувача",
                "Витягує потрібні поля з JSON",
                "Формує зрозумілий текст",
                "Використовує емодзі та структурування",
                "Адаптується до контексту запиту"
            ]
        )
    
    @staticmethod
    def get_object_creation_description() -> PromptDescription:
        """Опис промпту для створення об'єктів з автоматичним заповненням полів."""
        return PromptDescription(
            name="Object Creation Prompt",
            description="Створює об'єкти (товари, категорії, користувачі) з автоматичним заповненням полів та обробкою помилок",
            category=PromptCategory.DATA_CREATION,
            tags=["object_creation", "auto_fill", "error_handling", "conversation_context"],
            usage_examples=[
                "Створи нову категорію Електроніка",
                "Створи товар з назвою Телефон",
                "Створи користувача Іван Петренко",
                "Додай новий продукт"
            ],
            success_criteria=[
                "Автоматично заповнює обов'язкові поля",
                "Використовує контекст історії розмови",
                "Генерує реалістичні значення",
                "Обробляє помилки валідації",
                "Пропонує рішення без повторного введення",
                "Зберігає контекст діалогу"
            ]
        )
    
    @staticmethod
    def get_all_descriptions() -> Dict[str, PromptDescription]:
        """Повертає всі описи промптів."""
        return {
            "system": PromptDescriptions.get_system_prompt_description(),
            "intent_analysis": PromptDescriptions.get_intent_analysis_description(),
            "error_handling": PromptDescriptions.get_error_handling_description(),
            "response_formatting": PromptDescriptions.get_response_formatting_description(),
            "api_response_processing": PromptDescriptions.get_api_response_processing_description(),
            "object_creation": PromptDescriptions.get_object_creation_description()
        }
    
    @staticmethod
    def get_descriptions_by_category(category: PromptCategory) -> List[PromptDescription]:
        """Повертає описи промптів за категорією."""
        all_descriptions = PromptDescriptions.get_all_descriptions()
        return [desc for desc in all_descriptions.values() if desc.category == category]
    
    @staticmethod
    def get_descriptions_by_tag(tag: str) -> List[PromptDescription]:
        """Повертає описи промптів за тегом."""
        all_descriptions = PromptDescriptions.get_all_descriptions()
        return [desc for desc in all_descriptions.values() if tag in desc.tags]

class PromptRegistry:
    """Реєстр промптів з метаданими."""
    
    def __init__(self):
        self.descriptions = PromptDescriptions.get_all_descriptions()
        self.custom_descriptions = {}
    
    def register_custom_prompt(self, name: str, description: PromptDescription):
        """Реєструє кастомний промпт."""
        self.custom_descriptions[name] = description
    
    def get_prompt_description(self, name: str) -> PromptDescription:
        """Отримує опис промпту за назвою."""
        return self.descriptions.get(name) or self.custom_descriptions.get(name)
    
    def list_prompts_by_category(self, category: PromptCategory) -> List[str]:
        """Список промптів за категорією."""
        return [name for name, desc in self.descriptions.items() 
                if desc.category == category]
    
    def get_prompt_metadata(self, name: str) -> Dict[str, Any]:
        """Отримує метадані промпту."""
        desc = self.get_prompt_description(name)
        if desc:
            return {
                "name": desc.name,
                "description": desc.description,
                "category": desc.category.value,
                "tags": desc.tags,
                "version": desc.version,
                "author": desc.author,
                "is_deprecated": desc.is_deprecated,
                "usage_examples": desc.usage_examples,
                "success_criteria": desc.success_criteria
            }
        return None
