# init_db.py
# Разработчик А: Создание структуры базы данных
# Запустить ОДИН РАЗ: python init_db.py

import sqlite3

conn = sqlite3.connect('finance.db')
cursor = conn.cursor()

# Создаем таблицу для транзакций
cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    type TEXT NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Создаем таблицу для категорий
cursor.execute('''
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    icon TEXT DEFAULT '📦',
    type TEXT NOT NULL
)
''')

# Добавляем стандартные категории
categories = [
    ('Зарплата', '💰', 'income'),
    ('Фриланс', '💻', 'income'),
    ('Подарки', '🎁', 'income'),
    ('Инвестиции', '📈', 'income'),
    ('Еда', '🍔', 'expense'),
    ('Транспорт', '🚗', 'expense'),
    ('Развлечения', '🎮', 'expense'),
    ('Коммуналка', '🏠', 'expense'),
    ('Здоровье', '🏥', 'expense'),
    ('Одежда', '👕', 'expense'),
    ('Связь', '📱', 'expense'),
    ('Образование', '📚', 'expense')
]

for category in categories:
    try:
        cursor.execute('INSERT INTO categories (name, icon, type) VALUES (?, ?, ?)', category)
    except:
        pass  # Категория уже существует

conn.commit()
conn.close()
print("✅ База данных создана!")