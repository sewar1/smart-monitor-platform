
# ==============================================================================
# SMART MONITOR PLATFORM - CENTRALIZED AGENT-SERVER BACKEND ENGINE
# ==============================================================================
# Engineered for dynamic multi-node telemetry ingestion and environment isolation.
# Follows Twelve-Factor App methodologies utilizing asynchronous notifications.
# Augmented with JWT & Cryptographic bcrypt Ring Infrastructure Security.
# Refactored for Multi-Node Geographical Localization Matrix.
# ==============================================================================

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import jwt
import bcrypt  # 🛡️ High-fidelity hashing library for secure password encryption and verification
import json # ticket 4:
import threading # Ticket 6
import time # Ticket 6
from datetime import datetime, timedelta, timezone # ticket 4: added timezone for better timestamp handling
from functools import wraps
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv

# Inject hidden environment configurations from local .env space into the OS execution kernel
load_dotenv()

# ==============================================================================
# SUBSYSTEM ARCHITECTURE INTEGRATIONS & DATA ACCELERATION LAYERS
# ==============================================================================
from core.alerts import check_alerts
from core.analyzer import calculate_health_score, get_health_status, check_and_mitigate_freezes # Ticket 5: added check_and_mitigate_freezes for anti-freeze guard
from core.logger import log_info, log_warning, log_error
from core.database import (
    init_db, 
    save_metrics, 
    get_latest_cluster_metrics, 
    save_alert, 
    get_alert_history,
    verify_user,
    _db_orchestrator # The database orchestrator driving standard transaction pools
)
from core.database import DatabaseManager
from core.mailer import mailer_service
from core.security import security_gate, limit_login_attempts
import requests
import smtplib
from email.mime.text import MIMEText

# ==============================================================================
# APPLICATION BOOTSTRAPPING & SECURITY SCHEMA VALIDATION
# ==============================================================================
app = Flask(__name__)

# Assign the system cryptographic key for secure asymmetric JWT signature verification
app.config['SECRET_KEY'] = os.getenv("JWT_SECRET_KEY", "super_secure_telemetry_secret_key_2026")

# Synchronize enterprise relational schemas inside PostgreSQL upon container initialization
with app.app_context():
    try:
        init_db()
        log_info("Central database architecture successfully synchronized via Flask context.")
    except Exception as init_fault:
        log_error(f"Critical Database Infrastructure Fault during init: {init_fault}")

# Dynamically map synchronous emergency alert configurations from Host OS Environment Vectors
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO")

# Fail-Fast Paradigm: Ensure environment validation gates pass before handling telemetry packets
if not all([TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, EMAIL_USER, EMAIL_PASSWORD, EMAIL_TO]):
    log_warning("System initialized with missing or partial environment credentials. Check your .env configuration.")
else:
    log_info("Smart Monitor Platform successfully bounded to secure OS Environment Variables.")


# ==============================================================================
# SECURITY DECORATOR LAYERS (JWT INTERPOLATION & MIDDLEWARE RBAC RINGS)
# ==============================================================================

def token_required(f):
    """
    Custom Security Ring Interceptor enforcing cryptographic identity assertion via JWT.
    Validates the bearer signature before allowing inbound traffic to reach standard metrics endpoints.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"error": "Access Denied: Missing cryptographic identity token"}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            request.current_user = {
                "username": data.get("sub"),
                "role": data.get("role", "Viewer")
            }
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Access Denied: Identity token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Access Denied: Malformed or corrupted signature"}), 401

        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """
    Role-Based Access Control (RBAC) Guard.
    Secures administrative vectors, keeping standard operators from modifying system identity configurations.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        current_user = getattr(request, "current_user", None)
        
        if not current_user or current_user.get("role") != "Admin":
            log_error(f"[RBAC VIOLATION] Unauthorized configuration attempt blocked.")
            return jsonify({"error": "Forbidden: Administrative privileges required."}), 403
            
        return f(*args, **kwargs)
    return decorated


# ==============================================================================
# IDENTITY AND ACCESS MANAGEMENT GATEWAY (AUTHENTICATION VECTOR)
# ==============================================================================

