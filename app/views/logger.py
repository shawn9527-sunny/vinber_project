from flask import Blueprint, g, request, session, render_template
import sqlite3
from datetime import datetime
import json
import time
import queue
import threading
from contextlib import contextmanager

logger_blueprint = Blueprint('logger', __name__)

# 創建日誌隊列
log_queue = queue.Queue()

@contextmanager
def get_db_connection():
    conn = None
    try:
        conn = sqlite3.connect('management_system.db', timeout=20)
        conn.row_factory = sqlite3.Row
        yield conn
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

def process_log_queue():
    """處理日誌隊列的背景線程"""
    while True:
        try:
            # 從隊列中獲取日誌數據
            log_data = log_queue.get()
            if log_data is None:  # 結束信號
                break
                
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('PRAGMA busy_timeout = 5000')  # 設置忙碌超時
                
                cursor.execute('''
                    INSERT INTO operation_logs 
                    (user_id, username, action, table_name, record_id, details, ip_address)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    log_data['user_id'],
                    log_data['username'],
                    log_data['action'],
                    log_data['table_name'],
                    log_data['record_id'],
                    json.dumps(log_data['details']) if log_data['details'] else None,
                    log_data['ip_address']
                ))
                
                conn.commit()
                
        except Exception as e:
            print(f"處理日誌時發生錯誤: {str(e)}")
        finally:
            log_queue.task_done()

# 啟動日誌處理線程
log_thread = threading.Thread(target=process_log_queue, daemon=True)
log_thread.start()

def log_operation(action, table_name, record_id=None, details=None):
    """
    將日誌加入隊列
    """
    try:
        log_data = {
            'user_id': session.get('user_id'),
            'username': session.get('username'),
            'action': action,
            'table_name': table_name,
            'record_id': record_id,
            'details': details,
            'ip_address': request.remote_addr
        }
        log_queue.put(log_data)
    except Exception as e:
        print(f"添加日誌到隊列時發生錯誤: {str(e)}")

@logger_blueprint.route('/logs')
def view_logs():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('PRAGMA busy_timeout = 5000')
            
            cursor.execute('''
                SELECT * FROM operation_logs 
                ORDER BY created_at DESC 
                LIMIT 1000
            ''')
            logs = cursor.fetchall()
            
        return render_template('logs/view_logs.html', logs=logs)
        
    except Exception as e:
        print(f"查看日誌時發生錯誤: {str(e)}")
        return render_template('logs/view_logs.html', logs=[])

# 在應用關閉時清理
def cleanup():
    log_queue.put(None)  # 發送結束信號
    log_thread.join(timeout=5)  # 等待線程結束