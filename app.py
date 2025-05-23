from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DB_PATH = 'membership.db'


@app.template_filter('add_stars')
def add_stars(s: str) -> str:
    return f'★{s}★'


def init_db():
    if not os.path.exists(DB_PATH):
        print("Initializing database...")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS members (
            iid INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            phone TEXT,
            birthdate TEXT
        );
    ''')
    conn.commit()
    conn.close()


init_db()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        phone = request.form.get('phone', '').strip()
        birthdate = request.form.get('birthdate', '').strip()

        if not username or not email or not password or not birthdate:
            return render_template('error.html', message='請輸入用戶名、電子郵件、密碼及出生年月日')

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM members WHERE username = ?", (username,))
        if c.fetchone():
            conn.close()
            return render_template('error.html', message='用戶名已存在')

        try:
            c.execute("INSERT INTO members (username, email, password, phone, birthdate) VALUES (?, ?, ?, ?, ?)",
                      (username, email, password, phone, birthdate))
            conn.commit()
        except sqlite3.IntegrityError:
            # 如果 email 重複會觸發這裡，課程沒教複雜錯誤處理，直接用通用訊息
            return render_template('error.html', message='電子郵件已被使用')
        finally:
            conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not email or not password:
            return render_template('error.html', message='請輸入電子郵件和密碼')

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT iid, username FROM members WHERE email=? AND password=?", (email, password))
        result = c.fetchone()
        conn.close()

        if result:
            iid, username = result
            # welcome.html 使用 add_stars 過濾器
            return render_template('welcome.html', username=username, iid=iid)
        else:
            return render_template('error.html', message='電子郵件或密碼錯誤')

    return render_template('login.html')


@app.route('/welcome/<int:iid>')
def welcome(iid):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username FROM members WHERE iid=?", (iid,))
    row = c.fetchone()
    conn.close()

    if row:
        username = row[0]
        return render_template('welcome.html', username=username, iid=iid)
    else:
        return render_template('error.html', message='找不到用戶資料')


@app.route('/edit_profile/<int:iid>', methods=['GET', 'POST'])
def edit_profile(iid):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        phone = request.form.get('phone', '').strip()
        birthdate = request.form.get('birthdate', '').strip()

        if not email or not password:
            conn.close()
            return render_template('error.html', message='請輸入電子郵件和密碼')

        c.execute("SELECT iid FROM members WHERE email=? AND iid!=?", (email, iid))
        if c.fetchone():
            conn.close()
            return render_template('error.html', message='電子郵件已被使用')

        c.execute('''UPDATE members
                     SET email=?, password=?, phone=?, birthdate=?
                     WHERE iid=?''', (email, password, phone, birthdate, iid))
        conn.commit()
        conn.close()

        return redirect(url_for('welcome', iid=iid))

    else:
        c.execute("SELECT username, email, password, phone, birthdate FROM members WHERE iid=?", (iid,))
        row = c.fetchone()
        conn.close()

        if row:
            username, email, password, phone, birthdate = row
            return render_template('edit_profile.html',
                                   iid=iid,
                                   username=username,
                                   email=email,
                                   password=password,
                                   phone=phone,
                                   birthdate=birthdate)
        else:
            return render_template('error.html', message='找不到用戶資料')


@app.route('/delete/<int:iid>')
def delete(iid):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM members WHERE iid=?", (iid,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


