from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

# Имя файла базы
DB = 'ld2450.db'

# Инициализация базы — создаёт таблицу, если её нет
def init_db():
    conn = sqlite3.connect(DB)
    conn.execute('''
      CREATE TABLE IF NOT EXISTS targets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        frame_ts INTEGER NOT NULL,
        target_index INTEGER NOT NULL,
        angle REAL NOT NULL,
        distance REAL NOT NULL,
        velocity REAL NOT NULL,
        amplitude INTEGER NOT NULL,
        received_at TEXT NOT NULL
      )
    ''')
    conn.commit()
    conn.close()

# вызываем при старте
init_db()

app = Flask(__name__)

@app.route('/add', methods=['POST'])
def add_reading():
    data = request.get_json(force=True, silent=True)
    # проверяем, что JSON соответствует формату
    if not data or 'ts' not in data or 'targets' not in data:
        return jsonify({
            'error': 'invalid JSON, expected {"ts":…, "targets":[…]}'
        }), 400

    ts = data['ts']
    targets = data['targets']
    received = datetime.utcnow().isoformat()

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    for idx, t in enumerate(targets, start=1):
        # вставляем каждую цель в отдельную строку
        cursor.execute('''
          INSERT INTO targets
            (frame_ts, target_index, angle, distance, velocity, amplitude, received_at)
          VALUES (?,?,?,?,?,?,?)
        ''', (
          ts,
          idx,
          t.get('angle', 0),
          t.get('distance', 0),
          t.get('velocity', 0),
          t.get('amplitude', 0),
          received
        ))
    conn.commit()
    conn.close()

    return jsonify({'status': 'ok'}), 201

@app.route('/all', methods=['GET'])
def get_all():
    conn = sqlite3.connect(DB)
    rows = conn.execute('''
      SELECT frame_ts, target_index, angle, distance, velocity, amplitude, received_at
      FROM targets
      ORDER BY id DESC
    ''').fetchall()
    conn.close()

    # формируем список словарей
    result = []
    for r in rows:
        result.append({
            'frame_ts':     r[0],
            'target_index': r[1],
            'angle':        r[2],
            'distance':     r[3],
            'velocity':     r[4],
            'amplitude':    r[5],
            'received_at':  r[6]
        })
    return jsonify(result), 200

if __name__ == '__main__':
    # Для отладки можно включить debug=True
    app.run(host='0.0.0.0', port=8000)
