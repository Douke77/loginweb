from flask import Flask
import sqlite3
import os

app = Flask(__name__) # __name__ 代表目前執行的模組

@app.route("/")
def hello():
    """視圖函式 view function"""
    return "<p>Hello, World!</p>"

def init_db():
    db_path = 'membership.db'
    if not os.path.exists(db_path):
        print("Initializing database...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 建立資料表（若尚未存在）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            iid INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            phone TEXT,
            birthdate TEXT
        );
    ''')

    # 插入初始管理員帳號
    cursor.execute('''
        INSERT OR IGNORE INTO members (username, email, password, phone, birthdate)
        VALUES (?, ?, ?, ?, ?);
    ''', ('admin', 'admin@example.com', 'admin123', '0912345678', '1990-01-01'))

    conn.commit()
    conn.close()
init_db()