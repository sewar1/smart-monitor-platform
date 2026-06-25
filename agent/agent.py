# ==============================================================================
# SMART MONITOR INFRASTRUCTURE - DISTRIBUTED TELEMETRY AGENT
# ==============================================================================
# Target deployment: Standalone Linux/Windows host monitoring daemon.
# Streams metric payloads via persistent HTTP Sessions to the central controller.
# Optimized with HTTP Keep-Alive, structured logging, and production error handling.
# ==============================================================================

import os
import time
import sys
import socket
import logging
import psutil
import requests

# CONFIGURATION MATRIX & ENVIRONMENT BINDING
CENTRAL_SERVER_URL = os.getenv("CENTRAL_SERVER_URL", "http://localhost:5000/api/metrics/receiver") # add receiver endpoint to the URL
STREAM_INTERVAL_SECONDS = int(os.getenv("STREAM_INTERVAL_SECONDS", "5"))

# SETUP STRUCTURED PRODUCTION LOGGING
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("TelemetryAgent")

def get_node_metadata() -> str:
    """
    Extracts custom server alias, or falls back to the actual hostname machine identifier.
    Matches the AGENT_NAME environmental variable layout.
    """
    return os.getenv("AGENT_NAME", socket.gethostname())

def collect_system_metrics() -> dict:
    """Performs non-blocking kernel state polling to extract real-time metrics."""
    server_name = get_node_metadata()
    
    # Cross-Platform Guard: Windows clusters fail on '/' mount path inquiries
    disk_path = 'C:\\' if sys.platform.startswith('win') else '/'
    try:
        disk_percent = psutil.disk_usage(disk_path).percent
    except Exception:
        disk_percent = psutil.disk_usage('/').percent  # Absolute fallback

    return {
        "name": server_name,
        "cpu": psutil.cpu_percent(interval=None),
        "ram": psutil.virtual_memory().percent,
        "disk": disk_percent
    }

def stream_telemetry_loop():
    """Main lifecycle thread handling telemetry packaging and transmission."""
    server_name = get_node_metadata()
    logger.info(f"Smart Monitor Agent started successfully on node: {server_name}")
    logger.info(f"Target Central Server Endpoint: {CENTRAL_SERVER_URL}")
    logger.info("Commencing metric data synchronization pipeline...")

    # Initialize the CPU tracker interval on first boot loop
    psutil.cpu_percent(interval=None)
    time.sleep(1)

    # Reusable Persistent HTTP Session for connection pooling & Keep-Alive optimized performance
    with requests.Session() as session:
        while True:
            try:
                # 1. Gather dynamic localized metric snapshots
                payload = collect_system_metrics()
                
                # 2. Fire telemetry packet across the network using the persistent session
                response = session.post(CENTRAL_SERVER_URL, json=payload, timeout=3)
                
                # 3. Audit transmission success status
                if response.status_code in [200, 201]:
                    logger.info(
                        f"Telemetry synchronized | Node: {payload['name']} -> "
                        f"CPU: {payload['cpu']}% | RAM: {payload['ram']}% | DISK: {payload['disk']}%"
                    )
                else:
                    logger.warning(f"Central Server rejected payload with status code: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                logger.error(f"Transmit Fault: Unable to reach Central Server at {CENTRAL_SERVER_URL}. Retrying...")
            except Exception as general_fault:
                logger.critical(f"Unexpected Agent Fault: {general_fault}")
                
            # Yield execution control state back to the kernel
            time.sleep(STREAM_INTERVAL_SECONDS)

if __name__ == "__main__":
    try:
        stream_telemetry_loop()
    except KeyboardInterrupt:
        logger.info("Agent process terminated gracefully by user.")
        sys.exit(0)