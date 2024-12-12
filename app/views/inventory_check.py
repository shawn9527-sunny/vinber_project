from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
from datetime import datetime

inventory_check_blueprint = Blueprint('inventory_check', __name__)

def get_db_connection():
    conn = sqlite3.connect('management_system.db')
    conn.row_factory = sqlite3.Row
    return conn

@inventory_check_blueprint.route('/inventory_check', methods=['GET'])
def inventory_check():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 獲取所有產品列表供篩選使用
    cursor.execute("SELECT id, name FROM products ORDER BY name")
    products = cursor.fetchall()
    
    # 獲取所有供應商列表供篩選使用
    cursor.execute("SELECT taxid, name FROM suppliers ORDER BY name")
    suppliers = cursor.fetchall()
    
    # 預設查詢所有庫存
    cursor.execute("""
        SELECT 
            pur.id as sn_code,
            p.name as product_name,
            pur.cost,
            pur.purchase_order_number,
            s.name as supplier_name,
            s.taxid as supplier_id,
            p.id as product_id,
            GROUP_CONCAT(
                attr.name || ': ' || pa.attribute_value
            ) as attributes
        FROM purchases pur
        JOIN products p ON pur.product_id = p.id
        JOIN suppliers s ON pur.supplier_id = s.taxid
        LEFT JOIN purchase_attributes pa ON pur.id = pa.purchase_id
        LEFT JOIN attributes attr ON pa.attribute_name = attr.id
        GROUP BY pur.id
        ORDER BY pur.purchase_order_number DESC
    """)
    inventory_items = cursor.fetchall()
    
    conn.close()
    
    return render_template('inventory_check.html',
                         products=products,
                         suppliers=suppliers,
                         inventory_items=inventory_items)

@inventory_check_blueprint.route('/api/filter_inventory', methods=['POST'])
def filter_inventory():
    data = request.get_json()
    product_id = data.get('product_id')
    supplier_id = data.get('supplier_id')
    date_start = data.get('date_start')
    date_end = data.get('date_end')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT 
            pur.id as sn_code,
            p.name as product_name,
            pur.cost,
            pur.purchase_order_number,
            s.name as supplier_name,
            pur.purchase_date,
            GROUP_CONCAT(
                attr.name || ': ' || pa.attribute_value
            ) as attributes
        FROM purchases pur
        JOIN products p ON pur.product_id = p.id
        JOIN suppliers s ON pur.supplier_id = s.taxid
        LEFT JOIN purchase_attributes pa ON pur.id = pa.purchase_id
        LEFT JOIN attributes attr ON pa.attribute_name = attr.id
        WHERE 1=1
    """
    params = []
    
    if product_id:
        query += " AND p.id = ?"
        params.append(product_id)
    if supplier_id:
        query += " AND s.taxid = ?"
        params.append(supplier_id)
    if date_start:
        query += " AND DATE(pur.purchase_date) >= DATE(?)"
        params.append(date_start)
    if date_end:
        query += " AND DATE(pur.purchase_date) <= DATE(?)"
        params.append(date_end)
        
    query += " GROUP BY pur.id ORDER BY pur.purchase_order_number DESC"
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in results])

@inventory_check_blueprint.route('/api/export_inventory', methods=['POST'])
def export_inventory():
    # 這裡可以實現匯出功能
    pass 