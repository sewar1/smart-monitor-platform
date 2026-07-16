# ==============================================================================
# SMART MONITOR PLATFORM - ENTERPRISE PERSISTENCE LAYER (POSTGRESQL ENGINE)
# ==============================================================================
# Re-engineered for distributed high-concurrency architectures.
# Implements production-grade Connection Pooling to handle simultaneous multi-node traffic.
# Delegated schema initialization entirely to container-native scripts (init.sql).
# ==============================================================================

import os
from dotenv import load_dotenv
load_dotenv()
import bcrypt
import psycopg2
from psycopg2 import pool  # Enterprise Connection Pooling module
import json
from datetime import datetime, timezone
from typing import List, Tuple, Dict, Any, Optional
from core.logger import log_info, log_error

class DatabaseManager:
    """
    Manages centralized concurrent interaction with the PostgreSQL Persistent Cluster.
    Utilizes connection pooling to scale against heavy multi-agent parallel telemetry streams.
    """

    def __init__(self):
        # Fetching database network boundaries from container system environment
        self.host = os.getenv("POSTGRES_HOST", "db")
        self.database = os.getenv("POSTGRES_DB", "monitor_db")
        self.user = os.getenv("POSTGRES_USER", "postgres_admin")
        self.password = os.getenv("POSTGRES_PASSWORD", "secure_devops_pass")
        self.port = os.getenv("POSTGRES_PORT", "5432")
        
        # Initialize the Connection Pool (Min 1 connection, Max 20 concurrent connections)
        try:
            self._connection_pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=20,
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            log_info("PostgreSQL Thread-Safe Connection Pool initialized successfully.")
        except Exception as pool_fault:
            log_error(f"Failed to establish PostgreSQL Connection Pool: {pool_fault}")
            raise pool_fault
        
    def _get_pooled_connection(self):
        """Borrows an active runtime socket connection from the initialized pool."""
        return self._connection_pool.getconn()
    

    def _release_pooled_connection(self, conn) -> None:
        """Returns a borrowed connection back to the pool to prevent resource starvation leaks."""
        if conn:
            self._connection_pool.putconn(conn)

    def save_metrics(self, node_id : str, location: str, cpu_stat: float, ram_stat: float, disk_stat: float, top_processes_json: str = "[]") -> None:
        """
        [Ticket 4 Update]: Overhauls and persists dynamic multi-node telemetry and high-frequency 
        process maps (JSONB) into the PostgreSQL cluster with a dedicated tracking timestamp.
        """
        # =========================================================================
        # Safe Type Guard: If the backend sends a raw list/dict instead of string, serialize it dynamically
        # =========================================================================
        if not isinstance(top_processes_json, str):
            top_processes_json = json.dumps(top_processes_json)
        # =========================================================================

        connection = None
        cursor = None
        try:
            connection = self._get_pooled_connection()
            cursor = connection.cursor()

            # [Ticket 1 & 4 Matrix Injection]: Schema optimized with native metrics schema table constraints.
            # Captures both node hardware state vector and JSONB execution maps uniformly.

            # [Ticket 4]: The top_processes_json parameter is now included in the insert query to store the top processes data as a JSONB field in the metrics table, and add os_type to the insert query for telemetry ingestion
            insert_query ="""
                INSERT INTO metrics (node_id, location, os_type, cpu_usage, ram_usage, disk_usage, top_processes, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """

            # [Ticket 4]: Injects a UTC timestamp for cross-node consistency and chronological ordering in the metrics table.
            current_timestamp = datetime.now(timezone.utc)  # UTC timestamp for cross-node consistency
            detected_os = "Linux/Docker" # Ticket 4: OS type is now hardcoded for telemetry ingestion, can be extended to dynamic detection if needed
            cursor.execute(
                    insert_query,
                    (node_id, location, detected_os, float(cpu_stat), float(ram_stat), float(disk_stat), top_processes_json, current_timestamp) # Ticket 4: os_type added to the insert query for telemetry ingestion
            )

            connection.commit() # Commit the transaction to persist the metrics data
        except Exception as io_fault:
            if connection:
                connection.rollback()  # Rollback in case of any error during the transaction
            log_error(f"Failed to capture real-time remote agent metric transaction: {io_fault}") # Log the error for further investigation
            raise io_fault  # Re-raise the exception to propagate it up the call stack
        finally:
            if cursor:
                cursor.close()  # Close the cursor to free up resources
            self._release_pooled_connection(connection)  # Release the connection back to the pool


    def init_infrastructure_tables(self) -> None:
        """
        Maintains structural compatibility. Explicit table creations are now handled 
        declaratively inside /docker-entrypoint-initdb.d/init.sql for state isolation.
        """
        log_info("Database schema lifecycle validation delegated natively to init.sql orchestration.")
        # Seamlessly boot administration accounts verification matrix
        self._seed_default_admin()

    def _seed_default_admin(self) -> None:
        """Seeds or updates the administrative user securely using constant-time bcrypt hashing."""
        conn = None
        try:
            conn = self._get_pooled_connection()
            with conn.cursor() as cursor:
                password = "Admin@1234"
                salt = bcrypt.gensalt()
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
                
                # Check for pre-existing system operators based on unique username indices
                cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", ("admin",))
                
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO users (username, password_hash, role)
                        VALUES (%s, %s, %s)
                    """, ("admin", hashed_password, "administrator"))
                    log_info("[SECURITY SEED] Default cluster administrator deployed successfully.")
                else:
                    cursor.execute("""
                        UPDATE users 
                        SET password_hash = %s, role = %s
                        WHERE username = %s
                    """, (hashed_password, "administrator", "admin"))
                    log_info("[SECURITY SEED] Cluster administrative credentials synchronized.")
                
                conn.commit()
        except Exception as seed_fault:
            log_error(f"Failed to seed core security layer: {seed_fault}")
        finally:
            self._release_pooled_connection(conn)

    def persist_incident_log(self, server: str, location: str, message: str, level: str = "WARNING") -> None:
        """Records anomalies stream directly from the decentralized network edge nodes."""
        conn = None
        try:
            conn = self._get_pooled_connection()
            with conn.cursor() as cursor:
                # [Ticket 4 Update]: Column alignments standardized to node_id (past server_name) context
                cursor.execute("""
                    INSERT INTO alerts (node_id, location, alert_type, message, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                """, (server, location, level, message, datetime.now(timezone.utc)))
                conn.commit()
        except Exception as io_fault:
            log_error(f"Failed to persist remote incident to central engine: {io_fault}")
        finally:
            self._release_pooled_connection(conn)

    def fetch_historical_incidents(self, limit: int = 50, agent_name: Optional[str] = None) -> List[Tuple]:
        """Retrieves system anomaly timeline sequence records sorted by chronological inverse order."""
        conn = None
        try:
            conn = self._get_pooled_connection()
            with conn.cursor() as cursor:
                if agent_name and agent_name.lower() != 'all':
                    cursor.execute("""
                        SELECT timestamp, node_id, location, message, alert_type
                        FROM alerts
                        WHERE LOWER(node_id) = LOWER(%s)
                        ORDER BY id DESC
                        LIMIT %s
                    """, (agent_name, limit))
                else:
                    cursor.execute("""
                        SELECT timestamp, node_id, location, message, alert_type
                        FROM alerts
                        ORDER BY id DESC
                        LIMIT %s
                    """, (limit,))
                return cursor.fetchall()
        except Exception as read_fault:
            log_error(f"Failed to fetch historical alerts from persistence cache: {read_fault}")
            return []
        finally:
            self._release_pooled_connection(conn)

    def persist_telemetry_metrics(self, server: str, location: str, cpu: float, ram: float, disk: float) -> None:
        """Ingests multi-node hardware telemetry data bundles transmitted by edge agents."""
        conn = None
        try:
            conn = self._get_pooled_connection()
            with conn.cursor() as cursor:
                # Top processes schema mock array inject for data consistency matrix alignment
                import json
                empty_processes_matrix = json.dumps([])
                
                cursor.execute("""
                    INSERT INTO metrics (node_id, location, os_type, cpu_usage, ram_usage, disk_usage, top_processes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (server, location, "Linux/Windows", cpu, ram, disk, empty_processes_matrix))
                conn.commit()
        except Exception as io_fault:
            log_error(f"Failed to capture real-time remote agent metric transaction: {io_fault}")
        finally:
            self._release_pooled_connection(conn)

    def fetch_latest_cluster_state(self, agent_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        [Ticket 4 Update]: Queries unique state evaluation matrix for nodes dynamically.
        Preserves raw datetime objects to safeguard dashboard timezone-aware calculations.
        """
        conn = None
        try:
            conn = self._get_pooled_connection()
            with conn.cursor() as cursor:
                # [Ticket 4]: Dynamic agent filtering for multi-node deployments. If agent_name is provided, filter by that agent; otherwise, return all nodes.
                if agent_name and agent_name.lower() != 'all':
                    cursor.execute("""
                        SELECT node_id, location, cpu_usage, ram_usage, disk_usage, timestamp, top_processes
                        FROM metrics
                        WHERE LOWER(node_id) = LOWER(%s)
                        ORDER BY timestamp DESC
                        LIMIT 1
                    """, (agent_name,))
                else:
                    # Fetches the latest single record for every tracking node in parallel
                    cursor.execute("""
                        SELECT DISTINCT ON (node_id) node_id, location, cpu_usage, ram_usage, disk_usage, timestamp, top_processes
                        FROM metrics
                        ORDER BY node_id, id DESC
                    """)
                rows = cursor.fetchall()
                
                cluster_nodes = []
                for row in rows:
                    cluster_nodes.append({
                        "name": row[0],
                        "location": row[1],
                        "cpu": float(row[2]),
                        "ram": float(row[3]),
                        "disk": float(row[4]),
                        # [Ticket 4]: Preserves the raw timestamp object for timezone-aware calculations in the dashboard layer.
                        "last_seen": row[5],
                        "top_processes": row[6] # Injected to support the real-time process list container
                    })
                return cluster_nodes
        except Exception as query_fault:
            log_error(f"Failed to parse global cluster status metrics: {query_fault}")
            return []
        finally:
            if conn:
                self._release_pooled_connection(conn)

    def authenticate_user_credentials(self, username: str, plain_password: str) -> bool:
        """Evaluates identity structures safely against cryptographic side-channel vector threats."""
        conn = None
        try:
            conn = self._get_pooled_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
                record = cursor.fetchone()
                if not record:
                    return False
                
                hashed_password = record[0]
                return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as security_fault:
            log_error(f"Security Engine runtime validation error: {security_fault}")
            return False
        finally:
            self._release_pooled_connection(conn)


    def purge_historical_metrics(self) -> int:
        """
        [Ticket 6]: Wipes historical metric records older than 168 hours (7 days)
        to optimize storage layer index latency and prevent memory bloat.
        Returns the number of deleted rows.
        """
        connection = None 
        cursor = None
        rows_deleted = 0
        try:
            connection = self._get_pooled_connection()
            cursor = connection.cursor()

            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24) # Tichet 6 :

            purge_query ="""
                DELETE FROM metrics 
                WHERE timestamp < %s;
            """
            cursor.execute(purge_query, (cutoff_time,))
            rows_deleted = cursor.rowcount

            connection.commit()
            log_info(f"[DATABASE PURGE]: Successfully cleared {rows_deleted} obsolete metric records older than 24h.")

        except Exception as db_fault:
            if connection:
                connection.rollback()
            log_error(f"[DATABASE PURGE ERROR]: Failed to execute data retention cycle: {db_fault}")
        finally:
            if cursor:
                cursor.close()
            self._release_pooled_connection(connection)
        
        return rows_deleted




# ==============================================================================
# COMPATIBILITY EMULATION ROUTERS (PREVENTS SYSTEM INTEGRATION CRASHES)
# ==============================================================================
_db_orchestrator = DatabaseManager()

def init_db() -> None:
    _db_orchestrator.init_infrastructure_tables()

def save_alert(server: str, location: str, message: str, level: str = "WARNING") -> None:
    _db_orchestrator.persist_incident_log(server, location, message, level)

def get_alert_history(limit: int = 50, agent: Optional[str] = None) -> List[Tuple]:
    return _db_orchestrator.fetch_historical_incidents(limit=limit, agent_name=agent)

# [Ticket 4 Hotfix Alignment]: Emulation router re-mapped to support 6 positional parameters
def save_metrics(server: str, location: str, cpu: float, ram: float, disk: float, top_processes: str = "[]") -> None:
    _db_orchestrator.save_metrics(server, location, cpu, ram, disk, top_processes)

def get_latest_cluster_metrics(agent: Optional[str] = None) -> List[Dict[str, Any]]:
    return _db_orchestrator.fetch_latest_cluster_state(agent_name=agent)

def verify_user(username: str, plain_pass: str) -> bool:
    return _db_orchestrator.authenticate_user_credentials(username, plain_pass)