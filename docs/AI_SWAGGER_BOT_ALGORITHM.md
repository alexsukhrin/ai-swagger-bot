# 🤖 Повний алгоритм роботи AI Swagger Bot

## 📋 Загальний огляд системи

AI Swagger Bot - це інтелектуальний агент, який автоматично аналізує Swagger/OpenAPI специфікації та формує відповідні API запити на основі природномовних запитів користувача.

---

## 🔄 Повний алгоритм роботи

### 1️⃣ **Ініціалізація системи**

```python
# Створення агента
agent = SwaggerAgent(
    swagger_spec_path="examples/swagger_specs/shop_api.json",
    enable_api_calls=False,
    openai_api_key="your-api-key"
)
```

**Кроки ініціалізації:**
1. **Перевірка файлів** - валідація Swagger файлу
2. **Парсинг Swagger** - `SwaggerParser` аналізує специфікацію
3. **Ініціалізація RAG** - створення/завантаження векторної бази
4. **Налаштування LLM** - ініціалізація OpenAI моделі
5. **Підготовка середовища** - налаштування логування та конфігурації

### 2️⃣ **Обробка запиту користувача**

#### Вхід: `"Додай товар: синя сукня, розмір 22, кількість 10"`

#### Крок 1: Аналіз наміру (Intent Analysis)
```python
def _analyze_user_intent(self, user_query: str):
    prompt = f"""
    Проаналізуй запит користувача та визначи намір та параметри.
    
    Запит: {user_query}
    
    Поверни JSON з наступною структурою:
    {{
        "intent": "create",
        "operation": "POST", 
        "resource": "product",
        "parameters": {{
            "name": "синя сукня",
            "size": "22",
            "quantity": "10"
        }}
    }}
    """
    
    response = self.llm.invoke([HumanMessage(content=prompt)])
    return json.loads(response.content)
```

**Результат:**
```json
{
    "intent": "create",
    "operation": "POST",
    "resource": "product", 
    "parameters": {
        "name": "синя сукня",
        "size": "22",
        "quantity": "10"
    }
}
```

#### Крок 2: Пошук відповідних endpoints (RAG Search)
```python
def search_similar_endpoints(self, query: str, k: int = 3):
    # Пошук в векторній базі
    docs = self.vectorstore.similarity_search(query, k=k)
    
    results = []
    for doc in docs:
        result = {
            'content': doc.page_content,
            'metadata': doc.metadata
        }
        results.append(result)
    
    return results
```

**Результат пошуку:**
```python
[
    {
        'content': 'Endpoint: POST /products\nSummary: Create a new product (Admin only)\nDescription: Creates a new product...',
        'metadata': {
            'method': 'POST',
            'path': '/products',
            'summary': 'Create a new product (Admin only)'
        }
    }
]
```

#### Крок 3: Формування API запиту
```python
def _form_api_request(self, user_query: str, intent: Dict, endpoints: List[Dict]):
    prompt = f"""
    Сформуй API запит на основі запиту користувача та доступних endpoints.
    
    Запит користувача: {user_query}
    Намір: {json.dumps(intent)}
    Базовий URL: {self.base_url}
    Доступні endpoints: {endpoints_info}
    
    Поверни JSON:
    {{
        "method": "POST",
        "path": "/products",
        "headers": {{"Content-Type": "application/json"}},
        "data": {{
            "name": "синя сукня",
            "size": "22", 
            "quantity": 10
        }}
    }}
    """
    
    response = self.llm.invoke([HumanMessage(content=prompt)])
    return json.loads(response.content)
```

**Результат:**
```json
{
    "method": "POST",
    "url": "https://api.example.com/products",
    "headers": {
        "Content-Type": "application/json"
    },
    "data": {
        "name": "синя сукня",
        "size": "22",
        "quantity": 10
    }
}
```

#### Крок 4: Виконання API виклику (опціонально)
```python
def _call_api(self, api_request: Dict[str, Any]):
    # Додавання JWT токена для авторизації
    if api_request['method'] == 'POST' and 'ngrok-free.app' in api_request['url']:
        headers['Authorization'] = f'Bearer {jwt_token}'
    
    # Виконання запиту
    response = requests.request(
        method=api_request['method'],
        url=api_request['url'],
        headers=api_request.get('headers', {}),
        json=api_request.get('data'),
        timeout=30
    )
    
    return {
        'status_code': response.status_code,
        'headers': dict(response.headers),
        'data': response.json() if response.content else None
    }
```

#### Крок 5: Форматування відповіді
```python
def _format_response(self, api_request: Dict, response: Optional[Dict] = None):
    result = "📋 Сформований API запит:\n"
    result += f"🔗 URL: {api_request['url']}\n"
    result += f"📤 Метод: {api_request['method']}\n"
    
    if api_request.get('data'):
        result += f"📦 Дані: {json.dumps(api_request['data'], indent=2)}\n"
    
    if response:
        result += f"\n✅ Статус: {response['status_code']}"
        if response.get('data'):
            result += f"\n📥 Відповідь: {json.dumps(response['data'], indent=2)}"
    
    return result
```

