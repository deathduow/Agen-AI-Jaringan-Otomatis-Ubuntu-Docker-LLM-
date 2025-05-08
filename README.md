# 🛡️ Agen AI Jaringan Otomatis

Agen Python untuk mendeteksi aktivitas jaringan mencurigakan (port scanning), melakukan reasoning menggunakan AI lokal (Mistral via llama.cpp), mengirim notifikasi WhatsApp, serta menyimpan log ke PostgreSQL dan InfluxDB untuk divisualisasikan dengan Grafana.

---

## 🔧 Fitur Utama

* 🔍 Deteksi port scanning (TCP SYN)
* 🤖 Reasoning otomatis menggunakan AI lokal (Mistral 7B GGUF)
* 📬 Kirim notifikasi WA ke IT Support
* 🗃️ Simpan log ke PostgreSQL (`logs_network_event`)
* 📈 Simpan ke InfluxDB (`network_events`)
* 📊 Visualisasi via Grafana
* 🔁 Auto cleanup log bulanan

---

## 📁 Struktur Direktori

```
cybersec-agent/
├── agents/network_sniffer.py
├── config/.env
├── scripts/block_ip.sh (optional)
├── docker/docker-compose.yml
├── dashboards/ (Grafana panels)
├── database/ (PostgreSQL volume)
├── venv/ (virtualenv)
└── requirements.txt
```

---

## ⚙️ Instalasi Singkat

### 1. Siapkan Python Env

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Siapkan Llama.cpp + Mistral

```bash
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
mkdir models
wget https://.../mistral.gguf -O models/mistral.gguf
cmake -B build .
cmake --build build -j$(nproc)
```

### 3. Jalankan Docker Stack

```bash
cd docker
docker-compose up -d
```

### 4. Jalankan Agen

```bash
sudo systemctl start agen-ai.service
```

---

## ⚙️ File .env Contoh

```
WA_URL=http://101.255.92.243:3371/send
WA_API_KEY=xxxxx
POSTGRES_HOST=172.17.0.1
POSTGRES_PORT=5432
POSTGRES_DB=arista-cyber
POSTGRES_USER=devlinux
POSTGRES_PASSWORD=xxxxxx
INFLUX_HOST=172.17.0.1
INFLUX_PORT=8086
INFLUX_DB=cybersec
```

---

## 📊 Query Panel Grafana

### 1. Jumlah Alert per IP

```sql
SELECT ip_address, COUNT(*) AS total FROM logs_network_event GROUP BY ip_address ORDER BY total DESC
```

### 2. Top 5 Reasoning Terpanjang

```sql
SELECT waktu, ip_address, LENGTH(reasoning_text) AS panjang, reasoning_text FROM logs_network_event ORDER BY panjang DESC LIMIT 5
```

---

## ✅ Credits

* AI Model: Mistral-7B-Instruct via HuggingFace
* Backend AI: llama.cpp (C++ inference engine)
* Visualisasi: Grafana
* Agent: Python + Scapy + Subprocess

---

> Dibuat oleh Tim Keamanan Jaringan Arista Cyber – 2025

🛠️ Hubungi: devlinux\@it-support
