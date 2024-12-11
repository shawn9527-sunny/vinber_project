import sqlite3
import os

def init_db():
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
    # cursor.execute('''
    #     ALTER TABLE suppliers ADD COLUMN taxID TEXT UNIQUE NOT NULL;
    # ''')
    # 建立 customers 表
    cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        phone TEXT,
                        address TEXT,
                        email TEXT,
                        notes TEXT
                        )''')

    # 產品類別表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code_prefix TEXT NOT NULL  -- 自定義編號前綴，例如 "01" 代表蘋果
        )
    ''')

    # 屬性表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attributes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,  -- 關聯到對應的產品
            order_index INTEGER NOT NULL,
            name TEXT NOT NULL,  -- 屬性名稱，例如 "廠牌"、"型號"
            data_type TEXT NOT NULL,  -- 屬性資料類型（如 "TEXT" 或 "INTEGER"）
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        )
    ''')
    # cursor.execute('''
    #     ALTER TABLE attributes ADD COLUMN order_index INTEGER;
    # ''')
    
    # 進貨表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            id TEXT PRIMARY KEY,  -- SN Code，唯一值
            supplier_id TEXT NOT NULL,
            purchase_order_number TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            cost REAL NOT NULL,  -- 單價
            FOREIGN KEY (supplier_id) REFERENCES suppliers(taxid),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchase_attributes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            purchase_id TEXT NOT NULL,  -- 對應 purchases 表的 SN Code
            attribute_name INTEGER NOT NULL,  -- 存儲 attributes 表中的 ID
            attribute_value TEXT NOT NULL,
            FOREIGN KEY (purchase_id) REFERENCES purchases(id),
            FOREIGN KEY (attribute_name) REFERENCES attributes(id)
        );
    ''')

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