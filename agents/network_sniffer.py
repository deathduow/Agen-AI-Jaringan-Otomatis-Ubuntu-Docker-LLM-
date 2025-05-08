import time
import psycopg2
import requests
from scapy.all import sniff, TCP, IP
from dotenv import load_dotenv
import os
from influxdb import InfluxDBClient
import subprocess

# ====== 1. SETUP GLOBAL KONFIGURASI ======
ip_last_alert = {}  # Menyimpan waktu terakhir alert per IP
COOLDOWN = 600      # Delay antar alert per IP (10 menit)

# Load konfigurasi dari file .env
load_dotenv(dotenv_path="/home/devlinux/cybersec-agent/config/.env", override=True)

# Variabel dari .env
INFLUX_HOST = os.getenv("INFLUX_HOST", "localhost")
INFLUX_PORT = int(os.getenv("INFLUX_PORT", 8086))
INFLUX_DB = os.getenv("INFLUX_DB", "cybersec")

DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")

WA_URL = os.getenv("WA_URL")
WA_API_KEY = os.getenv("WA_API_KEY")

# ====== 2. FUNGSI ANALISA AI (LLAMA.CPP) ======
def analisa_ai(prompt):
    result = subprocess.run([
        "/home/devlinux/llama.cpp/build/bin/llama-cli",
        "-m", "/home/devlinux/llama.cpp/models/mistral.gguf",
        "-p", prompt,
        "--n-predict", "200"
    ], capture_output=True, text=True)
    return result.stdout

# ====== 3. KIRIM NOTIFIKASI WHATSAPP ======
def kirim_pesan_ke_it_support(pesan):
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASS,
        host=DB_HOST, port=DB_PORT
    )
    cur = conn.cursor()
    cur.execute("SELECT nomortelp FROM master_pic WHERE divisi = 'it support'")
    for (nomor,) in cur.fetchall():
        requests.post(WA_URL,
            headers={
                "x-api-key": WA_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "number": nomor,
                "message": pesan
            }
        )
    cur.close()
    conn.close()

# ====== 4. SIMPAN LOG KE POSTGRESQL ======
def log_event(event_type, ip_address, detail, action, reasoning_text=None):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS,
            host=DB_HOST, port=DB_PORT
        )
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO logs_network_event (event_type, ip_address, detail, action, reasoning_text)
            VALUES (%s, %s, %s, %s, %s)
        """, (event_type, ip_address, detail, action, reasoning_text))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[!] Gagal log ke PostgreSQL: {e}")


# ====== 5. SIMPAN LOG KE INFLUXDB ======
def kirim_ke_influx(ip, port, action):
    client = InfluxDBClient(host=INFLUX_HOST, port=INFLUX_PORT)
    client.switch_database(INFLUX_DB)
    json_body = [
        {
            "measurement": "network_events",
            "tags": {
                "ip": ip,
                "event_type": "port_scan"
            },
            "fields": {
                "port": int(port),
                "action": action
            }
        }
    ]
    client.write_points(json_body)
    client.close()

# ====== 6. DETEKSI SCAN PORT ======
def deteksi_scan(packet):
    if packet.haslayer(TCP) and packet[TCP].flags == 'S':
        ip = packet[IP].src
        port = packet[TCP].dport
        now = time.time()

        # Cegah spam alert dalam 10 menit
        if ip in ip_last_alert and now - ip_last_alert[ip] < COOLDOWN:
            return

        ip_last_alert[ip] = now
        detail = f"Deteksi scan SYN ke port {port}"
        print(f"[!] Port scan dari IP {ip} ke port {port}")

        # Kirim ke Influx
        kirim_ke_influx(ip, port, "blocked")

        # Dapatkan reasoning dari AI lokal
        prompt = f"### Instruction:\nIP {ip} melakukan scanning ke port {port}. Apa yang harus dilakukan oleh admin jaringan?\n\n### Response:"
        jawaban_ai = analisa_ai(prompt)

        # Simpan log ke PostgreSQL
        log_event("port_scan", ip, detail, "blocked", jawaban_ai)

        # Kirim pesan ke WhatsApp
        pesan = f"""⚠️ AGEN AI JARINGAN:
Deteksi scanning dari IP {ip}.
Port: {port}
Tindakan: IP diblokir otomatis.

AI Reasoning:
{jawaban_ai[:500]}..."""
        kirim_pesan_ke_it_support(pesan)

        # Opsi blokir otomatis (nonaktif sementara)
        # subprocess.run(["sudo", "/home/devlinux/cybersec-agent/scripts/block_ip.sh", ip])

# ====== 7. MULAI MONITORING ======
print("[*] Mulai monitoring jaringan... Tekan Ctrl+C untuk berhenti.")
sniff(filter="tcp", prn=deteksi_scan, store=0)
