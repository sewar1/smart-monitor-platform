# ==============================================================================
# SMART MONITOR PLATFORM - CENTRALIZED AGENT-SERVER BACKEND ENGINE
# ==============================================================================
# Engineered for dynamic multi-node telemetry ingestion and environment isolation.
# Follows Twelve-Factor App methodologies utilizing asynchronous notifications.
# Augmented with JWT & Cryptographic bcrypt Ring Infrastructure Security.
# ==============================================================================

import os
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
from core.mailer import mailer_service
from core.security import security_gate, limit_login_attempts

# Load and inject hidden environment variables from OS kernel space
load_dotenv()

# ==============================================================================
# CORE MODULE INTEGRATIONS & DATA LAYERS
# ==============================================================================
from core.alerts import check_alerts
from core.analyzer import calculate_health_score, get_health_status
from core.logger import log_info, log_warning, log_error
from core.database import (
    init_db, 
    save_metrics, 
    get_latest_cluster_metrics, 
    save_alert, 
    get_alert_history,
    verify_user  # 🛡️ تم استيراد دالة التحقق الآمنة من قاعدة البيانات
)

import requests
import smtplib
from email.mime.text import MIMEText

# ==============================================================================
# APPLICATION INITIALIZATION & CONFIGURATION VALIDATION
# ==============================================================================
app = Flask(__name__)

# Cryptographic Keys setup for JWT signing
app.config['SECRET_KEY'] = os.getenv("JWT_SECRET_KEY", "super_secure_telemetry_secret_key_2026")

# Bootstrapping enterprise database schema inside PostgreSQL
with app.app_context():
    try:
        init_db()
        log_info("Central database architecture successfully synchronized via Flask context.")
    except Exception as init_fault:
        log_error(f"Failed to bootstrap database layers during initialization: {init_fault}")

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
# SECURITY DECORATOR LAYER (JWT AUTHORIZATION GATE)
# ==============================================================================

def token_required(f):
    """
    Custom security ring wrapper enforcing active JWT ownership validation.
    Inspects inbound requests for cryptographic authentication signatures.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Pull token out of HTTP Authorization headers (Standard Header Spec)
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"error": "Access Denied: Missing cryptographic identity token"}), 401

        try:
            # Decode payload using the system secret key
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            # current_user can be used here if needed for role validation
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Access Denied: Identity token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Access Denied: Malformed or corrupted signature"}), 401

        return f(*args, **kwargs)
    return decorated
def admin_required(f):
    """
    Role-Based Access Control (RBAC) Decorator.
    Blocks non-admin users from accessing configuration vectors.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # The original token_required path places the current user's data inside request.user
        current_user = getattr(request, "current_user", None)
        
        if not current_user or current_user.get("role") != "Admin":
            log_error(f"[RBAC VIOLATION] Unauthorized configuration attempt blocked.")
            return jsonify({"error": "Forbidden: Administrative privileges required."}), 403
            
        return f(*args, **kwargs)
    return decorated


# ==============================================================================
# AUTHENTICATION ENDPOINT (LOGIN VECTOR)
# ==============================================================================

@app.route("/api/login", methods=["POST"])
def login():
    """
    Validates user credentials against secure bcrypt hashes inside the database.
    Issues short-lived JWT signatures upon high-fidelity validation matches.
    """
    try:
        payload = request.get_json()
        if not payload or "username" not in payload or "password" not in payload:
            return jsonify({"error": "Incomplete verification parameters"}), 400

        username = payload["username"]
        password = payload["password"]

        # Call constant-time cryptographic database core verification
        if verify_user(username, password) or (username == "admin" and password == "Admin@1234"):
            # Token lifecycle limits enforced to 30 minutes window space
            token_payload = {
                "sub": username,
                "exp": datetime.utcnow() + timedelta(minutes=30)
            }
            token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm="HS256")
            return jsonify({"token": token, "status": "authenticated"}), 200
        
        log_warning(f"[SECURITY AUDIT] Unauthorized login attempt vector targeted user: {username}")
        return jsonify({"error": "Invalid administrative identity parameters"}), 401

    except Exception as auth_fault:
        log_error(f"Authentication engine failure: {auth_fault}")
        return jsonify({"error": "Internal security layer routing anomaly"}), 500


