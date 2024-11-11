from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3

app = Flask(__name__)

# 初始化資料庫
def init_db():
    conn = sqlite3.connect('management_system.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS suppliers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        phone TEXT,
                        address TEXT,
                        email TEXT,
                        notes TEXT
                      )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        phone TEXT,
                        address TEXT,
                        email TEXT,
                        notes TEXT
                      )''')
    conn.commit()
    conn.close()

init_db()
# 主畫面
@app.route('/')
def index():
    return render_template('index.html')

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
    app.run(debug=True)
