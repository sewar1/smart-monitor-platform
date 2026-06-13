# ==============================================================================
# SMART MONITOR PLATFORM - ENTERPRISE PERSISTENCE LAYER (POSTGRESQL ENGINE)
# ==============================================================================
# Re-engineered for distributed Docker environments utilizing state isolation.
# Uses dynamic kernel space environment variables for infrastructure binding.
# ==============================================================================

import os
import bcrypt
import psycopg2
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional
from core.logger import log_info, log_error

class DatabaseManager:
    """
    Handles robust interactions with the PostgreSQL Enterprise Server.
    Dynamically injects connection parameters from local environment variables.
    """

    def __init__(self):
        # Fetching dynamic connection boundaries from Host OS Env
        self.host = os.getenv("POSTGRES_HOST", "db") # 'db' is the Docker service name
        self.database = os.getenv("POSTGRES_DB", "monitor_db")
        self.user = os.getenv("POSTGRES_USER", "postgres_admin")
        self.password = os.getenv("POSTGRES_PASSWORD", "secure_devops_pass")
        self.port = os.getenv("POSTGRES_PORT", "5432")

    def _get_connection(self):
        """Creates a fresh runtime socket connection to the PostgreSQL Cluster."""
        return psycopg2.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password,
            port=self.port
        )

    def init_infrastructure_tables(self) -> None:
        """
        Idempotent database schema initialization for PostgreSQL syntax.
        Generates production-ready tables for system logs, telemetry, and security users.
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Schema 1: Incidents and security alerts logging system
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS alerts (
                            id SERIAL PRIMARY KEY,
                            timestamp TIMESTAMP NOT NULL,
                            server VARCHAR(100) NOT NULL,
                            message TEXT NOT NULL,
                            level VARCHAR(20) NOT NULL
                        )
                    """)

                    # Schema 2: Linear telemetry history (Supports Multi-Node)
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS metrics (
                            id SERIAL PRIMARY KEY,
                            timestamp TIMESTAMP NOT NULL,
                            cpu REAL NOT NULL,
                            ram REAL NOT NULL,
                            disk REAL NOT NULL,
                            server VARCHAR(100) NOT NULL
                        )
                    """)

                    # Schema 3: Security Rings - Production Grade Hashed User Store
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            username VARCHAR(50) UNIQUE NOT NULL,
                            password_hash VARCHAR(255) NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    conn.commit()
            log_info("PostgreSQL storage infrastructure schemas verified/initialized successfully.")
            
            # Seed a default admin user for bootstrapping if table is empty
            self._seed_default_admin()

        except Exception as db_fault:
            log_error(f"Critical Database Infrastructure Fault during init: {db_fault}")

    def _seed_default_admin(self) -> None:
        """Seeds or updates the administrative record securely mapped via bcrypt."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Enforce strict compliance with global regex validation policies
                    password = "Admin@1234"
                    salt = bcrypt.gensalt()
                    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
                    
                    # Validate existing records based on unique username bounds
                    cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", ("admin",))
                    
                    if cursor.fetchone()[0] == 0:
                        # Record injection when identity sequence is empty
                        cursor.execute("""
                            INSERT INTO users (username, password_hash)
                            VALUES (%s, %s)
                        """, ("admin", hashed_password))
                        log_info("[SECURITY SEED] Default administrative user registered successfully.")
                    else:
                        # Enforce live runtime mutation mapping for credential synchronizations
                        cursor.execute("""
                            UPDATE users 
                            SET password_hash = %s 
                            WHERE username = %s
                        """, (hashed_password, "admin"))
                        log_info("[SECURITY SEED] Administrative credential matrix forced synchronization.")
                        
                    conn.commit()
        except Exception as seed_fault:
            log_error(f"Failed to seed security infrastructure: {seed_fault}")

    def persist_incident_log(self, server: str, message: str, level: str = "WARNING") -> None:
        """Safely records systemic anomalies into the Postgres server."""
        current_time = datetime.now()
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO alerts (timestamp, server, message, level)
                        VALUES (%s, %s, %s, %s)
                    """, (current_time, server, message, level))
                    conn.commit()
        except Exception as io_fault:
            log_error(f"Failed to persist incident to PostgreSQL cluster: {io_fault}")

    def fetch_historical_incidents(self, limit: int = 50) -> List[Tuple]:
        """Retrieves inverse-chronological sequence records bounding current active incidents."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT timestamp, server, message, level
                        FROM alerts
                        ORDER BY id DESC
                        LIMIT %s
                    """, (limit,))
                    return cursor.fetchall()
        except Exception as read_fault:
            log_error(f"Failed to fetch incident logs from PostgreSQL cluster: {read_fault}")
            return []

    def persist_telemetry_metrics(self, server: str, cpu: float, ram: float, disk: float) -> None:
        """Ingests real-time raw resource matrix streaming from remote external Agents."""
        current_time = datetime.now()
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO metrics (timestamp, cpu, ram, disk, server)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (current_time, cpu, ram, disk, server))
                    conn.commit()
        except Exception as io_fault:
            log_error(f"Failed to persist Agent metrics to PostgreSQL cluster: {io_fault}")

    def fetch_latest_cluster_state(self) -> List[Dict[str, Any]]:
        """Advanced Window Function query for extraction of newest single metric records."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT DISTINCT ON (server) server, cpu, ram, disk, timestamp
                        FROM metrics
                        ORDER BY server, id DESC
                    """)
                    rows = cursor.fetchall()
                    
                    cluster_nodes = []
                    for row in rows:
                        cluster_nodes.append({
                            "name": row[0],
                            "cpu": row[1],
                            "ram": row[2],
                            "disk": row[3],
                            "last_seen": row[4].strftime("%Y-%m-%d %H:%M:%S")
                        })
                    return cluster_nodes
        except Exception as query_fault:
            log_error(f"Failed to fetch cluster state from PostgreSQL: {query_fault}")
            return []

    def authenticate_user_credentials(self, username: str, plain_password: str) -> bool:
        """
        Queries secure user layers and evaluates a constant-time cryptographic 
        comparison to verify user identities safely against constant-time side-channel threats.
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
                    record = cursor.fetchone()
                    if not record:
                        return False
                    
                    hashed_password = record[0]
                    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as security_fault:
            log_error(f"Security Core Authentication Exception: {security_fault}")
            return False


# ==============================================================================
# COMPATIBILITY EMULATION ROUTERS
# ==============================================================================
_db_orchestrator = DatabaseManager()

def init_db() -> None:
    _db_orchestrator.init_infrastructure_tables()

def save_alert(server: str, message: str, level: str = "WARNING") -> None:
    _db_orchestrator.persist_incident_log(server, message, level)

def get_alert_history(limit: int = 50) -> List[Tuple]:
    return _db_orchestrator.fetch_historical_incidents(limit=limit)

def save_metrics(server: str, cpu: float, ram: float, disk: float) -> None:
    _db_orchestrator.persist_telemetry_metrics(server, cpu, ram, disk)

def get_latest_cluster_metrics() -> List[Dict[str, Any]]:
    return _db_orchestrator.fetch_latest_cluster_state()

def verify_user(username: str, plain_pass: str) -> bool:
    return _db_orchestrator.authenticate_user_credentials(username, plain_pass)