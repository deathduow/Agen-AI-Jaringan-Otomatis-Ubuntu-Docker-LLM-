import requests
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv(os.path.expanduser("~/cybersec-agent/config/.env"))

WA_URL = os.getenv("WA_URL")
WA_API_KEY = os.getenv("WA_API_KEY")

DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")

pesan = "🔔 Test pengiriman WA dari agen AI"

conn = psycopg2.connect(
    dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
)
cur = conn.cursor()
cur.execute("SELECT nomortelp FROM master_pic WHERE divisi = 'it support'")
for (nomor,) in cur.fetchall():
    print(f"Mengirim ke {nomor}...")
    r = requests.post(WA_URL,
        headers={
            "x-api-key": WA_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "number": nomor,
            "message": pesan
        }
    )
    print(r.status_code, r.text)
cur.close()
conn.close()
