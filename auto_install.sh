#!/usr/bin/env bash
# ==============================================================================
#  AUTO-INSTALLER: CLOUD WEB DESKTOP & VIDARA BOT V4.5
#  Supports: Ubuntu / Debian / Docker Cloud Sandboxes (amd64 & arm64)
# ==============================================================================
set -e

echo "======================================================================"
echo " 🚀 INSTALLING CLOUD WEB DESKTOP & VIDARA CLEAN BOT SUITE"
echo "======================================================================"

ARCH=$(uname -m)
echo "[*] System Architecture: $ARCH"

# 1. Update OS packages
echo "[*] Step 1/4: Memperbarui dependensi sistem..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update -y
    sudo apt-get install -y curl wget git python3 python3-pip python3-venv xvfb
fi

# 2. Pastikan Docker aktif
echo "[*] Step 2/4: Memeriksa Docker..."
if ! command -v docker &> /dev/null; then
    echo "[*] Memasang Docker Engine..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm -f get-docker.sh
fi

# 3. Jalankan Web Desktop (Webtop XFCE) di Port 3000
echo "[*] Step 3/4: Meluncurkan Web Desktop (Webtop XFCE) di Port 3000..."
if ! docker ps -a | grep -q "webtop"; then
    docker run -d \
      --name=webtop \
      --security-opt seccomp=unconfined \
      -e PUID=1000 \
      -e PGID=1000 \
      -e TZ=Asia/Jakarta \
      -p 3000:3000 \
      -v "$HOME":/config/Desktop/HostHome \
      --shm-size=2gb \
      --restart unless-stopped \
      lscr.io/linuxserver/webtop:ubuntu-xfce
    echo "✅ Container Webtop berhasil diluncurkan!"
else
    echo "ℹ️ Container Webtop sudah ada, memastikan status running..."
    docker start webtop || true
fi

# 4. Install Python Playwright & Browser Dependencies
echo "[*] Step 4/4: Memasang library bot Python & browser..."
pip install --break-system-packages playwright camoufox[geoip] requests[socks] urllib3 psutil pysocks curl_cffi || \
pip install playwright camoufox[geoip] requests[socks] urllib3 psutil pysocks curl_cffi

python3 -m playwright install chromium firefox || true

echo ""
echo "======================================================================"
echo " 🎉 INSTALASI SELESAI & SUKSES!"
echo "======================================================================"
echo " 🖥️ Web Desktop aktif di port: 3000"
echo " 📁 Folder Project ada di Desktop: HostHome"
echo " 🚀 Jalankan bot dengan perintah: cd HostHome && python3 vidara_bot.py"
echo "======================================================================"
