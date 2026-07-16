# ==============================================================================
# SMART MONITOR INFRASTRUCTURE - DISTRIBUTED TELEMETRY AGENT (PYTHON SIDE)
# ==============================================================================
# Target deployment: Standalone Linux/Windows host monitoring daemon.
# Streams metric payloads via persistent HTTP Sessions to the central controller.
# Optimized with HTTP Keep-Alive, structured logging, and production error handling.
#
# GERMAN MARKET PORTFOLIO ARCHITECTURE NOTE (POLYGLOT PATTERN):
# ------------------------------------------------------------------------------
# Why Python for the Agent & Java Spring Boot for the Central Core Gateway?
# This showcases a classic production-grade Microservices/Distributed Systems 
# architectural pattern (Enterprise Integration). 
# - Java Spring Boot provides robust, high-throughput, typed transactional REST APIs 
#   and solid Security Filter Chains on the centralized backend.
# - Python is leveraged on target nodes because it is the ultimate scripting 
#   standard for system automation, OS-level API access (via psutil), and low-overhead
#   telemetry collection.
# ==============================================================================

import os
import json
import random  # Restored and imported cleanly for localized simulation jitter
import time
import sys
import socket
import logging
import psutil
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environmental variables from .env file immediately to map runtime configs
load_dotenv()

# ==============================================================================
# CONFIGURATION MATRIX & ENVIRONMENT BINDING
# ==============================================================================

# UPDATED: Re-pointed default target gateway from Flask (Port 5000) to Spring Boot Ingestion (Port 8080)
# Dynamic endpoint fallback ensures no structural breakdowns in multi-environment setups.
RAW_SERVER_URL = os.getenv("CENTRAL_SERVER_URL", "http://127.0.0.1:8080/api/metrics/collect")
CENTRAL_SERVER_URL = RAW_SERVER_URL.replace("http:///", "http://")

STREAM_INTERVAL_SECONDS = int(os.getenv("STREAM_INTERVAL_SECONDS", "5"))

# SECURITY ENHANCEMENT: API Ingestion token matching the Java Spring Boot Interceptor/Filter
# Prevents unauthorized malicious payloads or spoofed metrics from poisoning DB.
AGENT_SECRET_TOKEN = os.getenv("AGENT_SECRET_TOKEN", "sewarl_secure_system_agent_token_2026")

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


# ==============================================================================
# MATHEMATICAL BOUNDARY STANDARDIZATION & JITTER UTILITIES
# ==============================================================================

def clamp_to_percentage_boundary(value: float) -> float:
    """
    Enforces absolute strict boundaries (0.0% - 100.0%) on system metrics.
    Prevents software component interface overflows on the Database / Backend side.
    """
    return max(0.0, min(100.0, value))


# ==============================================================================
# PROCESS TABLE HARVESTER (Derived from ProcessInvestigator)
# ==============================================================================

