# Operational Core & Deep Infrastructure Subsystems
The `core` directory serves as the decoupled, underlying business logic backbone of the whole platform. It maps data transformations, handles alerts, and controls relational data operations.

## Functional Structural Subsystems
- **PostgreSQL Abstraction Mapping (`database.py`):** Establishes database pool routines, manages structural schema mappings, and coordinates transactions safely.
- **Enterprise Notification Alerters (`alerts.py`, `mailer.py`):** Evaluates incoming telemetry signals against thresholds; pushes warning messages out to dedicated administrative **Telegram Bots** and transactional **SMTP email servers**.
- **Process Profiler & Analytical Tools (`processes.py`, `analyzer.py`):** Inspects active runtime PIDs, extracts high-footprint anomalies, and pipes metrics to the ledger tracking nodes.
- **Cryptographic Security Ring (`security.py`):** Powers hashing layers via `bcrypt` to protect stored credentials, handles token creation seeds, and manages signing validations.

## Structural File Blueprint
- **`database.py`**: Connectors managing pool threads directly talking to PostgreSQL.
- **`security.py`**: Security controller wrapping salting mechanisms and stateless JWT token signing keys.
- **`alerts.py` & `mailer.py`**: Automated alerting delivery vectors processing warning states.
- **`metrics.py` & `processes.py`**: Translators turning low-level kernel sensor logs into tabular structures.

---

## Legacy Native Linux Deployment (Alternative Setup)
If you wish to deploy directly to bare-metal systemd layers without containers (Simulated on VMware Bare-Metal):
1. Create virtual environment & dependencies
``` bash
python3 -m venv venv
source venv/bin/activate
pip install flask psutil requests gunicorn psycopg2-binary
```
2. Running the Application
   Development mode:
   ``` bash
   python dashboard/app.py
    ```
    Production execution via Gunicorn
    ```bash
    gunicorn --bind 0.0.0.0:5000 dashboard.app:app
    ```
---
3. systemd Service Setup (/etc/systemd/system/smart-monitor.service)
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
### Enable and start service
``` bash
sudo systemctl daemon-reload
sudo systemctl enable smart-monitor
sudo systemctl start smart-monitor
```
4. Nginx configuration
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
Reload Nginx:
``` bash
sudo nginx -t
sudo systemctl reload nginx
```
---

#### Production Deployment & Infrastructure Status

The application is integrated into the Linux service layers via systemd and Nginx. Below is the verified status of the services running in production.

![Nginx and System Services Status](screenshots/nginx-status.png)
*Figure 3: Active production verification for reverse proxy and backend services.*

---

## Production Verification (VMware Infrastructure Status)
Below is the verified operational status of the core infrastructure daemons running natively on the Linux server.

Figure 3: Active production verification for reverse proxy and systemd backend services.
