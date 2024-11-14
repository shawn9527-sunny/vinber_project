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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sn_code TEXT NOT NULL,                 -- 唯一的序號
            purchase_order_number TEXT NOT NULL,   -- 進貨單號
            product_name TEXT NOT NULL,            -- 當時的產品名稱快照
            cost REAL NOT NULL,                    -- 進貨成本
            supplier_id INTEGER,                   -- 供應商 ID
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchase_attributes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            purchase_id INTEGER NOT NULL,          -- 關聯到 purchases 表
            attribute_name TEXT NOT NULL,          -- 屬性名稱（當時的快照）
            attribute_value TEXT,                  -- 屬性值
            FOREIGN KEY (purchase_id) REFERENCES purchases(id) ON DELETE CASCADE
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