def harvest_detailed_process_table() -> list:
    """
    Scans the active OS process descriptor table.
    Safely maps system-level structures while guarding against volatile state shifts.
    (Derived from Advanced Process Investigator to enable deep telemetry auditing)
    """
    detailed_table = []
    target_attrs = ['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'create_time']

    for process in psutil.process_iter(target_attrs):
        try:
            p_info = process.info
            
            # Format epoch creation time into localized ISO standard
            raw_time = p_info.get("create_time")
            formatted_time = datetime.fromtimestamp(raw_time).strftime("%Y-%m-%d %H:%M:%S") if raw_time else "N/A"

            detailed_table.append({
                "pid": p_info.get("pid"),
                "name": p_info.get("name") or "unknown",
                "user": p_info.get("username") or "system",
                "cpu": p_info.get("cpu_percent") or 0.0,
                "memory": round(p_info.get("memory_percent") or 0.0, 2),
                "started_at": formatted_time
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Guard against volatile processes terminating during telemetry sweep (very common)
            continue
        except Exception:
            continue

    return detailed_table


def get_top_processes(limit: int = 5) -> list:
    """
    Profiles the system process state to extract isolated core metric consumers.
    Integrates deep auditing from harvest_detailed_process_table into top consumption lists.
    """
    all_processes = harvest_detailed_process_table()
    
    # Sort and filter the top resource-consuming processes on the host node
    top_consumers = sorted(all_processes, key=lambda x: x["cpu"], reverse=True)[:limit]

    return top_consumers


def collect_system_metrics() -> dict:
    """
    Performs non-blocking kernel state polling to extract real-time metrics.
    Integrates clamping boundaries and custom simulation jitters derived from metrics engine.
    """
    disk_path = 'C:\\' if sys.platform.startswith('win') else '/'
    try:
        disk_percent = psutil.disk_usage(disk_path).percent
    except Exception:
        disk_percent = psutil.disk_usage('/').percent

    # Dynamically determine the operating system type to send with the package
    current_os = 'Windows' if sys.platform.startswith('win') else 'Linux'

    # Extract raw hardware telemetry from OS Kernel layers using original names
    cpu_usage = psutil.cpu_percent(interval=None)
    ram_usage = psutil.virtual_memory().percent

    # Apply localized production infrastructure jitter to mimic standard server flux
    # and normalize values through boundary clamping
    jittered_cpu = cpu_usage + random.uniform(-1.5, 1.5)
    jittered_ram = ram_usage + random.uniform(-1.0, 1.0)

    final_cpu = round(clamp_to_percentage_boundary(jittered_cpu), 1)
    final_ram = round(clamp_to_percentage_boundary(jittered_ram), 1)
    final_disk = round(clamp_to_percentage_boundary(disk_percent), 1)

    # Extract the fresh state array
    raw_processes = get_top_processes()

    # Spring Boot Integration Note:
    # "node_id" mapping is natively compatible with PostgreSQL snake_case matching.
    # The JSON stringification of raw_processes matches JPA JSONB converter schemas.
    return {
        "node_id": NODE_ID,        # Matches backend receiver layout perfectly
        "location": NODE_LOCATION,
        "os_type": current_os,     # In order to work on the operating system
        "cpu_usage": final_cpu,    # cpu => cpu_usage and final_cpu to ensure clamped and jittered values
        "ram_usage": final_ram,    # ram => ram_usage and final_ram to ensure clamped and jittered values
        "disk_usage": final_disk,  # disk => disk_usage and final_disk to ensure clamped and jittered values
        "top_processes": json.dumps(raw_processes) # Serialized to avoid Spring Boot parsing mismatches
    }


def stream_telemetry_loop():
    """Main lifecycle thread handling telemetry packaging and transmission."""
    logger.info(f"Smart Monitor Agent successfully bound to Node ID: {NODE_ID} ({NODE_LOCATION})")
    logger.info(f"Target Central Server Endpoint: {CENTRAL_SERVER_URL}")
    logger.info("Commencing metric data synchronization pipeline...")

    # Prime psutil's CPU check to prevent 0.0% initial read anomaly
    psutil.cpu_percent(interval=None)
    time.sleep(1)

    # Architectural Optimization: Persisting standard HTTP Keep-Alive connection pool
    # significantly lowers TCP handshake overhead on high-frequency streaming.
    with requests.Session() as session:
        while True:
            try:
                payload = collect_system_metrics()
                
                # SECURITY IMPLEMENTATION:
                # Appending the custom token header to the outbound request. 
                # This must be intercepted and validated by Spring Boot Filter chain.
                headers = {
                    "Content-Type": "application/json",
                    "X-Agent-Token": AGENT_SECRET_TOKEN
                }
                
                response = session.post(CENTRAL_SERVER_URL, json=payload, headers=headers, timeout=4)
                
                if response.status_code in [200, 201]:
                    logger.info(
                        f"Telemetry synchronized | Node: {payload['node_id']} ({payload['location']}) -> "
                        f"CPU: {payload['cpu_usage']}% | RAM: {payload['ram_usage']}%"
                    )
                else:
                    logger.warning(
                        f"Central Server rejected payload with status code: {response.status_code}. "
                        f"Check if Spring Boot Gateway token verification is configured correctly."
                    )
                    
            except requests.exceptions.ConnectionError:
                logger.error(
                    f"Transmit Fault: Unable to reach Central Server at {CENTRAL_SERVER_URL}. "
                    f"Backend might be starting up or under maintenance. Retrying in {STREAM_INTERVAL_SECONDS}s..."
                )
            except Exception as general_fault:
                # Production Safeguard: Catch generic runtime exceptions to prevent background daemon crash.
                logger.critical(f"Unexpected Agent Fault: {general_fault}")
                
            time.sleep(STREAM_INTERVAL_SECONDS)


if __name__ == "__main__":
    try:
        stream_telemetry_loop()
    except KeyboardInterrupt:
        logger.info("Agent process terminated gracefully by user.")
        sys.exit(0)