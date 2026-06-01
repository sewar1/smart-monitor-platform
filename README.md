# Smart Monitor Platform

A Linux-based real-time monitoring system built using Flask, Gunicorn, Nginx, and systemd.  
The project simulates a production-grade DevOps deployment environment.

---

## Overview

This project collects system metrics such as CPU, RAM, Disk usage, and running processes, and exposes them via a REST API and web dashboard.

It is designed for DevOps learning, Linux administration practice, and production deployment simulation.

---

## Tech Stack

- Python 3
- Flask (REST API)
- psutil (system metrics collection)
- Gunicorn (WSGI server)
- Nginx (reverse proxy)
- systemd (service management)
- Linux (Ubuntu/Debian)
- Git & GitHub

---


---

## Installation

### Clone repository

``` bash
git clone git@github.com:sewar1/smart-monitor-platform.git
cd smart-monitor-platform
```

### Create virtual environment
``` bash
python3 -m venv venv
source venv/bin/activate
```

### Install dependencies
```bash
pip install flask psutil requests gunicorn
```
### Running the Application
## Development mode
```bash
python dashboard/app.py
```
## Production mode (Gunicorn)
```bash
gunicorn --bind 0.0.0.0:5000 dashboard.app:app
```
---

## Production Deployment
### systemd service setup

### Create service file:
## Project Structure
```bash
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
```
## Enable and start service
``` bash
sudo systemctl daemon-reload
sudo systemctl enable smart-monitor
sudo systemctl start smart-monitor
```

### Nginx configuration
```bash
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
```
## Reload Nginx:
``` bash
sudo nginx -t
sudo systemctl reload nginx
```
## API Endpoint
### GET /api/metrics
```bash

Returns real-time system metrics:
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
```
---

### Features
- Real-time system monitoring
- CPU / RAM / Disk tracking
- Process analytics
- Alert system
- REST API for integration
- Production-ready deployment stack
- What This Project Demonstrates
- Linux server administration
- Flask backend development
- Production WSGI deployment
- Nginx reverse proxy configuration
- systemd service management
- DevOps workflow (build → deploy → run)

---

### Future Improvements
- Docker containerization
- CI/CD pipeline (GitHub Actions)
- Prometheus & Grafana integration
- HTTPS with Let’s Encrypt
- Authentication system (JWT)
- Multi-node monitoring support

---

### Summary

This project demonstrates a complete DevOps lifecycle from development to production deployment on a Linux server.
