from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB = 'ld2450.db'

def init_db():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts INTEGER NOT NULL,
            data TEXT NOT NULL,
            received_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()  # вызываем при старте

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute('''
      CREATE TABLE IF NOT EXISTS readings (
        id INTEGER PRIMARY KEY,
        ts INTEGER,
        data TEXT,
        received_at TEXT
      )
    ''')
    conn.commit()
    conn.close()

@app.route('/add', methods=['POST'])
def add_reading():
    data = request.json
    ts = data['ts']
    reading_data = data['data']
    received_at = datetime.utcnow().isoformat()

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO readings (ts, data, received_at) VALUES (?, ?, ?)', (ts, reading_data, received_at))
    conn.commit()
    conn.close()

    return jsonify({'status': 'ok'}), 201


@app.route('/all', methods=['GET'])
def get_all():
    conn = sqlite3.connect(DB)
    rows = conn.execute('SELECT id, ts, data, received_at FROM readings ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify([{'id': r[0], 'ts': r[1], 'data': r[2], 'received_at': r[3]} for r in rows])

if __name__ == '__main__':
    init_db()
    # в продакшене используйте Gunicorn, здесь для отладки
    app.run(host='0.0.0.0', port=5000)