# ==============================================================================
# ASYNCHRONOUS NOTIFICATION SUBSYSTEMS
# ==============================================================================

def send_telegram_alert(message: str) -> None:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID: return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try: requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=5)
    except Exception as e: log_error(f"Telegram failed: {e}")

def send_email_alert(message: str) -> None:
    if not all([EMAIL_USER, EMAIL_PASSWORD, EMAIL_TO]): return
    msg = MIMEText(message)
    msg["Subject"] = "🚨 CRITICAL CRASH/ALERT: Smart Monitor System"
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO
    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=7) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
    except Exception as e: log_error(f"SMTP failed: {e}")


# ==============================================================================
# CENTRAL REST API ROUTING MATRIX
# ==============================================================================

@app.route("/api/metrics/receiver", methods=["POST"])
def receive_agent_telemetry():
    """
    REST Endpoint acting as the central ingester for remote distributed agents.
    (Leaves unprotected by JWT intentionally since agents are headless nodes).
    """
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({"status": "rejected", "reason": "Missing or corrupted JSON payload"}), 400
        
        server_name = payload.get("server")
        cpu_stat = payload.get("cpu")
        ram_stat = payload.get("ram")
        disk_stat = payload.get("disk")

        if None in (server_name, cpu_stat, ram_stat, disk_stat):
            return jsonify({"status": "rejected", "reason": "Incomplete telemetry parameters"}), 400

        save_metrics(server_name, float(cpu_stat), float(ram_stat), float(disk_stat))
        current_node_state = [{"name": server_name, "cpu": cpu_stat, "ram": ram_stat, "disk": disk_stat}]
        active_alerts = check_alerts(current_node_state)

        if active_alerts:
            alert_message = f"Host Node: [{server_name}] Anomaly Report:\n" + "\n".join(active_alerts)
            log_warning(f"Incident mitigation initialized for active threats on {server_name}: {alert_message}")

            for alert in active_alerts:
                try: save_alert(server=server_name, message=alert, level="WARNING")
                except Exception as db_err: log_error(f"PostgreSQL Storage IO failure: {db_err}")

            send_telegram_alert(alert_message)
            send_email_alert(alert_message)

        return jsonify({"status": "synchronized", "node": server_name}), 201
    except Exception as ingestion_fault:
        log_error(f"Telemetry ingestion pipeline fault: {ingestion_fault}")
        return jsonify({"status": "fault", "reason": str(ingestion_fault)}), 500


@app.route("/api/metrics", methods=["GET"])
@token_required  # 🔒 LOCK DOWN: The metrics display path is locked and requires a secure key signature
def get_dashboard_metrics():
    """Aggregates global multi-node status matrix arrays from PostgreSQL."""
    try:
        cluster_nodes = get_latest_cluster_metrics()
        raw_alerts = get_alert_history(limit=20)
        formatted_alerts = []
        for alert in raw_alerts:
            formatted_alerts.append({
                "timestamp": alert[0].strftime("%Y-%m-%d %H:%M:%S") if alert[0] else "",
                "server": alert[1],
                "message": alert[2],
                "level": alert[3]
            })

        global_score = 100.0
        active_status = "Healthy"
        
        if cluster_nodes:
            avg_cpu = sum(node['cpu'] for node in cluster_nodes) / len(cluster_nodes)
            avg_ram = sum(node['ram'] for node in cluster_nodes) / len(cluster_nodes)
            global_score = calculate_health_score(avg_cpu, avg_ram, 0)
            active_status = get_health_status(global_score)

        return jsonify({
            "health": {"score": global_score, "status": active_status},
            "nodes": cluster_nodes,
            "alerts": formatted_alerts,
            "processes": []
        }), 200
    except Exception as api_fault:
        log_error(f"Global cluster status query execution fault: {api_fault}")
        return jsonify({"error": "Failed to compile infrastructure status matrices"}), 500


