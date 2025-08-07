"""
Система динамічного управління промптами з збереженням в базі даних
"""

import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict

@dataclass
class PromptTemplate:
    """Клас для представлення промпт-шаблону."""
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    prompt_text: str = ""
    category: str = ""
    tags: List[str] = None
    is_active: bool = True
    created_at: str = ""
    updated_at: str = ""
    usage_count: int = 0
    success_rate: float = 0.0
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()

class DynamicPromptManager:
    """Менеджер для динамічного управління промптами."""
    
    def __init__(self, db_path: str = "prompts.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Ініціалізує базу даних для промптів."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Таблиця для промпт-шаблонів
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS prompt_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    prompt_text TEXT NOT NULL,
                    category TEXT,
                    tags TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TEXT,
                    updated_at TEXT,
                    usage_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0.0
                )
            ''')
            
            # Таблиця для історії використання промптів
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS prompt_usage_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_id INTEGER,
                    user_query TEXT,
                    context TEXT,
                    result TEXT,
                    success BOOLEAN,
                    created_at TEXT,
                    FOREIGN KEY (prompt_id) REFERENCES prompt_templates (id)
                )
            ''')
            
            # Таблиця для налаштувань промптів
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS prompt_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    description TEXT,
                    updated_at TEXT
                )
            ''')
            
            conn.commit()
    
    def add_prompt(self, prompt: PromptTemplate) -> int:
        """Додає новий промпт в базу даних."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO prompt_templates 
                (name, description, prompt_text, category, tags, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                prompt.name,
                prompt.description,
                prompt.prompt_text,
                prompt.category,
                json.dumps(prompt.tags),
                prompt.is_active,
                prompt.created_at,
                prompt.updated_at
            ))
            
            prompt_id = cursor.lastrowid
            conn.commit()
            return prompt_id
    
    def get_prompt(self, prompt_id: int) -> Optional[PromptTemplate]:
        """Отримує промпт за ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, description, prompt_text, category, tags, 
                       is_active, created_at, updated_at, usage_count, success_rate
                FROM prompt_templates WHERE id = ?
            ''', (prompt_id,))
            
            row = cursor.fetchone()
            if row:
                return self._row_to_prompt(row)
            return None
    
    def get_prompts_by_category(self, category: str) -> List[PromptTemplate]:
        """Отримує всі промпти за категорією."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, description, prompt_text, category, tags, 
                       is_active, created_at, updated_at, usage_count, success_rate
                FROM prompt_templates WHERE category = ? AND is_active = 1
                ORDER BY usage_count DESC, success_rate DESC
            ''', (category,))
            
            return [self._row_to_prompt(row) for row in cursor.fetchall()]
    
    def search_prompts(self, query: str, category: str = None) -> List[PromptTemplate]:
        """Шукає промпти за запитом."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if category:
                cursor.execute('''
                    SELECT id, name, description, prompt_text, category, tags, 
                           is_active, created_at, updated_at, usage_count, success_rate
                    FROM prompt_templates 
                    WHERE (name LIKE ? OR description LIKE ? OR prompt_text LIKE ?) 
                    AND category = ? AND is_active = 1
                    ORDER BY usage_count DESC, success_rate DESC
                ''', (f'%{query}%', f'%{query}%', f'%{query}%', category))
            else:
                cursor.execute('''
                    SELECT id, name, description, prompt_text, category, tags, 
                           is_active, created_at, updated_at, usage_count, success_rate
                    FROM prompt_templates 
                    WHERE (name LIKE ? OR description LIKE ? OR prompt_text LIKE ?) 
                    AND is_active = 1
                    ORDER BY usage_count DESC, success_rate DESC
                ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
            
            return [self._row_to_prompt(row) for row in cursor.fetchall()]
    
    def update_prompt(self, prompt_id: int, prompt: PromptTemplate) -> bool:
        """Оновлює існуючий промпт."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE prompt_templates 
                SET name = ?, description = ?, prompt_text = ?, category = ?, 
                    tags = ?, is_active = ?, updated_at = ?
                WHERE id = ?
            ''', (
                prompt.name,
                prompt.description,
                prompt.prompt_text,
                prompt.category,
                json.dumps(prompt.tags),
                prompt.is_active,
                datetime.now().isoformat(),
                prompt_id
            ))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_prompt(self, prompt_id: int) -> bool:
        """Видаляє промпт."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM prompt_templates WHERE id = ?', (prompt_id,))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def record_usage(self, prompt_id: int, user_query: str, context: str, 
                    result: str, success: bool):
        """Записує використання промпту."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Записуємо використання
            cursor.execute('''
                INSERT INTO prompt_usage_history 
                (prompt_id, user_query, context, result, success, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                prompt_id,
                user_query,
                context,
                result,
                success,
                datetime.now().isoformat()
            ))
            
            # Оновлюємо статистику промпту
            cursor.execute('''
                UPDATE prompt_templates 
                SET usage_count = usage_count + 1,
                    success_rate = (
                        SELECT CAST(SUM(CASE WHEN success THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*)
                        FROM prompt_usage_history 
                        WHERE prompt_id = ?
                    )
                WHERE id = ?
            ''', (prompt_id, prompt_id))
            
            conn.commit()
    
    def get_best_prompt_for_query(self, user_query: str, category: str = None) -> Optional[PromptTemplate]:
        """Знаходить найкращий промпт для запиту користувача."""
        # Спочатку шукаємо за категорією
        if category:
            prompts = self.get_prompts_by_category(category)
        else:
            # Шукаємо по всіх категоріях
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, description, prompt_text, category, tags, 
                           is_active, created_at, updated_at, usage_count, success_rate
                    FROM prompt_templates WHERE is_active = 1
                    ORDER BY usage_count DESC, success_rate DESC
                ''')
                prompts = [self._row_to_prompt(row) for row in cursor.fetchall()]
        
        if not prompts:
            return None
        
        # Простий алгоритм вибору найкращого промпту
        # В реальному випадку тут буде більш складний алгоритм
        return prompts[0]
    
    def add_prompt_from_user(self, user_query: str, prompt_text: str, 
                           category: str = "user_defined") -> int:
        """Додає промпт від користувача."""
        prompt = PromptTemplate(
            name=f"User Prompt - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            description=f"Промпт створений користувачем для запиту: {user_query}",
            prompt_text=prompt_text,
            category=category,
            tags=["user_defined", "dynamic"],
            is_active=True
        )
        
        return self.add_prompt(prompt)
    
    def _row_to_prompt(self, row: Tuple) -> PromptTemplate:
        """Конвертує рядок з БД в об'єкт PromptTemplate."""
        tags = json.loads(row[5]) if row[5] else []
        return PromptTemplate(
            id=row[0],
            name=row[1],
            description=row[2],
            prompt_text=row[3],
            category=row[4],
            tags=tags,
            is_active=bool(row[6]),
            created_at=row[7],
            updated_at=row[8],
            usage_count=row[9],
            success_rate=row[10]
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Отримує статистику по промптах."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Загальна статистика
            cursor.execute('''
                SELECT COUNT(*) as total_prompts,
                       COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_prompts,
                       AVG(success_rate) as avg_success_rate,
                       SUM(usage_count) as total_usage
                FROM prompt_templates
            ''')
            
            stats = cursor.fetchone()
            
            # Статистика по категоріях
            cursor.execute('''
                SELECT category, COUNT(*) as count, AVG(success_rate) as avg_success
                FROM prompt_templates 
                WHERE is_active = 1
                GROUP BY category
            ''')
            
            categories = [{"category": row[0], "count": row[1], "avg_success": row[2]} 
                        for row in cursor.fetchall()]
            
            return {
                "total_prompts": stats[0],
                "active_prompts": stats[1],
                "avg_success_rate": stats[2],
                "total_usage": stats[3],
                "categories": categories
            }

# Приклади використання
if __name__ == "__main__":
    # Створюємо менеджер
    manager = DynamicPromptManager()
    
    # Додаємо промпт від користувача
    user_query = "Покажи всі категорії"
    prompt_text = """
    Ти - експерт з API. Користувач хоче побачити всі категорії.
    
    ЗАПИТ КОРИСТУВАЧА: {user_query}
    
    ЗАВДАННЯ:
    1. Знайди endpoint для отримання всіх категорій
    2. Якщо endpoint має параметр {id} - виправ на endpoint без параметрів
    3. Виконай запит та поверни результат
    
    ВІДПОВІДЬ У ФОРМАТІ:
    {{
        "endpoint": "правильний endpoint",
        "explanation": "пояснення виправлення",
        "result": "результат запиту"
    }}
    """
    
    prompt_id = manager.add_prompt_from_user(user_query, prompt_text, "swagger_error")
    print(f"✅ Додано промпт з ID: {prompt_id}")
    
    # Знаходимо найкращий промпт для запиту
    best_prompt = manager.get_best_prompt_for_query("Покажи всі категорії", "swagger_error")
    if best_prompt:
        print(f"🎯 Найкращий промпт: {best_prompt.name}")
        print(f"📊 Успішність: {best_prompt.success_rate:.2%}")
    
    # Отримуємо статистику
    stats = manager.get_statistics()
    print(f"📈 Статистика: {stats['total_prompts']} промптів, {stats['active_prompts']} активних")
