# 🎬 Vibot: Vidara & DoodStream Multi-Proxy Viewer Bot V4.5

Bot pemutar video **DoodStream & Vidara** otomatis berbasis **Clean Multi-Proxy (HTTP & SOCKS5)** dengan sistem anti-detect stealth (Camoufox & Playwright), anti-ad popup killer, dan rotasi proxy otomatis.

Kini dilengkapi dengan **Proxy Scraper & Live Checker Otomatis** bawaan tanpa ribet mencari proxy manual!

---

## ⚡ Perintah Cepat 1 Baris untuk Install di VPS (CLI)

### 🐧 Di VPS Linux (Ubuntu / Debian / Docker):
Cukup copy-paste perintah ini ke terminal Linux kamu:
```bash
curl -fsSL https://raw.githubusercontent.com/AbyanZainZ/Vibot/main/install.sh | bash
```
> Program akan otomatis diinstall rapi di folder `/VidBot` (atau `~/VidBot`).

### 🪟 Di VPS Windows (PowerShell):
Buka PowerShell lalu jalankan:
```powershell
irm https://raw.githubusercontent.com/AbyanZainZ/Vibot/main/install.ps1 | iex
```

---

## 🚀 Cara Menjalankan

### Langkah 1: Cari & Validasi Proxy Live (Otomatis dari GitHub)
Program ini akan otomatis mengunduh ribuan proxy gratis dari 90+ repository GitHub, menguji mana yang aktif, dan **hanya menyimpan proxy LIVE** ke `proxy.txt` / `proxies.txt` (proxy mati otomatis dibuang).

- **Di Linux VPS / Docker**:
  ```bash
  cd /VidBot
  ./start_proxyScrape.sh
  ```
- **Di Windows VPS**:
  Klik 2x file `START_PROXY_SCRAPE.bat`

### Langkah 2: Isi Link Video Target
Masukkan link video Doodstream / Vidara kamu ke dalam file **`link.txt`** (1 baris per link).

### Langkah 3: Jalankan Viewer Bot
- **Di Linux VPS / Docker**:
  ```bash
  cd /VidBot
  ./start_bot.sh
  ```
- **Di Windows VPS**:
  Klik 2x file `START_BOT.bat`

---

## 📁 Struktur File Lengkap & Rapi

Semua komponen dibuat modular dan terpisah sendiri-sendiri agar mudah dikelola:

| File / Script | Fungsi | Keterangan |
| :--- | :--- | :--- |
| **`link.txt`** | **Daftar Link Video** | Masukkan link video target (1 baris per link). Bebas masukkan puluhan/ratusan link! |
| **`proxy.txt`** / **`proxies.txt`** | **Daftar Proxy Live** | Hasil otomatis dari scraper atau isi sendiri (HTTP & SOCKS5). |
| **`start_proxyScrape.sh`** | **Launcher Scraper (Linux)** | Jalankan untuk mencari & cek live proxy secara otomatis di Linux. |
| **`START_PROXY_SCRAPE.bat`** | **Launcher Scraper (Win)** | Klik 2x untuk mencari & cek live proxy di Windows. |
| **`start_bot.sh`** | **Launcher Bot (Linux)** | Jalankan bot viewer di VPS Linux / Docker. |
| **`START_BOT.bat`** | **Launcher Bot (Win)** | Klik 2x untuk menjalankan bot viewer di VPS Windows. |
| **`config.json`** | **Pengaturan Engine** | Cukup untuk mengatur durasi tonton, jumlah slot browser, headless, dll. |

---

## ⚙️ Pengaturan di `config.json`

```json
{
  "link_file": "link.txt",
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
    "default_protocol": "http",
    "rotation_mode": "random"
  }
}
```
