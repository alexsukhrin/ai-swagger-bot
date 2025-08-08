# 🤖 AI Swagger Bot Widget

Легкий віджет для вбудовування AI асистента на будь-який сайт.

## 🚀 Швидке вбудовування

### 1. Базовий варіант
Додайте цей код в секцію `<head>` вашого сайту:

```html
<script src="http://localhost:5050/embed.js"></script>
```

### 2. З налаштуваннями
```html
<script>
window.AIWidgetConfig = {
    apiUrl: 'http://localhost:5050',
    position: 'bottom-right', // bottom-right, bottom-left, top-right, top-left
    title: 'AI Асистент',
    subtitle: 'Запитайте мене про щось'
};
</script>
<script src="http://localhost:5050/embed.js"></script>
```

## 📋 Приклади використання

### WordPress
Додайте в `functions.php`:
```php
function add_ai_widget() {
    wp_enqueue_script('ai-widget', 'http://localhost:5050/embed.js', array(), '1.0.0', false);
}
add_action('wp_enqueue_scripts', 'add_ai_widget');
```

### React/Vue/Angular
Додайте в `index.html`:
```html
<head>
    <script src="http://localhost:5050/embed.js"></script>
</head>
```

### Shopify
Додайте в `theme.liquid`:
```liquid
<head>
    <script src="http://localhost:5050/embed.js"></script>
</head>
```

## ⚙️ Налаштування

### Конфігурація
```javascript
window.AIWidgetConfig = {
    apiUrl: 'http://localhost:5050',        // URL вашого API
    position: 'bottom-right',               // Позиція віджету
    title: 'AI Swagger Bot',                // Заголовок
    subtitle: 'Запитайте про API',          // Підзаголовок
    theme: 'default',                       // Тема (default, dark, light)
    language: 'uk'                          // Мова (uk, en)
};
```

### Позиції
- `bottom-right` - Правий нижній кут (за замовчуванням)
- `bottom-left` - Лівий нижній кут
- `top-right` - Правий верхній кут
- `top-left` - Лівий верхній кут

## 🎯 Функції

### ✅ Автоматичне з'явлення
Віджет з'являється автоматично після завантаження сторінки

### ✅ Згортання/розгортання
Користувач може згорнути віджет в маленьку кнопку

### ✅ Збереження історії
Історія чату зберігається в localStorage

### ✅ Responsive дизайн
Автоматично адаптується до мобільних пристроїв

### ✅ Анімації
Плавні переходи та анімації

## 🧪 Програмне керування

### Показати віджет
```javascript
window.aiWidgetInstance.show();
```

### Приховати віджет
```javascript
window.aiWidgetInstance.hide();
```

### Видалити віджет
```javascript
window.aiWidgetInstance.destroy();
```

### Відправити повідомлення
```javascript
window.aiWidgetInstance.sendMessage();
```

### Додати повідомлення
```javascript
window.aiWidgetInstance.addMessage('Текст повідомлення', 'user');
```

## 🎨 Кастомізація стилів

### Зміна кольорів
```css
.ai-widget-header {
    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
}

.ai-widget-message.user .ai-widget-bubble {
    background: #ff6b6b;
}
```

### Зміна розміру
```css
.ai-widget {
    width: 400px;
    height: 600px;
}
```

### Зміна позиції
```css
.ai-widget {
    bottom: 50px;
    right: 50px;
}
```

## 📱 Responsive дизайн

Віджет автоматично адаптується:

- **Десктоп**: 350x500px в кутку
- **Планшет**: Зменшений розмір
- **Мобільний**: Майже весь екран

## 🔧 API Інтеграція

### Endpoint
```
POST http://localhost:5050/api/chat
```

### Запит
```json
{
    "message": "Користувацьке повідомлення",
    "api_spec_url": "URL до Swagger специфікації"
}
```

### Відповідь
```json
{
    "id": 1234567890,
    "message": "Відповідь AI бота",
    "timestamp": "2024-01-01T12:00:00.000Z",
    "type": "bot"
}
```

## 🚀 Продакшен

### 1. Замініть URL
```javascript
window.AIWidgetConfig = {
    apiUrl: 'https://your-domain.com',  // Ваш домен
    // інші налаштування...
};
```

### 2. Використовуйте HTTPS
```html
<script src="https://your-domain.com/embed.js"></script>
```

### 3. Налаштуйте CORS
```javascript
// На сервері
app.use(cors({
    origin: ['https://your-site.com', 'https://www.your-site.com'],
    methods: ['GET', 'POST', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization']
}));
```

### 4. Додайте аутентифікацію (опціонально)
```javascript
window.AIWidgetConfig = {
    apiUrl: 'https://your-domain.com',
    headers: {
        'Authorization': 'Bearer your-token'
    }
};
```

## 📊 Моніторинг

### Логування
```javascript
// Відстежуйте події віджету
window.aiWidgetInstance.on('message', (data) => {
    console.log('Нове повідомлення:', data);
});
```

### Аналітика
```javascript
// Google Analytics
gtag('event', 'ai_widget_interaction', {
    'event_category': 'engagement',
    'event_label': 'widget_used'
});
```

## 🔒 Безпека

### Рекомендації
- ✅ Використовуйте HTTPS
- ✅ Налаштуйте CORS для ваших доменів
- ✅ Додайте rate limiting
- ✅ Валідуйте вхідні дані
- ✅ Логуйте помилки

### Rate Limiting
```javascript
// На сервері
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 хвилин
    max: 100 // максимум 100 запитів з IP
});

app.use('/api/chat', limiter);
```

## 🧪 Тестування

### Локальне тестування
1. Запустіть API сервер:
```bash
cd api-service
npm start
```

2. Відкрийте приклад:
```
http://localhost:3031/example.html
```

3. Перевірте віджет:
```
http://localhost:3031/embed.html
```

### Тестування на продакшені
1. Розгорніть API на вашому сервері
2. Оновіть URL в конфігурації
3. Протестуйте на різних пристроях
4. Перевірте продуктивність

## 📞 Підтримка

### Поширені проблеми

**Віджет не з'являється**
- Перевірте, чи запущений API сервер
- Перевірте консоль браузера на помилки
- Переконайтеся, що CORS налаштований

**Помилки CORS**
```javascript
// На сервері
app.use(cors({
    origin: '*', // Для тестування
    methods: ['GET', 'POST', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization']
}));
```

**Віджет не відповідає**
- Перевірте URL API в конфігурації
- Перевірте мережеві запити в DevTools
- Переконайтеся, що API endpoint працює

### Контакты
- 📧 Email: support@example.com
- 💬 Discord: https://discord.gg/ai-widget
- 📖 Документація: https://docs.example.com/widget

## 📄 Ліцензія

MIT License - дивіться файл LICENSE для деталей.

---

**Готово до використання! 🚀**

Просто додайте один рядок коду і AI асистент з'явиться на вашому сайті.
