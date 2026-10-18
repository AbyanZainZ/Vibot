# 🎬 Vibot: Vidara & DoodStream Multi-Proxy Viewer Bot V4.5

Bot pemutar video **DoodStream & Vidara** otomatis berbasis **Clean Multi-Proxy (HTTP & SOCKS5)** dengan sistem anti-detect stealth (Camoufox & Playwright), anti-ad popup killer, dan rotasi proxy otomatis.

---

## ⚡ Perintah Cepat 1 Baris untuk Install di VPS (CLI)

### 🐧 Di VPS Linux (Ubuntu / Debian):
Cukup copy-paste perintah ini ke terminal Linux kamu:
```bash
curl -fsSL https://raw.githubusercontent.com/AbyanZainZ/Vibot/main/install.sh | bash
```

### 🪟 Di VPS Windows (PowerShell):
Buka PowerShell lalu jalankan:
```powershell
irm https://raw.githubusercontent.com/AbyanZainZ/Vibot/main/install.ps1 | iex
```

---

## 📁 Struktur File Lebih Rapi (Terpisah Sendiri-Sendiri):

Sekarang kamu tidak perlu repot mengedit array di dalam config! Semuanya sudah dipisah sendiri-sendiri:

| File | Fungsi | Keterangan |
| :--- | :--- | :--- |
| **`link.txt`** | **Daftar Link Video** | Masukkan link video target (1 baris per link). Bebas masukkan puluhan/ratusan link! |
| **`proxies.txt`** | **Daftar Proxy** | Masukkan proxy kamu (1 baris per proxy). Mendukung HTTP & SOCKS5. |
| **`config.json`** | **Pengaturan Engine** | Cukup untuk mengatur durasi tonton, jumlah slot browser, headless, dll. |
| **`START_BOT.bat`** | **Launcher Windows** | Klik 2x untuk menjalankan bot di VPS Windows. |
| **`start_bot.sh`** | **Launcher Linux** | Jalankan `./start_bot.sh` di VPS Linux / Docker. |

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
