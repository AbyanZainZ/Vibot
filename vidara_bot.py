#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DoodStream and Vidara Multi-Proxy Viewer Bot V3.9 (Standalone CLI / Docker Edition)
Converted from Vidara_DoodStream_ProxyTXT-V3.9.ipynb
"""

import os
import sys
import time
import json
import math
import random
import re
import shutil
import asyncio
import datetime
import threading
from pathlib import Path

# Fix Windows console UTF-8 encoding support
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Safe terminal dummy for IPython display if running outside notebook
try:
    from IPython.display import display, HTML
except ImportError:
    class DummyHandle:
        def update(self, obj):
            pass
    def display(obj, display_id=False):
        return DummyHandle()
    def HTML(content):
        return content


# ================= 1. DYNAMIC CONFIGURATION LOADER =================
BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"

# Default fallback values
Engine_Mode = "Camoufox (Anti-Detect & Stealth - Rekomendasi)"
Headless_Mode = True
Tampilkan_System_Dashboard = True
Interval_Refresh_Dashboard_Detik = 3
Cetak_Log_Dashboard_Tiap_Detik = 45
Maksimal_Browser_Simultan = 2
Jeda_Mikro_Start_Simultan = 2.0
Durasi_Tonton_Detik = 180
Mode_Eksekusi = "LOOP TERUS-MENERUS (24 Jam Non-Stop)"
Jeda_Antar_Putaran_Detik = 10
Maksimal_Retry_Proxy_Gagal = 5
Nama_File_Proxy_Lokal = "proxies.txt"
Default_Protokol_Cadangan = "HTTP"
Nama_File_Link_Lokal = "link.txt"

if CONFIG_PATH.exists():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as cf:
            cfg = json.load(cf)
        if "link_file" in cfg:
            Nama_File_Link_Lokal = cfg["link_file"].strip()
        if "engine_mode" in cfg:
            if "playwright" in cfg["engine_mode"].lower():
                Engine_Mode = "Playwright Standar (Chromium)"
            else:
                Engine_Mode = "Camoufox (Anti-Detect & Stealth - Rekomendasi)"
        if "headless_mode" in cfg:
            Headless_Mode = bool(cfg["headless_mode"])
        if "max_concurrent_browsers" in cfg:
            Maksimal_Browser_Simultan = int(cfg["max_concurrent_browsers"])
        if "start_stagger_delay_sec" in cfg:
            Jeda_Mikro_Start_Simultan = float(cfg["start_stagger_delay_sec"])
        if "watch_duration_sec" in cfg:
            Durasi_Tonton_Detik = int(cfg["watch_duration_sec"])
        if "execution_mode" in cfg:
            Mode_Eksekusi = "LOOP TERUS-MENERUS (24 Jam Non-Stop)" if "loop" in cfg["execution_mode"].lower() else "HANYA 1 KALI PUTARAN"
        if "round_delay_sec" in cfg:
            Jeda_Antar_Putaran_Detik = int(cfg["round_delay_sec"])
        if "max_proxy_retries" in cfg:
            Maksimal_Retry_Proxy_Gagal = int(cfg["max_proxy_retries"])
        if "proxy_pool" in cfg:
            Nama_File_Proxy_Lokal = cfg["proxy_pool"].get("proxy_file", "proxies.txt")
            raw_proto = cfg["proxy_pool"].get("default_protocol", "HTTP").strip().lower()
            if "socks5" in raw_proto:
                Default_Protokol_Cadangan = "SOCKS5"
            elif "socks4" in raw_proto:
                Default_Protokol_Cadangan = "SOCKS4"
            else:
                Default_Protokol_Cadangan = "HTTP"
        print(f"✅ Berhasil memuat config.json | File Proxy: {Nama_File_Proxy_Lokal} | Default Protokol: {Default_Protokol_Cadangan}")
    except Exception as e:
        print(f"⚠️ Gagal membaca config.json ({e}), menggunakan konfigurasi default.")

# ================= 2. LOAD TARGET LINKS (DARI LINK.TXT) =================
target_urls = []
link_candidates = [
    BASE_DIR / Nama_File_Link_Lokal,
    Path(Nama_File_Link_Lokal),
    BASE_DIR / "link.txt",
    BASE_DIR / "links.txt",
    Path("link.txt"),
    Path("links.txt"),
]

for lp in link_candidates:
    if lp.exists() and lp.is_file():
        with open(lp, "r", encoding="utf-8", errors="ignore") as lf:
            for line in lf:
                l_str = line.strip()
                if l_str and not l_str.startswith("#") and l_str.startswith(("http://", "https://")):
                    target_urls.append(l_str)
        if target_urls:
            print(f"📖 Membaca {len(target_urls)} target link dari file: {lp.resolve()}")
            break

# Fallback jika link.txt belum ada / kosong
if not target_urls:
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as cf:
                cfg = json.load(cf)
            if "target_urls" in cfg and cfg["target_urls"]:
                target_urls = [u.strip() for u in cfg["target_urls"] if u.strip() and u.strip().startswith(("http://", "https://"))]
        except Exception:
            pass

if not target_urls:
    print(f"⚠️ Peringatan: Tidak ada link ditemukan di {Nama_File_Link_Lokal}! Silakan isi link video ke dalam file {Nama_File_Link_Lokal} (1 baris per link).")

# Windows Anti-Sleep Protection
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001 | 0x00000040)
        print("🛡️ [Windows Anti-Sleep] Sistem Windows dicegah sleep / suspend.")
    except Exception:
        pass

print("==================================================================")
print("🎬 VIDARA & DOODSTREAM BOT V4.5 (CLEAN PROXY-ONLY EDITION)")
print(f"Platform: {sys.platform.upper()} | Engine: {Engine_Mode}")
print(f"Simultan: {Maksimal_Browser_Simultan} Browser | Target Watch: {Durasi_Tonton_Detik}s")
print(f"Total Target Video: {len([u for u in target_urls if u])} Links")
print("==================================================================")
# ================= 2. PROXY PARSER =================

Sumber_Proxy = "Load dari File Lokal / Drive"
Nama_File_Proxy_Lokal = "proxies.txt"
Custom_Path_Proxy = ""
Default_Protokol_Cadangan = "HTTP"
Rotasi_Proxy = "Random (Acak Tiap Request)"

Input_Proxy_Manual = '''
# Contoh format bebas (otomatis dikenali):
# http://95.66.138.21:8880
# socks5://101.32.213.44:1080
# 123.45.67.89:8080:username:password
'''

import re
import os
from pathlib import Path

def parse_proxy_line(raw_line, default_protocol='http'):
    """
    Universal Multi-Format Proxy Parser.
    Mendukung format:
      - ip:port
      - ip:port:user:pass
      - user:pass@ip:port
      - user:pass:ip:port
      - Separator: ':', ';', '|', ',', '\t', space
      - Protocol prefix: http://, https://, socks5://, socks4://
    """
    line = raw_line.strip()
    if not line or line.startswith(('#', '//')):
        return None

    proto = default_protocol.lower().replace('://', '')
    if '://' in line:
        parts = line.split('://', 1)
        proto = parts[0].lower().strip()
        line = parts[1].strip()

    # Format user:pass@host:port atau host:port@user:pass
    if '@' in line:
        p1, p2 = line.split('@', 1)
        def is_hp(s):
            chunks = [c for c in re.split(r'[:|;,\t\s]+', s.strip()) if c]
            return len(chunks) == 2 and chunks[1].isdigit()

        if is_hp(p2): # user:pass@host:port
            auth_part = p1
            hp = [c for c in re.split(r'[:|;,\t\s]+', p2.strip()) if c]
            auth = auth_part.split(':', 1)
            return {
                'host': hp[0], 'port': int(hp[1]), 'protocol': proto,
                'user': auth[0], 'pass': auth[1] if len(auth) > 1 else ''
            }
        elif is_hp(p1): # host:port@user:pass
            hp = [c for c in re.split(r'[:|;,\t\s]+', p1.strip()) if c]
            auth = p2.split(':', 1)
            return {
                'host': hp[0], 'port': int(hp[1]), 'protocol': proto,
                'user': auth[0], 'pass': auth[1] if len(auth) > 1 else ''
            }

    # Split berdasarkan : | ; , atau whitespace
    parts = [p.strip() for p in re.split(r'[:|;,\t\s]+', line) if p.strip()]
    if len(parts) == 2:
        if parts[1].isdigit():
            return {'host': parts[0], 'port': int(parts[1]), 'protocol': proto, 'user': None, 'pass': None}
    elif len(parts) >= 4:
        if parts[1].isdigit(): # host:port:user:pass
            return {'host': parts[0], 'port': int(parts[1]), 'protocol': proto, 'user': parts[2], 'pass': ':'.join(parts[3:])}
        elif parts[3].isdigit(): # user:pass:host:port
            return {'host': parts[2], 'port': int(parts[3]), 'protocol': proto, 'user': parts[0], 'pass': parts[1]}

    # Fallback pencarian IP:PORT regex
    ip_match = re.search(r'(\b(?:\d{1,3}\.){3}\d{1,3}\b)[:|;,\s]+(\d{2,5})', line)
    if ip_match:
        return {'host': ip_match.group(1), 'port': int(ip_match.group(2)), 'protocol': proto, 'user': None, 'pass': None}

    return None

class ProxyItem:
    def __init__(self, host, port, protocol='http', user=None, password=None):
        self.host = str(host).strip()
        self.port = int(port)
        self.protocol = protocol.lower().replace('://', '')
        self.user = user
        self.password = password
        self.fail_count = 0
        self.is_alive = True

    def to_playwright(self):
        proto = self.protocol if self.protocol in ['http', 'https', 'socks5'] else 'http'
        cfg = {'server': f"{proto}://{self.host}:{self.port}"}
        if self.user and self.password:
            cfg['username'] = str(self.user)
            cfg['password'] = str(self.password)
        return cfg

    def __str__(self):
        auth = f"{self.user}:{self.password}@" if self.user and self.password else ""
        return f"{self.protocol}://{auth}{self.host}:{self.port}"

    def __repr__(self):
        return self.__str__()

raw_proxy_lines = []
active_source_label = Sumber_Proxy

if Sumber_Proxy == "Upload File .txt Sekarang (Widget)":
    try:
        from google.colab import files
        print("📁 Silakan klik tombol 'Choose Files' di bawah untuk mengunggah file .txt proxy kamu:")
        uploaded = files.upload()
        if uploaded:
            for fn, content in uploaded.items():
                print(f"   ✅ File '{fn}' berhasil diunggah ({len(content):,} bytes)!")
                raw_proxy_lines = content.decode('utf-8', errors='ignore').splitlines()
                active_source_label = f"Uploaded ({fn})"
                break
        else:
            print("⚠️ Tidak ada file yang diunggah. Beralih ke fallback file lokal...")
            Sumber_Proxy = "Load dari File Lokal / Drive"
    except ImportError:
        print("ℹ️ Widget google.colab.files hanya aktif di Colab. Menggunakan mode file lokal...")
        Sumber_Proxy = "Load dari File Lokal / Drive"

if Sumber_Proxy == "Load dari File Lokal / Drive":
    target_path = Custom_Path_Proxy.strip() if ('Custom_Path_Proxy' in globals() and Nama_File_Proxy_Lokal == "Custom Path" and Custom_Path_Proxy.strip()) else Nama_File_Proxy_Lokal
    base_dir = Path(__file__).resolve().parent
    candidate_paths = [
        Path(target_path),
        base_dir / target_path,
        Path('.') / target_path,
        Path('proxy.txt'),
        Path('proxies.txt'),
        base_dir / 'proxy.txt',
        base_dir / 'proxies.txt',
        Path('/content') / target_path,
        Path('/content/drive/MyDrive') / target_path,
        Path('/content/drive/MyDrive/Vidara_Proxies') / target_path,
    ]
    found = False
    for p in candidate_paths:
        if p.exists() and p.is_file():
            print(f"📖 Membaca proxy dari file lokal: {p.resolve()}")
            with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                raw_proxy_lines = f.readlines()
            found = True
            active_source_label = f"Local File ({p.name})"
            break
    if not found:
        print(f"⚠️ File proxy '{target_path}' tidak ditemukan di lokasi standar.")

elif Sumber_Proxy == "Paste Manual di Bawah":
    raw_proxy_lines = Input_Proxy_Manual.splitlines()
    active_source_label = "Paste Manual"

# Parse seluruh baris proxy
loaded_proxies = []
default_proto = Default_Protokol_Cadangan if 'Default_Protokol_Cadangan' in globals() else (Default_Protokol if 'Default_Protokol' in globals() else 'HTTP')
for line in raw_proxy_lines:
    parsed = parse_proxy_line(line, default_protocol=default_proto)
    if parsed:
        p_obj = ProxyItem(
            host=parsed['host'],
            port=parsed['port'],
            protocol=parsed['protocol'],
            user=parsed['user'],
            password=parsed['pass']
        )
        loaded_proxies.append(p_obj)

print("="*65)
if loaded_proxies:
    n_auth = sum(1 for p in loaded_proxies if p.user and p.password)
    n_http = sum(1 for p in loaded_proxies if p.protocol in ['http', 'https'])
    n_socks = sum(1 for p in loaded_proxies if 'socks' in p.protocol)
    print(f"🎉 SUKSES MEMUAT {len(loaded_proxies):,} PROXY AKTIF!")
    print(f"Sumber: {active_source_label}")
    print(f"Rincian: {n_http} HTTP/HTTPS | {n_socks} SOCKS | {n_auth} Dengan Autentikasi (User/Pass)")
    print(f"Contoh Proxy Pertama: {loaded_proxies[0]}")
    if len(loaded_proxies) > 1:
        print(f"Contoh Proxy Terakhir: {loaded_proxies[-1]}")
else:
    if Sumber_Proxy == "Direct (Tanpa Proxy)":
        print("🌐 Mode: DIRECT (Tanpa Proxy). Bot akan memutar video menggunakan koneksi internet langsung.")
    else:
        print("⚠️ Tidak ada proxy valid yang berhasil dimuat. Menggunakan mode Direct (Tanpa Proxy).")
print("="*65)

# ================= 3. PROXY & UA POOLS =================
import random
import threading
import time

class UniversalProxyPool:
    def __init__(self, proxy_list=None, rotation_mode="Random (Acak Tiap Request)"):
        self.proxies = list(proxy_list) if proxy_list else []
        self.dead_proxies = set()
        self.rotation_mode = rotation_mode
        self.index = 0
        self._lock = threading.Lock()

    def get_proxy(self):
        with self._lock:
            if not self.proxies:
                return None
            alive = [p for p in self.proxies if p not in self.dead_proxies]
            if not alive:
                print("⚠️ Semua proxy dalam pool sempat gagal, mereset daftar proxy mati...")
                self.dead_proxies.clear()
                alive = list(self.proxies)

            if "Random" in self.rotation_mode or "Acak" in self.rotation_mode:
                return random.choice(alive)
            elif "Sticky" in self.rotation_mode:
                return alive[0]
            else: # Round-Robin
                p = alive[self.index % len(alive)]
                self.index = (self.index + 1) % len(alive)
                return p

    def mark_dead(self, proxy, reason=""):
        if not proxy:
            return
        with self._lock:
            proxy.fail_count += 1
            if proxy.fail_count >= 2:
                self.dead_proxies.add(proxy)
                alive_count = len(self.proxies) - len(self.dead_proxies)
                print(f"💀 [Blacklist Proxy] {proxy} ditandai nonaktif (Sisa {alive_count} proxy hidup). Alasan: {reason[:40]}")

    def stats(self):
        with self._lock:
            tot = len(self.proxies)
            alive = tot - len(self.dead_proxies)
            n_http = sum(1 for p in self.proxies if p.protocol in ['http', 'https'])
            n_socks = sum(1 for p in self.proxies if 'socks' in p.protocol)
            return tot, alive, n_http, n_socks

    def __len__(self):
        return len(self.proxies)

USER_AGENTS_DB_V3 = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.86 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.70 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.117 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.92 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.70 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.101 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.71 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.138 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.120 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.120 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.89 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.183 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.127 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.142 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.113 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.208 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.91 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.124 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.87 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.129 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.185 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.225 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.2903.86', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.2903.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.2849.80', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.2849.56', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.2792.89', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.2792.65', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.2739.79', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.2739.54', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.2651.98', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.2651.74', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.2592.102', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.2592.81', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.2535.92', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.2535.67', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.2478.97', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.2420.97', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.86 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.117 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.101 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.138 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.120 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.183 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.142 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.208 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.117 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.138 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.86 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 15_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:133.0) Gecko/20100101 Firefox/133.0', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:132.0) Gecko/20100101 Firefox/132.0', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:131.0) Gecko/20100101 Firefox/131.0', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:130.0) Gecko/20100101 Firefox/130.0', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:129.0) Gecko/20100101 Firefox/129.0', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 OPR/115.0.0.0', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 OPR/114.0.5282.185', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/113.0.5230.86', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 OPR/112.0.5197.53', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 OPR/111.0.5168.61', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 OPR/114.0.5282.185', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/113.0.5230.86', 'Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.81 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 14; SM-S928U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.107 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 14; SM-S926B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.86 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 14; SM-S921B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.100 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.107 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 14; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.70 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 14; SM-A546B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.107 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 14; SM-A346B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.127 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 14; SM-A155F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.70 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.182 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.165 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 14; SM-F946B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.86 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 14; SM-F731B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.100 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/26.0 Chrome/122.0.0.0 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/25.0 Chrome/121.0.0.0 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 14; SM-A546B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/25.0 Chrome/121.0.0.0 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/24.0 Chrome/118.0.0.0 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 13; SM-A536B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/23.0 Chrome/115.0.0.0 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.81 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.107 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 14; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.100 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 14; Pixel 7a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.127 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 13; Pixel 6 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.182 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 13; Pixel 6a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.165 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 14; 23127PN0CG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.81 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 14; 2306EPN60G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.107 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 14; 23117PN60G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.100 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 13; 2210132G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.103 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 14; CPH2581) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.81 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 14; CPH2449) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.86 Mobile Safari/537.36', 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1', 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1', 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1', 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1', 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1', 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1', 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1', 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1', 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1', 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Mobile/15E148 Safari/604.1', 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1', 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1', 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1', 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1', 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/131.0.6778.85 Mobile/15E148 Safari/604.1', 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/129.0.6668.75 Mobile/15E148 Safari/604.1', 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/127.0.6533.82 Mobile/15E148 Safari/604.1', 'Mozilla/5.0 (iPad; CPU OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1', 'Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1', 'Mozilla/5.0 (iPad; CPU OS 17_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1', 'Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1', 'Mozilla/5.0 (iPad; CPU OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1', 'Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.86 Safari/537.36', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.117 Safari/537.36', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.101 Safari/537.36', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0', 'Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0', 'Mozilla/5.0 (Linux; Android 14; SM-A556B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.81 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 14; SM-A356B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.107 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/27.0 Chrome/125.0.0.0 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 14; Pixel 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.81 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 14; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.107 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 14; 2407FPN8EG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.81 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 14; V2324A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.86 Mobile Safari/537.36', 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1.1 Mobile/15E148 Safari/604.1', 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.7 Mobile/15E148 Safari/604.1', 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/131.0.6778.85 Mobile/15E148 Safari/604.1', 'Mozilla/5.0 (iPad; CPU OS 18_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1.1 Mobile/15E148 Safari/604.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.2903.86', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.2849.68', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.2903.86']

def detect_ua_device_profile(ua):
    """Mendeteksi tipe device (Mobile vs Desktop) dan browser untuk emulasi 100% konsisten agar tidak terdeteksi 'Unknown'."""
    ua_low = ua.lower()
    is_iphone = 'iphone' in ua_low
    is_ipad = 'ipad' in ua_low
    is_android = 'android' in ua_low and 'mobile' in ua_low
    is_mobile = is_iphone or is_android
    
    if is_iphone:
        viewport = random.choice([{'width': 393, 'height': 852}, {'width': 390, 'height': 844}, {'width': 430, 'height': 932}])
        scale = 3.0
    elif is_ipad:
        viewport = random.choice([{'width': 820, 'height': 1180}, {'width': 834, 'height': 1194}])
        scale = 2.0
    elif is_android:
        viewport = random.choice([{'width': 412, 'height': 915}, {'width': 360, 'height': 800}, {'width': 384, 'height': 854}])
        scale = 2.6
    else:
        viewport = random.choice([{'width': 1366, 'height': 768}, {'width': 1920, 'height': 1080}, {'width': 1536, 'height': 864}])
        scale = 1.0
        
    return {
        'is_mobile': is_mobile,
        'is_ipad': is_ipad,
        'has_touch': is_mobile or is_ipad,
        'viewport': viewport,
        'device_scale_factor': scale
    }

class UserAgentPool:
    def __init__(self, ua_list=None, rotation_mode="Random (Acak)"):
        self.rotation_mode = rotation_mode
        self.uas = ua_list or USER_AGENTS_DB_V3
        self.index = 0
        self._lock = threading.Lock()

    def get_ua(self):
        with self._lock:
            if not self.uas:
                return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            if self.rotation_mode == "Non-Aktif":
                return self.uas[0]
            if self.rotation_mode == "Random (Acak)":
                return random.choice(self.uas)
            ua = self.uas[self.index % len(self.uas)]
            self.index = (self.index + 1) % len(self.uas)
            return ua

    def __len__(self):
        return len(self.uas)


proxy_pool = UniversalProxyPool(
    proxy_list=loaded_proxies if 'loaded_proxies' in globals() else [],
    rotation_mode=Rotasi_Proxy if 'Rotasi_Proxy' in globals() else "Random (Acak Tiap Request)"
)

ua_pool = UserAgentPool(
    ua_list=USER_AGENTS_DB_V3,
    rotation_mode="Random (Acak)"
)

tot, alive, n_http, n_socks = proxy_pool.stats()
print(f"✅ [V3.9 Init Selesai] {alive:,} Proxy Siap Pakai ({n_http:,} HTTP, {n_socks:,} SOCKS5) | {len(ua_pool)} User-Agent Resmi Stealth!")

# ================= 4. PLAYWRIGHT ENGINE =================
import asyncio
import datetime
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
import time
import psutil

CHROMIUM_ARGS = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-software-rasterizer",
    "--disable-accelerated-2d-canvas",
    "--no-first-run",
    "--no-zygote",
    "--mute-audio",
    "--disable-background-timer-throttling",
    "--disable-backgrounding-occluded-windows",
    "--disable-renderer-backgrounding",
    "--disable-background-networking",
    "--disable-default-apps",
    "--disable-extensions",
    "--disable-sync",
    "--disable-translate",
    "--disable-ipc-flooding-protection",
    "--js-flags=--max-old-space-size=256",
    "--disable-features=AudioServiceOutOfProcess,IsolateOrigins,site-per-process,Translate,OptimizationHints,MediaRouter",
    "--disable-component-update"
]

CAMOUFOX_ARGS = [
    "--mute-audio",
    "--disable-gpu"
]

BROWSER_ARGS = CHROMIUM_ARGS

# ==============================================================================
# SISTEM MONITORING RESOURCE & BANDWIDTH KECEPATAN STREAMING
# ==============================================================================
class SystemTracker:
    def __init__(self):
        self.t_start = time.time()
        self.last_time = self.t_start
        try:
            net = psutil.net_io_counters()
            self.init_bytes_recv = net.bytes_recv
            self.init_bytes_sent = net.bytes_sent
            self.last_bytes_recv = net.bytes_recv
            self.last_bytes_sent = net.bytes_sent
        except Exception:
            self.init_bytes_recv = 0
            self.init_bytes_sent = 0
            self.last_bytes_recv = 0
            self.last_bytes_sent = 0
        # Prime cpu usage calculation
        psutil.cpu_percent(interval=None)

    def sample(self):
        now = time.time()
        dt = max(1e-3, now - self.last_time)
        try:
            net = psutil.net_io_counters()
            recv_cur = net.bytes_recv
            sent_cur = net.bytes_sent
        except Exception:
            recv_cur = self.last_bytes_recv
            sent_cur = self.last_bytes_sent

        dl_bytes_delta = max(0, recv_cur - self.last_bytes_recv)
        up_bytes_delta = max(0, sent_cur - self.last_bytes_sent)

        dl_speed_sec = dl_bytes_delta / dt
        up_speed_sec = up_bytes_delta / dt

        self.last_bytes_recv = recv_cur
        self.last_bytes_sent = sent_cur
        self.last_time = now

        total_dl = max(0, recv_cur - self.init_bytes_recv)
        total_up = max(0, sent_cur - self.init_bytes_sent)

        cpu_pct = psutil.cpu_percent(interval=None)
        try:
            vm = psutil.virtual_memory()
            ram_pct = vm.percent
            ram_used_gb = (vm.total - vm.available) / (1024**3)
            ram_total_gb = vm.total / (1024**3)
        except Exception:
            ram_pct, ram_used_gb, ram_total_gb = 0, 0, 0

        try:
            drive_path = "/content/drive/MyDrive" if os.path.exists("/content/drive/MyDrive") else "/content"
            drive_free_gb = shutil.disk_usage(drive_path).free / (1024**3)
        except Exception:
            drive_free_gb = 0.0

        def fmt_bytes(b):
            if b >= 1024**3:
                return f"{b / (1024**3):.2f} GB"
            elif b >= 1024**2:
                return f"{b / (1024**2):.2f} MB"
            elif b >= 1024:
                return f"{b / 1024:.2f} KB"
            return f"{b:.0f} B"

        def fmt_speed(bps):
            if bps >= 1024**2:
                return f"{bps / (1024**2):.2f} MB/s"
            elif bps >= 1024:
                return f"{bps / 1024:.2f} KB/s"
            return f"{bps:.0f} B/s"

        return {
            "cpu_pct": cpu_pct,
            "ram_pct": ram_pct,
            "ram_used_gb": ram_used_gb,
            "ram_total_gb": ram_total_gb,
            "dl_speed": fmt_speed(dl_speed_sec),
            "up_speed": fmt_speed(up_speed_sec),
            "total_dl": fmt_bytes(total_dl),
            "total_up": fmt_bytes(total_up),
            "drive_free_gb": f"{drive_free_gb:.2f} GB"
        }

    def format_box(self, title="LIVE PARALLEL DASHBOARD"):
        s = self.sample()
        return (
            "="*65 + "\n" +
            f"🔥 {title} [{timestamp()}] 🔥\n" +
            f"CPU USAGE    = {s['cpu_pct']:.1f} %\n" +
            f"RAM USAGE    = {s['ram_used_gb']:.2f} GB / {s['ram_total_gb']:.1f} GB ({s['ram_pct']} %)\n" +
            f"DL BANDWIDTH = {s['total_dl']} (Total Sesi Ini)\n" +
            f"UP BANDWIDTH = {s['total_up']} (Total Sesi Ini)\n" +
            f"DRIVE FREE   = {s['drive_free_gb']}\n" +
            f"DL SPEED     = {s['dl_speed']}\n" +
            f"UP SPEED     = {s['up_speed']}\n" +
            "="*65
        )

    def print_dashboard_box(self, title="LIVE PARALLEL DASHBOARD"):
        print(self.format_box(title))

    def get_html_dashboard(self, title="LIVE PARALLEL DASHBOARD"):
        s = self.sample()
        cpu_col = "#00e676" if s['cpu_pct'] < 60 else ("#ffd600" if s['cpu_pct'] < 85 else "#ff5252")
        ram_col = "#00e5ff" if s['ram_pct'] < 75 else "#ff5252"
        ref_sec = Interval_Refresh_Dashboard_Detik if 'Interval_Refresh_Dashboard_Detik' in globals() else 3
        net_mode_label = Mode_Jaringan if 'Mode_Jaringan' in globals() else "Proxy/VPN"
        if len(net_mode_label) > 28:
            net_mode_label = net_mode_label[:28] + "..."

        return f"""
        <div style="background: #070f1a; color: #e0f2fe; padding: 16px 20px; border-radius: 12px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, monospace; max-width: 880px; border: 1px solid #1a3a5c; box-shadow: 0 4px 20px rgba(0, 229, 255, 0.08); margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1a3a5c; padding-bottom: 10px; margin-bottom: 14px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="color: #00e5ff; font-weight: bold; font-size: 15px; letter-spacing: 0.5px;">⚡ {title}</span>
                    <span style="background: #0d2035; color: #90caf9; padding: 2px 8px; border-radius: 12px; font-size: 11px; border: 1px solid #1a3a5c;">{net_mode_label}</span>
                </div>
                <span style="background: #004d2a; color: #00e676; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: bold; font-family: monospace;">🟢 LIVE ({ref_sec}s) • {timestamp()}</span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 10px;">
                <div style="background: #0d2035; padding: 10px 14px; border-radius: 8px; border: 1px solid #1a3a5c; border-left: 4px solid {cpu_col};">
                    <div style="font-size: 10px; color: #90caf9; margin-bottom: 2px; font-weight: 600;">CPU USAGE</div>
                    <div style="font-size: 20px; font-weight: bold; color: {cpu_col}; font-family: monospace;">{s['cpu_pct']:.1f} %</div>
                </div>
                <div style="background: #0d2035; padding: 10px 14px; border-radius: 8px; border: 1px solid #1a3a5c; border-left: 4px solid {ram_col};">
                    <div style="font-size: 10px; color: #90caf9; margin-bottom: 2px; font-weight: 600;">RAM USAGE</div>
                    <div style="font-size: 17px; font-weight: bold; color: {ram_col}; font-family: monospace;">{s['ram_used_gb']:.2f} / {s['ram_total_gb']:.1f} GB <span style="font-size: 11px; color: #90caf9;">({s['ram_pct']}%)</span></div>
                </div>
                <div style="background: #0d2035; padding: 10px 14px; border-radius: 8px; border: 1px solid #1a3a5c; border-left: 4px solid #00e5ff;">
                    <div style="font-size: 10px; color: #90caf9; margin-bottom: 2px; font-weight: 600;">DL SPEED</div>
                    <div style="font-size: 20px; font-weight: bold; color: #00e5ff; font-family: monospace;">{s['dl_speed']}</div>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
                <div style="background: #0d2035; padding: 8px 14px; border-radius: 8px; border: 1px solid #1a3a5c; border-left: 4px solid #b388ff;">
                    <div style="font-size: 10px; color: #90caf9; font-weight: 600;">UP SPEED</div>
                    <div style="font-size: 15px; font-weight: bold; color: #b388ff; font-family: monospace;">{s['up_speed']}</div>
                </div>
                <div style="background: #0d2035; padding: 8px 14px; border-radius: 8px; border: 1px solid #1a3a5c; border-left: 4px solid #00e676;">
                    <div style="font-size: 10px; color: #90caf9; font-weight: 600;">DL BANDWIDTH (TOTAL)</div>
                    <div style="font-size: 15px; font-weight: bold; color: #00e676; font-family: monospace;">{s['total_dl']}</div>
                </div>
                <div style="background: #0d2035; padding: 8px 14px; border-radius: 8px; border: 1px solid #1a3a5c; border-left: 4px solid #ffd600;">
                    <div style="font-size: 10px; color: #90caf9; font-weight: 600;">DRIVE FREE</div>
                    <div style="font-size: 15px; font-weight: bold; color: #ffd600; font-family: monospace;">{s['drive_free_gb']}</div>
                </div>
            </div>
        </div>
        """

global_tracker = SystemTracker()

def timestamp():
    return datetime.datetime.now().strftime("%H:%M:%S")

def normalize_stream_url(url):
    """
    Normalisasi URL target (DoodStream / Playmogo dan Vidara) ke mode embed player (/e/<filecode>).
    Mendukung:
    - DoodStream mirrors: playmogo.com, doodstream.com, dood.to, dood.so, dood.wf, dood.cx,
      dood.sh, dood.watch, dood.ws, doods.pro, dood.re, ds2play.com, doply.net, do0od.com, dll.
      /d/<filecode> -> /e/<filecode>
    - Vidara: vidara.so, vidara.to
      /v/<filecode> -> /e/<filecode>
    """
    u = url.strip()
    if not u:
        return u

    is_vidara = any(v in u.lower() for v in ['vidara.to', 'vidara.so'])
    
    match = re.search(r'/(?:d|e|v)/([a-zA-Z0-9_-]+)', u)
    if match:
        file_code = match.group(1)
        from urllib.parse import urlparse
        parsed = urlparse(u)
        scheme = parsed.scheme or "https"
        netloc = parsed.netloc or "playmogo.com"
        if is_vidara:
            netloc = "vidara.to"
        return f"{scheme}://{netloc}/e/{file_code}"

    if is_vidara:
        return u.replace("vidara.so", "vidara.to")
    return u

def detect_platform(url):
    u = url.lower()
    if any(k in u for k in ['playmogo', 'doodstream', 'dood.', 'doods.', 'ds2play', 'doply', 'do0od', 'cloudatacdn']):
        return "DoodStream"
    elif any(k in u for k in ['vidara']):
        return "Vidara"
    return "Universal" 

async def human_curve_move(page, start_x, start_y, target_x, target_y, steps=15):
    ctrl_x = (start_x + target_x) / 2 + random.randint(-40, 40)
    ctrl_y = (start_y + target_y) / 2 + random.randint(-40, 40)
    for step in range(1, steps + 1):
        t = step / steps
        x = (1 - t)**2 * start_x + 2 * (1 - t) * t * ctrl_x + t**2 * target_x
        y = (1 - t)**2 * start_y + 2 * (1 - t) * t * ctrl_y + t**2 * target_y
        await page.mouse.move(x, y)
        await asyncio.sleep(random.uniform(0.01, 0.03))

async def watch_playback(task, proxy_pool, ua_pool, engine_type="camoufox", headless_mode=True, target_watch_sec=180, max_proxy_retries=5):
    url = normalize_stream_url(task["url"])
    platform = detect_platform(task["url"])
    retry_count = 0

    while retry_count < max_proxy_retries:
        proxy = proxy_pool.get_proxy()
        ua = ua_pool.get_ua()
        profile = detect_ua_device_profile(ua)
        pw_proxy = proxy.to_playwright() if proxy else None
        proxy_label = f"{proxy}" if proxy else "Direct (No Proxy)"

        heartbeat_count = 0
        view_counted = False
        dood_pass_unlocked = False
        dood_stream_active = False
        vidara_stream_active = False
        page_title = task.get("title", "")
        browser_obj = None
        pw_instance = None

        try:
            if engine_type == "camoufox":
                from camoufox.async_api import AsyncCamoufox
                # Camoufox hanya mendukung OS desktop internal: 'windows', 'macos', 'linux'
                if "mac" in ua.lower() and "iphone" not in ua.lower() and "ipad" not in ua.lower():
                    camoufox_os = "macos"
                elif "linux" in ua.lower() and "android" not in ua.lower():
                    camoufox_os = "linux"
                else:
                    camoufox_os = "windows"

                # Auto-heal BadStatusLine SOCKS proxy
                use_geoip = False
                try:
                    browser_cm = AsyncCamoufox(
                        headless=headless_mode,
                        os=camoufox_os,
                        args=CAMOUFOX_ARGS,
                        proxy=pw_proxy,
                        geoip=use_geoip
                    )
                    browser_obj = await browser_cm.__aenter__()
                except Exception as b_err:
                    b_err_str = str(b_err)
                    if "BadStatusLine" in b_err_str or "\x05" in b_err_str or "0x05" in b_err_str:
                        if proxy and proxy.protocol != "socks5":
                            print(f"[{task['id']}] 🔄 Mendeteksi port SOCKS5 pada {proxy.host}:{proxy.port}. Mengubah protokol otomatis ke SOCKS5...")
                            proxy.protocol = "socks5"
                            pw_proxy = proxy.to_playwright()
                            browser_cm = AsyncCamoufox(
                                headless=headless_mode,
                                os=camoufox_os,
                                args=CAMOUFOX_ARGS,
                                proxy=pw_proxy,
                                geoip=False
                            )
                            browser_obj = await browser_cm.__aenter__()
                    else:
                        raise b_err
                context = await browser_obj.new_context(
                    ignore_https_errors=True,
                    viewport=profile['viewport'],
                    user_agent=ua
                )
                page = await context.new_page()

                # V3.8 Popup Killer: Tutup otomatis popup/popunder tab iklan DoodStream (TIDAK menutup tab utama!)
                async def _auto_close_popup(new_page):
                    if new_page == page:
                        return
                    try:
                        await asyncio.sleep(1.0)
                        await new_page.close()
                    except Exception:
                        pass
                page.on("popup", lambda p: asyncio.create_task(_auto_close_popup(p)))
                context.on("page", lambda p: asyncio.create_task(_auto_close_popup(p)))
            else:
                from playwright.async_api import async_playwright
                pw_instance = await async_playwright().start()
                try:
                    browser_obj = await pw_instance.chromium.launch(
                        headless=headless_mode,
                        args=BROWSER_ARGS,
                        proxy=pw_proxy
                    )
                except Exception as launch_err:
                    err_msg = str(launch_err)
                    if "Executable doesn't exist" in err_msg or "playwright install" in err_msg:
                        print(f"[{task['id']}] ⏳ Mendownload binary Chromium Playwright otomatis...")
                        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
                        if os.name == 'posix':
                            subprocess.run(["playwright", "install-deps", "chromium"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                        browser_obj = await pw_instance.chromium.launch(
                            headless=headless_mode,
                            args=BROWSER_ARGS,
                            proxy=pw_proxy
                        )
                    else:
                        raise
                context = await browser_obj.new_context(
                    user_agent=ua,
                    viewport=profile['viewport'],
                    is_mobile=profile['is_mobile'],
                    has_touch=profile['has_touch'],
                    device_scale_factor=profile['device_scale_factor'],
                    ignore_https_errors=True
                )
                page = await context.new_page()
                page.on("popup", lambda p: asyncio.create_task(_auto_close_popup(p)))
                context.on("page", lambda p: asyncio.create_task(_auto_close_popup(p)))

            # V3.7 Resource-Saving Route Filter: Block heavy trackers/ad networks
            async def _filter_traffic(route):
                r_url = route.request.url.lower()
                r_type = route.request.resource_type
                # 1. JANGAN PERNAH blokir stream video, chunk, token api, atau script player penting
                essential_patterns = [
                    "/api/", ".mp4", ".m3u8", ".ts", "master.m3u8",
                    "vidara.to", "vidara.so",
                    "cloudatacdn", "doodcdn", "imgds", "pass_md5", "playmogo", "dood",
                    "video.js", "player", "jwplayer"
                ]
                if any(k in r_url for k in essential_patterns):
                    await route.continue_()
                    return

                # 2. Blokir pelacak iklan berat dan popunder network
                heavy_ad_trackers = [
                    "google-analytics", "googlesyndication", "adservice",
                    "popads", "onclick", "exdynsrv", "adcash", "histats",
                    "syndication", "yandex", "clarity.ms", "doubleclick"
                ]
                if any(ad in r_url for ad in heavy_ad_trackers):
                    if not any(cdn in r_url for cdn in ["cloudatacdn", "doodcdn", "pass_md5"]):
                        await route.abort()
                        return

                # 3. Blokir gambar / font non-player eksternal untuk hemat RAM
                if r_type in ["image", "font"] and not any(k in r_url for k in ["vidara", "dood", "imgds", "cloudatacdn", "player"]):
                    await route.abort()
                    return

                await route.continue_()

            try:
                await page.route("**/*", _filter_traffic)
            except Exception:
                pass

            # INJEKSI IDENTITAS BROWSER: Mencegah status 'Unknown' pada skrip analitik Vidara
            await page.add_init_script("""
            if (!window.chrome) {
                window.chrome = { runtime: {}, loadTimes: function() {}, csi: function() {}, app: {} };
            }
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            """)

            vidara_stream_active = False
            async def on_request(req):
                nonlocal heartbeat_count, view_counted, dood_pass_unlocked, dood_stream_active, vidara_stream_active
                req_url = req.url
                # Vidara metrics
                if "/api/heartbeat" in req_url:
                    heartbeat_count += 1
                    print(f"[{task['id']}] 🟢 [VIDARA] LIVE WATCHING AKTIF: /api/heartbeat #{heartbeat_count} terkirim!")
                elif "/api/count" in req_url:
                    view_counted = True
                    print(f"[{task['id']}] 🎯 [VIDARA] VIEW RESMI TERCATAT: /api/count (visitorData valid)!")
                elif "/api/stream" in req_url:
                    vidara_stream_active = True
                    print(f"[{task['id']}] 🔑 [VIDARA] STREAM TERAUTORISASI: /api/stream berhasil!")
                elif any(k in req_url for k in [".m3u8", "/seg_", "jwplayer6/ping.gif"]):
                    vidara_stream_active = True
                # DoodStream metrics
                elif "/pass_md5/" in req_url:
                    dood_pass_unlocked = True
                    print(f"[{task['id']}] 🔑 [DOODSTREAM] TOKEN TERBUKA: pass_md5 token streaming berhasil didapatkan!")
                elif ("cloudatacdn.com" in req_url or "dood" in req_url) and (".mp4" in req_url or "token=" in req_url or "/hls/" in req_url):
                    if not dood_stream_active:
                        dood_stream_active = True
                        view_counted = True
                        print(f"[{task['id']}] 🎯 [DOODSTREAM] STREAM VIDEO AKTIF: Chunk MP4 streaming dari CDN terdeteksi (View Dihitung)!")

            page.on("request", on_request)

            # Buka halaman embed target video
            response = await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            try:
                raw_t = await page.evaluate("""() => {
                    if (document.title) return document.title;
                    const og = document.querySelector('meta[property="og:title"]');
                    if (og && og.content) return og.content;
                    const el = document.querySelector('h1, .video-title, .title, .video_title');
                    return el ? el.innerText : '';
                }""")
                if raw_t:
                    clean_t = raw_t.replace(" - Vidara", "").replace(" - vidara", "")
                    clean_t = clean_t.replace(" - DoodStream", "").replace(" - Doodstream", "").replace(" - doodstream", "").strip()
                    if clean_t:
                        page_title = clean_t
                        task["title"] = clean_t
            except Exception:
                pass

            # Human mouse / touch interaction
            vp = profile['viewport']
            await human_curve_move(page, vp['width']//4, vp['height']//4, vp['width']//2, vp['height']//2, steps=15)

            # Verifikasi dan picu pemutaran video (DoodStream Video.js + Vidara JWPlayer)
            video_is_playing = False
            for play_attempt in range(12):
                has_video_tag = False
                try:
                    play_res = await page.evaluate("""() => {
                        // 1. Doodstream Video.js (dsplayer)
                        if (typeof dsplayer !== 'undefined' && dsplayer) {
                            try { dsplayer.muted(true); } catch(e) {}
                            try { dsplayer.play(); } catch(e) {}
                            if (typeof dsplayer.paused === 'function' && !dsplayer.paused()) return { playing: true, type: 'dsplayer' };
                        }

                        // 2. Vidara JWPlayer
                        if (window.jwplayer && typeof window.jwplayer === 'function') {
                            try {
                                const jw = window.jwplayer();
                                if (jw) {
                                    try { jw.setMute(true); } catch(e) {}
                                    try { jw.play(); } catch(e) {}
                                    const st = typeof jw.getState === 'function' ? jw.getState() : '';
                                    if (st === 'playing' || st === 'buffering') return { playing: true, type: 'jwplayer' };
                                }
                            } catch(e) {}
                        }

                        // 3. Native HTML5 Video Element
                        const vids = document.querySelectorAll('video');
                        if (vids.length > 0) {
                            for (let v of vids) {
                                try {
                                    v.muted = true;
                                    v.playsInline = true;
                                    v.play().catch(() => {});
                                    // PENTING: Jika tidak paused, video sedang aktif berputar atau buffering HLS
                                    if (!v.paused) return { playing: true, type: 'html5_video', ct: v.currentTime };
                                } catch(e) {}
                            }
                            return { playing: false, hasVideo: true };
                        }

                        const wt = typeof totalWatchTime !== 'undefined' ? totalWatchTime : 0;
                        if (wt > 0) return { playing: true, type: 'watchtime' };

                        return { playing: false, hasVideo: false };
                    }""")

                    if play_res.get('playing'):
                        video_is_playing = True
                        print(f"[{task['id']}] ▶️ Video terdeteksi aktif berputar ({play_res.get('type')})!")
                        break
                    has_video_tag = play_res.get('hasVideo', False)
                except Exception:
                    pass

                # Hapus overlay iklan transparan DoodStream & Vidara yang menghalangi klik
                try:
                    await page.evaluate("""() => {
                        const overlays = document.querySelectorAll('a[target="_blank"], div[id*="overlay"], div[class*="overlay"], div[style*="z-index: 2147483647"], div[style*="z-index: 999999"]');
                        overlays.forEach(el => el.remove());
                    }""")
                except Exception:
                    pass

                # Klik tombol play (Lakukan 2x klik cepat untuk membypass ad-trap popup)
                try:
                    play_btn = await page.query_selector(
                        ".vjs-big-play-button, button.vjs-big-play-button, .jw-display-icon-display, .jw-icon-playback, button[aria-label='Play'], .play-button, #os_player"
                    )
                    if play_btn and await play_btn.is_visible():
                        await play_btn.click(force=True)
                        await asyncio.sleep(0.5)
                        # Klik kedua untuk memulai video jika klik pertama diserap iklan
                        try:
                            if play_btn and await play_btn.is_visible():
                                await play_btn.click(force=True)
                        except Exception:
                            pass
                    else:
                        # Klik tengah layar video
                        await page.mouse.click(vp['width'] / 2, vp['height'] / 2)
                        await asyncio.sleep(0.5)
                        await page.mouse.click(vp['width'] / 2, vp['height'] / 2)
                except Exception:
                    pass
                await asyncio.sleep(1.5)

            # Loop pemutaran aktif & pengiriman heartbeat
            t_start = time.time()
            stuck_count = 0

            while time.time() - t_start < target_watch_sec:
                await asyncio.sleep(5)
                elapsed = int(time.time() - t_start)

                cur_wt = await page.evaluate("""() => {
                    if (typeof totalWatchTime !== 'undefined' && totalWatchTime > 0) return Math.floor(totalWatchTime);
                    if (typeof dsplayer !== 'undefined' && dsplayer && typeof dsplayer.currentTime === 'function') {
                        const ct = dsplayer.currentTime();
                        if (ct > 0) return Math.floor(ct);
                    }
                    const v = document.querySelector('video');
                    return v ? Math.floor(v.currentTime) : 0;
                }""")

                # Ambil judul video secara dinamis jika belum termuat
                if not task.get("title") or task.get("title") in ("Vidara", "vidara", "DoodStream", ""):
                    try:
                        t_eval = await page.evaluate("() => document.title || (document.querySelector('h1, .video-title, .title') ? document.querySelector('h1, .video-title, .title').innerText : '')")
                        if t_eval:
                            c_t = t_eval.replace(" - Vidara", "").replace(" - vidara", "").replace(" - DoodStream", "").strip()
                            if c_t:
                                task["title"] = c_t
                                page_title = c_t
                    except Exception:
                        pass

                video_title_display = task.get("title") or page_title or f"{platform} Video"

                # Deteksi View Valid Otomatis saat video terkonfirmasi berputar
                if not view_counted:
                    if cur_wt >= 10:
                        view_counted = True
                        print(f"[{task['id']}] 🎯 VIEW RESMI TERCATAT: Video berhasil ditonton {cur_wt}s (Target >= 10s terpenuhi)!")
                    elif (dood_stream_active or vidara_stream_active) and cur_wt >= 3:
                        view_counted = True
                        print(f"[{task['id']}] 🎯 VIEW RESMI TERCATAT: Stream Video Aktif ({cur_wt}s ditonton)!")

                # Sampling network & CPU speed real-time
                if elapsed % 20 < 6:
                    sys_stat = global_tracker.sample()
                    status_view = "VIEW TERCATAT" if view_counted else ("STREAM AKTIF" if (dood_stream_active or vidara_stream_active) else "Menunggu view")
                    print(f"[{task['id']}] ⏱️ {elapsed}s / {target_watch_sec}s | WT: {cur_wt}s | DL: {sys_stat['dl_speed']} | CPU: {sys_stat['cpu_pct']:.0f}% | {status_view} | {video_title_display}")

                # Jaga agar video tetap berputar (Video.js dsplayer + HTML5 video)
                is_p = await page.evaluate("""() => {
                    if (typeof dsplayer !== 'undefined' && dsplayer && typeof dsplayer.paused === 'function') {
                        if (!dsplayer.paused()) return true;
                    }
                    const v = document.querySelector('video');
                    return v && !v.paused;
                }""")
                if not is_p:
                    stuck_count += 1
                    if stuck_count >= 4:
                        print(f"[{task['id']}] ⚠️ Video terhenti/buffer, mencoba memicu play ulang...")
                        await page.evaluate("""() => {
                            if (typeof dsplayer !== 'undefined' && dsplayer) {
                                try { dsplayer.muted(true); dsplayer.play(); } catch(e) {}
                            }
                            const vids = document.querySelectorAll('video');
                            for (let v of vids) {
                                try { v.muted = true; v.play(); } catch(e) {}
                            }
                        }""")
                        try:
                            re_btn = await page.query_selector(".vjs-big-play-button, .jw-display-icon-display, .jw-icon-playback")
                            if re_btn and await re_btn.is_visible():
                                await re_btn.click()
                        except Exception:
                            pass
                        stuck_count = 0
                else:
                    stuck_count = 0

            # Selesai putaran ini
            video_title_display = task.get("title") or page_title or f"{platform} Video"
            status_desc = "View Sukses" if view_counted else ("Stream Aktif" if (dood_stream_active or vidara_stream_active) else "Waktu Terpenuhi")
            extra_info = f"Heartbeat: {heartbeat_count} | Stream: {vidara_stream_active}" if platform == "Vidara" else f"Token: {dood_pass_unlocked} | Stream: {dood_stream_active}"
            print(f"[{timestamp()}] [{task['id']}] 🏁 Selesai tonton ({target_watch_sec}s) | View: {view_counted} | {extra_info} | {video_title_display}")
            task["status"] = f"Selesai ({status_desc})"
            return True

        except Exception as exc:
            err_msg = str(exc)
            short_err = err_msg.replace("\n", " ")[:80]
            print(f"[{timestamp()}] [{task['id']}] ❌ Kendala: {short_err} (Proxy: {proxy_label})")

            # Cek apakah error karena binary Camoufox belum terpasang
            if "camoufox fetch" in err_msg.lower() or "not installed" in err_msg.lower():
                print(f"[{task['id']}] ⚠️ Browser Camoufox belum terpasang, mengunduh via 'camoufox fetch' sekarang...")
                import subprocess, sys
                subprocess.run([sys.executable, '-m', 'camoufox', 'fetch'], check=False)
                await asyncio.sleep(3)
                continue

            is_browser_local_err = any(k in err_msg.lower() for k in ["not installed", "camoufox fetch", "executable", "browsertype", "launch argument", "keyword argument"])
            is_proxy_issue = any(k in err_msg.lower() for k in ["proxy", "tunnel", "connection", "timeout", "socket", "econnreset", "net::err", "err_connection", "timed out", "unreachable", "reset by peer"])
            if is_proxy_issue and not is_browser_local_err:
                if proxy and 'proxy_pool' in globals():
                    proxy_pool.mark_dead(proxy, reason=short_err)
            retry_count += 1
            if retry_count < max_proxy_retries:
                print(f"[{task['id']}] 🔄 Beralih ke proxy lain (Percobaan {retry_count + 1}/{max_proxy_retries})...")
                await asyncio.sleep(2)
            else:
                task["status"] = f"Gagal ({short_err[:30]})"
                return False
        finally:
            try:
                if engine_type == "camoufox" and 'browser_cm' in locals() and browser_cm:
                    await browser_cm.__aexit__(None, None, None)
                elif browser_obj:
                    await browser_obj.close()
                if pw_instance:
                    await pw_instance.stop()
            except Exception:
                pass
            try:
                import gc
                gc.collect()
            except Exception:
                pass

async def main_engine_v3():
    global completed_videos_count
    completed_videos_count = 0
    # Init lock
    pass

    links = [l.strip() for l in target_urls if l and isinstance(l, str) and l.strip().startswith(('http://', 'https://'))]

    if not links:
        print("Daftar URL target kosong. Silakan isi slot Link di Cell 2.")
        return

    engine = "camoufox" if "Camoufox" in Engine_Mode else "playwright"
    # Pastikan binary Camoufox sudah terpasang sebelum multi-slot dimulai
    if engine == "camoufox":
        try:
            import subprocess, sys
            subprocess.run([sys.executable, '-m', 'camoufox', 'fetch'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        except Exception:
            pass

    sem_limit = Maksimal_Browser_Simultan if 'Maksimal_Browser_Simultan' in globals() else 3
    sem = asyncio.Semaphore(sem_limit)
    round_num = 1

    while True:
        print("\n" + "="*75)
        # Rotasi proxy otomatis dikelola oleh UniversalProxyPool
        print(f"[{timestamp()}] 🚀 MEMULAI PUTARAN #{round_num} — {len(links)} LINK (Max Simultan: {sem_limit} Browser Bersamaan)")
        rot_info = f"Pool ({len(proxy_pool)} Proxy)" if "proxy_pool" in globals() and len(proxy_pool) > 0 else "Direct (Tanpa Proxy)"
        print(f"Engine: {Engine_Mode} | Simultan: {sem_limit} Slot | Rotasi IP: {rot_info} | User-Agent: {len(ua_pool)} Asli")
        print("="*75)

        dashboard_handle = None
        stop_dashboard_event = asyncio.Event()
        dashboard_task = None

        if Tampilkan_System_Dashboard:
            global_tracker.print_dashboard_box(f"LIVE PARALLEL DASHBOARD (PUTARAN #{round_num})")
            try:
                from IPython.display import display, HTML
                dashboard_handle = display(HTML(global_tracker.get_html_dashboard(f"LIVE PARALLEL DASHBOARD (PUTARAN #{round_num})")), display_id=True)

                async def auto_refresher():
                    last_log_print = time.time()
                    ref_sec = max(1, Interval_Refresh_Dashboard_Detik if 'Interval_Refresh_Dashboard_Detik' in globals() else 3)
                    prt_sec = Cetak_Log_Dashboard_Tiap_Detik if 'Cetak_Log_Dashboard_Tiap_Detik' in globals() else 45
                    while not stop_dashboard_event.is_set():
                        try:
                            # 1. Update widget HTML di atas secara real-time in-place!
                            if dashboard_handle:
                                dashboard_handle.update(HTML(global_tracker.get_html_dashboard(f"LIVE PARALLEL DASHBOARD (PUTARAN #{round_num})")))

                            # 2. Cetak box di log terminal secara periodik jika diatur
                            now_t = time.time()
                            if prt_sec > 0 and (now_t - last_log_print >= prt_sec):
                                global_tracker.print_dashboard_box(f"UPDATE RESOURCE (PUTARAN #{round_num})")
                                last_log_print = now_t
                        except Exception:
                            pass
                        await asyncio.sleep(ref_sec)

                dashboard_task = asyncio.create_task(auto_refresher())
            except Exception:
                pass

        tasks = [{"id": f"Slot-{i+1:02d} (R{round_num})", "url": u, "status": "Antre", "title": ""} for i, u in enumerate(links)]

        async def runner(idx, t):
            async with sem:
                try:
                    if idx > 0 and Jeda_Mikro_Start_Simultan > 0:
                        await asyncio.sleep(Jeda_Mikro_Start_Simultan)
                    print(f"[{timestamp()}] [{t['id']}] Memulai proses: {t['url']} (Slot simultan aktif)")
                    await watch_playback(
                        task=t,
                        proxy_pool=proxy_pool,
                        ua_pool=ua_pool,
                        engine_type=engine,
                        headless_mode=Headless_Mode,
                        target_watch_sec=Durasi_Tonton_Detik,
                        max_proxy_retries=Maksimal_Retry_Proxy_Gagal
                    )

                    # ==============================================================
                    # Rotasi proxy baru otomatis diambil oleh runner tiap video baru
                except Exception as runner_err:
                    print(f"[{timestamp()}] [{t['id']}] ⚠️ Exception di runner: {runner_err}")
                    t['status'] = f"Gagal ({str(runner_err)[:30]})"


        await asyncio.gather(*(runner(i, t) for i, t in enumerate(tasks)))

        # Hentikan background auto-refresher setelah putaran selesai
        if stop_dashboard_event:
            stop_dashboard_event.set()
        if dashboard_task:
            try:
                await dashboard_task
            except Exception:
                pass

        print(f"\n[{timestamp()}] --- Putaran #{round_num} Selesai ---")
        for t in tasks:
            print(f"[{t['id']}] {t.get('title', t['url'])}: {t['status']}")

        if Tampilkan_System_Dashboard:
            global_tracker.print_dashboard_box(f"RINGKASAN RESOURCE & BANDWIDTH PUTARAN #{round_num}")

        if Mode_Eksekusi == "HANYA 1 KALI PUTARAN":
            print("\nMode 'HANYA 1 KALI PUTARAN' selesai. Engine berhenti.")
            break

        print(f"\nJeda {Jeda_Antar_Putaran_Detik} detik sebelum melanjutkan ke Putaran #{round_num + 1}...")
        await asyncio.sleep(Jeda_Antar_Putaran_Detik)
        round_num += 1

if __name__ == '__main__':
    try:
        asyncio.run(main_engine_v3())
    except KeyboardInterrupt:
        print("\n[!] Bot dihentikan oleh pengguna.")

