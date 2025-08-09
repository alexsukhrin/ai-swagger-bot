"""
Менеджер черги для асинхронного створення embeddings
"""

import asyncio
import json
import logging
import os
import tempfile
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from src.rag_engine import PostgresRAGEngine

logger = logging.getLogger(__name__)


class EmbeddingTask:
    """Завдання для створення embeddings"""

    def __init__(
        self,
        task_id: str,
        user_id: str,
        swagger_spec_id: str,
        swagger_data: dict,
        enable_gpt_enhancement: bool = True,
    ):
        self.task_id = task_id
        self.user_id = user_id
        self.swagger_spec_id = swagger_spec_id
        self.swagger_data = swagger_data
        self.enable_gpt_enhancement = enable_gpt_enhancement  # Нове поле для GPT
        self.status = "pending"  # pending, processing, completed, failed
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error_message: Optional[str] = None
        self.progress = 0  # 0-100


class QueueManager:
    """Менеджер черги для створення embeddings"""

    def __init__(self):
        self.tasks: Dict[str, EmbeddingTask] = {}
        self.processing = False
        self.worker_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def add_task(
        self,
        user_id: str,
        swagger_spec_id: str,
        swagger_data: dict,
        enable_gpt_enhancement: bool = True,
    ) -> str:
        """Додає нове завдання в чергу"""
        task_id = str(uuid4())

        with self._lock:
            task = EmbeddingTask(
                task_id, user_id, swagger_spec_id, swagger_data, enable_gpt_enhancement
            )
            self.tasks[task_id] = task
            logger.info(f"📋 Додано завдання {task_id} для користувача {user_id} з GPT покращенням")

            # Запускаємо worker якщо він не працює
            if not self.processing:
                self._start_worker()

        return task_id

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Отримує статус завдання"""
        with self._lock:
            task = self.tasks.get(task_id)
            if not task:
                return None

            return {
                "task_id": task.task_id,
                "status": task.status,
                "progress": task.progress,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "error_message": task.error_message,
            }

    def get_user_tasks(self, user_id: str) -> List[Dict]:
        """Отримує всі завдання користувача"""
        with self._lock:
            user_tasks = [task for task in self.tasks.values() if task.user_id == user_id]

            return [
                {
                    "task_id": task.task_id,
                    "swagger_spec_id": task.swagger_spec_id,
                    "status": task.status,
                    "progress": task.progress,
                    "created_at": task.created_at.isoformat(),
                    "started_at": task.started_at.isoformat() if task.started_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "error_message": task.error_message,
                }
                for task in user_tasks
            ]

    def _start_worker(self):
        """Запускає worker thread для обробки завдань"""
        if self.worker_thread and self.worker_thread.is_alive():
            return

        self.processing = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        logger.info("🚀 Worker thread запущено")

    def _worker_loop(self):
        """Основний цикл worker'а"""
        while self.processing:
            try:
                # Знаходимо наступне завдання
                next_task = None
                with self._lock:
                    for task in self.tasks.values():
                        if task.status == "pending":
                            next_task = task
                            break

                if next_task:
                    self._process_task(next_task)
                else:
                    # Немає завдань, чекаємо
                    time.sleep(1)

            except Exception as e:
                logger.error(f"❌ Помилка в worker loop: {e}")
                time.sleep(5)

    def _process_task(self, task: EmbeddingTask):
        """Обробляє одне завдання"""
        try:
            logger.info(f"🔄 Початок обробки завдання {task.task_id}")

            # Оновлюємо статус
            task.status = "processing"
            task.started_at = datetime.now()

            # Створюємо тимчасовий файл
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
                temp_file.write(json.dumps(task.swagger_data))
                temp_file_path = temp_file.name

            try:
                # Створюємо RAG engine
                rag_engine = PostgresRAGEngine(
                    user_id=task.user_id, swagger_spec_id=task.swagger_spec_id
                )

                # Оновлюємо прогрес
                task.progress = 25

                # Створюємо embeddings з GPT enhancement
                success = rag_engine.create_vectorstore_from_swagger(
                    temp_file_path, enable_gpt_enhancement=task.enable_gpt_enhancement
                )

                task.progress = 100

                if success:
                    task.status = "completed"
                    logger.info(f"✅ Завдання {task.task_id} завершено успішно")
                else:
                    task.status = "failed"
                    task.error_message = "Не вдалося створити embeddings"
                    logger.warning(f"⚠️ Завдання {task.task_id} завершено з помилкою")

            finally:
                # Видаляємо тимчасовий файл
                try:
                    os.unlink(temp_file_path)
                except:
                    pass

            task.completed_at = datetime.now()

        except Exception as e:
            logger.error(f"❌ Помилка обробки завдання {task.task_id}: {e}")
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.now()

    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Видаляє старі завершені завдання"""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)

        with self._lock:
            tasks_to_remove = []
            for task_id, task in self.tasks.items():
                if (
                    task.status in ["completed", "failed"]
                    and task.completed_at
                    and task.completed_at.timestamp() < cutoff_time
                ):
                    tasks_to_remove.append(task_id)

            for task_id in tasks_to_remove:
                del self.tasks[task_id]

            if tasks_to_remove:
                logger.info(f"🗑️ Видалено {len(tasks_to_remove)} старих завдань")


# Глобальний екземпляр менеджера черги
queue_manager = QueueManager()
