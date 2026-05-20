# HydroTemp

Aplikasi HydroTemp berbasis Flask yang dapat diakses dari berbagai perangkat baik laptop maupun handphone.

## Struktur aplikasi

- `app.py` - backend Flask, routing, login, analisis, dan pembacaan CSV
- `templates/` - halaman HTML Jinja2 untuk login, dashboard, analisis
- `static/css/style.css` - styling responsive modern
- `requirements.txt` - dependency Python
- `Dockerfile` - container deployment production-ready
- `Procfile` - deployment pada platform seperti Render atau Heroku
- `ngrok.yml` - template konfigurasi ngrok untuk tunneling sementara
- `runtime.txt` - versi Python yang direkomendasikan

## Akses lokal lintas perangkat

1. Jalankan aplikasi lokal:
   ```bash
   python app.py
   ```
2. Temukan IP laptop di jaringan WiFi:
   ```bash
   ipconfig
   ```
3. Buka browser perangkat lain di jaringan yang sama:
   ```text
   http://<IP_LAPTOP>:5000
   ```

> Contoh: `http://192.168.0.103:5000`

## Akses publik sementara menggunakan ngrok

### Setup ngrok

1. Install ngrok di komputer Anda.
2. Tambahkan `authtoken` ke `ngrok.yml` jika tersedia:
   ```yaml
authoken: YOUR_NGROK_AUTH_TOKEN
version: "2"
tunnels:
  hydrotemp:
    addr: 5000
    proto: http
    inspect: true
``` 
3. Jalankan aplikasi lokal:
   ```bash
   python app.py
   ```
4. Buka terminal baru dan jalankan:
   ```bash
   ngrok http 5000
   ```
5. Salin URL publik yang muncul, misal:
   ```text
   https://abcd-1234.ngrok-free.dev
   ```

### Perintah ngrok cepat

- Jalankan ngrok dari konfigurasi:
  ```bash
  ngrok start hydrotemp
  ```
- Atau langsung:
  ```bash
  ngrok http 5000
  ```

### Kapan gunakan ngrok

- untuk testing publik sementara
- untuk menunjukkan aplikasi di perangkat berbeda
- tidak untuk hosting permanen

## Deployment permanen production-ready

Aplikasi sudah disiapkan untuk deployment pada hosting server permanen sehingga tidak bergantung pada VS Code, localhost, atau tunnel sementara.

### 1. Deployment via Render

Render mendukung Python dan container.

- Buat akun Render.
- Buat "Web Service" baru.
- Pilih GitHub repository yang berisi aplikasi ini.
- Build command:
  ```bash
  pip install -r requirements.txt
  ```
- Start command:
  ```bash
  gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 4
  ```
- Render akan memberikan URL publik stabil seperti `https://hydrotemp.onrender.com`.
- Untuk custom domain, ikuti pengaturan domain di dashboard Render.

### 2. Deployment via PythonAnywhere

- Buat akun PythonAnywhere.
- Upload file ke repository atau gunakan `git clone`.
- Install virtualenv dan dependency:
  ```bash
  python3.13 -m venv ~/venv/hydrotemp
  source ~/venv/hydrotemp/bin/activate
  pip install -r requirements.txt
  ```
- Buat Web app baru, pilih `Flask`, dan gunakan `app.py` sebagai entry point.
- Pastikan `WSGI configuration file` memuat:
  ```python
  from app import app as application
  ```
- PythonAnywhere menyediakan domain stabil seperti `yourusername.pythonanywhere.com`.

### 3. Deployment via Docker

Gunakan `Dockerfile` untuk container production-ready.

Build image:
```bash
docker build -t hydrotemp-app .
```

Jalankan container:
```bash
docker run -d -p 5000:5000 hydrotemp-app
```

Kemudian deploy ke layanan seperti:
- AWS ECS / Fargate
- Google Cloud Run
- Azure App Service
- DigitalOcean App Platform

### 4. Deployment via Railway / Heroku

Untuk Heroku atau Railway, gunakan `Procfile` berikut:
```text
web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 4
```

Heroku menyediakan URL stabil seperti `https://hydrotemp.herokuapp.com`.
Railway menyediakan URL publik stabil dan dapat digunakan pada jaringan berbeda.

## Production-ready configuration

- `Dockerfile` sudah mengemas aplikasi dengan `gunicorn`
- `Procfile` tersedia untuk platform PaaS
- `runtime.txt` menyatakan Python 3.13
- `requirements.txt` sudah berisi `gunicorn`
- `app.py` kini menonaktifkan debug secara default dan membaca port dari env `PORT`

## Domain / Public URL stabil

Untuk URL stabil, gunakan hosting permanen seperti Render, PythonAnywhere, Railway, atau Heroku, lalu:
- gunakan URL bawaan platform
- atau tambahkan custom domain sendiri

## Akses multi-jaringan

- `localhost` hanya untuk perangkat yang sama
- `ngrok` hanya sementara dan bergantung pada komputer Anda
- hosting permanen memastikan backend terus berjalan walau VS Code dimatikan

## Login default

- `admin` / `admin123`
- `student` / `hydro2026`

## Ringkasannya

1. Untuk prototyping cepat: `python app.py` + `ngrok http 5000`
2. Untuk publik sementara: gunakan URL ngrok
3. Untuk produksi permanen: deploy ke Render, PythonAnywhere, Railway, Heroku, atau container hosting
4. Untuk akses lintas perangkat: gunakan URL publik dari hosting permanen, bukan localhost
