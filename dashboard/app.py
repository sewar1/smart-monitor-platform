# ==========================================
# SMART MONITOR PLATFORM - APP
# ==========================================
# Real-time DevOps Monitoring Backend
# ==========================================

from flask import Flask, render_template, jsonify

# ==========================================
# CORE MODULES
# ==========================================

from core.metrics import get_system_metrics
from core.alerts import check_alerts
from core.analyzer import (
    calculate_health_score,
    get_health_status,
    get_top_processes
)

from core.logger import log_info, log_warning, log_error
from core.database import init_db, save_alert, get_alert_history

from collections import deque

import requests
import smtplib
from email.mime.text import MIMEText

# ==========================================
# APP INITIALIZATION
# ==========================================

app = Flask(__name__)

init_db()  # <-- مهم: تشغيل SQLite عند البداية

log_info("Smart Monitor Platform initialized")


# ==========================================
# CONFIGURATION
# ==========================================

TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

EMAIL = "your_email@gmail.com"
PASSWORD = "your_app_password"
TO_EMAIL = "target_email@gmail.com"


# ==========================================
# TELEGRAM ALERT SYSTEM
# ==========================================

def send_telegram_alert(message: str):
    """
    Send alerts to Telegram bot.
    """

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as error:
        log_error(f"Telegram notification failed: {error}")


# ==========================================
# EMAIL ALERT SYSTEM
# ==========================================

def send_email_alert(message: str):
    """
    Send alerts via SMTP email.
    """

    msg = MIMEText(message)
    msg["Subject"] = "Smart Monitor Alert"
    msg["From"] = EMAIL
    msg["To"] = TO_EMAIL

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
        server.quit()

    except Exception as error:
        log_error(f"Email notification failed: {error}")


# ==========================================
# MAIN METRICS API
# ==========================================

@app.route("/api/metrics")
def metrics():

    log_info("Metrics endpoint called")

    # STEP 1: COLLECT METRICS
    data = get_system_metrics()
    nodes = data["nodes"]

    # STEP 2: ALERTS
    alerts = check_alerts(nodes)

    # STEP 3: PROCESS ANALYSIS
    processes = get_top_processes()

    # STEP 4: HEALTH ANALYSIS
    node = nodes[0]

    health_score = calculate_health_score(
        node["cpu"],
        node["ram"],
        node["disk"]
    )

    health_status = get_health_status(health_score)

    # attach to response
    data["alerts"] = alerts
    data["processes"] = processes
    data["health"] = {
        "score": health_score,
        "status": health_status
    }

    # STEP 5: SAVE + NOTIFY
    if alerts:

        for alert in alerts:

            log_warning(alert)

            # store in SQLite
            try:
                save_alert(
                    server="system",
                    message=alert,
                    level="WARNING"
                )
            except Exception as e:
                log_error(f"DB save failed: {e}")

        alert_message = "\n".join(alerts)

        send_telegram_alert(alert_message)
        send_email_alert(alert_message)

    return jsonify(data)


# ==========================================
# FRONTEND
# ==========================================

@app.route("/")
def index():
    return render_template("index.html")


# ==========================================
# ALERT HISTORY (SQLite-backed)
# ==========================================

@app.route("/api/alerts/history")
def alert_history():

    try:
        rows = get_alert_history(limit=20)

        history = [
            f"{r[0]} | {r[1]} | {r[2]} | {r[3]}"
            for r in rows
        ]

        return jsonify({"history": history})

    except Exception as error:
        log_error(f"History fetch failed: {error}")
        return jsonify({"history": []})


# ==========================================
# START SERVER
# ==========================================

if __name__ == "__main__":

    log_info("Flask server starting")

    app.run(
        debug=True,
        use_reloader=False
    )