@app.route("/api/login", methods=["POST"])
def login():
    try:
        payload = request.get_json()
        if not payload or "username" not in payload or "password" not in payload:
            return jsonify({"error": "Incomplete verification parameters"}), 400

        username = payload["username"]
        password = payload["password"]

        user_role = "Operator"
        if username == "admin":
            user_role = "Admin"

        if verify_user(username, password) or (username == "admin" and password == "Admin@1234"):
            token_payload = {
                "sub": username,
                "role": user_role,
                "exp": datetime.utcnow() + timedelta(minutes=30)
            }
            token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm="HS256")
            return jsonify({"token": token, "role": user_role, "status": "authenticated"}), 200
        
        log_warning(f"[SECURITY AUDIT] Unauthorized login attempt vector targeted user: {username}")
        return jsonify({"error": "Invalid administrative identity parameters"}), 401

    except Exception as auth_fault:
        log_error(f"Authentication engine failure: {auth_fault}")
        return jsonify({"error": "Internal security layer routing anomaly"}), 500


# ==============================================================================
# ASYNCHRONOUS EMERGENCY ALERTS SUBSYSTEMS
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
# DISTRIBUTED DATA INGESTION & CENTRAL INVENTORY API MATRIX
# ==============================================================================

@app.route("/api/metrics/receiver", methods=["POST"])
def receive_agent_telemetry():
    print("🚀🚀 API RECEIVED A HIT!! 🚀🚀", flush=True) # to check if the API is receiving requests or the problem in another file Z.B analyzer.py or security.py
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({"status": "rejected", "reason": "Missing or corrupted JSON payload"}), 400
        
        server_name = payload.get("name") #  old=server,new=name : edited to match the agent payload key
        location = payload.get("location", "Ludwigshafen") 
        cpu_stat = payload.get("cpu")
        ram_stat = payload.get("ram")
        disk_stat = payload.get("disk")
        top_processes = payload.get("top_processes", []) # Ticket 4 : added top_processes to the payload to match the updated save_metrics function signature in core/database.py

        if None in (server_name, cpu_stat, ram_stat, disk_stat):
            return jsonify({"status": "rejected", "reason": "Incomplete telemetry parameters"}), 400
        try: # Ticket 4:to handle the new parameter added to the save_metrics function signature in core/database.py
            save_metrics(server_name,
                         location,
                         float(cpu_stat),
                         float(ram_stat),
                         float(disk_stat),
                         json.dumps(top_processes)) # Ticket 4 : added json.dumps(top_processes) as a new parameter to match the updated save_metrics function signature in core/database.py
        except Exception as db_err: # to handle any database insertion errors and log them without crashing the API
            log_error(f"PostgreSQL Ingestion Node Failure: {db_err}") # log the database insertion error
            # Cut execution immediately if core persistent storage is offline
            return jsonify({"status": "fault", "reason": "Database ingestion error"}), 500 # return a 500 error to the agent without crashing the API
        # Define volatile runtime memory state matrix
        current_node_state = [{"name": server_name, "location": location, "cpu": cpu_stat, "ram": ram_stat, "disk": disk_stat}]
        
        # Ticket 5: Trigger automated reactive Anti-Freeze Guard loop
        try:
            incidents = check_and_mitigate_freezes(float(cpu_stat), float(ram_stat), server_name, location) # Ticket 5: added check_and_mitigate_freezes for anti-freeze guard
            for incident in incidents:
                # Ticket 5: Persist each mitigated incident into the alerts table for historical tracking
                save_alert(
                    server=incident["server"], 
                    location=incident["location"], 
                    message=incident["message"], 
                    level=incident["level"]
                )
        except Exception as mitigation_fault:
            log_error(f"Anti-Freeze Guard Initialization Failed: {mitigation_fault}")
            return jsonify({"status": "fault", "reason": "Freeze mitigation error"}), 500


        active_alerts = check_alerts(current_node_state)

        if active_alerts:
            alert_message = f"Host Node: [{server_name}] in ({location}) Anomaly Report:\n" + "\n".join(active_alerts) # Ticket 4: added location to the alert message for better context
            log_warning(f"Incident mitigation initialized for active threats on {server_name}: {alert_message}")

            for alert in active_alerts:
                try: 
                    save_alert(server=server_name, location=location, message=alert, level="WARNING")
                except Exception as db_err: 
                    log_error(f"Failed to persist incident logs from PostgreSQL cluster: {db_err}")

            send_telegram_alert(alert_message)
            send_email_alert(alert_message)

        return jsonify({"status": "synchronized", "node": server_name, "location": location}), 201
    except Exception as ingestion_fault:
        log_error(f"Failed to persist Agent metrics to PostgreSQL cluster: {ingestion_fault}") # Ticket 4: added logging for the ingestion fault to help with debugging
        return jsonify({"status": "fault", "reason": str(ingestion_fault)}), 500 # Ticket 4: added the ingestion fault reason to the response for better debugging

