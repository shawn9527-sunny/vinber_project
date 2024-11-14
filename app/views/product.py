from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3,json

product_blueprint = Blueprint('product', __name__)

# 顯示所有產品
@product_blueprint.route('/products')
def products():
    conn = sqlite3.connect('management_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return render_template('products.html', products=products)

# 新增產品
@product_blueprint.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        code_prefix = request.form['code_prefix']
        conn = sqlite3.connect('management_system.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, code_prefix) VALUES (?, ?)", (name, code_prefix))
        conn.commit()
        conn.close()
        flash("產品已新增", "success")
        return redirect(url_for('product.products'))
    return render_template('product_add.html')

# 刪除產品
@product_blueprint.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    conn = sqlite3.connect('management_system.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    cursor.execute("DELETE FROM attributes WHERE product_id = ?", (product_id,))
    conn.commit()
    conn.close()
    flash("產品已刪除", "success")
    return redirect(url_for('product.products'))

# 編輯產品頁面
@product_blueprint.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    conn = sqlite3.connect('management_system.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        # 更新商品資料
        name = request.form['name']
        code_prefix = request.form['code_prefix']
        cursor.execute("UPDATE products SET name = ?, code_prefix = ? WHERE id = ?", (name, code_prefix, product_id))

        # 更新屬性
        attribute_ids = request.form.getlist('edit_attribute_ids')
        attribute_names = request.form.getlist('edit_attribute_names')
        attribute_types = request.form.getlist('edit_attribute_types')
        for i, attribute_id in enumerate(attribute_ids):
            attribute_name = attribute_names[i]
            data_type = attribute_types[i]
            cursor.execute("UPDATE attributes SET name = ?, data_type = ? WHERE id = ?", (attribute_name, data_type, attribute_id))

        # 更新屬性順序
        attribute_order = request.form.get('attribute_order')
        print(attribute_order)
        if attribute_order:
            ordered_ids = json.loads(attribute_order)  # 將 JSON 字符串轉換為 Python 列表
            for i, attribute_id in enumerate(ordered_ids):
                cursor.execute("UPDATE attributes SET order_index = ? WHERE id = ?", (i, attribute_id))


        # 新增新屬性
        new_attribute_names = request.form.getlist('new_attribute_names')
        new_attribute_types = request.form.getlist('new_attribute_types')
        for i, new_name in enumerate(new_attribute_names):
            new_data_type = new_attribute_types[i]
            cursor.execute("INSERT INTO attributes (product_id, name, data_type , order_index) VALUES (?, ?, ? ,?)", (product_id, new_name, new_data_type, i))

        # 刪除屬性
        delete_attribute_ids = request.form.getlist('delete_attribute_ids')
        for attr_id in delete_attribute_ids:
            cursor.execute("DELETE FROM attributes WHERE id = ?", (attr_id,))

        conn.commit()
        conn.close()
        flash("商品已更新", "success")
        return redirect(url_for('product.products'))

    # 取得商品資料及其屬性
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    cursor.execute("SELECT * FROM attributes WHERE product_id = ? ORDER BY order_index", (product_id,))
    attributes = cursor.fetchall()
    conn.close()

    return render_template('product_edit.html', product=product, attributes=attributes)
