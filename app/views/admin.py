from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3
from .login import login_required

admin_blueprint = Blueprint('admin', __name__, template_folder='../templates')

# 管理者登入頁面
@admin_blueprint.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('management_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user and user[2] == 'admin':
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash("登入失敗，請檢查帳號和密碼", "danger")
    return render_template('admin_login.html')

# 管理者主控台
@admin_blueprint.route('/dashboard')
@login_required(role='admin')
def admin_dashboard():
    conn = sqlite3.connect('management_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE role = 'user'")
    users = cursor.fetchall()
    conn.close()
    return render_template('admin_dashboard.html', users=users)
