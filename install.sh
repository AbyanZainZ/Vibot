#!/usr/bin/env bash
# ==============================================================================
#  VIBOT ONE-LINE CLI INSTALLER FOR LINUX VPS
#  Repository: https://github.com/AbyanZainZ/Vibot
# ==============================================================================
set -e

echo "======================================================================"
echo " 🎬 MEMASANG VIBOT (VIDARA & DOODSTREAM MULTI-PROXY BOT) DI VPS"
echo "======================================================================"

TARGET_DIR="$HOME/Vibot"

# 1. Update & Paket Sistem
echo "⏳ [1/4] Memeriksa paket dasar sistem..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update -y
    sudo apt-get install -y python3 python3-pip python3-venv git curl
fi

# 2. Download / Clone Vibot
echo "⏳ [2/4] Mengunduh repository Vibot..."
if [ ! -d "$TARGET_DIR" ]; then
    git clone https://github.com/AbyanZainZ/Vibot.git "$TARGET_DIR"
else
    echo "ℹ️ Folder Vibot sudah ada, memperbarui kode..."
    cd "$TARGET_DIR" && git pull || true
fi

cd "$TARGET_DIR"

# 3. Pasang Library Python
echo "⏳ [3/4] Memasang dependensi Python..."
# Matikan proteksi PEP 668 secara global otomatis
pip config set global.break-system-packages true 2>/dev/null || true
python3 -m pip config set global.break-system-packages true 2>/dev/null || true

pip install --break-system-packages -r requirements.txt 2>/dev/null || \
python3 -m pip install --break-system-packages -r requirements.txt 2>/dev/null || \
pip install -r requirements.txt

# 4. Unduh Engine Browser Playwright
echo "⏳ [4/4] Memasang driver browser Playwright & Camoufox..."
python3 -m playwright install chromium firefox 2>/dev/null || \
playwright install chromium firefox 2>/dev/null || true

chmod +x start_bot.sh

echo ""
echo "======================================================================"
echo " ✅ INSTALASI VIBOT SELESAI & SIAP JALAN!"
echo "======================================================================"
echo " 📁 Lokasi Bot: $TARGET_DIR"
echo ""
echo " 🚀 Perintah untuk Menjalankan Bot:"
echo "    cd ~/Vibot && ./start_bot.sh"
echo ""
echo " ⚙️ Untuk Edit URL / Proxy:"
echo "    nano ~/Vibot/config.json"
echo "    nano ~/Vibot/proxies.txt"
echo "======================================================================"
