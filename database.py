# database.py
# Разработчик А: Все запросы к базе данных

import sqlite3
from datetime import datetime, timedelta

class Database:
    def __init__(self, db_name='finance.db'):
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_db(self):
        """Проверяет, существует ли БД"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def add_transaction(self, trans_type, amount, category, description):
        """Добавляет транзакцию"""
        conn = self.get_connection()
        cursor = conn.cursor()
        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        cursor.execute('''
            INSERT INTO transactions (date, type, amount, category, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (date, trans_type, amount, category, description))
        
        conn.commit()
        transaction_id = cursor.lastrowid
        conn.close()
        return transaction_id
    
    def get_all_transactions(self):
        """Возвращает все транзакции"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM transactions ORDER BY date DESC')
        rows = cursor.fetchall()
        conn.close()
        
        transactions = []
        for row in rows:
            transactions.append({
                'id': row[0],
                'date': row[1],
                'type': row[2],
                'amount': row[3],
                'category': row[4],
                'description': row[5]
            })
        return transactions
    
    def delete_transaction(self, trans_id):
        """Удаляет транзакцию"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM transactions WHERE id = ?', (trans_id,))
        conn.commit()
        conn.close()
    
    def update_transaction(self, trans_id, trans_type, amount, category, description):
        """Обновляет транзакцию"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE transactions 
            SET type=?, amount=?, category=?, description=?
            WHERE id=?
        ''', (trans_type, amount, category, description, trans_id))
        conn.commit()
        conn.close()
    
    def get_balance(self):
        """Возвращает текущий баланс"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT SUM(amount) FROM transactions WHERE type="income"')
        income = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT SUM(amount) FROM transactions WHERE type="expense"')
        expense = cursor.fetchone()[0] or 0
        
        conn.close()
        return income - expense
    
    def get_statistics(self, period='all'):
        """Возвращает статистику за период"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Определяем дату начала периода
        if period == 'today':
            start_date = datetime.now().strftime("%Y-%m-%d")
            condition = f"WHERE date LIKE '{start_date}%'"
        elif period == 'week':
            week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            condition = f"WHERE date >= '{week_ago}'"
        elif period == 'month':
            month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            condition = f"WHERE date >= '{month_ago}'"
        else:
            condition = ""
        
        # Статистика по категориям расходов
        cursor.execute(f'''
            SELECT category, SUM(amount) as total 
            FROM transactions 
            WHERE type="expense" {condition.replace('WHERE', 'AND') if condition else ''}
            GROUP BY category 
            ORDER BY total DESC
        ''')
        expense_by_category = cursor.fetchall()
        
        # Статистика по категориям доходов
        cursor.execute(f'''
            SELECT category, SUM(amount) as total 
            FROM transactions 
            WHERE type="income" {condition.replace('WHERE', 'AND') if condition else ''}
            GROUP BY category 
            ORDER BY total DESC
        ''')
        income_by_category = cursor.fetchall()
        
        conn.close()
        
        return {
            'expense_by_category': expense_by_category,
            'income_by_category': income_by_category
        }
    
    def get_categories(self):
        """Возвращает все доступные категории"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT name, icon, type FROM categories ORDER BY type, name')
        rows = cursor.fetchall()
        conn.close()
        
        categories = {'income': [], 'expense': []}
        for row in rows:
            categories[row[2]].append({'name': row[0], 'icon': row[1]})
        
        return categories