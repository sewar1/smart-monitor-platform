# ==========================================
# SQLITE DATABASE LAYER
# ==========================================

import sqlite3
import os
from datetime import datetime

# ==========================================
# DATABASE PATH
# ==========================================

DB_PATH = "logs/monitor.db"

# تأكد أن مجلد logs موجود
os.makedirs("logs", exist_ok=True)

# ==========================================
# INIT DATABASE
# ==========================================

def init_db():
    """
    Create required tables if they don't exist.
    """

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Alerts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            server TEXT,
            message TEXT,
            level TEXT
        )
    """)

    # Metrics history table (for future AI layer)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            cpu REAL,
            ram REAL,
            disk REAL,
            server TEXT
        )
    """)

    conn.commit()
    conn.close()


# ==========================================
# INSERT ALERT
# ==========================================

def save_alert(server, message, level="WARNING"):
    """
    Store alert in SQLite database.
    """

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO alerts (timestamp, server, message, level)
        VALUES (?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        server,
        message,
        level
    ))

    conn.commit()
    conn.close()


# ==========================================
# GET ALERT HISTORY
# ==========================================

def get_alert_history(limit=50):
    """
    Retrieve latest alerts from DB.
    """

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, server, message, level
        FROM alerts
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return rows