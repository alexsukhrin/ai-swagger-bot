/**
 * AI Swagger Bot Widget - Embed Script
 * Просто додайте цей скрипт на ваш сайт і віджет з'явиться автоматично
 */

(function() {
    'use strict';

    // Конфігурація за замовчуванням
    const DEFAULT_CONFIG = {
        apiUrl: 'http://localhost:5050',
        position: 'bottom-right',
        theme: 'default',
        language: 'uk',
        title: 'AI Swagger Bot',
        subtitle: 'Запитайте про API'
    };

    // Отримуємо конфігурацію з глобального об'єкта або використовуємо за замовчуванням
    const config = window.AIWidgetConfig || DEFAULT_CONFIG;

    // Стилі віджету
    const styles = `
        .ai-widget {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 350px;
            height: 500px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            transition: all 0.3s ease;
        }

        .ai-widget-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 16px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .ai-widget-title {
            font-size: 16px;
            font-weight: 600;
            margin: 0;
        }

        .ai-widget-subtitle {
            font-size: 12px;
            opacity: 0.8;
            margin: 4px 0 0 0;
        }

        .ai-widget-toggle {
            background: none;
            border: none;
            color: white;
            font-size: 20px;
            cursor: pointer;
            padding: 4px;
            border-radius: 4px;
            transition: background 0.2s;
        }

        .ai-widget-toggle:hover {
            background: rgba(255, 255, 255, 0.1);
        }

        .ai-widget-body {
            flex: 1;
            display: flex;
            flex-direction: column;
        }

        .ai-widget-chat {
            flex: 1;
            padding: 16px;
            overflow-y: auto;
            background: #f8f9fa;
        }

        .ai-widget-message {
            margin-bottom: 12px;
            display: flex;
            align-items: flex-start;
            animation: slideIn 0.3s ease;
        }

        .ai-widget-message.user {
            justify-content: flex-end;
        }

        .ai-widget-message.bot {
            justify-content: flex-start;
        }

        .ai-widget-bubble {
            max-width: 80%;
            padding: 12px 16px;
            border-radius: 18px;
            font-size: 14px;
            line-height: 1.4;
        }

        .ai-widget-message.user .ai-widget-bubble {
            background: #667eea;
            color: white;
            border-bottom-right-radius: 4px;
        }

        .ai-widget-message.bot .ai-widget-bubble {
            background: white;
            color: #333;
            border: 1px solid #e1e5e9;
            border-bottom-left-radius: 4px;
        }

        .ai-widget-input {
            padding: 16px;
            border-top: 1px solid #e1e5e9;
            background: white;
        }

        .ai-widget-input-form {
            display: flex;
            gap: 8px;
        }

        .ai-widget-input-field {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #e1e5e9;
            border-radius: 24px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
        }

        .ai-widget-input-field:focus {
            border-color: #667eea;
        }

        .ai-widget-send-btn {
            background: #667eea;
            color: white;
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s;
        }

        .ai-widget-send-btn:hover {
            background: #5a6fd8;
        }

        .ai-widget-send-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }

        .ai-widget-minimized {
            width: 60px;
            height: 60px;
        }

        .ai-widget-minimized .ai-widget-body {
            display: none;
        }

        .ai-widget-minimized .ai-widget-header {
            height: 100%;
            padding: 0;
            justify-content: center;
        }

        .ai-widget-minimized .ai-widget-title {
            display: none;
        }

        .ai-widget-minimized .ai-widget-subtitle {
            display: none;
        }

        .ai-widget-typing {
            display: flex;
            align-items: center;
            gap: 4px;
            padding: 12px 16px;
            background: white;
            border: 1px solid #e1e5e9;
            border-radius: 18px;
            border-bottom-left-radius: 4px;
            max-width: 80%;
        }

        .ai-widget-typing-dot {
            width: 8px;
            height: 8px;
            background: #999;
            border-radius: 50%;
            animation: typing 1.4s infinite;
        }

        .ai-widget-typing-dot:nth-child(2) {
            animation-delay: 0.2s;
        }

        .ai-widget-typing-dot:nth-child(3) {
            animation-delay: 0.4s;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes typing {
            0%, 60%, 100% {
                transform: translateY(0);
            }
            30% {
                transform: translateY(-10px);
            }
        }

        @media (max-width: 480px) {
            .ai-widget {
                width: calc(100vw - 40px);
                height: calc(100vh - 40px);
                bottom: 20px;
                right: 20px;
            }
        }
    `;

    // HTML шаблон віджету
    const widgetHTML = `
        <div class="ai-widget" id="aiWidget">
            <div class="ai-widget-header">
                <div>
                    <h3 class="ai-widget-title">${config.title}</h3>
                    <p class="ai-widget-subtitle">${config.subtitle}</p>
                </div>
                <button class="ai-widget-toggle" id="toggleBtn">−</button>
            </div>

            <div class="ai-widget-body">
                <div class="ai-widget-chat" id="chatContainer">
                    <div class="ai-widget-message bot">
                        <div class="ai-widget-bubble">
                            Привіт! Я AI Swagger Bot. Запитайте мене про API endpoints, документацію або як використовувати певні функції.
                        </div>
                    </div>
                </div>

                <div class="ai-widget-input">
                    <form class="ai-widget-input-form" id="chatForm">
                        <input
                            type="text"
                            class="ai-widget-input-field"
                            id="messageInput"
                            placeholder="Введіть ваше запитання..."
                            autocomplete="off"
                        >
                        <button type="submit" class="ai-widget-send-btn" id="sendBtn">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
                            </svg>
                        </button>
                    </form>
                </div>
            </div>
        </div>
    `;

    // Функція для встановлення позиції
    function setPosition(widget, position) {
        const positions = {
            'bottom-right': { bottom: '20px', right: '20px' },
            'bottom-left': { bottom: '20px', left: '20px' },
            'top-right': { top: '20px', right: '20px' },
            'top-left': { top: '20px', left: '20px' }
        };

        const pos = positions[position] || positions['bottom-right'];
        Object.assign(widget.style, pos);
    }

    // Функція для додавання стилів
    function injectStyles() {
        if (!document.getElementById('ai-widget-styles')) {
            const style = document.createElement('style');
            style.id = 'ai-widget-styles';
            style.textContent = styles;
            document.head.appendChild(style);
        }
    }

    // Функція для створення віджету
    function createWidget() {
        const div = document.createElement('div');
        div.innerHTML = widgetHTML;
        const widget = div.firstElementChild;

        // Встановлюємо позицію
        setPosition(widget, config.position);

        document.body.appendChild(widget);

        return widget;
    }

    // Функція для ініціалізації віджету
    function initWidget() {
        // Додаємо стилі
        injectStyles();

        // Створюємо віджет
        const widget = createWidget();

        // Отримуємо елементи
        const chatContainer = document.getElementById('chatContainer');
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        const toggleBtn = document.getElementById('toggleBtn');
        const chatForm = document.getElementById('chatForm');

        let isMinimized = false;
        let isTyping = false;

        // Функція для додавання повідомлення
        function addMessage(text, type) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `ai-widget-message ${type}`;

            const bubbleDiv = document.createElement('div');
            bubbleDiv.className = 'ai-widget-bubble';
            bubbleDiv.textContent = text;

            messageDiv.appendChild(bubbleDiv);
            chatContainer.appendChild(messageDiv);

            // Прокручуємо до останнього повідомлення
            chatContainer.scrollTop = chatContainer.scrollHeight;

            // Зберігаємо в історію
            saveMessage(text, type);
        }

        // Функція для показу індикатора набору
        function showTyping() {
            isTyping = true;
            const typingDiv = document.createElement('div');
            typingDiv.className = 'ai-widget-message bot';
            typingDiv.id = 'typingIndicator';

            const bubbleDiv = document.createElement('div');
            bubbleDiv.className = 'ai-widget-typing';
            bubbleDiv.innerHTML = `
                <div class="ai-widget-typing-dot"></div>
                <div class="ai-widget-typing-dot"></div>
                <div class="ai-widget-typing-dot"></div>
            `;

            typingDiv.appendChild(bubbleDiv);
            chatContainer.appendChild(typingDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        // Функція для приховування індикатора набору
        function hideTyping() {
            isTyping = false;
            const typingIndicator = document.getElementById('typingIndicator');
            if (typingIndicator) {
                typingIndicator.remove();
            }
        }

        // Функція для відправки повідомлення
        async function sendMessage() {
            const message = messageInput.value.trim();
            if (!message || isTyping) return;

            // Додаємо повідомлення користувача
            addMessage(message, 'user');
            messageInput.value = '';
            sendBtn.disabled = true;

            // Показуємо індикатор набору
            showTyping();

            try {
                const response = await fetch(`${config.apiUrl}/api/chat`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: message,
                        api_spec_url: window.location.origin + '/api/swagger.json'
                    })
                });

                const data = await response.json();

                // Приховуємо індикатор набору
                hideTyping();

                // Додаємо відповідь бота
                addMessage(data.message, 'bot');

            } catch (error) {
                console.error('Error sending message:', error);
                hideTyping();
                addMessage('Вибачте, сталася помилка. Спробуйте ще раз.', 'bot');
            }

            sendBtn.disabled = false;
            messageInput.focus();
        }

        // Функція для збереження повідомлення
        function saveMessage(text, type) {
            const history = getChatHistory();
            history.push({
                text,
                type,
                timestamp: new Date().toISOString()
            });

            // Зберігаємо тільки останні 50 повідомлень
            if (history.length > 50) {
                history.splice(0, history.length - 50);
            }

            localStorage.setItem('ai-widget-chat-history', JSON.stringify(history));
        }

        // Функція для отримання історії чату
        function getChatHistory() {
            const history = localStorage.getItem('ai-widget-chat-history');
            return history ? JSON.parse(history) : [];
        }

        // Функція для завантаження історії
        function loadChatHistory() {
            const history = getChatHistory();
            if (history.length > 0) {
                // Очищаємо початкове повідомлення
                chatContainer.innerHTML = '';

                // Завантажуємо історію
                history.forEach(msg => {
                    addMessage(msg.text, msg.type);
                });
            }
        }

        // Функція для перемикання віджету
        function toggleWidget() {
            isMinimized = !isMinimized;
            widget.classList.toggle('ai-widget-minimized', isMinimized);
            toggleBtn.textContent = isMinimized ? '+' : '−';
        }

        // Додаємо обробники подій
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            sendMessage();
        });

        toggleBtn.addEventListener('click', toggleWidget);

        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Завантажуємо історію
        loadChatHistory();

        // Повертаємо об'єкт для керування віджетом
        return {
            widget,
            show: () => { widget.style.display = 'flex'; },
            hide: () => { widget.style.display = 'none'; },
            destroy: () => {
                if (widget.parentNode) {
                    widget.parentNode.removeChild(widget);
                }
            },
            sendMessage,
            addMessage
        };
    }

    // Ініціалізуємо віджет після завантаження сторінки
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.aiWidgetInstance = initWidget();
        });
    } else {
        window.aiWidgetInstance = initWidget();
    }

})();
