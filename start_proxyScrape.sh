#!/usr/bin/env bash
# ==============================================================================
#  VIBOT PROXY SCRAPER & LIVE CHECKER (AUTO VENV DETECTION)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================================================"
echo "   ⚡ MENJALANKAN PROXY SCRAPER & LIVE CHECKER (VIBOT EDITION)"
echo "   📁 Direktori: $SCRIPT_DIR"
echo "======================================================================"

# Cek Virtual Environment bawaan atau python sistem
if [ -f "$SCRIPT_DIR/venv/bin/python" ] && "$SCRIPT_DIR/venv/bin/python" -c "import urllib3" &>/dev/null; then
    PY_BIN="$SCRIPT_DIR/venv/bin/python"
    echo "[*] Menggunakan Python Virtual Environment: $PY_BIN"
elif command -v python3 &> /dev/null; then
    PY_BIN="python3"
    echo "[*] Menggunakan System Python 3: $(which python3)"
elif [ -f "$SCRIPT_DIR/venv/bin/python" ]; then
    PY_BIN="$SCRIPT_DIR/venv/bin/python"
    echo "[*] Menggunakan Python Virtual Environment: $PY_BIN"
else
    echo "[!] Python tidak ditemukan! Silakan install python3 terlebih dahulu."
    exit 1
fi

# Pastikan dependensi terpenuhi
if ! "$PY_BIN" -c "import urllib3, requests" &>/dev/null; then
    echo "[*] Dependensi belum lengkap, menginstall dari requirements.txt..."
    "$PY_BIN" -m pip install -r "$SCRIPT_DIR/requirements.txt" 2>/dev/null || \
    pip3 install -r "$SCRIPT_DIR/requirements.txt" --break-system-packages 2>/dev/null || \
    pip install -r "$SCRIPT_DIR/requirements.txt" 2>/dev/null || true
fi

echo "[*] Memulai pencarian & pengujian proxy live..."
echo "Tekan Ctrl+C kapan saja untuk berhenti dan menyimpan hasil yang sudah live."
echo ""
"$PY_BIN" proxy_scraper.py
