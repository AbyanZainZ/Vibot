# 🎬 Vidara & DoodStream Viewer Bot V4.5 (Clean Proxy-Only Edition)

Versi bersih **khusus Proxy (HTTP & SOCKS5)** tanpa ketergantungan VPN Surfshark, wireproxy, atau konfigurasi kernel yang rumit. 100% Cross-Platform: bisa dijalankan di **VPS Windows**, **VPS Linux**, maupun **Docker Cloud Sandbox**.

---

## 🚀 Fitur Utama
* **Proxy-Only Engine:** Mendukung proxy **HTTP**, **HTTPS**, dan **SOCKS5** (dengan autentikasi username & password).
* **Multi-Format Parser:** Otomatis mengenali format proxy:
  * `ip:port`
  * `ip:port:user:pass`
  * `user:pass@ip:port`
  * `socks5://ip:port` atau `http://user:pass@ip:port`
* **Configurable `default_protocol`:** Bisa diatur ke `"http"` atau `"socks5"` di `config.json`.
* **Zero VPN Dependency:** Ringan, instan, tidak butuh admin WireGuard / wireproxy.exe.
* **Dual Engine:** Mendukung **Camoufox (Stealth Anti-Detect)** dan **Playwright Chromium (Low-CPU)**.
* **Auto Ad-Popup Killer:** Membunuh popunder dan tab iklan DoodStream / Vidara tanpa menutup video utama.
* **Cross-Platform:** Tersedia launcher otomatis untuk Windows (`.bat`) dan Linux (`.sh`).

---

## ⚙️ Panduan Konfigurasi (`config.json`)

Kamu bisa mengedit file `config.json` tanpa perlu menyentuh kode Python:

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

### Opsi `default_protocol`:
* `"socks5"`: Baris proxy polosan (`ip:port` atau `ip:port:user:pass`) akan otomatis dijalankan sebagai SOCKS5.
* `"http"`: Baris proxy polosan akan otomatis dijalankan sebagai HTTP proxy.
* *Catatan:* Jika baris proxy di file `proxies.txt` sudah diawali `socks5://` atau `http://`, bot akan otomatis mengikuti protokol di baris tersebut.

---

## 💻 Cara Menjalankan

### Di VPS Windows:
1. Masukkan list proxy ke file `proxies.txt`.
2. Klik 2x file:
   ```cmd
   START_BOT.bat
   ```
*(Script akan otomatis memeriksa Python, menginstal library jika belum ada, dan menjalankan bot).*

### Di VPS Linux / Docker Sandbox:
1. Berikan izin eksekusi:
   ```bash
   chmod +x start_bot.sh
   ./start_bot.sh
   ```

---

## 🌐 Auto-Installer untuk GitHub
Jika di-upload ke GitHub, kamu bisa memasang Web Desktop + Bot ini di VPS Linux baru hanya dengan 1 baris perintah:
```bash
curl -fsSL https://raw.githubusercontent.com/<username>/<repo>/main/auto_install.sh | bash
```
