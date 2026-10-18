#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ Fast Multi-Threaded Proxy Scraper & Live Checker for Vibot
Repository: https://github.com/AbyanZainZ/Vibot
Author: AbyanZainZ

Fungsi:
1. Mengunduh puluhan ribu proxy gratis dari 90+ repository GitHub terpercaya.
2. Melakukan tes koneksi super cepat (Multi-threaded Pre-Filter).
3. Hanya menyimpan proxy yang 100% AKTIF (LIVE) ke file 'proxy.txt' & 'proxies.txt'.
4. Bersih: Tidak menyimpan file sampah / proxy mati.
"""

import os
import sys
import time
import re
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from collections import deque
import urllib3
import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Konfigurasi Encoding Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_FILES = [BASE_DIR / "proxy.txt", BASE_DIR / "proxies.txt"]

# Pengaturan Kecepatan & Target
SCRAPE_WORKERS = 30
CHECK_WORKERS = 150
TIMEOUT_CHECK = 3.0
TARGET_CHECK_URL = "http://www.google.com/generate_204"
FALLBACK_CHECK_URL = "http://1.1.1.1/cdn-cgi/trace"
MAX_LIVE_TARGET = 300  # Otomatis selesai setelah menemukan sekian proxy hidup (0 = periksa semua)

# 90+ SUMBER GITHUB RAW PROXY TERBAIK (HTTP & SOCKS5)
GITHUB_SOURCES = [
    ("http", "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/refs/heads/master/http.txt"),
    ("socks5", "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/refs/heads/master/socks5.txt"),
    ("socks4", "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/refs/heads/master/socks4.txt"),
    ("http", "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/refs/heads/main/proxy_files/http_proxies.txt"),
    ("socks5", "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/refs/heads/main/proxy_files/socks5_proxies.txt"),
    ("socks4", "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/refs/heads/main/proxy_files/socks4_proxies.txt"),
    ("http", "https://raw.githubusercontent.com/ObcbO/getproxy/refs/heads/master/file/http.txt"),
    ("http", "https://raw.githubusercontent.com/ObcbO/getproxy/refs/heads/master/file/https.txt"),
    ("socks5", "https://raw.githubusercontent.com/ObcbO/getproxy/refs/heads/master/file/socks5.txt"),
    ("socks4", "https://raw.githubusercontent.com/ObcbO/getproxy/refs/heads/master/file/socks4.txt"),
    ("http", "https://raw.githubusercontent.com/TuanMinPay/live-proxy/refs/heads/master/http.txt"),
    ("socks5", "https://raw.githubusercontent.com/TuanMinPay/live-proxy/refs/heads/master/socks5.txt"),
    ("http", "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/http.txt"),
    ("http", "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/https.txt"),
    ("socks5", "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks5.txt"),
    ("http", "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/http/http.txt"),
    ("http", "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/https/https.txt"),
    ("socks5", "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt"),
    ("http", "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt"),
    ("socks5", "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks5.txt"),
    ("http", "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt"),
    ("socks5", "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks5.txt"),
    ("http", "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt"),
    ("socks5", "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt"),
    ("http", "https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/http.txt"),
    ("http", "https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/https.txt"),
    ("socks5", "https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/socks5.txt"),
    ("http", "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt"),
    ("socks5", "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt"),
    ("http", "https://raw.githubusercontent.com/B4RC0D3-TM/proxy-list/main/HTTP.txt"),
    ("socks5", "https://raw.githubusercontent.com/B4RC0D3-TM/proxy-list/main/SOCKS5.txt"),
    ("http", "https://raw.githubusercontent.com/yemix-zy/proxy-list/main/proxies/http.txt"),
    ("socks5", "https://raw.githubusercontent.com/yemix-zy/proxy-list/main/proxies/socks5.txt"),
    ("http", "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/generated/http_proxies.txt"),
    ("socks5", "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/generated/socks5_proxies.txt"),
    ("http", "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Https.txt"),
    ("socks5", "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks5.txt"),
    ("http", "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt"),
    ("http", "https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt"),
    ("socks5", "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt"),
    ("http", "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt")
]

IP_PORT_RE = re.compile(r'((?:\d{1,3}\.){3}\d{1,3}):(\d{2,5})')

def scrape_single_source(proto, url):
    """Mengambil list proxy dari satu URL GitHub raw."""
    found = []
    try:
        r = requests.get(url, timeout=12, headers={'User-Agent': 'Mozilla/5.0'})
        if r.status_code == 200:
            for match in IP_PORT_RE.finditer(r.text):
                ip, port = match.group(1), match.group(2)
                p_int = int(port)
                # Auto-deteksi port SOCKS
                p_proto = proto
                if p_int in [1080, 1081, 10808, 9050, 1085] and proto == "http":
                    p_proto = "socks5"
                found.append(f"{p_proto}://{ip}:{port}")
    except Exception:
        pass
    return found

def build_requests_proxies(p_url):
    """Membangun kamus proxy requests."""
    if p_url.startswith("socks5://"):
        hp = p_url.split("://", 1)[1]
        return {"http": f"socks5h://{hp}", "https": f"socks5h://{hp}"}
    elif p_url.startswith("socks4://"):
        hp = p_url.split("://", 1)[1]
        return {"http": f"socks4://{hp}", "https": f"socks4://{hp}"}
    else:
        return {"http": p_url, "https": p_url}

def check_single_proxy(p_url):
    """Menguji apakah proxy benar-benar hidup."""
    proxies = build_requests_proxies(p_url)
    t0 = time.perf_counter()
    try:
        r = requests.get(TARGET_CHECK_URL, proxies=proxies, timeout=TIMEOUT_CHECK, allow_redirects=False)
        lat = round((time.perf_counter() - t0) * 1000)
        if r.status_code in (200, 204, 301, 302):
            return True, p_url, lat
        # Fallback check
        r2 = requests.get(FALLBACK_CHECK_URL, proxies=proxies, timeout=TIMEOUT_CHECK, allow_redirects=False)
        lat2 = round((time.perf_counter() - t0) * 1000)
        if r2.status_code in (200, 204, 301, 302):
            return True, p_url, lat2
    except Exception:
        pass
    return False, p_url, 0

def main():
    print("==================================================================")
    print("⚡ FAST PROXY SCRAPER & LIVE CHECKER (VIBOT EDITION)")
    print(f"Sumber: {len(GITHUB_SOURCES)} Repository GitHub Resmi")
    print(f"Target Output: {', '.join([p.name for p in OUTPUT_FILES])}")
    print(f"Target Live Proxy yang Dicari: {MAX_LIVE_TARGET} Proxy")
    print("==================================================================\n")

    # 1. SCRAPING DARI GITHUB
    print("⏳ [1/2] Mengunduh proxy dari sumber GitHub raw...")
    all_raw = set()
    t_start_scrape = time.time()

    with ThreadPoolExecutor(max_workers=SCRAPE_WORKERS) as executor:
        futures = [executor.submit(scrape_single_source, proto, url) for proto, url in GITHUB_SOURCES]
        for f in as_completed(futures):
            res = f.result()
            for p in res:
                all_raw.add(p)

    candidate_list = list(all_raw)
    dur_scrape = time.time() - t_start_scrape
    print(f"✅ Scraping Selesai dalam {dur_scrape:.1f}s!")
    print(f"📊 Berhasil mengumpulkan {len(candidate_list):,} kandidat proxy unik (HTTP & SOCKS5).\n")

    if not candidate_list:
        print("❌ Tidak ada proxy yang berhasil discrape. Periksa koneksi internet.")
        return

    # 2. CHECKING PROXY (HANYA MENYIMPAN YANG LIVE)
    print("⏳ [2/2] Menguji koneksi & memfilter proxy hidup (Live Check)...")
    print(f"[*] Menjalankan {CHECK_WORKERS} thread simultan (Timeout: {TIMEOUT_CHECK}s)...")
    print("Tekan Ctrl+C kapan saja jika jumlah proxy hidup sudah dirasa cukup.\n")

    live_proxies = []
    dead_count = 0
    checked_count = 0
    file_lock = threading.Lock()
    t_start_check = time.time()

    # Bersihkan file output lama agar siap diisi proxy fresh
    for out_p in OUTPUT_FILES:
        with open(out_p, "w", encoding="utf-8") as f:
            f.write("# LIVE VERIFIED PROXIES - AUTO GENERATED BY VIBOT SCRAPER\n")

    def save_live_proxy(p_str):
        with file_lock:
            for out_p in OUTPUT_FILES:
                with open(out_p, "a", encoding="utf-8") as f:
                    f.write(p_str + "\n")

    try:
        with ThreadPoolExecutor(max_workers=CHECK_WORKERS) as executor:
            future_to_proxy = {executor.submit(check_single_proxy, p): p for p in candidate_list}
            for fut in as_completed(future_to_proxy):
                is_alive, p_url, latency = fut.result()
                checked_count += 1

                if is_alive:
                    live_proxies.append(p_url)
                    save_live_proxy(p_url)
                    print(f"🟢 [LIVE #{len(live_proxies)}] {p_url} ({latency}ms)")
                else:
                    dead_count += 1

                # Cetak progres tiap 50 proxy
                if checked_count % 50 == 0:
                    speed = checked_count / max(1, (time.time() - t_start_check))
                    print(f"   ⏱️ Progres: {checked_count:,}/{len(candidate_list):,} | Live: {len(live_proxies)} | Dead: {dead_count:,} | Speed: {speed:.0f} req/s")

                # Berhenti otomatis jika target tercapai
                if MAX_LIVE_TARGET > 0 and len(live_proxies) >= MAX_LIVE_TARGET:
                    print(f"\n🎯 Target {MAX_LIVE_TARGET} proxy aktif berhasil terpenuhi!")
                    break

    except KeyboardInterrupt:
        print("\n\n🛑 Proses dihentikan oleh pengguna.")

    total_dur = time.time() - t_start_check
    print("\n==================================================================")
    print(" 🎉 PROXY SCRAPING & CHECKING SELESAI!")
    print("==================================================================")
    print(f" Total Diperiksa : {checked_count:,} Proxy dalam {total_dur:.1f} detik")
    print(f" Total Live Aktif: {len(live_proxies)} Proxy")
    print(f" File Output     : {', '.join([str(p.name) for p in OUTPUT_FILES])} (Siap dipakai oleh bot!)")
    print("==================================================================")
    print("👉 Kamu bisa langsung menjalankan bot sekarang:")
    print("   Linux: ./start_bot.sh")
    print("   Windows: START_BOT.bat")

if __name__ == "__main__":
    main()
