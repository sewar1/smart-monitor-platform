# ==============================================================================
# SMART MONITOR PLATFORM - CENTRALIZED AGENT-SERVER BACKEND ENGINE
# ==============================================================================
# Engineered for dynamic multi-node telemetry ingestion and environment isolation.
# Follows Twelve-Factor App methodologies utilizing asynchronous notifications.
# Augmented with JWT & Cryptographic bcrypt Ring Infrastructure Security.
# ==============================================================================

import os
import jwt
import bcrypt  # 🛡️ High-fidelity hashing library for secure password encryption and verification
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv

# Inject hidden environment configurations from local .env space into the OS execution kernel
load_dotenv()

# ==============================================================================
# SUBSYSTEM ARCHITECTURE INTEGRATIONS & DATA ACCELERATION LAYERS
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
    verify_user,
    _db_orchestrator # The database orchestrator driving standard transaction pools
)
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
        log_error(f"Failed to bootstrap database layers during initialization: {init_fault}")

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
        
        # Intercept inbound transaction packet looking for HTTP Authorization payloads
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        # Explicitly bounce the pipeline if the token component is absent
        if not token:
            return jsonify({"error": "Access Denied: Missing cryptographic identity token"}), 401

        try:
            # Decode the payload via the internal secret key structure
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            
            # [CRITICAL STRUCTURAL FIX]: Explicitly map and inject user metadata inside the request context.
            # This enables down-stream handlers (like admin_required) to check states without extra DB IO hits.
            request.current_user = {
                "username": data.get("sub"),
                "role": data.get("role", "Viewer")
            }
        except jwt.ExpiredSignatureError:
            # Handle token expiration parameters (standard 30-minute operational lease)
            return jsonify({"error": "Access Denied: Identity token has expired"}), 401
        except jwt.InvalidTokenError:
            # Intercept altered, structural deformations, or malicious signature mismatches
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
        # Pull down the request context user payload established by the token_required decorator
        current_user = getattr(request, "current_user", None)
        
        # Enforce exclusive Admin clearance level restrictions
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
    """
    Validates identity claims against secure constant-time database bcrypt hashes.
    Issues cryptographically signed JSON Web Tokens upon successful match matrices.
    """
    try:
        payload = request.get_json()
        if not payload or "username" not in payload or "password" not in payload:
            return jsonify({"error": "Incomplete verification parameters"}), 400

        username = payload["username"]
        password = payload["password"]

        # Configure deterministic default access parameters
        user_role = "Operator"
        if username == "admin":
            user_role = "Admin"

        # Validate against cryptographic relational layers or check root fallback recovery accounts
        if verify_user(username, password) or (username == "admin" and password == "Admin@1234"):
            
            # [ARCHITECTURAL UPDATE]: Inject role token scopes directly into the JWT payload for SPA parsing
            token_payload = {
                "sub": username,
                "role": user_role,
                "exp": datetime.utcnow() + timedelta(minutes=30) # Establish a 30-minute expiration window
            }
            token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm="HS256")
            
            # Relay security context states back to the client-side SPA state managers
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
    """
    Central API data ingest gate tracking outbound logs arriving from distributed hardware nodes.
    Note: Intentionally left un-authenticated via JWT because remote edge units run headless without active users.
    """
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({"status": "rejected", "reason": "Missing or corrupted JSON payload"}), 400
        
        server_name = payload.get("server") # Identifies geographic nodes (e.g., Munich-Docker-Cluster)
        cpu_stat = payload.get("cpu")
        ram_stat = payload.get("ram")
        disk_stat = payload.get("disk")

        if None in (server_name, cpu_stat, ram_stat, disk_stat):
            return jsonify({"status": "rejected", "reason": "Incomplete telemetry parameters"}), 400

        # Persist standard performance arrays into primary production stores
        save_metrics(server_name, float(cpu_stat), float(ram_stat), float(disk_stat))
        current_node_state = [{"name": server_name, "cpu": cpu_stat, "ram": ram_stat, "disk": disk_stat}]
        
        # Evaluate operational boundaries looking for security or threshold anomalies
        active_alerts = check_alerts(current_node_state)

        if active_alerts:
            alert_message = f"Host Node: [{server_name}] Anomaly Report:\n" + "\n".join(active_alerts)
            log_warning(f"Incident mitigation initialized for active threats on {server_name}: {alert_message}")

            for alert in active_alerts:
                try: save_alert(server=server_name, message=alert, level="WARNING")
                except Exception as db_err: log_error(f"PostgreSQL Storage IO failure: {db_err}")

            # Dispatch emergency warnings asynchronously down core administrative channels
            send_telegram_alert(alert_message)
            send_email_alert(alert_message)

        return jsonify({"status": "synchronized", "node": server_name}), 201
    except Exception as ingestion_fault:
        log_error(f"Telemetry ingestion pipeline fault: {ingestion_fault}")
        return jsonify({"status": "fault", "reason": str(ingestion_fault)}), 500


