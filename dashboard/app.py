# app.py (в папке dashboard)

from flask import Flask, render_template, jsonify, request, g
import sqlite3, json
from datetime import datetime

app = Flask(__name__, static_url_path='/dashboard/static', static_folder='static')
DATABASE = '/opt/ld2450_service/ld2450.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exc):
    db = g.pop('db', None)
    if db: db.close()

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/live')
def api_live():
    since = request.args.get('since', default=0, type=int)
    db = get_db()
    cur = db.execute(
        "SELECT ts, data FROM readings WHERE ts > ? ORDER BY ts ASC",
        (since,)
    )
    rows = cur.fetchall()
    datasets = {}
    for r in rows:
        ts = r['ts']
        arr = json.loads(r['data'])
        for tgt in arr:
            idx = tgt.get('idx', tgt.get('target_index', 1))
            vel = tgt.get('velocity', 0)
            datasets.setdefault(idx, []).append({'x': ts, 'y': vel})
    # Формируем список словарей для Chart.js
    colors = {1:'red',2:'blue',3:'green'}
    out = []
    new_since = since
    for idx, pts in datasets.items():
        out.append({
            'label': f'Цель {idx}',
            'data': pts,
            'borderColor': colors.get(idx,'gray'),
            'fill': False
        })
        # обновляем since на максимальный ts
        for pt in pts:
            if pt['x'] > new_since:
                new_since = pt['x']
    # Дополнительно вернуть новый since
    return jsonify(datasets=out, since=new_since)

@app.route('/api/history')
def api_history():
    start = request.args.get('start','')
    end   = request.args.get('end','')
    try:
        sd = datetime.fromisoformat(start)
        ed = datetime.fromisoformat(end)
    except:
        return jsonify(error="Invalid time"),400
    ts0 = int(sd.timestamp()*1000)
    ts1 = int(ed.timestamp()*1000)
    db = get_db()
    cur = db.execute(
        "SELECT ts, data FROM readings WHERE ts BETWEEN ? AND ? ORDER BY ts ASC",
        (ts0, ts1)
    )
    rows = cur.fetchall()
    datasets = {}
    stats = {}
    for r in rows:
        ts = r['ts']
        arr = json.loads(r['data'])
        for tgt in arr:
            idx = tgt.get('idx', tgt.get('target_index', 1))
            vel = tgt.get('velocity', 0)
            datasets.setdefault(idx, []).append({'x': ts, 'y': vel})
            stats.setdefault(idx, {'act':0,'tot':0})
            stats[idx]['tot'] += 1
            if vel != 0:
                stats[idx]['act'] += 1
    colors = {1:'red',2:'blue',3:'green'}
    out = []
    perc = {}
    for idx, pts in datasets.items():
        out.append({
            'label': f'Цель {idx}',
            'data': pts,
            'borderColor': colors.get(idx,'gray'),
            'fill': False
        })
        st = stats[idx]
        perc[f'Цель {idx}'] = round(st['act']/st['tot']*100,2) if st['tot'] else 0
    return jsonify(datasets=out, stats=perc)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001)
