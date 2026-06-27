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

# ===================================================================================================
# [Ticket 9 - Configuration Externalization]: Load Environment Variables
# ===================================================================================================
# Reads configurations directly from the hosting OS environment or Docker ENV containers
CENTRAL_SERVER_URL = os.environ.get("CENTRAL_SERVER_URL", "http://localhost:5000/api/metrics/receiver")
NODE_ID = os.environ.get("NODE_ID", "Docker_Production_Container")
NODE_LOCATION = os.environ.get("NODE_LOCATION", "Ludwigshafen")

print(f"📡 Agent initialized for Node: [{NODE_ID}] at ({NODE_LOCATION})")
print(f"🔗 Target Ingestion API: {CENTRAL_SERVER_URL}")
# ===================================================================================================
# Here the script completes its original function to send data (reading psutil and sending payload)
# Just make sure your payload uses the new variables like this:
# payload = {
# "name": NODE_ID,
# "location": NODE_LOCATION,
# "cpu": psutil.cpu_percent(interval=1),
# ...
# }
#====================================================================================================




# CONFIGURATION MATRIX & ENVIRONMENT BINDING
CENTRAL_SERVER_URL = os.getenv("CENTRAL_SERVER_URL", "http://localhost:5000/api/metrics/receiver") #Ticket 2 : add receiver endpoint to the URL
STREAM_INTERVAL_SECONDS = int(os.getenv("STREAM_INTERVAL_SECONDS", "5"))

NODE_ID = os.getenv("NODE_ID", f"node-{socket.gethostname().lower()}") # Ticket 3 : Unique node identifier for distributed deployments
LOCATION = os.getenv("LOCATION", "Ludwigshafen")  # Ticket 3 : Location identifier for distributed deployments

# SETUP STRUCTURED PRODUCTION LOGGING
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("TelemetryAgent")

def get_top_processes() -> list: # Ticket 3 : this function is used to get the top 5 processes consuming the most CPU and RAM on the host node
    """
    Extracts the top 5 resource-consuming processes on the host node.
    Returns a list of dictionaries containing process name, PID, CPU%, and RAM%.
    """
    try:
        processes = []
        for proc in sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']),
                           key=lambda p: p.info.get('cpu_percent', 0) or 0,
                           reverse=True)[:5]:
            processes.append({
                'pid': proc.info.get('pid'),
                'name': proc.info.get('name'),
                'cpu_percent': proc.info.get('cpu_percent'),
                'memory_percent': round(proc.info.get('memory_percent', 0.0), 2)
            })
      
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as proc_err: #Ticket 3 : Handle specific process-related errors
        logger.warning(f"Non-blocking omission harvesting transient process rings: {proc_err}") # Ticket 3 :Log the specific process-related error
    except Exception as general_proc_fault: # Handle any other unexpected errors during process harvesting
        logger.warning(f"Unexpected process harvester discrepancy encountered: {general_proc_fault}") # Log the unexpected error for further investigation


    return processes

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
        "name": NODE_ID, # Ticket 3 : changed from server_name to NODE_ID to ensure unique identification across distributed deployments
        "location": LOCATION, # Ticket 3 : added location to the payload to match the updated save_metrics function signature in core/database.py
        "cpu": psutil.cpu_percent(interval=None),
        "ram": psutil.virtual_memory().percent,
        "disk": disk_percent,
        "top_processes": get_top_processes() # Ticket 3 : added top_processes to the payload to match the updated save_metrics function signature in core/database.py
    }

def stream_telemetry_loop():
    """Main lifecycle thread handling telemetry packaging and transmission."""
    server_name = get_node_metadata()

    logger.info(f"Smart Monitor Agent successfully bound to Node ID: {NODE_ID} ({LOCATION})") # Ticket 3 :Log the successful binding to the node
    logger.info(f"Target Central Server Endpoint: {CENTRAL_SERVER_URL}") #Ticket 3 : Log the target central server endpoint for telemetry transmission
    logger.info("Commencing metric data synchronization pipeline...") #Ticket 3 : Log the commencement of the metric data synchronization pipeline


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
                response = session.post(CENTRAL_SERVER_URL, json=payload, timeout=4) # Ticket 3 : Send the telemetry payload to the central server with a timeout of 4 seconds
                
                # 3. Audit transmission success status
                if response.status_code in [200, 201]:
                    logger.info(
                        f"Telemetry synchronized | Node: {payload['name']} ({payload['location']}) -> " # Ticket 3 : Log the telemetry synchronization with node name and location
                        f"CPU: {payload['cpu']}% | RAM: {payload['ram']}% | Top Processes Cached: {len(payload['top_processes'])}" # Ticket 3 : Log the number of top processes cached in the payload
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