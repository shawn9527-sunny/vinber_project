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

                    # 插入屬性
                    for attr_id, attr_value in attributes.items():
                        cursor.execute('''
                            INSERT INTO purchase_attributes (purchase_id, attribute_name, attribute_value)
                            VALUES (?, ?, ?)
                        ''', (sn_code, attr_id, attr_value))
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


# # 取得產品屬性 API
# @purchase_blueprint.route('/get_attributes/<int:product_id>', methods=['GET'])
# def get_attributes(product_id):
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     # 查詢指定產品的屬性
#     cursor.execute("SELECT name, data_type FROM attributes WHERE product_id = ?", (product_id,))
#     attributes = cursor.fetchall()
#     conn.close()

#     # 返回 JSON 格式的屬性列表
#     return jsonify([{"name": attr["name"], "data_type": attr["data_type"]} for attr in attributes])
@purchase_blueprint.route('/get_attributes/<int:product_id>', methods=['GET'])
def get_attributes(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 查詢指定產品的屬性，確保返回 ID 和名稱
    cursor.execute("SELECT id, name, data_type FROM attributes WHERE product_id = ?", (product_id,))
    attributes = cursor.fetchall()
    conn.close()

    # 返回 JSON 格式的屬性列表
    return jsonify([{"id": attr["id"], "name": attr["name"], "data_type": attr["data_type"]} for attr in attributes])


# 生成進貨單流水號
def generate_purchase_order_number(cursor):
    from datetime import datetime
    date_str = datetime.now().strftime("%Y%m%d")
    cursor.execute("SELECT COUNT(*) FROM purchases WHERE purchase_order_number LIKE ?", (f"PO-{date_str}-%",))
    count = cursor.fetchone()[0] + 1
    return f"PO-{date_str}-{count:04d}"

# 批量删除進貨單
@purchase_blueprint.route('/delete_purchases', methods=['POST'])
def delete_purchases():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 获取提交的进货单号列表
        purchase_order_numbers = request.form.getlist('purchase_order_numbers')

        if not purchase_order_numbers:
            flash("未選擇進貨單進行刪除！", "danger")
            return redirect(url_for('purchase.purchase'))

        # 删除相关进货单及其属性记录
        cursor.executemany("DELETE FROM purchases WHERE purchase_order_number = ?", [(number,) for number in purchase_order_numbers])
        cursor.executemany("DELETE FROM purchase_attributes WHERE purchase_id IN (SELECT id FROM purchases WHERE purchase_order_number = ?)",
                           [(number,) for number in purchase_order_numbers])

        conn.commit()
        flash(f"成功刪除 {len(purchase_order_numbers)} 筆進貨單！", "success")
    except Exception as e:
        conn.rollback()
        flash(f"刪除失敗: {str(e)}", "danger")
    finally:
        conn.close()

    return redirect(url_for('purchase.purchase'))

# 進貨單詳細頁
@purchase_blueprint.route('/purchase_detail/<string:purchase_order_number>', methods=['GET', 'POST'])
def purchase_detail(purchase_order_number):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        try:
            updates = request.get_json()
            print(updates)
            updated_products = updates.get('updated_products', [])

            if not updated_products:
                return jsonify(success=False, message="未收到更新的產品數據")

            for product in updated_products:
                sn_codes = product.get('sn_codes', [])
                attributes = product.get('attributes', {})

                for sn in sn_codes:
                    sn_code = sn.get('sn_code')
                    cost = sn.get('cost')

                    if not sn_code or cost is None:
                        continue  # 跳過無效的數據

                    # 更新產品單價
                    cursor.execute(
                        "UPDATE purchases SET cost = ? WHERE id = ?",
                        (cost, sn_code)
                    )

                    # 更新屬性
                    if sn_code in attributes:
                        for attr_name, attr_value in attributes[sn_code].items():
                            cursor.execute('''
                                INSERT INTO purchase_attributes (purchase_id, attribute_name, attribute_value)
                                VALUES (?, ?, ?)
                                ON CONFLICT(purchase_id, attribute_name) DO UPDATE SET attribute_value = excluded.attribute_value
                            ''', (sn_code, attr_name, attr_value))

            conn.commit()
            return jsonify(success=True, message="進貨單更新成功！")

        except Exception as e:
            conn.rollback()
            return jsonify(success=False, message=f"更新失敗: {str(e)}")



    # 查詢進貨單的產品數據
    cursor.execute('''
        SELECT p.id AS sn_code, p.product_id, pr.name AS product_name, p.cost,
               s.name AS supplier_name, p.purchase_order_number
        FROM purchases p
        JOIN products pr ON p.product_id = pr.id
        JOIN suppliers s ON p.supplier_id = s.taxid
        WHERE p.purchase_order_number = ?
        ORDER BY p.product_id
    ''', (purchase_order_number,))
    purchases = cursor.fetchall()

    # 分組產品數據
    grouped_products = {}
    for row in purchases:
        product_id = row['product_id']
        if product_id not in grouped_products:
            grouped_products[product_id] = {
                'product_name': row['product_name'],
                'sn_codes': []
            }
        grouped_products[product_id]['sn_codes'].append({
            'sn_code': row['sn_code'],
            'cost': row['cost']
        })

    # # 查詢屬性並添加到分組數據
    # for product_id, data in grouped_products.items():
    #     for sn in data['sn_codes']:
    #         cursor.execute('''
    #             SELECT attribute_name, attribute_value
    #             FROM purchase_attributes
    #             WHERE purchase_id = ?
    #         ''', (sn['sn_code'],))
    #         sn['attributes'] = {row['attribute_name']: row['attribute_value'] for row in cursor.fetchall()}
    # 查詢屬性並添加到分組數據
    for product_id, data in grouped_products.items():
        for sn in data['sn_codes']:
            cursor.execute('''
                SELECT a.name AS attribute_name, pa.attribute_value
                FROM purchase_attributes pa
                JOIN attributes a ON pa.attribute_name = a.id
                WHERE pa.purchase_id = ?
            ''', (sn['sn_code'],))
            sn['attributes'] = {row['attribute_name']: row['attribute_value'] for row in cursor.fetchall()}
    conn.close()
    return render_template('purchase_detail.html', grouped_products=grouped_products, purchase_order_number=purchase_order_number)


