import sqlite3
import os

def init_db():
    # 檢查資料庫文件是否存在，如果不存在則創建
    if not os.path.exists('management_system.db'):
        conn = sqlite3.connect('management_system.db')
        cursor = conn.cursor()

        # 建立 suppliers 表
        cursor.execute('''CREATE TABLE IF NOT EXISTS suppliers (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            phone TEXT,
                            address TEXT,
                            email TEXT,
                            notes TEXT
                          )''')

        # 建立 customers 表
        cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            phone TEXT,
                            address TEXT,
                            email TEXT,
                            notes TEXT
                          )''')

        # 建立 users 表
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL UNIQUE,
                            password TEXT NOT NULL,
                            role TEXT NOT NULL,  -- 'admin' 或 'user'
                            permissions TEXT
                          )''')

        # 建立 features 表
        cursor.execute('''CREATE TABLE IF NOT EXISTS features (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL UNIQUE
                          )''')

        # 插入預設管理員賬戶
        cursor.execute('SELECT * FROM users WHERE username = "admin"')
        if cursor.fetchone() is None:
            cursor.execute('INSERT INTO users (username, password, role, permissions) VALUES (?, ?, ?, ?)',
                           ('admin', 'password', 'admin', 'all'))

        # 提交並關閉連接
        conn.commit()
        conn.close()
        print("Database initialized successfully.")