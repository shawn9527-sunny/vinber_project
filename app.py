from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3

app = Flask(__name__)

# 初始化資料庫
def init_db():
    conn = sqlite3.connect('management_system.db')
    cursor = conn.cursor()
    #供應商
    cursor.execute('''CREATE TABLE IF NOT EXISTS suppliers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        phone TEXT,
                        address TEXT,
                        email TEXT,
                        notes TEXT
                      )''')
    #客戶
    cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        phone TEXT,
                        address TEXT,
                        email TEXT,
                        notes TEXT
                      )''')
    #使用者
    # 用戶表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL,  -- 'admin' 或 'user'
            permissions TEXT  -- 存儲用戶可以訪問的功能，以逗號分隔
        )
    ''')

    # 功能表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    # 預設管理者帳號
    cursor.execute('SELECT * FROM users WHERE username = "admin"')
    if cursor.fetchone() is None:
        cursor.execute('INSERT INTO users (username, password, role, permissions) VALUES (?, ?, ?, ?)',
                       ('admin', 'password', 'admin', 'all'))
    
    conn.commit()
    conn.close()

init_db()

# 主畫面
@app.route('/')
def index():
    return render_template('index.html')

# 主畫面（僅限授權功能訪問）
@app.route('/index')
@login_required()
def index():
    conn = sqlite3.connect('management_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT permissions FROM users WHERE id = ?", (session['user_id'],))
    permissions = cursor.fetchone()[0].split(',') if cursor.fetchone() else []
    conn.close()
    return render_template('index.html', permissions=permissions)
    
# ===============================使用者===============================
# 登入檢查裝飾器
def login_required(role=None):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("請先登入", "warning")
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                flash("無權限訪問此頁面", "danger")
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return wrapper

# 登入頁面（管理者）
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('management_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user and user[2] == 'admin':
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            if password == 'password':  # 預設密碼
                return redirect(url_for('change_password'))
            return redirect(url_for('admin_dashboard'))
        else:
            flash("登入失敗，請檢查帳號和密碼", "danger")
    return render_template('admin_login.html')

# 登入頁面（一般使用者）
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('management_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user and user[3] == 'user':
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            if password == 'password':  # 預設密碼
                return redirect(url_for('change_password'))
            return redirect(url_for('index'))
        else:
            flash("登入失敗，請檢查帳號和密碼", "danger")
    return render_template('login.html')

# 強制更改密碼
@app.route('/change_password', methods=['GET', 'POST'])
@login_required()
def change_password():
    if request.method == 'POST':
        new_password = request.form['new_password']
        conn = sqlite3.connect('management_system.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, session['user_id']))
        conn.commit()
        conn.close()
        flash("密碼已更新", "success")
        if session['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('index'))
    return render_template('change_password.html')

# 管理者主控台
@app.route('/admin_dashboard')
@login_required(role='admin')
def admin_dashboard():
    conn = sqlite3.connect('management_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE role = 'user'")
    users = cursor.fetchall()
    conn.close()
    return render_template('admin_dashboard.html', users=users)

# 新增使用者
@app.route('/add_user', methods=['POST'])
@login_required(role='admin')
def add_user():
    username = request.form['username']
    password = 'password'  # 預設密碼
    permissions = ','.join(request.form.getlist('permissions'))
    
    conn = sqlite3.connect('management_system.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, role, permissions) VALUES (?, ?, ?, ?)",
                   (username, password, 'user', permissions))
    conn.commit()
    conn.close()
    flash("已新增使用者", "success")
    return redirect(url_for('admin_dashboard'))
# ===============================使用者===============================

# ===============================供應商===============================
# 供應商列表頁面
@app.route('/suppliers')
def suppliers():
    conn = sqlite3.connect('management_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM suppliers")
    suppliers = cursor.fetchall()
    conn.close()
    return render_template('suppliers.html', suppliers=suppliers)

# 新增供應商
@app.route('/add_supplier', methods=['POST'])
def add_supplier():
    name = request.form['name']
    phone = request.form['phone']
    address = request.form['address']
    email = request.form['email']
    notes = request.form['notes']

    conn = sqlite3.connect('management_system.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO suppliers (name, phone, address, email, notes) VALUES (?, ?, ?, ?, ?)", 
                   (name, phone, address, email, notes))
    conn.commit()
    conn.close()
    return redirect(url_for('suppliers'))

# 刪除供應商
@app.route('/delete_suppliers', methods=['POST'])
def delete_suppliers():
    ids = request.form.getlist('supplier_ids')
    conn = sqlite3.connect('management_system.db')
    cursor = conn.cursor()
    cursor.executemany("DELETE FROM suppliers WHERE id = ?", [(id,) for id in ids])
    conn.commit()
    conn.close()
    return redirect(url_for('suppliers'))

# 供應商詳細資訊頁面
@app.route('/supplier/<int:supplier_id>')
def supplier_detail(supplier_id):
    conn = sqlite3.connect('management_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
    supplier = cursor.fetchone()
    conn.close()
    return render_template('supplier_detail.html', supplier=supplier)

# 更新供應商資訊
@app.route('/update_supplier/<int:supplier_id>', methods=['POST'])
def update_supplier(supplier_id):
    name = request.form['name']
    phone = request.form['phone']
    address = request.form['address']
    email = request.form['email']
    notes = request.form['notes']

    conn = sqlite3.connect('management_system.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE suppliers SET name = ?, phone = ?, address = ?, email = ?, notes = ? WHERE id = ?", 
                   (name, phone, address, email, notes, supplier_id))
    conn.commit()
    conn.close()
    return redirect(url_for('suppliers'))
# ===============================供應商===============================
# ===============================客戶===============================
# 客戶管理頁面
@app.route('/customers')
def customers():
    conn = sqlite3.connect('management_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()
    conn.close()
    return render_template('customers.html', customers=customers)

# 新增客戶
@app.route('/add_customer', methods=['POST'])
def add_customer():
    name = request.form['name']
    phone = request.form['phone']
    address = request.form['address']
    email = request.form['email']
    
    conn = sqlite3.connect('management_system.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO customers (name, phone, address, email) VALUES (?, ?, ?, ?)", 
                   (name, phone, address, email))
    conn.commit()
    conn.close()
    return redirect(url_for('customers'))

# 刪除客戶
@app.route('/delete_customers', methods=['POST'])
def delete_customers():
    ids = request.form.getlist('customer_ids')
    conn = sqlite3.connect('management_system.db')
    cursor = conn.cursor()
    cursor.executemany("DELETE FROM customers WHERE id = ?", [(id,) for id in ids])
    conn.commit()
    conn.close()
    return redirect(url_for('customers'))

# 客戶詳細資料頁面
@app.route('/customer/<int:customer_id>')
def customer_detail(customer_id):
    conn = sqlite3.connect('management_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
    customer = cursor.fetchone()
    conn.close()
    return render_template('customer_detail.html', customer=customer)

# 更新客戶資料
@app.route('/update_customer/<int:customer_id>', methods=['POST'])
def update_customer(customer_id):
    name = request.form['name']
    phone = request.form['phone']
    address = request.form['address']
    email = request.form['email']
    notes = request.form['notes']

    conn = sqlite3.connect('management_system.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE customers SET name = ?, phone = ?, address = ?, email = ?, notes = ? WHERE id = ?", 
                   (name, phone, address, email, notes, customer_id))
    conn.commit()
    conn.close()
    return redirect(url_for('customers'))
# ===============================客戶===============================
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
