# ==============================================================================
# SMART MONITOR INFRASTRUCTURE - DISTRIBUTED TELEMETRY AGENT
# ==============================================================================
# Target deployment: Standalone Linux/Windows host monitoring daemon.
# Streams metric payloads via persistent HTTP Sessions to the central controller.
# Optimized with HTTP Keep-Alive, structured logging, and production error handling.
# ==============================================================================

import os
import json
import time
import sys
import socket
import logging
import psutil
import requests
from dotenv import load_dotenv

# Load environmental variables from .env file immediately
load_dotenv()

# ==============================================================================
# CONFIGURATION MATRIX & ENVIRONMENT BINDING (Ticket 9 & Unified Nomenclature)
# ==============================================================================

RAW_SERVER_URL = os.getenv("CENTRAL_SERVER_URL", "http://127.0.0.1:5000/api/metrics/receiver")
CENTRAL_SERVER_URL = RAW_SERVER_URL.replace("http:///", "http://")


# CENTRAL_SERVER_URL = os.getenv("CENTRAL_SERVER_URL", "http:///127.0.0.1:5000/api/metrics/receiver")
STREAM_INTERVAL_SECONDS = int(os.getenv("STREAM_INTERVAL_SECONDS", "5"))




# Unified Node ID mapping (falls back to hardware hostname if env is missing)
NODE_ID = os.getenv("NODE_ID", f"node-{socket.gethostname().lower()}")
NODE_LOCATION = os.getenv("NODE_LOCATION", os.getenv("LOCATION", "Ludwigshafen"))

# SETUP STRUCTURED PRODUCTION LOGGING
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("TelemetryAgent")

print(f"📡 Agent initialized for Node: [{NODE_ID}] at ({NODE_LOCATION})")
print(f"🔗 Target Ingestion API: {CENTRAL_SERVER_URL}")


def get_top_processes() -> list:
    """
    Extracts the top 5 resource-consuming processes on the host node.
    """
    processes = []
    try:
        for proc in sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']),
                           key=lambda p: p.info.get('cpu_percent', 0) or 0,
                           reverse=True)[:5]:
            processes.append({
                'pid': proc.info.get('pid'),
                'name': proc.info.get('name'),
                'cpu_percent': proc.info.get('cpu_percent'),
                'memory_percent': round(proc.info.get('memory_percent', 0.0), 2)
            })
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as proc_err:
        logger.warning(f"Non-blocking omission harvesting transient process rings: {proc_err}")
    except Exception as general_proc_fault:
        logger.warning(f"Unexpected process harvester discrepancy encountered: {general_proc_fault}")

    return processes


def collect_system_metrics() -> dict:
    """Performs non-blocking kernel state polling to extract real-time metrics."""
    disk_path = 'C:\\' if sys.platform.startswith('win') else '/'
    try:
        disk_percent = psutil.disk_usage(disk_path).percent
    except Exception:
        disk_percent = psutil.disk_usage('/').percent

    # Dynamically determine the operating system type to send with the package
    current_os = 'Windows' if sys.platform.startswith('win') else 'Linux'

    # Extract the fresh state array
    raw_processes = get_top_processes()

    
    # FIXED: node_id is now natively used as the JSON key and correctly references the config variable
    # Activated json.dumps() to serialize the process tree into a string for strict JSONB insertion
    return {
        "node_id": NODE_ID,        # Matches backend receiver layout perfectly
        "location": NODE_LOCATION,
        "os_type": current_os,     # In order to work on the operating system
        "cpu_usage": psutil.cpu_percent(interval=None), # cpu => cpu_usage
        "ram_usage": psutil.virtual_memory().percent, # ram => ram_usage
        "disk_usage": disk_percent, # disk => disk_usage
        "top_processes": json.dumps(raw_processes) # Activated json module to avoid 400 Bad Request
    }


def stream_telemetry_loop():
    """Main lifecycle thread handling telemetry packaging and transmission."""
    logger.info(f"Smart Monitor Agent successfully bound to Node ID: {NODE_ID} ({NODE_LOCATION})")
    logger.info(f"Target Central Server Endpoint: {CENTRAL_SERVER_URL}")
    logger.info("Commencing metric data synchronization pipeline...")

    psutil.cpu_percent(interval=None)
    time.sleep(1)

    with requests.Session() as session:
        while True:
            try:
                payload = collect_system_metrics()
                response = session.post(CENTRAL_SERVER_URL, json=payload, timeout=4)
                
                if response.status_code in [200, 201]:
                    logger.info(
                        f"Telemetry synchronized | Node: {payload['node_id']} ({payload['location']}) -> "
                        f"CPU: {payload['cpu_usage']}% | RAM: {payload['ram_usage']}%"
                        # Top Processes Cached: {len(payload['top_processes'])}"
                    )
                else:
                    logger.warning(f"Central Server rejected payload with status code: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                logger.error(f"Transmit Fault: Unable to reach Central Server at {CENTRAL_SERVER_URL}. Retrying...")
            except Exception as general_fault:
                logger.critical(f"Unexpected Agent Fault: {general_fault}")
                
            time.sleep(STREAM_INTERVAL_SECONDS)


if __name__ == "__main__":
    try:
        stream_telemetry_loop()
    except KeyboardInterrupt:
        logger.info("Agent process terminated gracefully by user.")
        sys.exit(0)