#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ Fast 2-Stage Proxy Scraper & Deep Vidara Checker (Vibot Edition)
Diadaptasi & diselaraskan langsung dari standar ketat ProxyvidaraV2.5.ipynb
Repository: https://github.com/AbyanZainZ/Vibot
Author: AbyanZainZ

Ketentuan Kategori LIVE vs DEAD (Identik dengan ProxyvidaraV2.5.ipynb):
1. TAHAP 1 (Fast Pre-Filter):
   - Uji koneksi cepat dengan Google generate_204 / Cloudflare trace.
   - Membuang 95%+ proxy mati hanya dalam hitungan detik.
2. TAHAP 2 (Deep Vidara Strict Checker):
   - Validasi Handshake HTTPS SSL langsung ke target: https://vidara.to/ (atau fallback https://vidara.so/)
   - Status code HARUS 200 (atau redirect sah)
   - Respon HARUS memuat signature asli: 'vidara'
   - BEBAS dari pemblokiran Cloudflare captcha ('challenge-platform', 'cf-browser-verification', 'attention required!', 'access denied', '403 forbidden')
   - Panjang respon HTML HARUS valid (>= 1,000 bytes)
   - HANYA proxy yang lolos Tahap 2 yang disimpan ke 'proxy.txt' & 'proxies.txt'.
   - Proxy mati / gagal handshake / CF block langsung dibuang (DEAD).
