#!/usr/bin/env bash
# ==============================================================================
#  VIDARA & DOODSTREAM VIEWER BOT V4.5 (LINUX & DOCKER LAUNCHER)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================================================"
echo "   VIDARA & DOODSTREAM VIEWER BOT V4.5 (LINUX / CLOUD DOCKER)"
echo "   Clean Proxy-Only Edition (Zero VPN Daemon / Zero Wireproxy)"
echo "======================================================================"

# Cek Python 3
if ! command -v python3 &> /dev/null; then
    echo "[!] Python 3 belum terpasang. Memasang python3 & pip..."
    sudo apt update && sudo apt install -y python3 python3-pip python3-venv
fi

# Cek dependensi
if ! python3 -c "import playwright, camoufox, curl_cffi, psutil" &> /dev/null; then
    echo "[*] Menginstal library python..."
    pip config set global.break-system-packages true 2>/dev/null || true
    python3 -m pip config set global.break-system-packages true 2>/dev/null || true
    pip install --break-system-packages -r requirements.txt || pip install -r requirements.txt
    python3 -m playwright install chromium firefox || playwright install chromium firefox
fi

echo "[*] Menjalankan Bot Viewer..."
echo "Tekan Ctrl+C untuk berhenti."
echo ""
python3 vidara_bot.py
