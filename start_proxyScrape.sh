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

# Cek Virtual Environment bawaan
if [ -f "$SCRIPT_DIR/venv/bin/python" ]; then
    PY_BIN="$SCRIPT_DIR/venv/bin/python"
    echo "[*] Menggunakan Python Virtual Environment: $PY_BIN"
elif command -v python3 &> /dev/null; then
    PY_BIN="python3"
    echo "[*] Menggunakan System Python 3: $(which python3)"
else
    echo "[!] Python tidak ditemukan! Silakan install python3 terlebih dahulu."
    exit 1
fi

echo "[*] Memulai pencarian & pengujian proxy live..."
echo "Tekan Ctrl+C kapan saja untuk berhenti dan menyimpan hasil yang sudah live."
echo ""
"$PY_BIN" proxy_scraper.py