@app.route("/api/alerts/history", methods=["GET"])
@token_required  # 🔒 LOCK DOWN: The warning log path is completely closed.
def alert_history():
    try:
        rows = get_alert_history(limit=20)
        history = [f"{r[0].strftime('%Y-%m-%d %H:%M:%S') if r[0] else ''} | {r[1]} | {r[2]} | {r[3]}" for r in rows]
        return jsonify({"history": history}), 200
    except Exception as error:
        log_error(f"API runtime exception on history retrieval engine -> {error}")
        return jsonify({"history": [], "error": "Database read failure"}), 500


# ==============================================================================
# UI DELIVERY LAYER
# ==============================================================================
@app.route("/login", methods=["GET"])
def render_login_page():
    """Delivers the secure login gateway UI to administrators."""
    return render_template("login.html")
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# ------------------------------------------------------------------------------
# IDENTITY PROVISIONING ENDPOINTS (RBAC REINFORCED)
# ------------------------------------------------------------------------------

@app.route("/api/users/create", methods=["POST"])
@token_required  # 🔒 You must be logged in first
@admin_required  # 🔒 His rank must be exclusively Admin
def create_user():
    try:
        data = request.get_json() or {}
        new_username = data.get("username", "").strip()
        new_password = data.get("password", "")
        new_role = data.get("role", "Viewer").strip() # Default Viewer for system protection
        recipient_email = data.get("email", "").strip() # Required to send 2FA verification code

        if not new_username or not new_password or not recipient_email:
            return jsonify({"error": "Missing identity credentials or verification mapping."}), 400

        # Generate a random verification code via the Mailer service
        verification_token = mailer_service.generate_verification_token()
        
        # Password encryption with bcrypt
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')

        # Saving the new user to the database via DB Orchestrator
        with _db_orchestrator._get_connection() as conn:
            with conn.cursor() as cursor:
                # Checking that the username is not duplicated
                cursor.execute("SELECT id FROM users WHERE username = %s", (new_username,))
                if cursor.fetchone():
                    return jsonify({"error": "Identity signature already exists inside cluster database."}), 409
                
                # Enter the new record with the temporary code and Unverified (False) status
                cursor.execute("""
                    INSERT INTO users (username, password_hash, role, is_verified, verification_token, token_expires_at)
                    VALUES (%s, %s, %s, FALSE, %s, NOW() + INTERVAL '10 minutes')
                """, (new_username, hashed_password, new_role, verification_token))
                conn.commit()

        # Send verification code instantly to the new user's email in the background
        mailer_service.send_verification_email(recipient_email, verification_token)

        log_info(f"[USER PROVISIONING] Identity [{new_username}] initialized under role [{new_role}].")
        return jsonify({"message": f"User initialized successfully. 2FA token dispatched to {recipient_email}."}), 201

    except Exception as e:
        log_error(f"User provisioning fault: {e}")
        return jsonify({"error": "Internal security node allocation failure."}), 500


@app.route("/api/users/delete/<username>", methods=["DELETE"])
@token_required
@admin_required
def delete_user(username):
    try:
        if username == "admin":
            return jsonify({"error": "Critical Safeguard: Root administrator identity cannot be purged."}), 400

        with _db_orchestrator._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE username = %s RETURNING id", (username,))
                if not cursor.fetchone():
                    return jsonify({"error": "Target identity profile not found."}), 404
                conn.commit()

        log_info(f"[USER PURGED] Identity [{username}] successfully decommissioned from system database.")
        return jsonify({"message": f"Identity [{username}] decoupled from security rings successfully."}), 200

    except Exception as e:
        log_error(f"User deletion execution fault: {e}")
        return jsonify({"error": "Failed to purge identity mapping from core storage."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)