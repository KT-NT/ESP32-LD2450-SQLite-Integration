from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # смените на свой секретный ключ в продакшене
DATABASE = 'data.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    # Создаём таблицу пользователей
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )""")
    # Добавляем пользователя admin, если его нет
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        hashed = generate_password_hash('admin123', method='sha256')
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', hashed))
    # Создаём таблицу targets
    c.execute("""
    CREATE TABLE IF NOT EXISTS targets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp INTEGER NOT NULL,    -- время в миллисекундах
        velocity REAL NOT NULL,       -- скорость
        target_index INTEGER NOT NULL -- индекс цели (1,2,3)
    )""")
    conn.commit()
    conn.close()

# Инициализируем базу данных при старте
init_db()

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        c = db.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        if user and check_password_hash(user['password'], password):
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Неверное имя пользователя или пароль")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['user'])

@app.route('/api/live')
def api_live():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    since = request.args.get('since', default=0, type=int)
    db = get_db()
    # Берём данные, поступившие после метки времени since
    c = db.execute("""
        SELECT timestamp, velocity, target_index 
        FROM targets 
        WHERE timestamp > ? 
        ORDER BY timestamp ASC
    """, (since,))
    rows = c.fetchall()
    data = {}
    for row in rows:
        t = row['target_index']
        data.setdefault(t, []).append({'x': row['timestamp'], 'y': row['velocity']})
    # Готовим массив для графика Chart.js
    datasets = []
    colors = {1: 'red', 2: 'blue', 3: 'green'}
    for t, points in data.items():
        datasets.append({
            'label': f'Цель {t}',
            'data': points,
            'borderColor': colors.get(t, 'gray'),
            'fill': False
        })
    return jsonify(datasets)

@app.route('/api/history')
def api_history():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    start_str = request.args.get('start', '')
    end_str = request.args.get('end', '')
    if not start_str or not end_str:
        return jsonify({"error": "Missing start or end parameter"}), 400
    try:
        # Ожидаем формат "YYYY-MM-DDTHH:MM"
        start_dt = datetime.fromisoformat(start_str)
        end_dt = datetime.fromisoformat(end_str)
    except ValueError:
        return jsonify({"error": "Invalid datetime format"}), 400
    start_ts = int(start_dt.timestamp() * 1000)
    end_ts = int(end_dt.timestamp() * 1000)
    db = get_db()
    c = db.execute("""
        SELECT timestamp, velocity, target_index 
        FROM targets 
        WHERE timestamp BETWEEN ? AND ? 
        ORDER BY timestamp ASC
    """, (start_ts, end_ts))
    rows = c.fetchall()
    data = {}
    stats = {}
    for row in rows:
        t = row['target_index']
        if t not in data:
            data[t] = []
            stats[t] = {'active': 0, 'total': 0}
        data[t].append({'x': row['timestamp'], 'y': row['velocity']})
        stats[t]['total'] += 1
        if row['velocity'] > 0:
            stats[t]['active'] += 1
    # Готовим данные для графика
    datasets = []
    colors = {1: 'red', 2: 'blue', 3: 'green'}
    for t, points in data.items():
        datasets.append({
            'label': f'Цель {t}',
            'data': points,
            'borderColor': colors.get(t, 'gray'),
            'fill': False
        })
    # Вычисляем процент активности
    percents = {}
    for t, val in stats.items():
        if val['total'] > 0:
            percents[f'Цель {t}'] = round((val['active'] / val['total']) * 100, 2)
        else:
            percents[f'Цель {t}'] = 0.0
    return jsonify({'datasets': datasets, 'stats': percents})

if __name__ == '__main__':
    app.run(debug=True)
