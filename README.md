# 🎬 Vibot: Vidara & DoodStream Multi-Proxy Viewer Bot V4.5

Bot pemutar video **DoodStream & Vidara** otomatis berbasis **Clean Multi-Proxy (HTTP & SOCKS5)** dengan sistem anti-detect stealth (Camoufox & Playwright), anti-ad popup killer, dan rotasi proxy otomatis.

---

## ⚡ Perintah Cepat 1 Baris untuk Install di VPS (CLI)

### 🐧 Di VPS Linux (Ubuntu / Debian):
Cukup copy-paste perintah ini ke terminal Linux kamu:
```bash
curl -fsSL https://raw.githubusercontent.com/AbyanZainZ/Vibot/main/install.sh | bash
```
*(Script akan otomatis meng-clone Vibot ke `~/Vibot`, memasang python3, pip, playwright, dan dependensi browser).*

### 🪟 Di VPS Windows (PowerShell):
Buka PowerShell lalu jalankan:
```powershell
irm https://raw.githubusercontent.com/AbyanZainZ/Vibot/main/install.ps1 | iex
```
*(Script akan otomatis mengunduh Vibot ke Desktop / `C:\Vibot` dan menyiapkan dependensinya).*

---

## 🚀 Cara Menjalankan Bot Setelah Terpasang

### Di Linux:
```bash
cd ~/Vibot
./start_bot.sh
```

### Di Windows:
Masuk ke folder `Vibot` di Desktop, lalu double-click file:
```cmd
START_BOT.bat
```

---

## ⚙️ Panduan Konfigurasi (`config.json`)

Kamu bisa mengedit target URL dan pengaturan bot di file `config.json` tanpa menyentuh kode python:

```json
{
  "target_urls": [
    "https://vidara.so/v/UDQvQR86iSidN",
    "https://vidara.to/v/bajvKatP3cxK",
    "https://playmogo.com/d/2kgtwakxl10w"
  ],
  "engine_mode": "camoufox",
  "headless_mode": true,
  "max_concurrent_browsers": 2,
  "start_stagger_delay_sec": 2.0,
  "watch_duration_sec": 180,
  "execution_mode": "loop",
  "round_delay_sec": 10,
  "max_proxy_retries": 5,
  "prevent_windows_sleep": true,
  "proxy_pool": {
    "proxy_file": "proxies.txt",
    "default_protocol": "socks5",
    "rotation_mode": "random"
  }
}
```

### Opsi Protokol Proxy:
* `"default_protocol": "socks5"` -> Jika daftar proxy berupa IP:PORT polosan SOCKS5.
* `"default_protocol": "http"` -> Jika daftar proxy berupa IP:PORT polosan HTTP.
* Jika baris proxy di `proxies.txt` sudah ada prefix `http://` atau `socks5://`, bot akan otomatis mengikuti protokol di baris tersebut.
