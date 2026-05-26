# ==============================
# IMPORTS
# ==============================

from flask import Flask, render_template, jsonify
from core.metrics import get_system_metrics 
import requests                    # For sending Telegram alerts
import smtplib                     # For sending email alerts
from email.mime.text import MIMEText  # For building email messages

# ==============================
# FLASK APP INITIALIZATION
# ==============================

app = Flask(__name__)

# ==============================
# CONFIGURATION
# ==============================

# Telegram configuration (Bot token + chat ID)
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

# Email configuration (SMTP - Gmail example)
EMAIL = "your_email@gmail.com"
PASSWORD = "your_app_password"   # MUST be App Password (not real password)
TO_EMAIL = "target_email@gmail.com"


# ==============================
# SYSTEM METRICS SIMULATION
# ==============================


# ==============================
# ALERT ENGINE (RULE-BASED SYSTEM)
# ==============================

def check_alerts(nodes):
    """
    Evaluates system metrics against thresholds.
    This mimics real-world alerting systems like Prometheus Alertmanager.
    """

    alerts = []

    for node in nodes:

        # CPU threshold check
        if node["cpu"] > 85:
            alerts.append(
                f"{node['name']} - HIGH CPU USAGE: {node['cpu']:.1f}%"
            )

        # RAM threshold check
        if node["ram"] > 85:
            alerts.append(
                f"{node['name']} - HIGH RAM USAGE: {node['ram']:.1f}%"
            )

    return alerts


# ==============================
# TELEGRAM NOTIFICATION SYSTEM
# ==============================

def send_telegram_alert(message):
    """
    Sends alert messages to a Telegram bot using Telegram API.
    This is commonly used in DevOps for real-time incident notifications.
    """

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram notification failed:", e)


# ==============================
# EMAIL NOTIFICATION SYSTEM
# ==============================

def send_email_alert(message):
    """
    Sends alert emails using SMTP (Gmail server in this case).
    Used in enterprise systems for incident reporting and logging.
    """

    msg = MIMEText(message)
    msg["Subject"] = "DevOps Alert - System Monitoring"
    msg["From"] = EMAIL
    msg["To"] = TO_EMAIL

    try:
        # Connect to Gmail SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)

        # Enable encryption
        server.starttls()

        # Login to email account
        server.login(EMAIL, PASSWORD)

        # Send email
        server.send_message(msg)

        # Close connection
        server.quit()

    except Exception as e:
        print("Email notification failed:", e)


# ==============================
# API ENDPOINT (CORE MONITORING DATA)
# ==============================

@app.route("/api/metrics")
def metrics():
    """
    Core monitoring endpoint.

    Workflow:
    1. Collect system metrics (multi-node simulation)
    2. Analyze metrics for anomalies
    3. Trigger alerts if necessary
    4. Return data to frontend dashboard
    """

    # Step 1: Collect system data
    data = get_system_metrics()
    nodes = data["nodes"]

    # Step 2: Analyze system state
    alerts = check_alerts(nodes)

    # Step 3: Trigger notifications if alerts exist
    if alerts:
        alert_message = "\n".join(alerts)

        send_telegram_alert(alert_message)
        send_email_alert(alert_message)

    # Step 4: Return JSON response to frontend
    return jsonify(data)


# ==============================
# FRONTEND ROUTE
# ==============================

@app.route("/")
def index():
    """
    Renders the main dashboard UI.
    """
    return render_template("index.html")


# ==============================
# APPLICATION ENTRY POINT
# ==============================

if __name__ == "__main__":
    """
    Starts Flask development server.
    In production, this should be replaced with a WSGI server (e.g. Gunicorn).
    """

    app.run(
        debug=True,
        use_reloader=False
    )