from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import base64
import binascii

DB = 'ld2450.db'

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute('''
      CREATE TABLE IF NOT EXISTS readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts INTEGER NOT NULL,
        data_b64 TEXT NOT NULL,
        data_hex TEXT NOT NULL,
        received_at TEXT NOT NULL
      )
    ''')
    conn.commit()
    conn.close()

init_db()

app = Flask(__name__)

@app.route('/add', methods=['POST'])
def add_reading():
    data = request.get_json(force=True, silent=True)
    if not data or 'ts' not in data or 'data' not in data:
        return jsonify({'error':'invalid JSON, expected {"ts":…, "data":…}'}), 400

    ts = data['ts']
    b64 = data['data']
    try:
        raw = base64.b64decode(b64)
    except binascii.Error as e:
        return jsonify({'error':'invalid base64','detail':str(e)}), 400

    # Представим, что мы просто хотим видеть HEX‑строку
    hex_str = raw.hex()

    received_at = datetime.utcnow().isoformat()

    try:
        conn = sqlite3.connect(DB)
        conn.execute(
            'INSERT INTO readings (ts, data_b64, data_hex, received_at) VALUES (?,?,?,?)',
            (ts, b64, hex_str, received_at)
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
    rows = conn.execute(
        'SELECT id, ts, data_b64, data_hex, received_at FROM readings ORDER BY id DESC'
    ).fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({
            'id':        r[0],
            'ts':        r[1],
            'data_b64':  r[2],
            'data_hex':  r[3],
            'received_at': r[4]
        })
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
