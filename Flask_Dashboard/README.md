# 📡 Flask System Monitor Dashboard

A real-time system monitoring dashboard built with Flask and psutil, featuring live charts and auto-refreshing UI.

---

## 🚀 Features

- 📊 Real-time CPU monitoring
- 🧠 Live RAM usage tracking
- 💾 Disk usage visualization
- 🔄 Auto-refresh dashboard (no page reload)
- 📈 Interactive charts using Chart.js
- 🌙 Clean dark-mode UI

---

## 🧩 How It Works

- Backend uses **psutil** to collect system metrics
- Flask exposes an API endpoint: `/api/metrics`
- Frontend fetches data using JavaScript (Fetch API)
- Charts update dynamically using Chart.js

---

## 🌐 Usage

Open your browser: `http://127.0.0.1:5000`

---


## 🧠 Tech Stack

- Python (Flask)
- psutil
- HTML / CSS
- JavaScript (Chart.js)
- Bootstrap

---

## 📊 Dashboard Preview

![Dashboard Screenshot](screenshot.png)

---

## 💡 Future Improvements

- 🚨 Alert system (Email / Telegram)
- 🖥 Multi-machine monitoring
- 🐳 Docker containerization
- 🔐 Authentication & user roles

---

## 👨‍💻 Author

Built as a hands-on DevOps learning project to practice:

- System monitoring
- Backend API design
- Real-time dashboards

---

## ⚙️ Installation

```bash
git clone https://github.com/sewar1/flask-system-monitor.git
cd flask-system-monitor
pip install -r requirements.txt
python app.py