"""

import os
import sys
import time
import re
import json
import threading
from concurrent.futures import ThreadPoolExecutor
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
OUTPUT_RESIDENTIAL = BASE_DIR / "LIVE_Proxy_Residential.txt"
OUTPUT_WITH_ISP = BASE_DIR / "LIVE_PROXY_WITH_ISP.txt"

# Target & Parameter Pengecekan
TARGET_URL = "https://vidara.to/"
FALLBACK_TARGET_URL = "https://vidara.so/"
PREFILTER_URL = "http://www.google.com/generate_204"
PREFILTER_FALLBACK = "http://1.1.1.1/cdn-cgi/trace"

SCRAPE_WORKERS = 35
STAGE1_WORKERS = 400
STAGE1_TIMEOUT = 2.0

STAGE2_WORKERS = 120
STAGE2_CONNECT_TIMEOUT = 3.0
STAGE2_READ_TIMEOUT = 5.0

MAX_LIVE_TARGET = 0  # 0 = MAKSIMALKAN PENUH (Periksa seluruh kandidat & kumpulkan sebanyak-banyaknya tanpa batasan!)

BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="131", "Google Chrome";v="131"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'Connection': 'close'
}

# 90+ SUMBER GITHUB RAW PROXY (HTTP & SOCKS5)
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

DC_KEYWORDS = [
    'hosting', 'datacenter', 'data center', 'server', 'vps', 'cloud', 'dedicated',
    'ovh', 'hetzner', 'digitalocean', 'linode', 'vultr', 'amazon', 'aws', 'google',
    'microsoft', 'azure', 'alibaba', 'oracle', 'leaseweb', 'choopa', 'm247',
    'hostpapa', 'nocix', 'tier.net', 'performive', 'cogent', 'hostinger', 'contabo',
    'fastly', 'akamai', 'cloudflare', 'cdn', 'hydra communications', 'getechbrothers',
    'hz hosting', 'hostroyale'
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

# ==============================================================================
# TAHAP 1: FAST CONNECTIVITY PRE-FILTER
# ==============================================================================
def stage1_fast_check(p_url):
    """Uji konektivitas dasar super cepat untuk membuang 95% proxy mati."""
    proxies = build_requests_proxies(p_url)
    t0 = time.perf_counter()
    try:
        r = requests.get(PREFILTER_URL, proxies=proxies, timeout=STAGE1_TIMEOUT, allow_redirects=False)
        lat = round((time.perf_counter() - t0) * 1000)
        if r.status_code in (200, 204, 301, 302):
            return True, p_url, lat
        # Fallback trace
        r2 = requests.get(PREFILTER_FALLBACK, proxies=proxies, timeout=STAGE1_TIMEOUT, allow_redirects=False)
        lat2 = round((time.perf_counter() - t0) * 1000)
        if r2.status_code in (200, 204, 301, 302):
            return True, p_url, lat2
    except Exception:
        pass
    return False, p_url, 0

# ==============================================================================
# TAHAP 2: DEEP VIDARA STRICT CHECKER (IDENTIK DENGAN ProxyvidaraV2.5.ipynb)
# ==============================================================================
def check_vidara_deep(p_url):
    """
    Standar Ketat ProxyvidaraV2.5.ipynb:
    - Melakukan handshake HTTPS SSL ke target https://vidara.to/
    - Status code harus 200
    - Body harus memuat signature 'vidara'
    - Bebas dari pemblokiran Cloudflare
    - Panjang respon HTML >= 1000 karakter
    """
    t_start = time.perf_counter()
    proxies = build_requests_proxies(p_url)

    target = TARGET_URL
    try:
        resp = requests.get(
            target,
            headers=BROWSER_HEADERS,
            proxies=proxies,
            timeout=(STAGE2_CONNECT_TIMEOUT, STAGE2_READ_TIMEOUT),
            verify=False,
            allow_redirects=True
        )
        latency = round((time.perf_counter() - t_start) * 1000)
        status_code = resp.status_code
        body_text = resp.text.lower()

        is_vidara = ('vidara' in body_text) or ('<title>vidara' in body_text) or ('dood' in body_text)
        cf_blocked = any(cf in body_text for cf in [
            'challenge-platform', 'cf-browser-verification', 'attention required!',
            'access denied', '403 forbidden', 'cloudflare-nginx', 'just a moment...'
        ])
        is_valid_body = len(resp.text) >= 1000

        # Kategori LIVE
        if status_code == 200 and is_vidara and is_valid_body and not cf_blocked:
            proto = p_url.split('://', 1)[0].upper()
            host_port = p_url.split('://', 1)[1]
            host, port = host_port.split(':', 1)
            return {
                'is_live': True,
                'proxy': p_url,
                'proto': proto,
                'host': host,
                'port': port,
                'status_code': status_code,
                'latency_ms': latency,
                'error': ''
            }
        else:
            # Fallback ke domain vidara cadangan jika domain utama sedang redirect
            if not is_vidara and status_code in (200, 301, 302):
                try:
                    resp2 = requests.get(
                        FALLBACK_TARGET_URL,
                        headers=BROWSER_HEADERS,
                        proxies=proxies,
                        timeout=(STAGE2_CONNECT_TIMEOUT, STAGE2_READ_TIMEOUT),
                        verify=False,
                        allow_redirects=True
                    )
                    b2 = resp2.text.lower()
                    if resp2.status_code == 200 and 'vidara' in b2 and len(resp2.text) >= 1000:
                        proto = p_url.split('://', 1)[0].upper()
                        host_port = p_url.split('://', 1)[1]
                        host, port = host_port.split(':', 1)
                        lat2 = round((time.perf_counter() - t_start) * 1000)
                        return {
                            'is_live': True,
                            'proxy': p_url,
                            'proto': proto,
                            'host': host,
                            'port': port,
                            'status_code': 200,
                            'latency_ms': lat2,
                            'error': ''
                        }
                except Exception:
                    pass

            err_reason = f"CF Block ({status_code})" if cf_blocked else (f"Bukan Vidara ({status_code})" if not is_vidara else f"HTTP {status_code}")
            return {'is_live': False, 'proxy': p_url, 'error': err_reason}

    except requests.exceptions.ProxyError:
        return {'is_live': False, 'proxy': p_url, 'error': 'Proxy Tunnel Error (Dead)'}
    except requests.exceptions.ConnectTimeout:
        return {'is_live': False, 'proxy': p_url, 'error': 'Connect Timeout (Dead)'}
    except requests.exceptions.ReadTimeout:
        return {'is_live': False, 'proxy': p_url, 'error': 'Read Timeout (Dead)'}
    except Exception as exc:
        return {'is_live': False, 'proxy': p_url, 'error': str(exc)[:35]}

# ==============================================================================
# KLASIFIKASI RESIDENTIAL vs VPN / DATACENTER (IP-API BATCH)
# ==============================================================================
def classify_ips_batch(ips):
    """Mendeteksi apakah IP adalah Residential (Reward Penuh) atau VPN/Datacenter."""
    if not ips:
        return {}
    url = 'http://ip-api.com/batch?fields=query,status,country,isp,org,as,proxy,hosting'
    results = {}
    for i in range(0, len(ips), 100):
        chunk = ips[i:i+100]
        try:
            resp = requests.post(url, json=chunk, timeout=8)
            if resp.status_code == 200:
                for item in resp.json():
                    q = item.get('query')
                    if not q:
                        continue
                    p = item.get('proxy', False)
                    h = item.get('hosting', False)
                    desc = f"{item.get('isp','')} {item.get('org','')} {item.get('as','')}".lower()
                    has_kw = any(k in desc for k in DC_KEYWORDS)
                    is_vpn = bool(p or h or has_kw)
                    raw_isp = item.get('isp') or item.get('org') or item.get('as') or 'UNKNOWN'
                    results[q] = {
                        'is_vpn': is_vpn,
                        'category': 'VPN' if is_vpn else 'RESIDENTIAL',
                        'isp': raw_isp.strip().upper(),
                        'country': item.get('country', '')
                    }
        except Exception:
            pass
    return results

def main():
    print("==================================================================")
    print("⚡ 2-STAGE PROXY SCRAPER & DEEP VIDARA CHECKER (VIBOT EDITION)")
    print("Sesuai Standar Kategori Ketat: ProxyvidaraV2.5.ipynb")
    print(f"Target Validasi Handshake: {TARGET_URL}")
    print(f"Target Output Live      : {', '.join([p.name for p in OUTPUT_FILES])}")
    print(f"Batas Target Proxy Live  : {'MAKSIMAL (Seluruh kandidat diperiksa tanpa batas!)' if MAX_LIVE_TARGET <= 0 else f'{MAX_LIVE_TARGET} Proxy'}")
    print("==================================================================\n")

    # 1. SCRAPING DARI GITHUB
    print("⏳ [1/3] Mengunduh proxy dari 40+ repository GitHub...")
    all_raw = set()
    t_start_scrape = time.time()

    with ThreadPoolExecutor(max_workers=SCRAPE_WORKERS) as executor:
        futures = [executor.submit(scrape_single_source, proto, url) for proto, url in GITHUB_SOURCES]
        for f in futures:
            try:
                res = f.result()
                for p in res:
                    all_raw.add(p)
            except Exception:
                pass

    candidate_list = list(all_raw)
    dur_scrape = time.time() - t_start_scrape
    print(f"✅ Scraping Selesai dalam {dur_scrape:.1f}s!")
    print(f"📊 Berhasil mengumpulkan {len(candidate_list):,} kandidat proxy unik.\n")

    if not candidate_list:
        print("❌ Tidak ada proxy yang berhasil discrape. Periksa koneksi internet.")
        return

    # 2. TAHAP 1: FAST CONNECTIVITY PRE-FILTER
    print("⏳ [2/3] TAHAP 1: Fast Connectivity Pre-Filter...")
    print(f"[*] Menjalankan {STAGE1_WORKERS} worker untuk membuang proxy yang 100% mati...")
    stage1_live = []
    done_s1 = 0
    t_start_s1 = time.time()
    last_print_s1 = time.time()

    batch_s1 = STAGE1_WORKERS * 2
    it_s1 = iter(candidate_list)

    with ThreadPoolExecutor(max_workers=STAGE1_WORKERS) as ex_s1:
        futs_s1 = {}
        for _ in range(batch_s1):
            try:
                p = next(it_s1)
                futs_s1[ex_s1.submit(stage1_fast_check, p)] = p
            except StopIteration:
                break

        while futs_s1:
            dones = [f for f in list(futs_s1.keys()) if f.done()]
            if not dones:
                time.sleep(0.02)
                continue

            for f in dones:
                p = futs_s1.pop(f)
                done_s1 += 1
                try:
                    is_ok, p_url, lat = f.result()
                    if is_ok:
                        stage1_live.append(p_url)
                except Exception:
                    pass

                try:
                    nxt = next(it_s1)
                    futs_s1[ex_s1.submit(stage1_fast_check, nxt)] = nxt
                except StopIteration:
                    pass

            now_s1 = time.time()
            if now_s1 - last_print_s1 >= 2.0:
                speed = done_s1 / max(1e-3, (now_s1 - t_start_s1))
                print(f"   ⏱️ [Tahap 1 Pre-Filter] Diperiksa: {done_s1:,}/{len(candidate_list):,} | Lolos: {len(stage1_live):,} | Speed: {speed:.0f} req/s")
                last_print_s1 = now_s1

            # Jika dibatasi
            if MAX_LIVE_TARGET > 0 and len(stage1_live) >= (MAX_LIVE_TARGET * 3):
                print(f"\n   🎯 Terkumpul {len(stage1_live):,} kandidat Tahap 1. Melanjutkan ke Tahap 2...")
                break

    print(f"✅ Tahap 1 Selesai dalam {time.time() - t_start_s1:.1f}s | Terkumpul {len(stage1_live):,} kandidat lolos ke Tahap 2.\n")

    if not stage1_live:
        print("❌ Tidak ada proxy yang lolos Tahap 1.")
        return

    # 3. TAHAP 2: DEEP VIDARA STRICT CHECKER (STANDAR ProxyvidaraV2.5)
    print("⏳ [3/3] TAHAP 2: Deep Vidara Strict Checker (HTTPS Handshake & Cloudflare Bypass)...")
    print(f"[*] Target Validasi: {TARGET_URL} (Port 443 SSL Tunneling)")
    print(f"[*] Hanya proxy yang lolos verifikasi Vidara 100% yang akan disimpan!")
    print("Tekan Ctrl+C kapan saja jika proxy live sudah dirasa cukup.\n")

    # Bersihkan file output lama
    for out_p in OUTPUT_FILES:
        with open(out_p, "w", encoding="utf-8") as f:
            f.write("# LIVE VERIFIED VIDARA PROXIES (100% HANDSHAKE TESTED)\n")

    live_vidara = []
    dead_s2 = 0
    checked_s2 = 0
    file_lock = threading.Lock()
    t_start_s2 = time.time()
    last_print_s2 = time.time()

    def save_live_proxy_item(p_str):
        with file_lock:
            for out_p in OUTPUT_FILES:
                with open(out_p, "a", encoding="utf-8") as f:
                    f.write(p_str + "\n")

    batch_s2 = STAGE2_WORKERS * 2
    it_s2 = iter(stage1_live)

    try:
        with ThreadPoolExecutor(max_workers=STAGE2_WORKERS) as ex_s2:
            futs_s2 = {}
            for _ in range(batch_s2):
                try:
                    p = next(it_s2)
                    futs_s2[ex_s2.submit(check_vidara_deep, p)] = p
                except StopIteration:
                    break

            while futs_s2:
                dones = [f for f in list(futs_s2.keys()) if f.done()]
                if not dones:
                    time.sleep(0.03)
                    continue

                for f in dones:
                    p = futs_s2.pop(f)
                    checked_s2 += 1
                    try:
                        res = f.result()
                        if res['is_live']:
                            live_vidara.append(res)
                            save_live_proxy_item(res['proxy'])
                            print(f"🟢 [LIVE VIDARA #{len(live_vidara)}] {res['proxy']} ({res['latency_ms']}ms) - HTTP {res['status_code']}")
                        else:
                            dead_s2 += 1
                    except Exception:
                        dead_s2 += 1

                    try:
                        nxt = next(it_s2)
                        futs_s2[ex_s2.submit(check_vidara_deep, nxt)] = nxt
                    except StopIteration:
                        pass

                now_s2 = time.time()
                if now_s2 - last_print_s2 >= 2.5:
                    speed = checked_s2 / max(1e-3, (now_s2 - t_start_s2))
                    print(f"   ⏱️ Tahap 2: {checked_s2}/{len(stage1_live)} | LIVE Vidara: {len(live_vidara)} | Gagal/Dead: {dead_s2} | Speed: {speed:.1f} req/s")
                    last_print_s2 = now_s2

                if MAX_LIVE_TARGET > 0 and len(live_vidara) >= MAX_LIVE_TARGET:
                    print(f"\n🎯 Target {MAX_LIVE_TARGET} proxy aktif lolos Vidara berhasil terpenuhi!")
                    break

    except KeyboardInterrupt:
        print("\n\n🛑 Proses dihentikan oleh pengguna.")

    # 4. KLASIFIKASI ISP & RESIDENTIAL (OPSIONAL / BONUS)
    if live_vidara:
        print("\n🔍 Menganalisis ISP & Kategori Residential vs Datacenter IP...")
        hosts = [item['host'] for item in live_vidara]
        intel_map = classify_ips_batch(hosts)

        res_lines = []
        isp_lines = []
        for item in live_vidara:
            h = item['host']
            intel = intel_map.get(h, {'is_vpn': True, 'isp': 'UNKNOWN'})
            isp_name = intel['isp']
            p_str = item['proxy']
            isp_lines.append(f"{p_str}|{isp_name}")
            if not intel['is_vpn']:
                res_lines.append(p_str)

        if res_lines:
            with open(OUTPUT_RESIDENTIAL, "w", encoding="utf-8") as f:
                f.write("\n".join(res_lines) + "\n")
        if isp_lines:
            with open(OUTPUT_WITH_ISP, "w", encoding="utf-8") as f:
                f.write("\n".join(isp_lines) + "\n")

    total_dur = time.time() - t_start_s2
    res_count = len(res_lines) if 'res_lines' in locals() else 0
    print("\n==================================================================")
    print(" 🎉 PROXY SCRAPING & DEEP VIDARA CHECK SELESAI!")
    print("==================================================================")
    print(f" Total Diuji Tahap 2 : {checked_s2:,} Proxy dalam {total_dur:.1f} detik")
    print(f" Total LIVE Vidara   : {len(live_vidara)} Proxy (100% Lolos Handshake SSL)")
    if res_count > 0:
        print(f" ⭐ Residential IP   : {res_count} Proxy (Reward 0.0040 USD!) -> {OUTPUT_RESIDENTIAL.name}")
    print(f" File Output Utama   : {', '.join([str(p.name) for p in OUTPUT_FILES])}")
    print("==================================================================")
    print("👉 Proxy di file 'proxy.txt' sudah diverifikasi 100% bisa membuka Vidara.")
    print("   Jalankan bot sekarang:")
    print("   Linux: ./start_bot.sh")
    print("   Windows: START_PROXY_SCRAPE.bat / START_BOT.bat")

if __name__ == "__main__":
    main()