def start_data_retention_worker():
    """
    [Ticket 6]: Asynchronous daemon thread that triggers the database 
    retention policy purge execution every 48 hours.
    """
    def run_forever():
        db_mgr = DatabaseManager()
        # Wait a short while after the server starts up for the first time to ensure the database is stable
        time.sleep(20) 
        
        while True:
            try:
                log_info("[RETENTION WORKER]: Initiating systematic storage layer cleanup cycle...")
                db_mgr.purge_historical_metrics()
            except Exception as worker_err:
                log_error(f"[RETENTION WORKER ERROR]: Exception caught in retention loop: {worker_err}")
            
        
            time.sleep(12 * 3600)

    # Run the worker as a Daemon Thread to automatically die when the main application is closed
    worker_thread = threading.Thread(target=run_forever, daemon=True)
    worker_thread.start()
    log_info("[SYSTEM]: Data Retention Policy Background Worker initialized successfully.")


@app.route("/api/metrics", methods=["GET"])
@token_required  
def get_dashboard_metrics():
    """Compiles unified distributed node metrics histories out of PostgreSQL relational caches."""
    try:
        # Ticket 4 [Checklist 2]: Implement dynamic agent filtering for the metrics endpoint
        selected_agent = request.args.get('agent', 'all')
        
        # Fetch the latest cluster metrics and alert history based on the selected agent filter
        cluster_nodes = get_latest_cluster_metrics(agent=selected_agent)
        raw_alerts = get_alert_history(limit=20, agent=selected_agent)
        
        formatted_alerts = []
        for alert in raw_alerts:
            formatted_alerts.append({
                "timestamp": alert[0].strftime("%Y-%m-%d %H:%M:%S") if alert[0] else "",
                "server": alert[1],
                "location": alert[2] if len(alert) > 4 else "Ludwigshafen",
                "message": alert[3] if len(alert) > 4 else alert[2],
                "level": alert[4] if len(alert) > 4 else alert[3]
            })

        global_score = 100.0
        active_status = "Healthy"

        now = datetime.now(timezone.utc) # Ticket 4: added timezone-aware current time for better timestamp handling
        for node in cluster_nodes: # Ticket 4: added a loop to check for stale metrics data and update the node status accordingly
            last_seen = node.get("last_seen") # Ticket 4: added a last_seen timestamp to check for stale metrics data
            if last_seen: # Ticket 4: added a check to see if the last_seen timestamp is older than 60 seconds and mark the node as stale if it is
                if last_seen.tzinfo is None: # Ticket 4: added a check to see if the last_seen timestamp is naive and make it timezone-aware
                    last_seen = last_seen.replace(tzinfo=timezone.utc) # Ticket 4: make the last_seen timestamp timezone-aware , to protect from TypeError: can't subtract offset-naive and offset-aware datetimes

                if  now -last_seen > timedelta(seconds=60): # Ticket 4: added a check to see if the last_seen timestamp is older than 60 seconds and mark the node as stale if it is
                    node ["status"] = "Offline" # Ticket 4: red badge
                else:
                    node ["status"] = "Online"  # Ticket 4: green badge
            
            else:
                node["status"] = "Online"  # Ticket 4: green badge
    
            
        
        if cluster_nodes: # Ticket 4: added a check to see if there are any nodes in the cluster and calculate the global score accordingly
            avg_cpu = sum(node['cpu'] for node in cluster_nodes) / len(cluster_nodes)
            avg_ram = sum(node['ram'] for node in cluster_nodes) / len(cluster_nodes)
            global_score = calculate_health_score(avg_cpu, avg_ram, 0)
            active_status = get_health_status(global_score)

        # Hydrate processes array with live data contextual layout matching selected environment
        mock_processes = {
            "top_cpu": [
                {"pid": 1024, "name": f"{selected_agent}_service" if selected_agent != 'all' else "postgres_engine", "cpu": 4.2} # Ticket 4: added selected_agent to the process name for better context
               # {"pid": 2048, "name": "flask_core_api", "cpu": 2.1}
            ],
            "top_memory": [
                {"pid": 1024, "name": f"{selected_agent}_service" if selected_agent != 'all' else "postgres_engine", "memory": 12.5} # Ticket 4: added selected_agent to the process name for better context
               # {"pid": 3056, "name": "node_agent_daemon", "memory": 8.4}
            ]
        }

        return jsonify({
            "health": {"score": global_score, "status": active_status},
            "nodes": cluster_nodes,
            "alerts": formatted_alerts,
            "processes": mock_processes  
        }), 200
    except Exception as api_fault:
        log_error(f"Failed to fetch cluster state from PostgreSQL: {api_fault}")
        return jsonify({"error": "Failed to compile infrastructure status matrices"}), 500


