# 🔐 БЕЗПЕЧНЕ НАЛАШТУВАННЯ API КЛЮЧА

## ⚠️ **ВАЖЛИВО: Безпека API ключа**

API ключ OpenAI **НЕ ПОВИНЕН** з'являтися в коді або публічних файлах!

## 🛡️ **Правильні способи налаштування:**

### 1. **Змінні середовища (Рекомендовано):**
```bash
# Встановлення для поточної сесії
export OPENAI_API_KEY=your_api_key_here

# Або додати до ~/.zshrc або ~/.bash_profile для постійності
echo 'export OPENAI_API_KEY=your_api_key_here' >> ~/.zshrc
source ~/.zshrc
```

### 2. **Файл .env (для розробки):**
```bash
# Створіть файл .env в корені проекту
echo "OPENAI_API_KEY=your_api_key_here" > .env

# Додайте .env до .gitignore
echo ".env" >> .gitignore
```

### 3. **Перевірка наявності ключа:**
```bash
# Перевірте чи ключ встановлений
echo $OPENAI_API_KEY

# Або в Python
python -c "import os; print('API ключ встановлений' if os.getenv('OPENAI_API_KEY') else 'API ключ не знайдено')"
```

## 🚫 **ЩО НЕ РОБИТИ:**

### ❌ **Неправильно:**
```python
# НЕ додавайте ключ прямо в код
api_key = "sk-..."  # ❌ НЕ РОБІТЬ ЦЕ!

# НЕ комітьте .env файл
git add .env  # ❌ НЕ РОБІТЬ ЦЕ!
```

### ✅ **Правильно:**
```python
# Використовуйте змінні середовища
import os
api_key = os.getenv('OPENAI_API_KEY')  # ✅ Правильно
```

## 🔧 **Налаштування для проекту:**

### 1. **Створіть .env файл:**
```bash
cat > .env << EOF
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
LOG_LEVEL=INFO
REQUEST_TIMEOUT=30
EOF
```

### 2. **Додайте до .gitignore:**
```bash
echo ".env" >> .gitignore
echo "*.key" >> .gitignore
echo "secrets/" >> .gitignore
```

### 3. **Перевірте .gitignore:**
```bash
cat .gitignore
```

## 🚀 **Запуск з правильним середовищем:**

### **Для розробки:**
```bash
# Активуйте conda середовище
source $HOME/miniconda3/etc/profile.d/conda.sh
conda activate ai-swagger

# Встановіть API ключ
export OPENAI_API_KEY=your_api_key_here

# Запустіть Streamlit
streamlit run app.py --server.port 8501
```

### **Для продакшн:**
```bash
# Використовуйте змінні середовища сервера
# НЕ хардкодьте ключі в коді!
```

## 🔍 **Перевірка безпеки:**

### **Пошук хардкодних ключів:**
```bash
# Знайдіть всі файли з можливими API ключами
grep -r "sk-" . --exclude-dir=.git --exclude-dir=__pycache__

# Перевірте .env файл
ls -la .env
```

### **Перевірка .gitignore:**
```bash
# Переконайтеся що .env в .gitignore
grep ".env" .gitignore
```

## 📋 **Чек-лист безпеки:**

- [ ] API ключ НЕ в коді
- [ ] .env файл в .gitignore
- [ ] Використовуються змінні середовища
- [ ] Немає комітів з секретами
- [ ] Перевірено всі файли на наявність ключів

## 🎯 **Результат:**
- ✅ API ключ безпечно зберігається
- ✅ Код можна публікувати без ризику
- ✅ Секрети не потраплять в репозиторій
- ✅ Проект готовий до продакшн

## 💡 **Додаткові поради:**

1. **Регулярно ротуйте API ключі**
2. **Використовуйте різні ключі для розробки та продакшн**
3. **Моніторте використання API ключів**
4. **Налаштуйте сповіщення про підозрілу активність**

## 🚨 **У разі компрометації:**
1. Немедленно деактивуйте ключ в OpenAI
2. Створіть новий ключ
3. Оновіть всі середовища
4. Перевірте логи на підозрілу активність
