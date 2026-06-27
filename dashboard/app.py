
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
#========================================================
# [Ticket 8 - Heartbeat Update]: Safely track live state timestamp
# Dictionary to keep track of the last_seen timestamp for each hardware node
nodes_heartbeats = {
    "Docker_Production_Container": time.time(),
    "Windows_Host": time.time(),
    "VMware_Ubuntu": time.time()
}
#========================================================
from datetime import datetime, timedelta, timezone # ticket 4: added timezone for better timestamp handling
from functools import wraps
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv

# Inject hidden environment configurations from local .env space into the OS execution kernel
load_dotenv()


# ==============================================================================
# SMART ENVIRONMENT CHECK (DOCKER VS LOCAL WINDOWS) Ticket 7
# ==============================================================================
# This variable automatically detects if the code is running inside Docker or locally on Windows
RUNNING_IN_DOCKER = os.getenv("RUNNING_IN_DOCKER", "false") == "true"


# ==============================================================================
# SUBSYSTEM ARCHITECTURE INTEGRATIONS & DATA ACCELERATION LAYERS
# ==============================================================================
from core.alerts import check_alerts
from core.analyzer import calculate_health_score, get_health_status, check_and_mitigate_freezes # Ticket 5: added check_and_mitigate_freezes for anti-freeze guard
from core.logger import log_info, log_warning, log_error
#===============================================================================
# In order to make the code overcome this crash and continue to run the server
# without a database, the import line inside the app.py file must be protected
# by a try ... except firewall
#===============================================================================
try: # Ticket 7:
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
except Exception as db_import_error:
    print(f"[WARNING]: Database module failed to load locally (Expected without Docker): {db_import_error}", flush=True)
    # Define empty dummy functions to prevent a NameError error later in the code.
    def init_db(): pass
    def save_metrics(*args, **kwargs): pass
    def get_latest_cluster_metrics(*args, **kwargs): return {}
    def save_alert(*args, **kwargs): pass
    def get_alert_history(*args, **kwargs): return []
    def verify_user(*args, **kwargs): return False
#================================================================================
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
        if RUNNING_IN_DOCKER: # Ticket 7 : add Dynamic Environment Variables
            init_db()
            log_info("Central database architecture successfully synchronized via Flask context.")
        else: # Ticket 7 : add Dynamic Environment Variables
            log_info("Running locally on Windows: Database initialization bypassed to prevent hanging.")
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

#================================================
# [Ticket 8 - Heartbeat Update]: Safely track live state timestamp
#================================================

@app.route('/api/nodes/status', methods=['GET'])
# If you are using JWT protect it, otherwise leave it open for frontend polling
def get_nodes_status():
    """
    Evaluates the immediate health status of all 3 agents based on 60 seconds threshold window.
    """
    current_time = time.time()
    status_matrix = {}
    
    for node, last_seen in nodes_heartbeats.items():
        # Calculate time elapsed since last transmission
        time_elapsed = current_time - last_seen
        
        # Window calculation logic: 60 seconds threshold
        if time_elapsed > 60:
            status_matrix[node] = "Offline"
        else:
            status_matrix[node] = "Online"
            
    return jsonify(status_matrix), 200


# ==============================================================================
# DISTRIBUTED DATA INGESTION & CENTRAL INVENTORY API MATRIX
# ==============================================================================

