import os
import sqlite3
from datetime import datetime

import pandas as pd
from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, 'greenhouse_data.csv')
DATABASE = os.path.join(BASE_DIR, 'hydrotemp.db')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hydrotemp-secret-key-2026'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

DEFAULT_USERS = [
    {'username': 'admin', 'password': 'admin123'},
    {'username': 'student', 'password': 'hydro2026'}
]

CROP_OPTIONS = ['Selada', 'Tomat', 'Cabai', 'Mentimun']

SAMPLE_DATA = [
    {'Timestamp': '2026-05-10 08:00', 'Tanaman': 'Selada', 'Suhu': 24, 'Kelembapan': 72},
    {'Timestamp': '2026-05-10 10:00', 'Tanaman': 'Tomat', 'Suhu': 29, 'Kelembapan': 65},
    {'Timestamp': '2026-05-10 12:00', 'Tanaman': 'Cabai', 'Suhu': 33, 'Kelembapan': 55},
    {'Timestamp': '2026-05-10 14:00', 'Tanaman': 'Mentimun', 'Suhu': 22, 'Kelembapan': 78},
    {'Timestamp': '2026-05-11 09:00', 'Tanaman': 'Selada', 'Suhu': 18, 'Kelembapan': 58},
    {'Timestamp': '2026-05-11 11:00', 'Tanaman': 'Tomat', 'Suhu': 31, 'Kelembapan': 89},
]


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(BASE_DIR, exist_ok=True)
    conn = get_db_connection()
    with conn:
        conn.execute(
            'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)'
        )
        for user in DEFAULT_USERS:
            hashed = generate_password_hash(user['password'])
            try:
                conn.execute(
                    'INSERT INTO users (username, password) VALUES (?, ?)',
                    (user['username'], hashed),
                )
            except sqlite3.IntegrityError:
                pass
    conn.close()

init_db()


def ensure_dataset():
    if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
        df = pd.DataFrame(SAMPLE_DATA)
        df.to_csv(CSV_FILE, index=False)
    try:
        df = pd.read_csv(CSV_FILE)
    except Exception:
        df = pd.DataFrame(SAMPLE_DATA)
        df.to_csv(CSV_FILE, index=False)
    return df


def load_dataset(crop_filter=None):
    df = ensure_dataset()
    if crop_filter and crop_filter != 'Semua':
        df = df[df['Tanaman'] == crop_filter]
    return df


def calculate_status(temperature, humidity):
    temperature = float(temperature)
    humidity = float(humidity)
    fan = 'Mati'
    heater = 'Mati'
    humidifier = 'Mati'
    ventilation = 'Mati'
    recommendations = []

    if temperature > 30:
        fan = 'Nyala'
        recommendations.append('Nyalakan kipas untuk menurunkan suhu.')
    elif temperature < 20:
        heater = 'Aktif'
        recommendations.append('Aktifkan pemanas untuk menaikkan suhu.')
    else:
        recommendations.append('Suhu berada di kisaran ideal.')

    if humidity < 60:
        humidifier = 'Aktif'
        recommendations.append('Nyalakan humidifier untuk menambah kelembapan.')
    elif humidity > 85:
        ventilation = 'Aktif'
        recommendations.append('Buka ventilasi untuk mengurangi kelembapan.')
    else:
        recommendations.append('Kelembapan berada di kisaran ideal.')

    condition = 'Baik'
    if fan == 'Nyala' or heater == 'Aktif' or humidifier == 'Aktif' or ventilation == 'Aktif':
        condition = 'Perlu perhatian'
    else:
        condition = 'Stabil'

    return {
        'suhu_status': fan if temperature > 30 else heater if temperature < 20 else 'Normal',
        'kelembapan_status': humidifier if humidity < 60 else ventilation if humidity > 85 else 'Normal',
        'fan': fan,
        'heater': heater,
        'humidifier': humidifier,
        'ventilation': ventilation,
        'condition': condition,
        'recommendation': ' '.join(recommendations)
    }


def login_required(view):
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return view(**kwargs)
    wrapped_view.__name__ = view.__name__
    return wrapped_view


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            error = 'Username dan password harus diisi.'
        else:
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            conn.close()
            if user is None or not check_password_hash(user['password'], password):
                error = 'Username atau password salah.'
            else:
                session.clear()
                session['user_id'] = user['id']
                session['username'] = user['username']
                flash('Login berhasil. Selamat datang, {}!'.format(user['username']), 'success')
                return redirect(url_for('dashboard'))

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    flash('Anda berhasil logout.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    crop_filter = request.args.get('crop', 'Semua')
    df = load_dataset(crop_filter)
    latest = None
    summary = {
        'Suhu': '-',
        'Kelembapan': '-',
        'Tanaman': '-',
        'Status Kipas': '-',
        'Status Humidifier': '-',
        'Kondisi': '-',
    }
    if not df.empty:
        latest = df.iloc[-1]
        env_status = calculate_status(latest['Suhu'], latest['Kelembapan'])
        summary = {
            'Suhu': f"{latest['Suhu']} °C",
            'Kelembapan': f"{latest['Kelembapan']} %",
            'Tanaman': latest['Tanaman'],
            'Status Kipas': env_status['fan'],
            'Status Humidifier': env_status['humidifier'],
            'Kondisi': env_status['condition'],
        }

    analysis = session.get('analysis')
    return render_template(
        'dashboard.html',
        username=session.get('username'),
        crops=CROP_OPTIONS,
        crop_filter=crop_filter,
        table_data=df.to_dict(orient='records'),
        summary=summary,
        analysis=analysis,
    )


@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    suhu = request.form.get('suhu', '').strip()
    kelembapan = request.form.get('kelembapan', '').strip()
    tanaman = request.form.get('tanaman', '').strip()
    error = None

    if not suhu or not kelembapan or not tanaman:
        error = 'Semua input monitoring harus diisi.'
    else:
        try:
            suhu_val = float(suhu)
            kelembapan_val = float(kelembapan)
        except ValueError:
            error = 'Suhu dan kelembapan harus berupa angka yang valid.'

    if error:
        flash(error, 'danger')
        return redirect(url_for('dashboard'))

    result = calculate_status(suhu_val, kelembapan_val)
    result.update(
        {
            'suhu': suhu_val,
            'kelembapan': kelembapan_val,
            'tanaman': tanaman,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'message': 'Data berhasil dianalisis.',
        }
    )

    try:
        df = ensure_dataset()
        new_row = pd.DataFrame([
            {
                'Timestamp': result['timestamp'],
                'Tanaman': result['tanaman'],
                'Suhu': result['suhu'],
                'Kelembapan': result['kelembapan'],
            }
        ])
        new_row.to_csv(CSV_FILE, mode='a', index=False, header=not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0)
    except Exception:
        pass

    session['analysis'] = result
    flash('Analisis greenhouse berhasil disimpan.', 'success')
    return redirect(url_for('analysis'))


@app.route('/analysis')
@login_required
def analysis():
    analysis = session.get('analysis')
    if not analysis:
        flash('Tidak ada data analisis terbaru. Silakan isi formulir monitoring.', 'warning')
        return redirect(url_for('dashboard'))
    return render_template('analysis.html', analysis=analysis)


@app.route('/reset', methods=['POST'])
@login_required
def reset():
    session.pop('analysis', None)
    flash('Hasil analisis direset.', 'info')
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    init_db()
    debug_mode = os.getenv('FLASK_DEBUG', '0') == '1'
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
