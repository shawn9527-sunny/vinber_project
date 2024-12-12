import sqlite3
import os

def init_db():
    conn = sqlite3.connect('management_system.db')
    cursor = conn.cursor()

    # 用戶表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,  -- 'admin' 或 'user'
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_login TEXT
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
            purchase_date TEXT,  -- 使用 TEXT 類型存儲日期時間
            FOREIGN KEY (supplier_id) REFERENCES suppliers(taxid),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );
    ''')

    # 檢查是否已存在 purchase_date 欄位
    cursor.execute("PRAGMA table_info(purchases)")
    columns = cursor.fetchall()
    if not any(column[1] == 'purchase_date' for column in columns):
        # 如果不存在，則添加欄位
        cursor.execute('''
            ALTER TABLE purchases ADD COLUMN purchase_date TEXT;
        ''')
        # 更新現有記錄的 purchase_date
        cursor.execute('''
            UPDATE purchases SET purchase_date = CURRENT_TIMESTAMP
            WHERE purchase_date IS NULL;
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


    # 用戶表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,  -- 'admin' 或 'user'
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_login TEXT
        )
    ''')

    # 檢查是否已存在管理員帳戶
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        # 創建默認管理員帳戶 (密碼需要在首次登入時修改)
        cursor.execute('''
            INSERT INTO users (username, password, role)
            VALUES ('admin', 'admin', 'admin')
        ''')

    # 提交並關閉連接
    conn.commit()
    conn.close()
    print("Database initialized successfully.")