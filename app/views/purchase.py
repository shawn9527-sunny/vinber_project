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
        try:
            # 确保数据以 JSON 格式接收
            payload = request.get_json()
            supplier_id = payload.get('supplier_id')
            products = payload.get('products', [])

            if not supplier_id:
                return jsonify(success=False, message="供應商必須填寫！")

            if not products:
                return jsonify(success=False, message="請新增至少一項產品！")

            purchase_order_number = generate_purchase_order_number(cursor)

            for product_data in products:
                product_id = product_data.get('product_id')
                cost = product_data.get('cost')
                quantity = product_data.get('quantity')
                sn_codes = product_data.get('sn_codes', [])
                attributes = product_data.get('attributes', {})

                if not (product_id and cost and quantity and sn_codes):
                    return jsonify(success=False, message="所有產品字段必須完整！")

                # 插入每个 SN Code
                for sn_code in sn_codes:
                    cursor.execute('''
                        INSERT INTO purchases (id, supplier_id, purchase_order_number, product_id, cost)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (sn_code, supplier_id, purchase_order_number, product_id, cost))

                    # 插入属性
                    for attr_name, attr_value in attributes.items():
                        cursor.execute('''
                            INSERT INTO purchase_attributes (purchase_id, attribute_name, attribute_value)
                            VALUES (?, ?, ?)
                        ''', (sn_code, attr_name, attr_value))

            conn.commit()
            return jsonify(success=True, message="進貨資料已成功添加")

        except Exception as e:
            conn.rollback()
            return jsonify(success=False, message=f"提交失敗: {str(e)}")

    # 查询现有进货单
    cursor.execute('''
        SELECT p.purchase_order_number, 
               s.name AS supplier_name, 
               SUM(p.cost) AS total_cost
        FROM purchases p
        JOIN suppliers s ON p.supplier_id = s.taxid
        GROUP BY p.purchase_order_number, s.name
        ORDER BY p.purchase_order_number
    ''')
    purchases = cursor.fetchall()

    # 查询产品和供应商
    cursor.execute("SELECT id, name FROM products")
    products = cursor.fetchall()
    cursor.execute("SELECT taxid, name FROM suppliers")
    suppliers = cursor.fetchall()

    conn.close()
    return render_template('purchase.html', products=products, suppliers=suppliers, purchases=purchases)


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

# 生成進貨單流水號
def generate_purchase_order_number(cursor):
    from datetime import datetime
    date_str = datetime.now().strftime("%Y%m%d")
    cursor.execute("SELECT COUNT(*) FROM purchases WHERE purchase_order_number LIKE ?", (f"PO-{date_str}-%",))
    count = cursor.fetchone()[0] + 1
    return f"PO-{date_str}-{count:04d}"
