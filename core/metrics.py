
# ==========================================
# SYSTEM METRICS MODULE
# ==========================================
# مسؤول عن:
# - جمع بيانات CPU / RAM / Disk
# - محاكاة multi-node environment
# - ضمان استقرار القيم (0–100%)
# ==========================================

import psutil
import random


# ==========================================
# INITIALIZATION (IMPORTANT FIX)
# ==========================================
# psutil.cpu_percent يحتاج warm-up
# حتى لا يرجع 0 في أول استدعاء

psutil.cpu_percent(interval=0.1)


# ==========================================
# HELPER: NORMALIZATION
# ==========================================

def clamp_percentage(value: float) -> float:
    """
    Ensures metric values stay within valid range (0–100).
    Prevents invalid spikes due to randomness or system noise.
    """

    return max(0.0, min(100.0, value))


# ==========================================
# CORE: SINGLE NODE METRICS
# ==========================================

def collect_node_metrics(node_name: str) -> dict:
    """
    Collects system metrics for a single node.

    In real DevOps systems:
    - This represents one server / VM / container
    """

    # ------------------------------
    # CPU USAGE
    # ------------------------------
    cpu = psutil.cpu_percent(interval=None)
    cpu += random.uniform(-4, 4)

    # ------------------------------
    # RAM USAGE
    # ------------------------------
    ram = psutil.virtual_memory().percent
    ram += random.uniform(-3, 3)

    # ------------------------------
    # DISK USAGE
    # ------------------------------
    disk = psutil.disk_usage("/").percent

    # ------------------------------
    # RETURN NORMALIZED DATA
    # ------------------------------
    return {
        "name": node_name,
        "cpu": round(clamp_percentage(cpu), 1),
        "ram": round(clamp_percentage(ram), 1),
        "disk": round(clamp_percentage(disk), 1)
    }


# ==========================================
# CORE: MULTI-NODE SYSTEM SIMULATION
# ==========================================

def get_system_metrics(nodes_count: int = 3) -> dict:
    """
    Simulates distributed infrastructure monitoring.

    Example:
    - server-1
    - server-2
    - server-3
    """

    nodes = []

    for i in range(1, nodes_count + 1):

        node = collect_node_metrics(f"server-{i}")
        nodes.append(node)

    return {
        "nodes": nodes
    }