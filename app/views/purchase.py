from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import sqlite3

purchase_blueprint = Blueprint('purchase', __name__)

# 資料庫連線函數
def get_db_connection():
    conn = sqlite3.connect('management_system.db')
    conn.row_factory = sqlite3.Row  # 讓結果以字典形式返回
    return conn

# 進貨表單頁面
@purchase_blueprint.route('/purchases', methods=['GET', 'POST'])
def purchase():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        supplier_id = request.form.get('supplier_id')
        cost = request.form.get('cost')
        product_id = request.form.get('product_id')
        sn_codes = request.form.getlist('sn_codes[]')  # 獲取所有 SN Code

        if not sn_codes:
            flash("請輸入至少一個 SN Code", "danger")
            return redirect(url_for('purchase.purchase'))

        # 處理每個 SN Code
        for sn_code in sn_codes:
            purchase_order_number = generate_purchase_order_number(cursor)
            cursor.execute('''
                INSERT INTO purchases (purchase_order_number, sn_code, product_name, cost, supplier_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (purchase_order_number, sn_code, product_id, cost, supplier_id))

        conn.commit()
        conn.close()
        flash("進貨資料已成功添加", "success")
        return redirect(url_for('purchase.purchase'))

    # 從資料庫中獲取產品列表
    cursor.execute("SELECT id, name FROM products")
    products = cursor.fetchall()

    # 從資料庫中獲取供應商列表
    cursor.execute("SELECT id, name FROM suppliers")
    suppliers = cursor.fetchall()

    conn.close()

    # 傳遞產品和供應商數據到模板
    return render_template('purchase.html', products=products, suppliers=suppliers)

# 取得產品屬性 API
@purchase_blueprint.route('/get_attributes/<int:product_id>', methods=['GET'])
def get_attributes(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 查詢指定產品的屬性
    cursor.execute("SELECT name, data_type FROM attributes WHERE product_id = ?", (product_id,))
    attributes = cursor.fetchall()
    conn.close()

    # 返回 JSON 格式的屬性列表
    return jsonify([{"name": attr["name"], "data_type": attr["data_type"]} for attr in attributes])

# 生成唯一進貨單號
def generate_purchase_order_number(cursor):
    from datetime import datetime
    date_str = datetime.now().strftime("%Y%m%d")
    cursor.execute("SELECT COUNT(*) FROM purchases WHERE purchase_order_number LIKE ?", (f"PO-{date_str}-%",))
    count = cursor.fetchone()[0] + 1
    return f"PO-{date_str}-{count:04d}"
