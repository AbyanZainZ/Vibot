#!/usr/bin/env bash
# ==============================================================================
#  VIDBOT ONE-LINE CLI INSTALLER FOR LINUX VPS & DOCKER WEB TOP
#  Repository: https://github.com/AbyanZainZ/Vibot
# ==============================================================================
set -e

echo "======================================================================"
echo " 🎬 MEMASANG VIDBOT (VIDARA & DOODSTREAM MULTI-PROXY BOT)"
echo "======================================================================"

# Tentukan folder target rapi: /VidBot atau ~/VidBot
if [ "$(id -u)" -eq 0 ]; then
    TARGET_DIR="/VidBot"
else
    TARGET_DIR="$HOME/VidBot"
fi

echo "[*] Lokasi Instalasi Target: $TARGET_DIR"

# 1. Update & Paket Sistem
echo ""
echo "⏳ [1/4] Memeriksa paket dasar sistem..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update -y 2>/dev/null || true
    sudo apt-get install -y python3 python3-pip python3-venv git curl 2>/dev/null || true
fi

# 2. Download / Clone VidBot ke foldernya sendiri
echo ""
echo "⏳ [2/4] Mengunduh source code VidBot ke: $TARGET_DIR ..."
if [ ! -d "$TARGET_DIR" ]; then
    git clone https://github.com/AbyanZainZ/Vibot.git "$TARGET_DIR"
    echo "✅ Berhasil mengunduh ke: $TARGET_DIR"
else
    echo "ℹ️ Folder $TARGET_DIR sudah ada, memperbarui file terbaru..."
    cd "$TARGET_DIR" && git pull || true
fi

cd "$TARGET_DIR"

# 3. Setup Virtual Environment (VENV) di dalam folder VidBot
echo ""
echo "⏳ [3/4] Menyiapkan environment Python khusus di $TARGET_DIR/venv ..."
if [ ! -d "$TARGET_DIR/venv" ]; then
    python3 -m venv "$TARGET_DIR/venv"
fi

# Upgrade pip & install requirements
echo "[*] Memasang library Python..."
"$TARGET_DIR/venv/bin/python" -m pip install --upgrade pip 2>/dev/null || true
"$TARGET_DIR/venv/bin/pip" install -r requirements.txt

# 4. Unduh Engine Browser Playwright
echo ""
echo "⏳ [4/4] Memasang driver browser Playwright (Chromium & Firefox)..."
"$TARGET_DIR/venv/bin/playwright" install chromium firefox 2>/dev/null || true

chmod +x "$TARGET_DIR/start_bot.sh"
chmod +x "$TARGET_DIR/start_proxyScrape.sh" 2>/dev/null || true

echo ""
echo "======================================================================"
echo " 🎉 INSTALASI VIDBOT SUKSES BESAR!"
echo "======================================================================"
echo " 📁 Lokasi Penyimpanan: $TARGET_DIR"
echo " 📂 Path Lengkap: $(cd "$TARGET_DIR" && pwd)"
echo ""
echo " 🚀 Cara Menjalankan:"
echo "    cd $TARGET_DIR"
echo "    1. Cari Proxy Live Otomatis (GitHub):"
echo "       ./start_proxyScrape.sh"
echo ""
echo "    2. Jalankan Viewer Bot:"
echo "       ./start_bot.sh"
echo ""
echo " ⚙️ File Konfigurasi:"
echo "    - $TARGET_DIR/link.txt     (Daftar target link video)"
echo "    - $TARGET_DIR/proxy.txt    (Daftar live proxy verified)"
echo "    - $TARGET_DIR/config.json  (Pengaturan engine & durasi tonton)"
echo "======================================================================"
