# Smart Monitor Platform

Real-time Linux monitoring system built with Flask, Gunicorn, Nginx, and systemd.
Designed to simulate a production DevOps environment.

---

## Architecture


Client Browser
|
v
Nginx (Reverse Proxy)
|
v
Gunicorn (WSGI Server)
|
v
Flask Application
|
v
Linux System Metrics (CPU / RAM / Disk / Processes)


---

## Tech Stack

- Python 3
- Flask
- psutil
- Gunicorn
- Nginx
- systemd
- Linux (Ubuntu/Debian)
- Git + GitHub (SSH)

---

## Project Structure


smart-monitor-platform/
│
├── cli/
├── core/
│ ├── metrics.py
│ ├── alerts.py
│ ├── analyzer.py
│ ├── logger.py
│ ├── database.py
│ └── processes.py
│
├── dashboard/
│ ├── app.py
│ ├── templates/
│ └── static/
│
├── logs/
├── venv/
└── README.md


---

## Installation (Local Linux Setup)

### 1. Clone Repository
```bash
git clone git@github.com:sewar1/smart-monitor-platform.git
cd smart-monitor-platform
2. Create Virtual Environment
python3 -m venv venv
source venv/bin/activate
3. Install Dependencies
pip install flask psutil requests gunicorn
Run Application
Development Mode
python dashboard/app.py
Production Mode
gunicorn --bind 0.0.0.0:5000 dashboard.app:app
Production Deployment
systemd Service

Create service file:

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

Enable service:

sudo systemctl daemon-reload
sudo systemctl enable smart-monitor
sudo systemctl start smart-monitor
Nginx Reverse Proxy

Configuration:

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

Reload Nginx:

sudo nginx -t
sudo systemctl reload nginx
API Endpoint
GET /api/metrics

Example response:

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
What This Project Demonstrates
Linux system administration
Process monitoring with psutil
REST API development (Flask)
Production WSGI deployment (Gunicorn)
Reverse proxy setup (Nginx)
systemd service management
Git + SSH workflow
Deployment Flow
Flask → Gunicorn → systemd → Nginx → Client
Future Improvements
Docker containerization
CI/CD pipeline (GitHub Actions)
Prometheus + Grafana monitoring
HTTPS with Let's Encrypt
JWT authentication
Multi-node monitoring
Summary

This project demonstrates a complete DevOps lifecycle from development to production deployment on Linux.