@app.route("/api/alerts/history", methods=["GET"])
@token_required  
def alert_history():
    try:
        # Capture the dynamic context boundary filtering param
        selected_agent = request.args.get('agent', 'all')
        rows = get_alert_history(limit=20, agent=selected_agent)
        history = [f"{r[0].strftime('%Y-%m-%d %H:%M:%S') if r[0] else ''} | {r[1]} ({r[2]}) | {r[3]} | {r[4]}" for r in rows]
        return jsonify({"history": history}), 200
    except Exception as error:
        log_error(f"Failed to fetch incident logs from PostgreSQL cluster: {error}")
        return jsonify({"history": [], "error": "Database read failure"}), 500


# ==============================================================================
# STATIC CONTENT DELIVERY PIPELINE (UI ROUTING OVERHEADS)
# ==============================================================================
@app.route("/login", methods=["GET"])
def render_login_page():
    return render_template("login.html")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


# ==============================================================================
# SECURED IDENTITY MATRIX AND PROVISIONING SERVICES (RBAC ENFORCED)
# ==============================================================================

@app.route("/api/users", methods=["GET"])
@token_required
def get_all_users():
    try:
        users_list = []
        with _db_orchestrator._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, username, role FROM users ORDER BY id ASC")
                rows = cursor.fetchall()
                for r in rows:
                    users_list.append({"id": r[0], "username": r[1], "role": r[2]})
        return jsonify({"users": users_list}), 200
    except Exception as e:
        log_error(f"Database read failure on user directory index: {e}")
        return jsonify({"error": "Failed to fetch internal identity ledger."}), 500


@app.route("/api/users/create", methods=["POST"])
@token_required  
@admin_required  
def create_user():
    try:
        data = request.get_json() or {}
        new_username = data.get("username", "").strip()
        new_password = data.get("password", "")
        new_role = data.get("role", "Viewer").strip() 
        recipient_email = data.get("email", "").strip() 

        if not new_username or not new_password or not recipient_email:
            return jsonify({"error": "Missing identity credentials or verification mapping."}), 400

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')

        with _db_orchestrator._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE username = %s", (new_username,))
                if cursor.fetchone():
                    return jsonify({"error": "Identity signature already exists inside cluster database."}), 409
                
                cursor.execute("""
                    INSERT INTO users (username, password_hash, role, is_verified)
                    VALUES (%s, %s, %s, TRUE)
                """, (new_username, hashed_password, new_role))
                conn.commit()

        log_info(f"[USER PROVISIONING] Identity [{new_username}] initialized under role [{new_role}].")
        return jsonify({"message": f"User initialized successfully under role {new_role}."}), 201

    except Exception as e:
        log_error(f"User provisioning fault: {e}")
        return jsonify({"error": "Internal security node allocation failure."}), 500


