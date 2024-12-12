from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import sqlite3
from functools import wraps

auth_blueprint = Blueprint('auth', __name__)

def get_db_connection():
    conn = sqlite3.connect('management_system.db')
    conn.row_factory = sqlite3.Row
    return conn

# 登入要求裝飾器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# 管理員要求裝飾器
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_role' not in session or session['user_role'] != 'admin':
            flash('需要管理員權限', 'danger')
            return redirect(url_for('index.index'))
        return f(*args, **kwargs)
    return decorated_function

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if user and user['password'] == password:  # 實際應用中應使用密碼雜湊
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_role'] = user['role']
            
            # 更新最後登入時間
            cursor.execute('''
                UPDATE users 
                SET last_login = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (user['id'],))
            conn.commit()
            
            flash('登入成功！', 'success')
            return redirect(url_for('index.index'))
        else:
            flash('帳號或密碼錯誤', 'danger')
        
        conn.close()
    
    return render_template('auth/login.html')

@auth_blueprint.route('/logout')
def logout():
    session.clear()
    flash('已登出', 'info')
    return redirect(url_for('auth.login'))

@auth_blueprint.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash('新密碼不一致', 'danger')
            return redirect(url_for('auth.change_password'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
        user = cursor.fetchone()
        
        if user and user['password'] == old_password:  # 實際應使用密碼雜湊
            cursor.execute('''
                UPDATE users 
                SET password = ? 
                WHERE id = ?
            ''', (new_password, session['user_id']))
            conn.commit()
            flash('密碼已更新', 'success')
            return redirect(url_for('index'))
        else:
            flash('原密碼錯誤', 'danger')
        
        conn.close()
    
    return render_template('auth/change_password.html') 