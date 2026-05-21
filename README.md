# HydroTemp

Aplikasi HydroTemp berbasis Flask yang dapat diakses dari laptop dan handphone.

## Cara akses dari perangkat lain (WiFi lokal)

1. Jalankan aplikasi:
   ```bash
   python app.py
   ```
2. Pada laptop, buka terminal atau PowerShell, lalu jalankan:
   ```bash
   ipconfig
   ```
3. Cari alamat `IPv4 Address` pada adaptor WiFi.
4. Dari handphone yang terhubung ke jaringan WiFi yang sama, buka browser dan masukkan:
   ```text
   http://<ALAMAT_IP_LAPTOP>:5000
   ```
   Contoh: `http://192.168.1.10:5000`

> Aplikasi sudah dikonfigurasi pada `app.py` dengan `host='0.0.0.0'`, sehingga dapat diakses oleh perangkat lain di jaringan yang sama.

## Akses lewat jaringan seluler / data

Untuk mengakses dari handphone dengan koneksi data seluler, Anda membutuhkan layanan tunneling atau port forwarding dari jaringan publik:

- Gunakan `ngrok`:
  1. Instal ngrok di laptop.
  2. Jalankan:
     ```bash
     ngrok http 5000
     ```
  3. Salin URL publik yang diberikan, lalu buka di handphone.

- Atau gunakan layanan serupa seperti `localtunnel` atau `serveo`.

## Catatan keamanan

- Jangan jalankan mode `debug=True` saat memberikan akses publik.
- Gunakan `ngrok` hanya untuk pengujian ringan.

## Login default

- `admin` / `admin123`
- `student` / `hydro2026`
