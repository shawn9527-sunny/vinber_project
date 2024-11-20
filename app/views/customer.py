from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3

customer_blueprint = Blueprint('customer', __name__, template_folder='templates')

def get_db_connection():
    conn = sqlite3.connect('management_system.db')
    conn.row_factory = sqlite3.Row
    return conn

# 客戶管理頁面
@customer_blueprint.route('/customers', strict_slashes=False)
def customers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()
    conn.close()
    return render_template('customers.html', customers=customers)

# 新增客戶
@customer_blueprint.route('/add_customer', methods=['POST'])
def add_customer():
    taxid = request.form['id']
    name = request.form['name']
    phone = request.form['phone']
    address = request.form['address']
    email = request.form['email']

    if not name:
        flash("客戶名稱為必填！", "danger")
        return redirect(url_for('customer.customers'))

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 驗證 taxID 是否唯一
    cursor.execute("SELECT 1 FROM customers WHERE id = ?", (taxid,))
    if cursor.fetchone():
        conn.close()
        flash("公司統編 重複，請輸入唯一的公司統編！", "danger")
        return redirect(url_for('supplier.suppliers'))
    
    cursor.execute("INSERT INTO customers (id, name, phone, address, email) VALUES (?, ?, ?, ?, ?)", 
                   (taxid, name, phone, address, email))
    conn.commit()
    conn.close()
    flash("新增客戶成功！", "success")
    return redirect(url_for('customer.customers'))

# 刪除客戶
@customer_blueprint.route('/delete_customers', methods=['POST'])
def delete_customers():
    ids = request.form.getlist('customer_ids')
    if not ids:
        flash("請選擇要刪除的客戶！", "danger")
        return redirect(url_for('customer.customers'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.executemany("DELETE FROM customers WHERE id = ?", [(id,) for id in ids])
    conn.commit()
    conn.close()
    flash("刪除客戶成功！", "success")
    return redirect(url_for('customer.customers'))

# 客戶詳細資料頁面
@customer_blueprint.route('/customer/<int:customer_id>')
def customer_detail(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
    customer = cursor.fetchone()
    conn.close()

    if not customer:
        flash("客戶不存在！", "danger")
        return redirect(url_for('customer.customers'))

    return render_template('customer_detail.html', customer=customer)

# 更新客戶資料
@customer_blueprint.route('/update_customer/<int:customer_id>', methods=['POST'])
def update_customer(customer_id):
    name = request.form['name']
    phone = request.form['phone']
    address = request.form['address']
    email = request.form['email']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE customers SET name = ?, phone = ?, address = ?, email = ? WHERE id = ?", 
        (name, phone, address, email, customer_id)
    )
    conn.commit()
    conn.close()
    flash("更新客戶資料成功！", "success")
    return redirect(url_for('customer.customers'))
