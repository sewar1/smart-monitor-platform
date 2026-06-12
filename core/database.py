# ==============================================================================
# SMART MONITOR PLATFORM - ENTERPRISE PERSISTENCE LAYER (POSTGRESQL ENGINE)
# ==============================================================================
# Re-engineered for distributed Docker environments utilizing state isolation.
# Uses dynamic kernel space environment variables for infrastructure binding.
# ==============================================================================

import os
import psycopg2
from datetime import datetime
from typing import List, Tuple
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
        Generates production-ready tables for system logs and telemetry.
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

                    # Schema 2: Linear telemetry history
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
                    conn.commit()
            log_info("PostgreSQL storage infrastructure schemas verified/initialized successfully.")
        except Exception as db_fault:
            log_error(f"Critical Database Infrastructure Fault during init: {db_fault}")

    def persist_incident_log(self, server: str, message: str, level: str = "WARNING") -> None:
        """
        Safely records systemic anomalies into the Postgres server via parameterized query layers.
        """
        current_time = datetime.now()
        
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Note: PostgreSQL uses %s placeholder instead of SQLite's ?
                    cursor.execute("""
                        INSERT INTO alerts (timestamp, server, message, level)
                        VALUES (%s, %s, %s, %s)
                    """, (current_time, server, message, level))
                    conn.commit()
        except Exception as io_fault:
            log_error(f"Failed to persist incident to PostgreSQL cluster: {io_fault}")

    def fetch_historical_incidents(self, limit: int = 50) -> List[Tuple]:
        """
        Retrieves inverse-chronological sequence records bounding current active incidents.
        """
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


# ==============================================================================
# COMPATIBILITY EMULATION ROUTERS (Guarantees absolute safety for app.py)
# ==============================================================================
_db_orchestrator = DatabaseManager()

def init_db() -> None:
    _db_orchestrator.init_infrastructure_tables()

def save_alert(server: str, message: str, level: str = "WARNING") -> None:
    _db_orchestrator.persist_incident_log(server, message, level)

def get_alert_history(limit: int = 50) -> List[Tuple]:
    return _db_orchestrator.fetch_historical_incidents(limit=limit)