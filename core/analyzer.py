# ==========================================
# SYSTEM HEALTH ANALYZER
# ==========================================

import psutil

# ==========================================
# TOP PROCESS ANALYZER
# ==========================================

def get_top_processes(limit=5):
    """
    Returns the top CPU and RAM consuming processes.
    """

    processes = []

    for process in psutil.process_iter(
        ['pid', 'name', 'cpu_percent', 'memory_percent']
    ):

        try:

            processes.append({
                "pid": process.info["pid"],
                "name": process.info["name"],
                "cpu": process.info["cpu_percent"],
                "memory": round(
                    process.info["memory_percent"],
                    2
                )
            })

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):
            continue

    # Sort by CPU usage
    top_cpu = sorted(
        processes,
        key=lambda x: x["cpu"],
        reverse=True
    )[:limit]

    # Sort by RAM usage
    top_memory = sorted(
        processes,
        key=lambda x: x["memory"],
        reverse=True
    )[:limit]

    return {
        "top_cpu": top_cpu,
        "top_memory": top_memory
    }


# ==========================================
# SYSTEM HEALTH SCORE
# ==========================================

def calculate_health_score(cpu, ram, disk):
    """
    Calculates overall system health score.
    """

    cpu_score = 100 - cpu
    ram_score = 100 - ram
    disk_score = 100 - disk

    final_score = (
        (cpu_score * 0.4) +
        (ram_score * 0.4) +
        (disk_score * 0.2)
    )

    return round(final_score, 1)


# ==========================================
# HEALTH STATUS CLASSIFIER
# ==========================================

def get_health_status(score):
    """
    Converts health score into readable status.
    """

    if score >= 80:
        return "Healthy"

    elif score >= 60:
        return "Warning"

    else:
        return "Critical"