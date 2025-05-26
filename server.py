from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime

DB = 'ld2450.db'

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute('''
      CREATE TABLE IF NOT EXISTS targets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        frame_ts    INTEGER NOT NULL,
        target_index INTEGER NOT NULL,
        angle       REAL NOT NULL,
        distance    REAL NOT NULL,
        velocity    REAL NOT NULL,
        amplitude   REAL NOT NULL,
        received_at TEXT NOT NULL
      )
    ''')
    conn.commit()
    conn.close()

init_db()
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_reading():
    data = request.get_json(force=True)
    if not data or not all(k in data for k in ("velocity","angle","distance")):
        return jsonify({'error':'invalid JSON'}), 400

    ts   = int(datetime.utcnow().timestamp())
    vel  = float(data['velocity'])
    ang  = float(data['angle'])
    dist = float(data['distance'])
    amp  = float(data.get('amplitude', 0))
    received = datetime.utcnow().isoformat()

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute('''
      INSERT INTO targets
        (frame_ts, target_index, angle, distance, velocity, amplitude, received_at)
      VALUES (?,?,?,?,?,?,?)
    ''', (ts, 1, ang, dist, vel, amp, received))
    conn.commit()
    conn.close()
    return jsonify({'status':'ok'}), 201

@app.route('/all')
def all_data():
    conn = sqlite3.connect(DB)
    rows = conn.execute('SELECT frame_ts, velocity FROM targets ORDER BY frame_ts').fetchall()
    conn.close()
    return jsonify([{'frame_ts':r[0], 'velocity':r[1]} for r in rows])

@app.route('/range')
def range_data():
    start = request.args.get('start', type=int)
    end   = request.args.get('end',   type=int)
    if start is None or end is None:
        return jsonify({'error':'need start and end'}), 400
    conn = sqlite3.connect(DB)
    rows = conn.execute('''
      SELECT frame_ts, velocity FROM targets
      WHERE frame_ts BETWEEN ? AND ? ORDER BY frame_ts
    ''', (start, end)).fetchall()
    conn.close()
    return jsonify([{'frame_ts':r[0], 'velocity':r[1]} for r in rows])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
