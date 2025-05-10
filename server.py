from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB = 'ld2450.db'

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute('''
      CREATE TABLE IF NOT EXISTS readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts INTEGER NOT NULL,
        data TEXT NOT NULL,
        received_at TEXT NOT NULL
      )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/add', methods=['POST'])
def add_reading():
    # пытаемся получить JSON, даже если нет заголовка
    data = request.get_json(force=True, silent=True)
    if not data or 'ts' not in data or 'data' not in data:
        return jsonify({'error':'invalid JSON, expected {"ts":…, "data":…}'}), 400

    ts = data['ts']
    reading_data = data['data']
    received_at = datetime.utcnow().isoformat()

    try:
        conn = sqlite3.connect(DB)
        conn.execute(
            'INSERT INTO readings (ts, data, received_at) VALUES (?,?,?)',
            (ts, reading_data, received_at)
        )
        conn.commit()
    except Exception as e:
        return jsonify({'error':'db write failed','detail':str(e)}), 500
    finally:
        conn.close()

    return jsonify({'status':'ok'}), 201

@app.route('/all', methods=['GET'])
def get_all():
    conn = sqlite3.connect(DB)
    rows = conn.execute('SELECT id, ts, data, received_at FROM readings ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify([{'id':r[0],'ts':r[1],'data':r[2],'received_at':r[3]} for r in rows])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
