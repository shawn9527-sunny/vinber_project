from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3

customer_blueprint = Blueprint('customer', __name__, template_folder='templates')

# 客戶管理頁面
@customer_blueprint .route('/customers')
def customers():
    conn = sqlite3.connect('management_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()
    conn.close()
    return render_template('customers.html', customers=customers)

# 新增客戶
@customer_blueprint .route('/add_customer', methods=['POST'])
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
@customer_blueprint .route('/delete_customers', methods=['POST'])
def delete_customers():
    ids = request.form.getlist('customer_ids')
    conn = sqlite3.connect('management_system.db')
    cursor = conn.cursor()
    cursor.executemany("DELETE FROM customers WHERE id = ?", [(id,) for id in ids])
    conn.commit()
    conn.close()
    return redirect(url_for('customers'))

# 客戶詳細資料頁面
@customer_blueprint .route('/customer/<int:customer_id>')
def customer_detail(customer_id):
    conn = sqlite3.connect('management_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
    customer = cursor.fetchone()
    conn.close()
    return render_template('customer_detail.html', customer=customer)

# 更新客戶資料
@customer_blueprint .route('/update_customer/<int:customer_id>', methods=['POST'])
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