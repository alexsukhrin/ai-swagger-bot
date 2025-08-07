"""
Покращений Streamlit чат-інтерфейс для InteractiveSwaggerAgent
"""

import streamlit as st
import os
import sys
from pathlib import Path
import json
import requests
from datetime import datetime
import logging
from typing import Dict, Any, List
import time
from dotenv import load_dotenv

# Завантажуємо змінні середовища з .env файлу
load_dotenv()

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Додаємо шлях до src
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

try:
    from interactive_api_agent import InteractiveSwaggerAgent
except ImportError as e:
    st.error(f"❌ Помилка імпорту InteractiveSwaggerAgent: {e}")
    st.info("💡 Переконайтеся що ви використовуєте conda середовище: conda activate ai-swagger")
    st.stop()


def check_environment():
    """Перевіряє налаштування середовища."""
    if not os.getenv('OPENAI_API_KEY'):
        st.error("❌ Не знайдено OPENAI_API_KEY в змінних середовища!")
        st.info("Створіть файл .env з OPENAI_API_KEY=your_key_here")
        return False
    return True


def initialize_session_state():
    """Ініціалізує стан сесії для чату."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'swagger_path' not in st.session_state:
        st.session_state.swagger_path = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if 'needs_followup' not in st.session_state:
        st.session_state.needs_followup = False
    if 'last_interaction' not in st.session_state:
        st.session_state.last_interaction = None
    if 'chat_started' not in st.session_state:
        st.session_state.chat_started = False
    if 'api_calls_enabled' not in st.session_state:
        st.session_state.api_calls_enabled = False


def initialize_agent(swagger_path: str, enable_api_calls: bool = False):
    """Ініціалізує InteractiveSwaggerAgent."""
    try:
        with st.spinner("🤖 Ініціалізація InteractiveSwaggerAgent..."):
            agent = InteractiveSwaggerAgent(
                swagger_spec_path=swagger_path,
                enable_api_calls=enable_api_calls,
                openai_api_key=os.getenv('OPENAI_API_KEY'),
                jwt_token=os.getenv('JWT_TOKEN')
            )
            return agent
    except Exception as e:
        st.error(f"❌ Помилка ініціалізації агента: {e}")
        return None


def format_message(content: str, role: str, timestamp: datetime = None, status: str = None):
    """Форматує повідомлення для чату."""
    if timestamp is None:
        timestamp = datetime.now()
    
    return {
        "role": role,
        "content": content,
        "timestamp": timestamp,
        "status": status
    }


def display_message(message: Dict[str, Any]):
    """Відображає повідомлення в чаті."""
    role = message["role"]
    content = message["content"]
    timestamp = message.get("timestamp", datetime.now())
    status = message.get("status")
    
    if role == "user":
        with st.chat_message("user", avatar="👤"):
            st.write(content)
            st.caption(f"🕐 {timestamp.strftime('%H:%M:%S')}")
    elif role == "assistant":
        with st.chat_message("assistant", avatar="🤖"):
            # Додаємо статус якщо є
            if status:
                status_emoji = {
                    'success': '✅',
                    'error': '❌',
                    'needs_followup': '🔄',
                    'preview': '👁️'
                }.get(status, '❓')
                st.markdown(f"{status_emoji} **Статус: {status.upper()}**")
                st.markdown("---")
            
            st.markdown(content)
            st.caption(f"🕐 {timestamp.strftime('%H:%M:%S')}")
    elif role == "system":
        with st.chat_message("assistant", avatar="⚙️"):
            st.info(content)
            st.caption(f"🕐 {timestamp.strftime('%H:%M:%S')}")


def process_user_message(user_message: str, agent: InteractiveSwaggerAgent, user_id: str):
    """Обробляє повідомлення користувача."""
    try:
        if st.session_state.needs_followup:
            # Обробляємо додатковий запит
            response = agent.process_followup_query(user_message, user_id)
            st.session_state.needs_followup = response.get('needs_followup', False)
        else:
            # Обробляємо новий запит
            response = agent.process_interactive_query(user_message, user_id)
            st.session_state.needs_followup = response.get('needs_followup', False)
        
        return response
        
    except Exception as e:
        logger.error(f"Помилка обробки повідомлення: {e}")
        return {
            'response': f"❌ Помилка обробки запиту: {str(e)}",
            'status': 'error',
            'needs_followup': False
        }


def get_enhanced_chat_style():
    """Повертає покращені CSS стилі для чату."""
    return """
    <style>
    /* Основні стилі */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    
    .chat-container {
        background-color: #f8f9fa;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid #e9ecef;
    }
    
    .message-bubble {
        background-color: white;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        border-left: 4px solid #007bff;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
    }
    
    .assistant-message {
        background-color: #f3e5f5;
        border-left-color: #9c27b0;
    }
    
    .system-message {
        background-color: #fff3e0;
        border-left-color: #ff9800;
    }
    
    .status-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 10px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .status-success {
        background-color: #4caf50;
        color: white;
    }
    
    .status-error {
        background-color: #f44336;
        color: white;
    }
    
    .status-needs-followup {
        background-color: #ff9800;
        color: white;
    }
    
    .status-preview {
        background-color: #2196f3;
        color: white;
    }
    
    .sidebar-section {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid #e9ecef;
    }
    
    .input-container {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        border: 2px solid #e9ecef;
        margin-top: 20px;
    }
    
    .button-primary {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 20px;
        font-weight: bold;
    }
    
    .button-secondary {
        background-color: #6c757d;
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 20px;
    }
    
    .stats-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid #e9ecef;
        text-align: center;
    }
    
    .stats-number {
        font-size: 24px;
        font-weight: bold;
        color: #007bff;
    }
    
    .stats-label {
        font-size: 12px;
        color: #6c757d;
        text-transform: uppercase;
    }
    </style>
    """


def display_chat_stats():
    """Відображає статистику чату."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stats-card">
            <div class="stats-number">""" + str(len(st.session_state.messages)) + """</div>
            <div class="stats-label">Повідомлень</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{user_messages}</div>
            <div class="stats-label">Ваших запитів</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        assistant_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{assistant_messages}</div>
            <div class="stats-label">Відповідей бота</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if st.session_state.needs_followup:
            status_text = "🔄 Очікує"
            status_color = "#ff9800"
        else:
            status_text = "✅ Готовий"
            status_color = "#4caf50"
        
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number" style="color: {status_color};">{status_text}</div>
            <div class="stats-label">Статус</div>
        </div>
        """, unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="AI Swagger Bot - Розумний Чат",
        page_icon="💬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Додаємо CSS стилі
    st.markdown(get_enhanced_chat_style(), unsafe_allow_html=True)
    
    # Перевіряємо середовище
    if not check_environment():
        return
    
    # Ініціалізуємо стан сесії
    initialize_session_state()
    
    # Заголовок
    st.markdown("""
    <div class="main-header">
        <h1>💬 AI Swagger Bot - Розумний Чат</h1>
        <p>🤖 Інтерактивний агент для роботи з API через природну мову</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Бічна панель для налаштувань
    with st.sidebar:
        st.header("⚙️ Налаштування")
        
        # Вибір Swagger файлу
        swagger_files = list(Path("examples/swagger_specs").glob("*.json"))
        swagger_files.extend(Path("examples/swagger_specs").glob("*.yaml"))
        swagger_files.extend(Path("examples/swagger_specs").glob("*.yml"))
        
        if swagger_files:
            selected_file = st.selectbox(
                "📄 Swagger файл:",
                [f.name for f in swagger_files],
                index=0
            )
            swagger_path = f"examples/swagger_specs/{selected_file}"
        else:
            st.error("❌ Не знайдено Swagger файлів в examples/swagger_specs/")
            return
        
        # Налаштування API викликів
        enable_api_calls = st.checkbox("🔗 Дозволити виклики API", value=False)
        
        # Ініціалізація агента
        if st.button("🚀 Ініціалізувати агента", type="primary"):
            agent = initialize_agent(swagger_path, enable_api_calls)
            if agent:
                st.session_state.agent = agent
                st.session_state.swagger_path = swagger_path
                st.session_state.api_calls_enabled = enable_api_calls
                st.session_state.chat_started = True
                st.success("✅ Агент успішно ініціалізовано!")
                
                # Додаємо привітальне повідомлення
                welcome_message = format_message(
                    f"🤖 Привіт! Я InteractiveSwaggerAgent готовий допомогти вам працювати з API.\n\n"
                    f"📋 Поточні налаштування:\n"
                    f"• Swagger файл: {selected_file}\n"
                    f"• API виклики: {'✅ Увімкнено' if enable_api_calls else '❌ Вимкнено'}\n"
                    f"• Користувач ID: {st.session_state.user_id}\n\n"
                    f"💡 Спробуйте запити як:\n"
                    f"• 'Створи нову категорію'\n"
                    f"• 'Покажи всі товари'\n"
                    f"• 'Отримай товар з ID 1'\n"
                    f"• 'Створи товар з назвою Телефон'",
                    "assistant"
                )
                st.session_state.messages.append(welcome_message)
                st.rerun()
            else:
                st.error("❌ Помилка ініціалізації агента")
        
        # Інформація про агента
        if st.session_state.agent:
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.subheader("📊 Інформація про агента")
            
            # Отримуємо інформацію про API
            try:
                api_summary = st.session_state.agent.get_api_summary()
                st.write(f"🌐 Базовий URL: {api_summary.get('base_url', 'Невідомо')}")
                st.write(f"📋 Endpoints: {api_summary.get('total_endpoints', 0)}")
                st.write(f"📚 Схеми: {api_summary.get('total_schemas', 0)}")
            except Exception as e:
                st.warning(f"⚠️ Не вдалося отримати інформацію про API: {e}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Кнопки керування
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.subheader("🎛️ Керування")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🗑️ Очистити історію"):
                    st.session_state.messages = []
                    st.session_state.needs_followup = False
                    st.session_state.last_interaction = None
                    st.success("✅ Історія очищена!")
                    st.rerun()
            
            with col2:
                if st.button("📥 Експорт чату"):
                    export_chat_history()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Статус сесії
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.subheader("📈 Статус сесії")
        st.write(f"👤 Користувач: {st.session_state.user_id}")
        st.write(f"💬 Повідомлень: {len(st.session_state.messages)}")
        if st.session_state.needs_followup:
            st.warning("🔄 Очікує додаткової інформації")
        else:
            st.success("✅ Готовий до нових запитів")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Основний контент
    if not st.session_state.agent:
        st.info("🚀 Натисніть 'Ініціалізувати агента' в бічній панелі для початку роботи")
        return
    
    # Статистика чату
    display_chat_stats()
    
    # Чат контейнер
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.subheader("💬 Історія розмови")
    
    # Відображаємо всі повідомлення
    for message in st.session_state.messages:
        display_message(message)
    
    # Показуємо статус якщо потрібна додаткова інформація
    if st.session_state.needs_followup:
        st.warning("🔄 Очікуємо додаткової інформації від вас...")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Поле введення
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    st.subheader("✍️ Введіть ваш запит")
    
    # Визначаємо placeholder
    if st.session_state.needs_followup:
        placeholder = "💡 Надайте додаткову інформацію..."
    else:
        placeholder = "💬 Введіть ваш запит природною мовою..."
    
    # Поле введення
    user_input = st.text_area(
        "Ваше повідомлення:",
        placeholder=placeholder,
        height=100,
        key="user_input"
    )
    
    # Кнопки дій
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        if st.button("📤 Надіслати", type="primary"):
            if user_input.strip():
                process_user_input(user_input.strip())
    
    with col2:
        if st.button("🔄 Оновити"):
            st.rerun()
    
    with col3:
        if st.button("🗑️ Очистити поле"):
            # Використовуємо ключ для очищення поля
            st.rerun()
    
    with col4:
        if st.button("💡 Підказки"):
            show_tips()
    
    st.markdown('</div>', unsafe_allow_html=True)


def process_user_input(user_input: str):
    """Обробляє введений користувачем текст."""
    if not user_input.strip():
        return
    
    # Додаємо повідомлення користувача
    user_message = format_message(user_input, "user")
    st.session_state.messages.append(user_message)
    
    # Обробляємо запит
    with st.spinner("🤖 Обробляю запит..."):
        response = process_user_message(
            user_input, 
            st.session_state.agent, 
            st.session_state.user_id
        )
    
    # Форматуємо відповідь
    status = response.get('status', 'unknown')
    content = response.get('response', 'Немає відповіді')
    
    # Додаємо відповідь асистента
    assistant_message = format_message(content, "assistant", status=status)
    st.session_state.messages.append(assistant_message)
    
    # Оновлюємо сторінку (без очищення поля введення)
    st.rerun()


def export_chat_history():
    """Експортує історію чату."""
    if not st.session_state.messages:
        st.warning("📭 Немає повідомлень для експорту")
        return
    
    # Форматуємо історію
    export_data = {
        "user_id": st.session_state.user_id,
        "timestamp": datetime.now().isoformat(),
        "messages": st.session_state.messages
    }
    
    # Створюємо файл для завантаження
    json_str = json.dumps(export_data, ensure_ascii=False, indent=2, default=str)
    
    st.download_button(
        label="📥 Завантажити історію чату",
        data=json_str,
        file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )


def show_tips():
    """Показує підказки для користувача."""
    tips = [
        "💡 Спробуйте запити як: 'Створи нову категорію'",
        "💡 Для отримання даних: 'Покажи всі товари'",
        "💡 Для оновлення: 'Онови товар з ID 1'",
        "💡 Для видалення: 'Видали категорію 2'",
        "💡 Якщо потрібна додаткова інформація - бот запитає її",
        "💡 Бот пам'ятає контекст попередніх запитів",
        "💡 Використовуйте природну мову - бот зрозуміє"
    ]
    
    st.info("💡 **Корисні підказки:**")
    for tip in tips:
        st.write(tip)


if __name__ == "__main__":
    main()
