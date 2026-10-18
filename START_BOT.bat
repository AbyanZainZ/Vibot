@echo off
title Vidara & DoodStream Viewer Bot V4.5 (Clean Proxy-Only)
color 0A
cd /d "%~dp0"

echo ======================================================================
echo    VIDARA & DOODSTREAM VIEWER BOT V4.5 (PROXY-ONLY EDITION)
echo    Cross-Platform: Windows Server & Linux Compatible
echo ======================================================================
echo.

:: Cek Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python belum terpasang atau belum masuk PATH!
    echo Silakan install Python 3.10+ dari python.org (Centang "Add Python to PATH").
    pause
    exit /b
)

:: Cek dependensi
echo [*] Memeriksa dependensi...
python -c "import playwright, camoufox, curl_cffi, psutil" >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Memasang dependensi otomatis...
    pip install -r requirements.txt
    playwright install chromium firefox
    camoufox fetch --geoip
)

echo [*] Menjalankan Vidara Bot...
echo Tekan Ctrl+C untuk menghentikan bot.
echo.
python vidara_bot.py

pause