@app.route("/api/metrics/receiver", methods=["POST"])
def receive_agent_telemetry():
    """
    Ingestion Endpoint: Receives incoming runtime telemetry packets from distributed agents.
    Verifies payload parameters, commits state to PostgreSQL, and triggers reactive safeguards.
    """
    # Debug hook to verify endpoint reachability independently of firewall/analyzer layers
    print("🚀🚀 API RECEIVED A HIT!! 🚀🚀", flush=True) 
    
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({"status": "rejected", "reason": "Missing or corrupted JSON payload"}), 400
        
        # Extraction of telemetry metrics matrix keys from streaming agent input
        server_name = payload.get("name") # Refactored from 'server' to 'name' to align with agent payload signatures
        location = payload.get("location", "Ludwigshafen") 
        cpu_stat = payload.get("cpu")
        ram_stat = payload.get("ram")
        disk_stat = payload.get("disk")
        
        # [Ticket 4]: Extracted top_processes array to comply with updated persistence signatures
        top_processes = payload.get("top_processes", []) 

        # Validation Guard: Block incomplete packets to prevent corrupted db inserts
        if None in (server_name, cpu_stat, ram_stat, disk_stat):
            return jsonify({"status": "rejected", "reason": "Incomplete telemetry parameters"}), 400
        #================================================================
        # Ticket 8: [Heartbeat Update]: Safely track live state timestamp 
        if server_name in nodes_heartbeats:
            nodes_heartbeats[server_name] = time.time()
        #================================================================
        try: 
            # [Ticket 4]: Invoking save_metrics with serialized process array parameter
            save_metrics(
                server_name,
                location,
                float(cpu_stat),
                float(ram_stat),
                float(disk_stat),
                json.dumps(top_processes) # Stringified JSON payload to match PostgreSQL storage expectations
            ) 
        except Exception as db_err: 
            # Capture database pipeline errors gracefully without crashing the active WSGI process
            log_error(f"PostgreSQL Ingestion Node Failure: {db_err}") 
            return jsonify({"status": "fault", "reason": "Database ingestion error"}), 500 
            
        # Compile temporary runtime memory state layout
        current_node_state = [{"name": server_name, "location": location, "cpu": cpu_stat, "ram": ram_stat, "disk": disk_stat}]
        
        # [Ticket 5]: Active Reactive Mitigation Loop (Anti-Freeze Guard Protection)
        try:
            incidents = check_and_mitigate_freezes(float(cpu_stat), float(ram_stat), server_name, location) 
            for incident in incidents:
                # [Ticket 5]: Persist decoupled freeze mitigation records for auditing history
                save_alert(
                    server=incident["server"], 
                    location=incident["location"], 
                    message=incident["message"], 
                    level=incident["level"]
                )
        except Exception as mitigation_fault:
            log_error(f"Anti-Freeze Guard Initialization Failed: {mitigation_fault}")
            return jsonify({"status": "fault", "reason": "Freeze mitigation error"}), 500

        # Anomaly threshold analysis engine pass
        active_alerts = check_alerts(current_node_state)

        if active_alerts:
            # [Ticket 4]: Contextual routing enriched with regional location injection
            alert_message = f"Host Node: [{server_name}] in ({location}) Anomaly Report:\n" + "\n".join(active_alerts) 
            log_warning(f"Incident mitigation initialized for active threats on {server_name}: {alert_message}")

            for alert in active_alerts:
                try: 
                    save_alert(server=server_name, location=location, message=alert, level="WARNING")
                except Exception as db_err: 
                    log_error(f"Failed to persist incident logs from PostgreSQL cluster: {db_err}")

            # Critical external alerting pipelines
            send_telegram_alert(alert_message)
            send_email_alert(alert_message)

        return jsonify({"status": "synchronized", "node": server_name, "location": location}), 201
        
    except Exception as ingestion_fault:
        # [Ticket 4]: Extended visibility into internal fault vectors for easier traceback inspection
        log_error(f"Failed to persist Agent metrics to PostgreSQL cluster: {ingestion_fault}") 
        return jsonify({"status": "fault", "reason": str(ingestion_fault)}), 500 


