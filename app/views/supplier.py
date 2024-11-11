from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3

supplier_blueprint = Blueprint('supplier', __name__, template_folder='templates')

# 供應商列表頁面
@supplier_blueprint.route('/suppliers', strict_slashes=False)
def suppliers():
    conn = sqlite3.connect('management_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM suppliers")
    suppliers = cursor.fetchall()
    conn.close()
    return render_template('suppliers.html', suppliers=suppliers)

# 新增供應商
@supplier_blueprint.route('/add_supplier', methods=['POST'])
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
    return redirect(url_for('supplier.suppliers'))

# 刪除供應商
@supplier_blueprint.route('/delete_suppliers', methods=['POST'])
def delete_suppliers():
    ids = request.form.getlist('supplier_ids')
    conn = sqlite3.connect('management_system.db')
    cursor = conn.cursor()
    cursor.executemany("DELETE FROM suppliers WHERE id = ?", [(id,) for id in ids])
    conn.commit()
    conn.close()
    return redirect(url_for('supplier.suppliers'))

# 供應商詳細資訊頁面
@supplier_blueprint.route('/supplier/<int:supplier_id>')
def supplier_detail(supplier_id):
    conn = sqlite3.connect('management_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
    supplier = cursor.fetchone()
    conn.close()
    return render_template('supplier_detail.html', supplier=supplier)

# 更新供應商資訊
@supplier_blueprint.route('/update_supplier/<int:supplier_id>', methods=['POST'])
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
    return redirect(url_for('supplier.suppliers'))