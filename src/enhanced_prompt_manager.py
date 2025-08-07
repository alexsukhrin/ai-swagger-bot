"""
Покращений менеджер промптів з інтеграцією описів та метаданих.
"""

import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

from .dynamic_prompt_manager import DynamicPromptManager, PromptTemplate
from .prompt_descriptions import PromptDescriptions, PromptCategory, PromptRegistry

@dataclass
class EnhancedPromptTemplate(PromptTemplate):
    """Розширений промпт-шаблон з метаданими."""
    metadata: Dict[str, Any] = None
    description_object: Any = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.metadata is None:
            self.metadata = {}

class EnhancedPromptManager(DynamicPromptManager):
    """Покращений менеджер промптів з інтеграцією описів."""
    
    def __init__(self, db_path: str = "prompts.db", config_path: str = None):
        super().__init__(db_path)
        self.registry = PromptRegistry()
        self.config_path = config_path or "prompt_config.json"
        self.load_prompt_config()
    
    def load_prompt_config(self):
        """Завантажує конфігурацію промптів з файлу."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self._apply_config(config)
            except Exception as e:
                print(f"⚠️ Помилка завантаження конфігурації промптів: {e}")
    
    def save_prompt_config(self):
        """Зберігає конфігурацію промптів в файл."""
        config = {
            "prompts": self._get_prompts_config(),
            "categories": self._get_categories_config(),
            "settings": self._get_settings_config(),
            "last_updated": datetime.now().isoformat()
        }
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Помилка збереження конфігурації промптів: {e}")
    
    def _apply_config(self, config: Dict[str, Any]):
        """Застосовує конфігурацію."""
        if "prompts" in config:
            for prompt_config in config["prompts"]:
                self._apply_prompt_config(prompt_config)
    
    def _apply_prompt_config(self, prompt_config: Dict[str, Any]):
        """Застосовує конфігурацію промпту."""
        prompt = EnhancedPromptTemplate(
            name=prompt_config.get("name", ""),
            description=prompt_config.get("description", ""),
            prompt_text=prompt_config.get("prompt_text", ""),
            category=prompt_config.get("category", ""),
            tags=prompt_config.get("tags", []),
            metadata=prompt_config.get("metadata", {})
        )
        
        # Перевіряємо чи існує промпт
        existing = self.search_prompts(prompt.name, prompt.category)
        if existing:
            # Оновлюємо існуючий
            self.update_prompt(existing[0].id, prompt)
        else:
            # Додаємо новий
            self.add_prompt(prompt)
    
    def _get_prompts_config(self) -> List[Dict[str, Any]]:
        """Отримує конфігурацію всіх промптів."""
        prompts = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, description, prompt_text, category, tags, 
                       is_active, created_at, updated_at, usage_count, success_rate
                FROM prompt_templates WHERE is_active = 1
            ''')
            
            for row in cursor.fetchall():
                prompt = self._row_to_prompt(row)
                prompts.append({
                    "name": prompt.name,
                    "description": prompt.description,
                    "prompt_text": prompt.prompt_text,
                    "category": prompt.category,
                    "tags": prompt.tags,
                    "metadata": {
                        "usage_count": prompt.usage_count,
                        "success_rate": prompt.success_rate,
                        "created_at": prompt.created_at,
                        "updated_at": prompt.updated_at
                    }
                })
        
        return prompts
    
    def _get_categories_config(self) -> Dict[str, Any]:
        """Отримує конфігурацію категорій."""
        categories = {}
        for category in PromptCategory:
            descriptions = PromptDescriptions.get_descriptions_by_category(category)
            categories[category.value] = {
                "name": category.value,
                "description": f"Промпти для {category.value}",
                "prompt_count": len(descriptions),
                "tags": list(set([tag for desc in descriptions for tag in desc.tags]))
            }
        return categories
    
    def _get_settings_config(self) -> Dict[str, Any]:
        """Отримує налаштування системи."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT key, value, description FROM prompt_settings')
            settings = {row[0]: {"value": row[1], "description": row[2]} 
                       for row in cursor.fetchall()}
        return settings
    
    def add_enhanced_prompt(self, prompt: EnhancedPromptTemplate) -> int:
        """Додає покращений промпт з метаданими."""
        # Додаємо опис з реєстру
        if prompt.description_object:
            self.registry.register_custom_prompt(prompt.name, prompt.description_object)
        
        return self.add_prompt(prompt)
    
    def get_prompt_with_metadata(self, prompt_id: int) -> Optional[EnhancedPromptTemplate]:
        """Отримує промпт з метаданими."""
        prompt = self.get_prompt(prompt_id)
        if prompt:
            enhanced_prompt = EnhancedPromptTemplate(**asdict(prompt))
            enhanced_prompt.metadata = self._get_prompt_metadata(prompt_id)
            return enhanced_prompt
        return None
    
    def _get_prompt_metadata(self, prompt_id: int) -> Dict[str, Any]:
        """Отримує метадані промпту."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT usage_count, success_rate, created_at, updated_at
                FROM prompt_templates WHERE id = ?
            ''', (prompt_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    "usage_count": row[0],
                    "success_rate": row[1],
                    "created_at": row[2],
                    "updated_at": row[3]
                }
        return {}
    
    def get_prompts_by_category_with_metadata(self, category: str) -> List[EnhancedPromptTemplate]:
        """Отримує промпти за категорією з метаданими."""
        prompts = self.get_prompts_by_category(category)
        enhanced_prompts = []
        
        for prompt in prompts:
            enhanced_prompt = EnhancedPromptTemplate(**asdict(prompt))
            enhanced_prompt.metadata = self._get_prompt_metadata(prompt.id)
            enhanced_prompts.append(enhanced_prompt)
        
        return enhanced_prompts
    
    def get_prompt_statistics(self) -> Dict[str, Any]:
        """Отримує детальну статистику промптів."""
        stats = self.get_statistics()
        
        # Додаємо статистику по категоріях
        category_stats = {}
        for category in PromptCategory:
            prompts = self.get_prompts_by_category(category.value)
            if prompts:
                category_stats[category.value] = {
                    "count": len(prompts),
                    "avg_success_rate": sum(p.success_rate for p in prompts) / len(prompts),
                    "total_usage": sum(p.usage_count for p in prompts),
                    "most_used": max(prompts, key=lambda x: x.usage_count).name if prompts else None
                }
        
        stats["category_details"] = category_stats
        stats["registry_info"] = {
            "total_descriptions": len(self.registry.descriptions),
            "custom_descriptions": len(self.registry.custom_descriptions)
        }
        
        return stats
    
    def export_prompts_to_file(self, file_path: str, format: str = "json"):
        """Експортує промпти в файл."""
        prompts = self._get_prompts_config()
        
        if format.lower() == "json":
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(prompts, f, ensure_ascii=False, indent=2)
        elif format.lower() == "yaml":
            import yaml
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(prompts, f, default_flow_style=False, allow_unicode=True)
        
        print(f"✅ Промпти експортовано в {file_path}")
    
    def import_prompts_from_file(self, file_path: str, format: str = "json"):
        """Імпортує промпти з файлу."""
        if not os.path.exists(file_path):
            print(f"❌ Файл не знайдено: {file_path}")
            return
        
        try:
            if format.lower() == "json":
                with open(file_path, 'r', encoding='utf-8') as f:
                    prompts = json.load(f)
            elif format.lower() == "yaml":
                import yaml
                with open(file_path, 'r', encoding='utf-8') as f:
                    prompts = yaml.safe_load(f)
            
            for prompt_config in prompts:
                self._apply_prompt_config(prompt_config)
            
            print(f"✅ Промпти імпортовано з {file_path}")
        except Exception as e:
            print(f"❌ Помилка імпорту: {e}")
    
    def create_prompt_from_template(self, template_name: str, **kwargs) -> int:
        """Створює промпт з шаблону."""
        description = self.registry.get_prompt_description(template_name)
        if not description:
            print(f"❌ Шаблон не знайдено: {template_name}")
            return -1
        
        # Створюємо базовий промпт
        prompt = EnhancedPromptTemplate(
            name=kwargs.get("name", f"{template_name}_custom"),
            description=kwargs.get("description", description.description),
            prompt_text=kwargs.get("prompt_text", ""),
            category=kwargs.get("category", description.category.value),
            tags=kwargs.get("tags", description.tags),
            description_object=description
        )
        
        return self.add_enhanced_prompt(prompt)
    
    def get_prompt_suggestions(self, user_query: str) -> List[Dict[str, Any]]:
        """Отримує пропозиції промптів для запиту."""
        suggestions = []
        
        # Аналізуємо запит для визначення категорії
        query_lower = user_query.lower()
        
        if any(word in query_lower for word in ["покажи", "отримай", "знайди"]):
            category = PromptCategory.DATA_RETRIEVAL
        elif any(word in query_lower for word in ["створи", "додай", "новий"]):
            category = PromptCategory.DATA_CREATION
        elif any(word in query_lower for word in ["онови", "зміни", "редагуй"]):
            category = PromptCategory.DATA_UPDATE
        elif any(word in query_lower for word in ["видали", "видаляй"]):
            category = PromptCategory.DATA_DELETION
        elif any(word in query_lower for word in ["помилка", "не працює", "проблема"]):
            category = PromptCategory.ERROR_HANDLING
        else:
            category = PromptCategory.USER_DEFINED
        
        # Знаходимо відповідні промпти
        prompts = self.get_prompts_by_category(category.value)
        
        for prompt in prompts[:3]:  # Топ-3 промпти
            suggestions.append({
                "id": prompt.id,
                "name": prompt.name,
                "description": prompt.description,
                "success_rate": prompt.success_rate,
                "usage_count": prompt.usage_count,
                "relevance_score": self._calculate_relevance_score(user_query, prompt)
            })
        
        # Сортуємо за релевантністю
        suggestions.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return suggestions
    
    def _calculate_relevance_score(self, user_query: str, prompt: PromptTemplate) -> float:
        """Розраховує релевантність промпту для запиту."""
        score = 0.0
        
        # Базовий скор за успішність
        score += prompt.success_rate * 0.4
        
        # Скор за використання (нормалізований)
        score += min(prompt.usage_count / 100.0, 1.0) * 0.3
        
        # Скор за схожість тексту
        query_words = set(user_query.lower().split())
        prompt_words = set(prompt.name.lower().split() + prompt.description.lower().split())
        
        if prompt_words:
            similarity = len(query_words.intersection(prompt_words)) / len(query_words.union(prompt_words))
            score += similarity * 0.3
        
        return score

# Приклади використання
if __name__ == "__main__":
    # Створюємо покращений менеджер
    manager = EnhancedPromptManager()
    
    # Створюємо промпт з шаблону
    prompt_id = manager.create_prompt_from_template(
        "intent_analysis",
        name="Custom Intent Analysis",
        prompt_text="Ти експерт API. Аналізуй запит: {user_query}",
        tags=["custom", "intent"]
    )
    
    print(f"✅ Створено промпт з ID: {prompt_id}")
    
    # Отримуємо пропозиції
    suggestions = manager.get_prompt_suggestions("Покажи всі товари")
    print(f"🎯 Знайдено {len(suggestions)} пропозицій")
    
    # Експортуємо конфігурацію
    manager.save_prompt_config()
    print("💾 Конфігурація збережена")
