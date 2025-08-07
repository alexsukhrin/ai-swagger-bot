"""
RAG (Retrieval-Augmented Generation) двигун для роботи з API endpoints.
Використовує векторну базу даних для зберігання та пошуку інформації про API.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Імпортуємо enhanced_swagger_parser
try:
    from .enhanced_swagger_parser import EnhancedSwaggerParser
except ImportError:
    from enhanced_swagger_parser import EnhancedSwaggerParser

# Налаштовуємо логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGEngine:
    """RAG двигун для роботи з API endpoints."""
    
    def __init__(self, swagger_spec_path: str, persist_directory: str = None, config: Dict[str, Any] = None):
        """
        Ініціалізація RAG двигуна.
        
        Args:
            swagger_spec_path: Шлях до Swagger специфікації
            persist_directory: Директорія для зберігання векторної бази
            config: Конфігурація RAG
        """
        from src.config import Config
        
        self.swagger_spec_path = swagger_spec_path
        self.persist_directory = persist_directory or Config.CHROMA_DB_PATH
        
        # Використовуємо конфігурацію або значення за замовчуванням
        if config:
            chunk_size = config.get('chunk_size', 1000)
            chunk_overlap = config.get('chunk_overlap', 200)
        else:
            chunk_size = 1000
            chunk_overlap = 200
        
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        self.vectorstore = None
        
        logger.info(f"Ініціалізація RAG Engine: {swagger_spec_path}")
        logger.info(f"Директорія бази: {self.persist_directory}")
        
        # Ініціалізуємо базу
        self._initialize_vectorstore()
    
    def _initialize_vectorstore(self):
        """Ініціалізація векторної бази даних."""
        try:
            # Спробуємо завантажити існуючу базу
            if not self.load_vectorstore():
                # Створюємо нову базу
                self._create_vectorstore_from_swagger()
        except Exception as e:
            logger.error(f"Помилка ініціалізації векторної бази: {e}")
            raise
    
    def _create_vectorstore_from_swagger(self):
        """Створює векторну базу з Swagger специфікації."""
        try:
            logger.info("Парсинг Swagger специфікації...")
            # Парсимо Swagger файл
            parser = EnhancedSwaggerParser(self.swagger_spec_path)
            
            # Використовуємо новий метод для створення chunks
            chunks = parser.create_enhanced_endpoint_chunks()
            logger.info(f"Створено {len(chunks)} chunks")
            
            # Створюємо векторну базу
            self.create_vectorstore(chunks)
            logger.info("Векторна база створена успішно")
            
        except Exception as e:
            logger.error(f"Помилка створення векторної бази: {e}")
            raise
    
    def create_vectorstore(self, chunks: List[Dict[str, Any]]) -> None:
        """
        Створює векторну базу даних з chunks.
        
        Args:
            chunks: Список chunks з метаданими
        """
        documents = []
        
        for chunk in chunks:
            # Створюємо Document об'єкт для LangChain
            doc = Document(
                page_content=chunk['text'],
                metadata=chunk['metadata']
            )
            documents.append(doc)
        
        # Створюємо векторну базу без розбиття на частини
        # щоб уникнути дублікатів endpoints
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        
        # Зберігаємо базу
        self.vectorstore.persist()
        
    def load_vectorstore(self) -> bool:
        """
        Завантажує існуючу векторну базу.
        
        Returns:
            True якщо база завантажена успішно, False інакше
        """
        try:
            if os.path.exists(self.persist_directory):
                logger.info(f"Завантаження існуючої бази: {self.persist_directory}")
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
                logger.info("База завантажена успішно")
                return True
        except Exception as e:
            logger.error(f"Помилка завантаження векторної бази: {e}")
        return False
    
    def search_similar_endpoints(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Шукає подібні endpoints за запитом.
        
        Args:
            query: Пошуковий запит
            k: Кількість результатів для повернення
            
        Returns:
            Список релевантних endpoints з метаданими
        """
        if not self.vectorstore:
            return []
        
        try:
            # Виконуємо пошук
            docs = self.vectorstore.similarity_search(query, k=k)
            
            results = []
            for doc in docs:
                result = {
                    'content': doc.page_content,
                    'metadata': doc.metadata
                }
                results.append(result)
                
            return results
        except Exception as e:
            logger.error(f"Помилка пошуку endpoints: {e}")
            return []
    
    def get_endpoint_by_method_and_path(self, method: str, path: str) -> Optional[Dict[str, Any]]:
        """
        Знаходить конкретний endpoint за методом та шляхом.
        
        Args:
            method: HTTP метод (GET, POST, etc.)
            path: Шлях endpoint
            
        Returns:
            Endpoint з метаданими або None
        """
        if not self.vectorstore:
            return None
        
        try:
            # Створюємо запит для пошуку конкретного endpoint
            query = f"{method} {path}"
            docs = self.vectorstore.similarity_search(query, k=1)
            
            if docs:
                return {
                    'content': docs[0].page_content,
                    'metadata': docs[0].metadata
                }
        except Exception as e:
            logger.error(f"Помилка пошуку endpoint: {e}")
        
        return None
    
    def get_all_endpoints(self) -> List[Dict[str, Any]]:
        """
        Отримує всі endpoints з бази.
        
        Returns:
            Список всіх endpoints з метаданими
        """
        if not self.vectorstore:
            return []
        
        try:
            # Отримуємо всі документи
            docs = self.vectorstore.get()
            
            results = []
            documents = docs.get('documents', [])
            metadatas = docs.get('metadatas', [])
            
            for i, content in enumerate(documents):
                metadata = metadatas[i] if i < len(metadatas) else {}
                results.append({
                    'content': content,
                    'metadata': metadata
                })
                
            return results
        except Exception as e:
            print(f"Помилка отримання endpoints: {e}")
            return []
    
    def clear_database(self) -> None:
        """Очищає векторну базу даних."""
        try:
            if self.vectorstore:
                self.vectorstore.delete_collection()
                self.vectorstore = None
            
            # Видаляємо директорію
            import shutil
            if os.path.exists(self.persist_directory):
                shutil.rmtree(self.persist_directory)
        except Exception as e:
            print(f"Помилка очищення бази: {e}")
