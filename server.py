# server.py
from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import struct, base64

# --- Configuration ---
DB = 'ld2450.db'
FRAME_HEADER = b"\xAA\xFF"
FRAME_FOOTER = b"\x55\xCC"
NUM_TARGETS = 3

# Database initialization: create table for radar targets
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
        amplitude REAL NOT NULL,
        received_at TEXT NOT NULL
      )
    ''')
    conn.commit()
    conn.close()

init_db()
app = Flask(__name__)

# Helper: parse a single 10-byte target record
# structure: <H H h H => angle_raw, dist_raw, vel_raw, amp_raw
# angle in hundredths of degree, distance in mm, velocity in hundredths m/s
TARGET_STRUCT = '<H H h H'
RECORD_SIZE = struct.calcsize(TARGET_STRUCT)

@app.route('/add', methods=['POST'])
def add_reading():
    data = request.get_json(force=True, silent=True)
    if not data or 'ts' not in data or 'data' not in data:
        return jsonify({'error':'invalid JSON, expected {"ts":…, "data":…}'}), 400

    ts = data['ts']
    b64 = data['data']
    try:
        raw = base64.b64decode(b64)
    except Exception:
        return jsonify({'error':'invalid base64'}), 400

    # find header and footer
    if not raw.startswith(FRAME_HEADER) or not raw.endswith(FRAME_FOOTER):
        return jsonify({'error':'invalid frame format'}), 400

    payload = raw[len(FRAME_HEADER):-len(FRAME_FOOTER)]
    conn = sqlite3.connect(DB)
    received_at = datetime.utcnow().isoformat()
    for idx in range(NUM_TARGETS):
        start = idx * RECORD_SIZE
        chunk = payload[start:start+RECORD_SIZE]
        if len(chunk) < RECORD_SIZE:
            break
        angle_raw, dist_raw, vel_raw, amp_raw = struct.unpack(TARGET_STRUCT, chunk)
        angle = angle_raw / 100.0          # hundredths of degree
        distance = dist_raw / 1000.0       # convert mm to meters
        velocity = vel_raw / 100.0         # hundredths m/s to m/s
        amplitude = amp_raw                # raw amplitude
        # Save even zero targets if desired
        conn.execute(
            'INSERT INTO targets (frame_ts, target_index, angle, distance, velocity, amplitude, received_at) VALUES (?,?,?,?,?,?,?)',
            (ts, idx+1, angle, distance, velocity, amplitude, received_at)
        )
    conn.commit()
    conn.close()
    return jsonify({'status':'ok'}), 201

@app.route('/all', methods=['GET'])
def get_all():
    conn = sqlite3.connect(DB)
    rows = conn.execute(
        'SELECT id, frame_ts, target_index, angle, distance, velocity, amplitude, received_at FROM targets ORDER BY id DESC'
    ).fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({
            'id': r[0],
            'ts': r[1],
            'target': r[2],
            'angle': r[3],
            'distance': r[4],
            'velocity': r[5],
            'amplitude': r[6],
            'received_at': r[7]
        })
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
