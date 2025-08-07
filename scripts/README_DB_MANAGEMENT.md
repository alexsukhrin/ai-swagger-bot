# Управління базою даних AI Swagger Bot

## 🧹 Очищення бази даних

### Автоматичне очищення при старті
```bash
./run_enhanced_chat.sh
```
Скрипт автоматично очищує базу даних та переіндексує Swagger файли.

### Ручне очищення
```bash
python scripts/clear_chroma_db.py
```

### Автоматичне очищення без підтвердження
```bash
python scripts/clear_chroma_db.py --auto
```

## 🔄 Переіндексація Swagger файлів

### Після очищення бази
```bash
python scripts/reindex_swagger.py
```

### Швидкий старт (очищення + переіндексація)
```bash
./scripts/fresh_start.sh
```

## 📁 Структура файлів

- `scripts/clear_chroma_db.py` - Очищення Chroma бази даних
- `scripts/reindex_swagger.py` - Переіндексація Swagger файлів
- `scripts/fresh_start.sh` - Швидкий старт (очищення + переіндексація)
- `scripts/check_dependencies.py` - Перевірка залежностей
- `run_enhanced_chat.sh` - Запуск чату з автоматичним очищенням

## 🔧 Вирішення проблем

### Проблема: ModuleNotFoundError (yaml, openai, etc.)
Якщо виникають помилки з відсутніми модулями:

1. **Перевірте залежності:**
   ```bash
   python scripts/check_dependencies.py
   ```

2. **Активуйте правильне середовище:**
   ```bash
   conda activate ai-swagger
   ```

3. **Встановіть відсутні пакети:**
   ```bash
   pip install PyYAML openai langchain chromadb streamlit
   ```

### Проблема: Permission denied
Якщо скрипти не запускаються:

```bash
chmod +x run_enhanced_chat.sh
chmod +x scripts/*.sh
```

### Проблема: Старі дані в базі
Якщо ви оновили Swagger файл, але бот все ще показує старі endpoints:

1. Очистіть базу даних:
   ```bash
   python scripts/clear_chroma_db.py --auto
   ```

2. Переіндексуйте файли:
   ```bash
   python scripts/reindex_swagger.py
   ```

3. Запустіть чат:
   ```bash
   ./run_enhanced_chat.sh
   ```

### Проблема: NumPy помилки
Якщо виникають помилки з NumPy:

```bash
conda activate ai-swagger
pip install "numpy<2.0"
```

### Проблема: Chroma помилки
Якщо виникають помилки з Chroma:

```bash
conda activate ai-swagger
pip install --upgrade chromadb
```

### Проблема: Використання venv замість conda
Якщо ви використовуєте venv, переключіться на conda:

```bash
# Деактивуйте venv
deactivate

# Активуйте conda середовище
conda activate ai-swagger

# Перевірте середовище
which python
```

## 📊 Перевірка стану бази

### Аналіз бази даних
```bash
python scripts/analyze_chroma_db.py
```

### Перевірка індексованих endpoints
```bash
python scripts/check_rag_status.py
```

### Перевірка залежностей
```bash
python scripts/check_dependencies.py
```

## 🚀 Типові сценарії використання

### 1. Перший запуск
```bash
# Перевірте залежності
python scripts/check_dependencies.py

# Активуйте conda середовище
conda activate ai-swagger

# Запустіть чат
./run_enhanced_chat.sh
```

### 2. Оновлення Swagger файлу
```bash
# Очистіть та переіндексуйте
./scripts/fresh_start.sh

# Запустіть чат
./run_enhanced_chat.sh
```

### 3. Додавання нового Swagger файлу
1. Додайте файл в `examples/swagger_specs/`
2. Запустіть переіндексацію:
   ```bash
   python scripts/reindex_swagger.py
   ```

### 4. Повне очищення та перезапуск
```bash
# Очистіть все
python scripts/clear_chroma_db.py --auto

# Переіндексуйте
python scripts/reindex_swagger.py

# Запустіть чат
./run_enhanced_chat.sh
```

## 📝 Примітки

- База даних зберігається в `./temp_chroma_db/`
- При очищенні видаляються ВСІ дані
- Після очищення потрібно переіндексувати Swagger файли
- Автоматичне очищення відбувається при кожному запуску `run_enhanced_chat.sh`
- **ВАЖЛИВО**: Використовуйте conda середовище `ai-swagger`, а не venv