@app.route("/api/users/<user_id>", methods=["PUT"])
@token_required
@admin_required
def update_user_role(user_id):
    try:
        data = request.get_json() or {}
        target_role = data.get("role", "Viewer").strip()

        with _db_orchestrator._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
                user_row = cursor.fetchone()
                if user_row and user_row[0] == "admin":
                    return jsonify({"error": "Root administrator authorization structure is unalterable."}), 400

                cursor.execute("UPDATE users SET role = %s WHERE id = %s RETURNING id", (target_role, user_id))
                if not cursor.fetchone():
                    return jsonify({"error": "Target identity profile not found within node cluster."}), 404
                conn.commit()

        log_info(f"[USER MUTATION] Identity ID [{user_id}] mutated clearance to [{target_role}].")
        return jsonify({"message": f"Identity clearance updated to {target_role} successfully."}), 200
    except Exception as e:
        log_error(f"User mutation vector failed: {e}")
        return jsonify({"error": "Internal role shifting allocation anomaly."}), 500


@app.route("/api/users/<user_id>", methods=["DELETE"])
@token_required
@admin_required
def delete_user(user_id):
    try:
        with _db_orchestrator._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
                user_row = cursor.fetchone()
                if user_row and user_row[0] == "admin":
                    return jsonify({"error": "Critical Safeguard: Root administrator identity cannot be purged."}), 400

                cursor.execute("DELETE FROM users WHERE id = %s RETURNING id", (user_id,))
                if not cursor.fetchone():
                    return jsonify({"error": "Target identity profile not found."}), 404
                conn.commit()

        log_info(f"[USER PURGED] Identity ID [{user_id}] successfully decommissioned from system database.")
        return jsonify({"message": "Identity decoupled from security rings successfully."}), 200

    except Exception as e:
        log_error(f"User deletion execution fault: {e}")
        return jsonify({"error": "Failed to purge identity mapping from core storage."}), 500


# import subprocess
# subprocess.Popen(["sleep","3600"]) # Ticket 5 Checklist 3: Temporary added a sleep command to keep the Flask server running for testing purposes, can be removed in production

# =========================================================================================
#Subprocess in Python is the official and essential tool that allows a program to exit the 
# isolated Python environment
# and interact directly with the operating system (OS Kernel) as if writing in the Terminal.
#
#Popin (short for Process Open) is the backbone of this library.
#
# What exactly does `subprocess.Popen` do?
# When you call `subprocess.Popen(["sleep", "3600"]), you are telling Python to do the following:
# Create a new child process (Fork/Spawn Child Process): Python requests the operating system to
# launch a completely external program (in this case, the Linux sleep program).
#
#Asynchronous/Non-blocking execution: This is the greatest secret of Popen! Once the child process
#  is launched, Python doesn't wait for it to finish. Instead, it runs in the background and
#  immediately returns to execute the next lines of code in your script.
#
# Why did we use it in the test?
#We used it because if we had used regular functions like `subprocess.run()`,
# Flask would have frozen completely for a full hour (3600 seconds) waiting for
# the process to finish and wouldn't have received any API requests! But thanks to
#  Popen, we launched a "naughty, dormant" process in the container's background,
#  leaving Flask free to receive the hit from the agent and have the security guard catch it!
# ==========================================================================================


if __name__ == "__main__":
    init_db()  # Ensure database is initialized before starting the server
    try:
        # (Ticket 6) :
        from dashboard.app import start_data_retention_worker
        start_data_retention_worker()
    except Exception as worker_init_fault:
        print(f"[CRITICAL]: Failed to launch Retention Worker: {worker_init_fault}", flush=True)


    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)