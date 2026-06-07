# ==============================================================================
# SMART MONITOR PLATFORM - PRODUCTION-GRADE BACKEND ENGINE
# ==============================================================================
# Engineered for high-availability DevOps monitoring and environment isolation.
# Follows Twelve-Factor App methodologies utilizing asynchronous notifications.
# ==============================================================================

import os
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv

# Load and inject hidden environment variables from OS kernel space
load_dotenv()

# ==============================================================================
# CORE MODULE INTEGRATIONS
# ==============================================================================
from core.metrics import get_system_metrics
from core.alerts import check_alerts
from core.analyzer import (
    calculate_health_score,
    get_health_status,
    get_top_processes
)
from core.logger import log_info, log_warning, log_error
from core.database import init_db, save_alert, get_alert_history

import requests
import smtplib
from email.mime.text import MIMEText

# ==============================================================================
# APPLICATION INITIALIZATION & CONFIGURATION VALIDATION
# ==============================================================================
app = Flask(__name__)

# Initialize persistence layer (SQLite Embedded DB)
init_db()

# Read configurations dynamically from Host OS Environment Variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO")

# Fail-Fast Validation: Ensure secure credentials exist before handling requests
if not all([TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, EMAIL_USER, EMAIL_PASSWORD, EMAIL_TO]):
    log_warning("System initialized with missing or partial environment credentials. Check your .env configuration.")
else:
    log_info("Smart Monitor Platform successfully bounded to secure OS Environment Variables.")


# ==============================================================================
# ASYNCHRONOUS NOTIFICATION SUBSYSTEMS
# ==============================================================================

def send_telegram_alert(message: str) -> None:
    """
    Dispatches alerts to the administrative Telegram channel via Bot API.
    Guarded with strict network timeouts to ensure API responsiveness.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log_error("Aborted Telegram alert dispatch: Missing credentials inside kernel env.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    try:
        # 5-second timeout enforces network boundary isolation
        response = requests.post(url, data=payload, timeout=5)
        if response.status_code == 200:
            log_info("Incident log pushed successfully to Telegram Gateway.")
        else:
            log_error(f"Telegram Gateway rejected payload with status code: {response.status_code}")
    except requests.exceptions.RequestException as net_error:
        log_error(f"Network boundary isolation triggered: Telegram routing failed -> {net_error}")


def send_email_alert(message: str) -> None:
    """
    Transmits incident reports to System Administrators via encrypted TLS SMTP.
    Uses context managers to avoid unclosed sockets/file descriptors on crashes.
    """
    if not all([EMAIL_USER, EMAIL_PASSWORD, EMAIL_TO]):
        log_error("Aborted Email alert dispatch: Incomplete SMTP environment definitions.")
        return

    msg = MIMEText(message)
    msg["Subject"] = "🚨 CRITICAL CRASH/ALERT: Smart Monitor System"
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO

    try:
        # Utilizing standard secure TLS port 587
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=7) as server:
            server.starttls()  # Upgrade connection to secure TLS layer
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
        log_info("Incident email delivered to administrative inbox.")
    except Exception as smtp_error:
        log_error(f"Infrastructure core fault: SMTP transport mechanism crashed -> {smtp_error}")


# ==============================================================================
# CENTRAL REST API ROUTING MATRIX
# ==============================================================================

@app.route("/api/metrics", methods=["GET"])
def metrics():
    """
    Main metrics ingestion route. Polled asynchronously by frontend engines.
    Aggregates Linux telemetry, checks alarm states, and executes automatic persistence.
    """
    log_info("Ingested standard poll request on API Endpoint: /api/metrics")

    try:
        # STEP 1: Harvest low-level Linux metrics via psutil abstract layers
        data = get_system_metrics()
        nodes = data.get("nodes", [])
        
        if not nodes:
            raise ValueError("Telemetry core returned an empty node structure.")

        node = nodes[0]

        # STEP 2: Execute state analysis and alert triggers
        alerts = check_alerts(nodes)
        processes = get_top_processes()

        # STEP 3: Generate complex system health score matrix
        health_score = calculate_health_score(node.get("cpu", 0), node.get("ram", 0), node.get("disk", 0))
        health_status = get_health_status(health_score)

        # STEP 4: Build normalized JSON response payload
        data["alerts"] = alerts
        data["processes"] = processes
        data["health"] = {
            "score": health_score,
            "status": health_status
        }

        # STEP 5: Automated incident response and logging
        if alerts:
            alert_message = "\n".join(alerts)
            log_warning(f"Incident mitigation initialized for active threats: {alert_message}")

            # Persist alerts locally into SQLite database
            for alert in alerts:
                try:
                    save_alert(server=node.get("name", "linux-node"), message=alert, level="WARNING")
                except Exception as db_err:
                    log_error(f"Local storage IO failure: Database write halted -> {db_err}")

            # Dispatch external notifications safely
            send_telegram_alert(alert_message)
            send_email_alert(alert_message)

        return jsonify(data), 200

    except Exception as runtime_err:
        log_error(f"API runtime exception captured on metrics engine -> {runtime_err}")
        return jsonify({"error": "Internal Server Telemetry Fault", "status": 500}), 500


@app.route("/api/alerts/history", methods=["GET"])
def alert_history():
    """
    Fetches legacy historical warnings recorded by systemd inside the local DB.
    """
    try:
        rows = get_alert_history(limit=20)
        history = [f"{r[0]} | {r[1]} | {r[2]} | {r[3]}" for r in rows]
        return jsonify({"history": history}), 200
    except Exception as error:
        log_error(f"API runtime exception on history retrieval engine -> {error}")
        return jsonify({"history": [], "error": "Database read failure"}), 500


# ==============================================================================
# UI DELIVERY LAYER
# ==============================================================================

@app.route("/", methods=["GET"])
def index():
    """
    Delivers base HTML layout matrix to standard web browsers.
    """
    return render_template("index.html")


# ==============================================================================
# SYSTEM BOOTSTRAPPER (LOCAL RUNTIME)
# ==============================================================================
if __name__ == "__main__":
    log_info("Starting local development webserver matrix...")
    # use_reloader=False prevents double service instantiation bugs in local test environments
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)