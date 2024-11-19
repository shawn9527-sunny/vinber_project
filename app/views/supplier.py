from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3

supplier_blueprint = Blueprint('supplier', __name__, template_folder='templates')

# 資料庫連線函數
def get_db_connection():
    conn = sqlite3.connect('management_system.db')
    conn.row_factory = sqlite3.Row  # 讓結果以字典形式返回
    return conn

# 供應商列表頁面
@supplier_blueprint.route('/suppliers', strict_slashes=False)
def suppliers():
    conn = get_db_connection()
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
    taxID = request.form['taxID']  # 新增 taxID 字段

    # 驗證字段是否完整
    if not all([name, phone, address, email, taxID]):
        flash("所有字段均為必填，請確認輸入！", "danger")
        return redirect(url_for('supplier.suppliers'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # 驗證 taxID 是否唯一
    cursor.execute("SELECT 1 FROM suppliers WHERE taxID = ?", (taxID,))
    if cursor.fetchone():
        print("123")
        conn.close()
        flash("TaxID 重複，請輸入唯一的公司統編！", "danger")
        return redirect(url_for('supplier.suppliers'))

    try:
        cursor.execute(
            "INSERT INTO suppliers (name, phone, address, email, notes, taxID) VALUES (?, ?, ?, ?, ?, ?)", 
            (name, phone, address, email, notes, taxID)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        flash("TaxID 必須唯一，請確認輸入的 TaxID 沒有重複！", "danger")
        return redirect(url_for('supplier.suppliers'))

    conn.close()
    flash("供應商新增成功！", "success")
    return redirect(url_for('supplier.suppliers'))

# 刪除供應商
@supplier_blueprint.route('/delete_suppliers', methods=['POST'])
def delete_suppliers():
    tax_ids = request.form.getlist('supplier_ids')  # 用 taxID 替代 id
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.executemany("DELETE FROM suppliers WHERE taxID = ?", [(tax_id,) for tax_id in tax_ids])
    conn.commit()
    conn.close()
    flash("選取的供應商已成功刪除！", "success")
    return redirect(url_for('supplier.suppliers'))

# 供應商詳細資訊頁面
@supplier_blueprint.route('/supplier/<taxID>')
def supplier_detail(taxID):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM suppliers WHERE taxID = ?", (taxID,))
    supplier = cursor.fetchone()
    conn.close()

    if not supplier:
        flash("找不到該供應商！", "danger")
        return redirect(url_for('supplier.suppliers'))

    return render_template('supplier_detail.html', supplier=supplier)

# 更新供應商資訊
@supplier_blueprint.route('/update_supplier/<taxID>', methods=['POST'])
def update_supplier(taxID):
    name = request.form['name']
    phone = request.form['phone']
    address = request.form['address']
    email = request.form['email']
    notes = request.form['notes']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE suppliers SET name = ?, phone = ?, address = ?, email = ?, notes = ? WHERE taxID = ?", 
        (name, phone, address, email, notes, taxID)
    )
    conn.commit()
    conn.close()
    flash("供應商資訊已更新！", "success")
    return redirect(url_for('supplier.suppliers'))