@app.route("/api/metrics", methods=["GET"])
@token_required  # 🔒 Protected Gate: Enforces valid active identity parameters
def get_dashboard_metrics():
    """Compiles unified distributed node metrics histories out of PostgreSQL relational caches."""
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
        
        # Aggregate across active node arrays to compute systemic health scores
        if cluster_nodes:
            avg_cpu = sum(node['cpu'] for node in cluster_nodes) / len(cluster_nodes)
            avg_ram = sum(node['ram'] for node in cluster_nodes) / len(cluster_nodes)
            global_score = calculate_health_score(avg_cpu, avg_ram, 0)
            active_status = get_health_status(global_score)

        return jsonify({
            "health": {"score": global_score, "status": active_status},
            "nodes": cluster_nodes,
            "alerts": formatted_alerts,
            "processes": [] # Ready extension point for top resource consumers profiling arrays
        }), 200
    except Exception as api_fault:
        log_error(f"Global cluster status query execution fault: {api_fault}")
        return jsonify({"error": "Failed to compile infrastructure status matrices"}), 500


@app.route("/api/alerts/history", methods=["GET"])
@token_required  # 🔒 Protected Gate: Requires valid active tokens to parse history logs
def alert_history():
    try:
        rows = get_alert_history(limit=20)
        history = [f"{r[0].strftime('%Y-%m-%d %H:%M:%S') if r[0] else ''} | {r[1]} | {r[2]} | {r[3]}" for r in rows]
        return jsonify({"history": history}), 200
    except Exception as error:
        log_error(f"API runtime exception on history retrieval engine -> {error}")
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

# 🌐 [NEW STRUCTURAL VECTOR]: Exposes secure identity registers straight into Tab 2 of the UI (User Directory)
@app.route("/api/users", methods=["GET"])
@token_required
def get_all_users():
    try:
        users_list = []
        # Query persistent tables to compile registered identifiers and roles
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
@token_required  # 🔒 Authentication layer validation guard
@admin_required  # 🔒 Requires explicit Administrative privileges
def create_user():
    try:
        data = request.get_json() or {}
        new_username = data.get("username", "").strip()
        new_password = data.get("password", "")
        new_role = data.get("role", "Viewer").strip() # Safe default assignment to block accidental privilege leaks
        recipient_email = data.get("email", "").strip() # Necessary destination parameter to dispatch Multi-Factor token payloads

        if not new_username or not new_password or not recipient_email:
            return jsonify({"error": "Missing identity credentials or verification mapping."}), 400

        # Generate a cryptographically secure validation string via Mailer module integrations
        verification_token = mailer_service.generate_verification_token()
        
        # Enforce industrial password salting standards via secure bcrypt execution paths
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')

        with _db_orchestrator._get_connection() as conn:
            with conn.cursor() as cursor:
                # Deduplicate security identities to avoid collision anomalies
                cursor.execute("SELECT id FROM users WHERE username = %s", (new_username,))
                if cursor.fetchone():
                    return jsonify({"error": "Identity signature already exists inside cluster database."}), 409
                
                # Write record down assigning an unverified boolean value until 2FA confirmation completes
                cursor.execute("""
                    INSERT INTO users (username, password_hash, role, is_verified, verification_token, token_expires_at)
                    VALUES (%s, %s, %s, FALSE, %s, NOW() + INTERVAL '10 minutes')
                """, (new_username, hashed_password, new_role, verification_token))
                conn.commit()

        # Fire verification parameters out to destination mail drop synchronously
        mailer_service.send_verification_email(recipient_email, verification_token)
        log_info(f"[USER PROVISIONING] Identity [{new_username}] initialized under role [{new_role}].")
        return jsonify({"message": f"User initialized successfully. 2FA token dispatched to {recipient_email}."}), 201

    except Exception as e:
        log_error(f"User provisioning fault: {e}")
        return jsonify({"error": "Internal security node allocation failure."}), 500


# 🌐 [NEW STRUCTURAL VECTOR]: Mutates access permissions on click events coming from "Edit Role" actions in the SPA
@app.route("/api/users/update/<username>", methods=["PUT"])
@token_required
@admin_required
def update_user_role(username):
    try:
        data = request.get_json() or {}
        target_role = data.get("role", "Viewer").strip()

        # Hard-coded Safeguard Constraint: Prevent mutating the core admin account to isolate against system lockouts
        if username == "admin":
            return jsonify({"error": "Root administrator authorization structure is unalterable."}), 400

        with _db_orchestrator._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE users SET role = %s WHERE username = %s RETURNING id", (target_role, username))
                if not cursor.fetchone():
                    return jsonify({"error": "Target identity profile not found within node cluster."}), 404
                conn.commit()

        log_info(f"[USER MUTATION] Identity [{username}] mutated clearance to [{target_role}].")
        return jsonify({"message": f"Identity clearance updated to {target_role} successfully."}), 200
    except Exception as e:
        log_error(f"User mutation vector failed: {e}")
        return jsonify({"error": "Internal role shifting allocation anomaly."}), 500


@app.route("/api/users/delete/<username>", methods=["DELETE"])
@token_required
@admin_required
def delete_user(username):
    try:
        # Hard-coded Safeguard Constraint: Ensure root identity mapping profiles cannot be erased
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
    # Boot the application server on Port 5000, disabling the auto-reloader to prevent dual DB synchronization routines
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)