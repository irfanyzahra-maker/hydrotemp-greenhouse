# Jalankan HydroTemp dan buat tautan publik dengan ngrok.
# Pastikan ngrok sudah terinstal dan tersedia di PATH.

Write-Host "Menjalankan aplikasi HydroTemp pada port 5000..." -ForegroundColor Cyan
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "app.py"

Start-Sleep -Seconds 2
Write-Host "Jika ngrok sudah diinstal, jalankan perintah berikut di terminal lain:" -ForegroundColor Yellow
Write-Host "ngrok http 5000" -ForegroundColor Green
Write-Host "Salin URL publik yang ditampilkan di ngrok, misal https://xxxxxx.ngrok.io" -ForegroundColor Green
