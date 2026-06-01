🟦 Smart Monitor Platform
🚀 Real-Time Linux Monitoring & DevOps Deployment System

A production-style Linux monitoring platform built with Flask, Gunicorn, Nginx, and systemd, demonstrating real-world DevOps deployment practices.

📌 Architecture Overview
🧠 System Architecture
┌──────────────────────────────┐
│        Client Browser        │
└──────────────┬───────────────┘
               │ HTTP (port 80)
               ▼
┌──────────────────────────────┐
│            Nginx             │  ← Reverse Proxy
│  - Static routing            │
│  - Proxy /api → backend      │
└──────────────┬───────────────┘
               │ localhost:5000
               ▼
┌──────────────────────────────┐
│          Gunicorn            │  ← WSGI Server
│  - Multiple workers          │
│  - Process management        │
└──────────────┬───────────────┘
               │ WSGI
               ▼
┌──────────────────────────────┐
│        Flask Application     │
│  - Metrics API               │
│  - Alerts Engine             │
│  - Process Analyzer          │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│     Linux System Layer       │
│  - CPU / RAM / Disk metrics  │
│  - Process monitoring        │
└──────────────────────────────┘
⚙️ Tech Stack
Backend: Python 3, Flask
Monitoring: psutil
WSGI Server: Gunicorn
Reverse Proxy: Nginx
Process Manager: systemd
OS: Linux (Ubuntu / Debian-based)
Version Control: Git + GitHub (SSH)
🧩 Project Structure
smart-monitor-platform/
│
├── cli/                 # CLI tools
├── core/                # Core monitoring engine
│   ├── metrics.py      # System metrics collector
│   ├── alerts.py       # Alert engine
│   ├── analyzer.py     # Process analysis
│   ├── logger.py       # Logging system
│   ├── database.py     # SQLite integration
│   └── processes.py    # Process inspection
│
├── dashboard/          # Web UI (Flask app)
│   ├── app.py
│   ├── templates/
│   └── static/
│
├── logs/               # Runtime logs & DB
├── venv/               # Virtual environment (not committed)
├── requirements.txt
└── README.md


🧪 Local Development Setup (Linux)
1. Clone Repository
git clone git@github.com:sewar1/smart-monitor-platform.git
cd smart-monitor-platform
2. Create Virtual Environment
python3 -m venv venv
source venv/bin/activate
3. Install Dependencies
pip install flask psutil requests gunicorn
4. Run Flask App (Development)
python dashboard/app.py

OR production-style:

gunicorn --bind 0.0.0.0:5000 dashboard.app:app
🌐 Production Deployment (Linux)
Step 1 — Gunicorn Service

Run backend as a persistent service:

gunicorn --bind 127.0.0.1:5000 dashboard.app:app
Step 2 — systemd Service

Service file:

[Unit]
Description=Smart Monitor Platform
After=network.target

[Service]
User=seka
WorkingDirectory=/home/seka/smart-monitor-platform
ExecStart=/home/seka/smart-monitor-platform/venv/bin/gunicorn --bind 127.0.0.1:5000 dashboard.app:app
Restart=always

[Install]
WantedBy=multi-user.target

Enable:

sudo systemctl daemon-reload
sudo systemctl enable smart-monitor
sudo systemctl start smart-monitor
Step 3 — Nginx Reverse Proxy

Config:

server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

Reload:

sudo nginx -t
sudo systemctl reload nginx
🔌 API Endpoints
Metrics API
GET /api/metrics
Response:
{
  "health": {
    "score": 73.0,
    "status": "Warning"
  },
  "nodes": [
    {
      "name": "server-1",
      "cpu": 5.6,
      "ram": 44.7,
      "disk": 33.6
    }
  ],
  "alerts": []
}
🧠 What I Built (Linux & DevOps Skills Demonstrated)

✔ Linux system monitoring
✔ Process inspection (psutil)
✔ Logging & alert engine
✔ Flask REST API
✔ WSGI production server (Gunicorn)
✔ Reverse proxy (Nginx)
✔ systemd service management
✔ Git workflow + SSH deployment

📸 Proof of Deployment Flow
Flask App → Gunicorn → systemd → Nginx → Linux Host
🚀 Future Improvements (VERY IMPORTANT FOR JOBS)
1. Containerization (Docker)
Dockerfile
docker-compose
2. CI/CD Pipeline
GitHub Actions:
lint
test
auto deploy
3. Observability Layer
Prometheus metrics export
Grafana dashboards
4. Security Enhancements
HTTPS (Let's Encrypt)
API authentication (JWT)
5. Scalability
Multi-node monitoring
Redis queue for alerts
This project demonstrates a full DevOps lifecycle:

Code → Build → Run → Deploy → Proxy → Service Management → Monitoring
