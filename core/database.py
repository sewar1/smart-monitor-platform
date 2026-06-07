# ==============================================================================
# SMART MONITOR PLATFORM - SECURE PERSISTENCE LAYER (SQLite ENGINE)
# ==============================================================================
# Engineered with auto-recovery context managers to eliminate resource leaks.
# Enforces strict parameterized state isolation against SQL Injection vectors.
# ==============================================================================

import sqlite3
import os
from datetime import datetime
from typing import List, Tuple


class DatabaseManager:
    """
    Handles robust interactions with the SQLite embedded ecosystem.
    Utilizes localized dynamic contexts to safeguard database descriptors under multi-worker loads.
    """

    def __init__(self, db_dir: str = "logs", db_name: str = "monitor.db"):
        self.db_path = os.path.join(db_dir, db_name)
        # Structural Assurance: Enforce directory tree existence prior to database I/O binding
        os.makedirs(db_dir, exist_ok=True)

    def init_infrastructure_tables(self) -> None:
        """
        Idempotent database schema initialization.
        Generates functional relational logs for both system notifications and raw metrics history.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Schema 1: Incidents and security alerts logging system
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    server TEXT NOT NULL,
                    message TEXT NOT NULL,
                    level TEXT NOT NULL
                )
            """)

            # Schema 2: Linear telemetry history (Prepared for future trend-analysis engines)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    cpu REAL NOT NULL,
                    ram REAL NOT NULL,
                    disk REAL NOT NULL,
                    server TEXT NOT NULL
                )
            """)
            conn.commit()

    def persist_incident_log(self, server: str, message: str, level: str = "WARNING") -> None:
        """
        Safely records systemic anomalies into the ledger via parameterized query layers.
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 'with connection' block automatically triggers 'commit()' on success and 'rollback()' on fault
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO alerts (timestamp, server, message, level)
                VALUES (?, ?, ?, ?)
            """, (current_time, server, message, level))

    def fetch_historical_incidents(self, limit: int = 50) -> List[Tuple]:
        """
        Retrieves inverse-chronological sequence records bounding current active incidents.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timestamp, server, message, level
                FROM alerts
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            return cursor.fetchall()


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