from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3
from functools import wraps

login_blueprint = Blueprint('login', __name__, template_folder='../templates')

# 登入檢查裝飾器
def login_required(role=None):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("請先登入", "warning")
                return redirect(url_for('login.login'))
            if role and session.get('role') != role:
                flash("無權限訪問此頁面", "danger")
                return redirect(url_for('admin.admin_dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return wrapper

# 登入頁面（一般使用者）
@login_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('management_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user and user[3] == 'user':
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash("登入失敗，請檢查帳號和密碼", "danger")
    return render_template('login.html')
