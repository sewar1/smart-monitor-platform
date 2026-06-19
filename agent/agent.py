# ==============================================================================
# SMART MONITOR INFRASTRUCTURE - DISTRIBUTED TELEMETRY AGENT
# ==============================================================================
# Target deployment: Standalone Linux/Windows host monitoring daemon.
# Streams metric payloads via REST outbound channels to the central controller.
# Refactored to match the centralized database and app.py filtering contracts.
# ==============================================================================

import os
import time
import sys
import socket
import psutil
import requests

# CONFIGURATION MATRIX & ENVIRONMENT BINDING
# Dynamically reads from Host Environment mapped to match your centralized dashboard ports
CENTRAL_SERVER_URL = os.getenv("CENTRAL_SERVER_URL", "http://localhost:5000/api/metrics")
STREAM_INTERVAL_SECONDS = int(os.getenv("STREAM_INTERVAL_SECONDS", "5"))

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
        disk_percent = psutil.disk_usage('/').percent # Absolute fallback

    # Returns the exact keys required by app.py and database ingestion models
    return {
        "name": server_name,
        "cpu": psutil.cpu_percent(interval=None),
        "ram": psutil.virtual_memory().percent,
        "disk": disk_percent
    }

def stream_telemetry_loop():
    """Main lifecycle thread handling telemetry packaging and transmission."""
    server_name = get_node_metadata()
    print(f"[+] Smart Monitor Agent started successfully on node: {server_name}")
    print(f"[+] Target Central Server Endpoint: {CENTRAL_SERVER_URL}")
    print("[-] Commencing metric data synchronization pipeline...\n")

    # Initialize the CPU tracker interval on first boot loop
    psutil.cpu_percent(interval=None)
    time.sleep(1)

    while True:
        try:
            # 1. Gather dynamic localized metric snapshots
            payload = collect_system_metrics()
            
            # 2. Fire telemetry packet across the network
            response = requests.post(CENTRAL_SERVER_URL, json=payload, timeout=3)
            
            # 3. Audit transmission success status (Accepts 200 or 201 based on backend setup)
            if response.status_code in [200, 201]:
                print(f"[SUCCESS] Telemetry synchronized at {time.strftime('%X')} | Node: {payload['name']} -> CPU: {payload['cpu']}% | RAM: {payload['ram']}% | DISK: {payload['disk']}%")
            else:
                print(f"[WARNING] Central Server rejected payload with status code: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"[ERROR] Transmit Fault: Unable to reach Central Server at {CENTRAL_SERVER_URL}. Retrying...")
        except Exception as general_fault:
            print(f"[CRITICAL AGENT FAULT]: {general_fault}")
            
        # Yield execution control state back to the kernel for the configured buffer time
        time.sleep(STREAM_INTERVAL_SECONDS)

if __name__ == "__main__":
    stream_telemetry_loop()