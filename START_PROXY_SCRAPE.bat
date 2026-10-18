@echo off
title Vibot Proxy Scraper & Live Checker
color 0B
cd /d "%~dp0"

echo ======================================================================
echo    ⚡ VIBOT PROXY SCRAPER & LIVE CHECKER (WINDOWS EDITION)
echo ======================================================================
echo.

:: Cek Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python belum terpasang atau belum masuk PATH!
    echo Silakan install Python 3.10+ dari python.org.
    pause
    exit /b
)

:: Cek dependensi
python -c "import requests, urllib3" >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Memasang dependensi otomatis...
    pip install requests urllib3 pysocks
)

echo [*] Menjalankan Proxy Scraper & Live Checker...
echo Tekan Ctrl+C kapan saja untuk berhenti dan menyimpan proxy yang sudah live.
echo.
python proxy_scraper.py

pause