**Фінальна відповідь:**
```
📋 Сформований API запит:
🔗 URL: https://api.example.com/products
📤 Метод: POST
📦 Дані: {
  "name": "синя сукня",
  "size": "22",
  "quantity": 10
}

✅ Статус: 201
📥 Відповідь: {
  "id": 123,
  "name": "синя сукня",
  "size": "22",
  "quantity": 10,
  "created_at": "2025-08-07T13:50:17Z"
}
```

---

## 🏗️ Архітектура системи

### Основні компоненти:

#### 1. **SwaggerParser** (`src/swagger_parser.py`)
- Парсить Swagger/OpenAPI специфікації
- Витягує інформацію про endpoints
- Створює структуровані дані для RAG

#### 2. **RAGEngine** (`src/rag_engine.py`)
- Зберігає ембедінги в Chroma DB
- Виконує семантичний пошук endpoints
- Керує векторною базою даних

#### 3. **SwaggerAgent** (`src/api_agent.py`)
- Основний логічний компонент
- Координує всі процеси
- Взаємодіє з LLM для аналізу та формування запитів

#### 4. **LLM Integration** (OpenAI GPT)
- Аналіз наміру користувача
- Формування API запитів
- Обробка природної мови

---

## 🔄 Детальний процес обробки

### Фаза 1: Підготовка даних
```
Swagger файл → SwaggerParser → Endpoints → RAGEngine → Vector Database
```

### Фаза 2: Обробка запиту
```
User Query → Intent Analysis → RAG Search → API Formation → API Call → Response
```

### Фаза 3: Відповідь
```
API Response → Format Response → User Output
```

---

## 🎯 Приклади роботи

### Приклад 1: Створення товару
**Вхід:** `"Додай товар: синя сукня, розмір 22, кількість 10"`
**Результат:** POST /products з даними товару

### Приклад 2: Отримання товарів
**Вхід:** `"Покажи всі товари"`
**Результат:** GET /products

### Приклад 3: Оновлення товару
**Вхід:** `"Зміни ціну товару з ID 123 на 150 грн"`
**Результат:** PATCH /products/123 з новою ціною

---

## 🔧 Технічні деталі

### Векторна база даних:
- **Технологія:** Chroma DB
- **Розмір:** 6.0 MB бінарних даних
- **Документи:** 98 endpoints
- **Зберігання:** SQLite + бінарні файли

### LLM інтеграція:
- **Модель:** GPT-4 або GPT-3.5-turbo
- **Температура:** 0 (детерміновані відповіді)
- **Контекст:** Swagger специфікація + запит користувача

### API виклики:
- **Таймаут:** 30 секунд
- **Авторизація:** JWT токени для продакшн
- **Обробка помилок:** Timeout, Connection, JSON parsing

---

## 🚀 Інтерфейси

### 1. **CLI інтерфейс**
```bash
python cli.py
```

### 2. **Streamlit веб-інтерфейс**
```bash
streamlit run app.py
```

### 3. **Python API**
```python
from src.api_agent import SwaggerAgent
agent = SwaggerAgent("swagger.json")
response = agent.process_query("Додай товар")
```

---

## 📊 Статистика роботи

### Поточний стан:
- ✅ **80 endpoints** розпарсено з Swagger
- ✅ **98 документів** в векторній базі
- ✅ **6.0 MB** даних збережено
- ✅ **Підтримка** GET, POST, PUT, PATCH, DELETE

### Продуктивність:
- **Ініціалізація:** ~2-3 секунди
- **Обробка запиту:** ~1-2 секунди
- **API виклик:** ~0.5-2 секунди (залежить від API)

---

## 🔮 Розширення та покращення

### Можливі покращення:
1. **Кешування** - зберігання результатів API викликів
2. **Batch обробка** - одночасна обробка кількох запитів
3. **Аналітика** - відстеження використання endpoints
4. **Автоматичне оновлення** - синхронізація зі змінами API
5. **Мультимовність** - підтримка різних мов

### Архітектурні покращення:
1. **Мікросервіси** - розділення на окремі сервіси
2. **Асинхронність** - використання async/await
3. **Моніторинг** - метрики та логування
4. **Безпека** - валідація вхідних даних

---

## 📝 Висновок

AI Swagger Bot представляє собою комплексну систему, яка поєднує:
- **RAG (Retrieval-Augmented Generation)** для пошуку endpoints
- **LLM (Large Language Model)** для розуміння запитів
- **API інтеграцію** для виконання запитів
- **Векторну базу даних** для ефективного пошуку

Система автоматично перетворює природномовні запити в точні API виклики, що значно спрощує роботу з API для розробників та користувачів.
