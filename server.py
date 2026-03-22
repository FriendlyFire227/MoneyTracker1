# server.py
# Разработчик А: Улучшенный сервер с API

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import os
from database import Database

# Подключаем базу данных
db = Database()

class FinanceHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Обработка GET запросов"""
        
        # Статические файлы
        if self.path == "/" or self.path == "/index.html":
            self.serve_static_file("static/index.html", "text/html")
        elif self.path == "/style.css":
            self.serve_static_file("static/style.css", "text/css")
        elif self.path == "/script.js":
            self.serve_static_file("static/script.js", "application/javascript")
        elif self.path == "/charts.js":
            self.serve_static_file("static/charts.js", "application/javascript")
        
        # API: получить все транзакции
        elif self.path == "/api/transactions":
            self.send_json(db.get_all_transactions())
        
        # API: получить баланс
        elif self.path == "/api/balance":
            self.send_json({"balance": db.get_balance()})
        
        # API: получить статистику
        elif self.path.startswith("/api/statistics"):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            period = params.get('period', ['all'])[0]
            self.send_json(db.get_statistics(period))
        
        # API: получить категории
        elif self.path == "/api/categories":
            self.send_json(db.get_categories())
        
        else:
            self.send_error(404, "Файл не найден")
    
    def do_POST(self):
        """Обработка POST запросов"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode()
        
        # Добавление транзакции
        if self.path == "/api/add":
            params = urllib.parse.parse_qs(post_data)
            trans_type = params.get('type', [''])[0]
            amount = float(params.get('amount', ['0'])[0])
            category = params.get('category', [''])[0]
            description = params.get('description', [''])[0]
            
            db.add_transaction(trans_type, amount, category, description)
            
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
        
        # Обновление транзакции
        elif self.path.startswith("/api/update/"):
            trans_id = int(self.path.split('/')[-1])
            params = urllib.parse.parse_qs(post_data)
            
            trans_type = params.get('type', [''])[0]
            amount = float(params.get('amount', ['0'])[0])
            category = params.get('category', [''])[0]
            description = params.get('description', [''])[0]
            
            db.update_transaction(trans_id, trans_type, amount, category, description)
            
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
        
        # Удаление транзакции
        elif self.path.startswith("/api/delete/"):
            trans_id = int(self.path.split('/')[-1])
            db.delete_transaction(trans_id)
            
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
        
        else:
            self.send_error(404)
    
    def send_json(self, data):
        """Отправляет JSON ответ"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def serve_static_file(self, filepath, content_type):
        """Отдает статические файлы"""
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, f"Файл {filepath} не найден")

def run_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, FinanceHandler)
    print("=" * 50)
    print("🚀 MoneyTracker Pro запущен!")
    print("=" * 50)
    print("📍 Откройте в браузере: http://localhost:8080")
    print("📊 База данных: SQLite")
    print("=" * 50)
    print("Нажмите Ctrl+C для остановки")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()