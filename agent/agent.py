# ==============================================================================
# SMART MONITOR INFRASTRUCTURE - DISTRIBUTED TELEMETRY AGENT
# ==============================================================================
# Target deployment: Standalone Linux/Windows host monitoring daemon.
# Streams metric payloads via REST outbound channels to the central controller.
# ==============================================================================

import time
import socket
import psutil
import requests

# 🌐 CONFIGURATION MATRIX
# Change 'localhost' to your central server's IP address when deploying on remote hosts
CENTRAL_SERVER_URL = "http://localhost:5000/api/metrics/receiver"
STREAM_INTERVAL_SECONDS = 5

def get_hostname() -> str:
    """Extracts the unique network identifier node name of the current host."""
    return socket.gethostname()

def collect_system_metrics() -> dict:
    """Performs non-blocking kernel state polling to extract real-time metrics."""
    return {
        "server": get_hostname(),
        "cpu": psutil.cpu_percent(interval=None),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent
    }

def stream_telemetry_loop():
    """Main lifecycle thread handling telemetry packaging and transmission."""
    hostname = get_hostname()
    print(f"[+] Smart Monitor Agent started successfully on host: {hostname}")
    print(f"[+] Target Central Server Endpoint: {CENTRAL_SERVER_URL}")
    print("[-] Commencing metric data synchronization pipeline...\n")

    while True:
        try:
            # 1. Gather dynamic metric snapshots
            payload = collect_system_metrics()
            
            # 2. Fire telemetry packet across the network
            response = requests.post(CENTRAL_SERVER_URL, json=payload, timeout=3)
            
            # 3. Audit transmission success status
            if response.status_code == 201:

                print(f"[SUCCESS] Telemetry synchronized at {time.strftime('%X')} -> CPU: {payload['cpu']}% | RAM: {payload['ram']}% | DISK: {payload['disk']}%")
            else:
                print(f"[WARNING] Server rejected payload with status code: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"[ERROR] Transmit Fault: Unable to reach Central Server at {CENTRAL_SERVER_URL}. Retrying...")
        except Exception as general_fault:
            print(f"[CRITICAL AGENT FAULT]: {general_fault}")
            
        # Yield execution control state back to the kernel for the configured buffer time
        time.sleep(STREAM_INTERVAL_SECONDS)

if __name__ == "__main__":
    stream_telemetry_loop()