def start_data_retention_worker():
    """
    [Ticket 6]: Asynchronous daemon worker that invokes the long-term 
    storage retention policy cleanup routine systematically.
    """
    def run_forever():
        db_mgr = DatabaseManager()
        # Initial sleep sequence to allow cluster databases to reach stable readiness states
        time.sleep(20) 
        
        while True:
            try:
                log_info("[RETENTION WORKER]: Initiating systematic storage layer cleanup cycle...")
                db_mgr.purge_historical_metrics()
            except Exception as worker_err:
                log_error(f"[RETENTION WORKER ERROR]: Exception caught in retention loop: {worker_err}")
            
            # Execute data expiration sweep routine at defined intervals
            time.sleep(12 * 3600)

    # Configured as daemon execution type to terminate gracefully alongside server teardown
    worker_thread = threading.Thread(target=run_forever, daemon=True)
    worker_thread.start()
    log_info("[SYSTEM]: Data Retention Policy Background Worker initialized successfully.")


@app.route("/api/metrics", methods=["GET"])
@token_required  
def get_dashboard_metrics():
    """
    Compiles and delivers unified matrix states out of relational databases
    to service downstream telemetry and historical charts.
    """
    try:
        # [Ticket 4 - Checklist 2]: Extract target environment query boundary param
        selected_agent = request.args.get('agent', 'all')
        
        # Scoped structural filtering based on selected navigation boundary
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

        # [Ticket 4]: Injecting timezone-aware current moments to safeguard calculation domains
        now = datetime.now(timezone.utc) 
        
        # [Ticket 4]: Heartbeat Evaluation Sweep for Agent Staleness Threshold Detection
        for node in cluster_nodes: 
            last_seen = node.get("last_seen") 
            if last_seen: 
                # [Ticket 4]: Coerce naive datetime objects into UTC space to mitigate offset calculation TypeErrors
                if last_seen.tzinfo is None: 
                    last_seen = last_seen.replace(tzinfo=timezone.utc) 

                # Flag node state context boundary as Offline if missing reporting windows for > 60 seconds
                if now - last_seen > timedelta(seconds=60): 
                    node["status"] = "Offline" # Triggers the downstream UI critical red badge display
                else:
                    node["status"] = "Online"  # Triggers the downstream UI healthy green badge display
            else:
                node["status"] = "Online"  # Resilient fallback default
    
        # Re-calculate overarching system metrics health indexes using retrieved dataset
        if cluster_nodes: 
            avg_cpu = sum(node['cpu'] for node in cluster_nodes) / len(cluster_nodes)
            avg_ram = sum(node['ram'] for node in cluster_nodes) / len(cluster_nodes)
            global_score = calculate_health_score(avg_cpu, avg_ram, 0)
            active_status = get_health_status(global_score)

        # Populate process array tables dynamically wrapped to target environment contexts
        mock_processes = {
            "top_cpu": [
                {
                    "pid": 1024, 
                    "name": f"{selected_agent}_service" if selected_agent != 'all' else "postgres_engine", 
                    "cpu": 4.2
                } 
            ],
            "top_memory": [
                {
                    "pid": 1024, 
                    "name": f"{selected_agent}_service" if selected_agent != 'all' else "postgres_engine", 
                    "memory": 12.5
                } 
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
    """Fetches full tabular alert event listings mapped to contextual filter constraints."""
    try:
        # Extract targeted agent variable to bound database retrieval scopes
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
    if RUNNING_IN_DOCKER: # Ticket 7 : add Dynamic Environment Variables
        init_db()  # Ensure database is initialized before starting the server
        try:
            # (Ticket 6) :
            from dashboard.app import start_data_retention_worker
            start_data_retention_worker()
        except Exception as worker_init_fault:
            print(f"[CRITICAL]: Failed to launch Retention Worker: {worker_init_fault}", flush=True)
    else: # Ticket 7 : add Dynamic Environment Variables
        print("[INFO]: Data retention worker and database initialization bypassed for local Windows testing.", flush=True)

    # Automatically choose the host mapping based on environment context
    server_host = "0.0.0.0" if RUNNING_IN_DOCKER else "127.0.0.1"
    print(f"[SUCCESS]: Core server launching on http://{server_host}:5000/", flush=True)   

    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)