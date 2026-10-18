#!/usr/bin/env bash
# ==============================================================================
#  VIDBOT VIEWER BOT LAUNCHER (AUTO VENV DETECTION)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================================================"
echo "   🎬 MENJALANKAN VIDBOT (VIDARA & DOODSTREAM VIEWER BOT)"
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

echo "[*] Menjalankan Bot Viewer..."
echo "Tekan Ctrl+C untuk berhenti."
echo ""
"$PY_BIN" vidara_bot.py
