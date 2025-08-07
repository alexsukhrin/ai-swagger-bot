# Аналіз RAG системи в AI Swagger Bot

## 📋 Відповіді на питання

### 1. Чи парсимо ми кожного разу Swagger?

**НІ, не кожного разу.** Система працює наступним чином:

#### Процес ініціалізації:
1. **При першому запуску** - парситься Swagger файл і створюється векторна база
2. **При наступних запусках** - завантажується існуюча база з диску

#### Код в `rag_engine.py`:
```python
def _initialize_vectorstore(self):
    """Ініціалізація векторної бази даних."""
    try:
        # Спробуємо завантажити існуючу базу
        if not self.load_vectorstore():
            # Створюємо нову базу
            self._create_vectorstore_from_swagger()
    except Exception as e:
        print(f"Помилка ініціалізації векторної бази: {e}")
```

### 2. Де зберігаються ембедінги?

#### Фізичне зберігання:
- **Директорія**: `./chroma_db/`
- **SQLite база**: `chroma_db/chroma.sqlite3` (1.22 MB)
- **Бінарні файли**: `chroma_db/22d97def-cb41-4ebe-a3c6-03681d7a7004/`
  - `data_level0.bin` (6.1 MB) - самі вектори
  - `length.bin` (3.9 KB) - індекси
  - `header.bin` (100 B) - метадані

#### Структура даних:
```python
# В SQLite зберігаються:
- embeddings (вектори)
- documents (тексти)
- metadatas (метадані endpoints)
```

### 3. Чи в оперативній пам'яті?

**ТАК, під час роботи.** Ембедінги завантажуються в пам'ять при ініціалізації:

```python
def load_vectorstore(self) -> bool:
    """Завантажує існуючу векторну базу."""
    try:
        if os.path.exists(self.persist_directory):
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            return True
    except Exception as e:
        print(f"Помилка завантаження векторної бази: {e}")
    return False
```

### 4. Як перевірити поточний стан?

#### Запустіть скрипт перевірки:
```bash
python check_rag_status.py
```

#### Результати перевірки:
- ✅ **Chroma база даних**: 98 документів, 1.22 MB
- ✅ **Парсинг Swagger**: 80 endpoints
- ❌ **Ембедінги в пам'яті**: потребує OPENAI_API_KEY
- ❌ **Генерація ембедінгів**: потребує OPENAI_API_KEY

### 5. Як оновлюється RAG?

#### Автоматичне оновлення:
1. **При зміні Swagger файлу** - потрібно перезапустити
2. **При додаванні нових endpoints** - потрібно оновити файл

#### Ручне оновлення:
```python
# Очистити базу
rag_engine.clear_database()

# Перестворити
rag_engine._create_vectorstore_from_swagger()
```

## 🔧 Технічна архітектура

### Процес створення ембедінгів:

1. **Парсинг Swagger** → `SwaggerParser`
2. **Створення chunks** → `_create_vectorstore_from_swagger()`
3. **Генерація ембедінгів** → `OpenAIEmbeddings`
4. **Збереження в Chroma** → `Chroma.from_documents()`

### Структура chunks:
```python
chunk = {
    'text': f"""
    Endpoint: {endpoint.method} {endpoint.path}
    Summary: {endpoint.summary}
    Description: {endpoint.description}
    Parameters: ...
    Request Body: ...
    Responses: ...
    """,
    'metadata': {
        'path': endpoint.path,
        'method': endpoint.method,
        'summary': endpoint.summary,
        'tags': ', '.join(endpoint.tags)
    }
}
```

## 📊 Поточний стан системи

### Що працює:
- ✅ Swagger парсинг (80 endpoints)
- ✅ Збереження в Chroma DB (98 документів)
- ✅ Структура проекту

### Що потребує налаштування:
- ❌ OPENAI_API_KEY для генерації ембедінгів
- ❌ Перевірка SQLite схеми (колонка metadata)

## 🚀 Рекомендації

### 1. Налаштування API ключа:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 2. Перевірка роботи:
```bash
conda activate ai-swagger
python check_rag_status.py
```

### 3. Оновлення Swagger:
```python
# В коді
rag_engine.clear_database()
rag_engine._create_vectorstore_from_swagger()
```

## 📈 Висновки

1. **Swagger парситься один раз** при створенні бази
2. **Ембедінги зберігаються** в `./chroma_db/` на диску
3. **В пам'яті** завантажуються при ініціалізації
4. **Перевірити стан** можна через `check_rag_status.py`
5. **Оновлення** потребує перезапуску або ручного очищення бази

Система працює ефективно, але потребує налаштування API ключа для повної функціональності.
