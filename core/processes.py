# ==========================================
# IMPORTS
# ==========================================

import psutil


# ==========================================
# PROCESS ANALYZER
# ==========================================

def get_top_processes(limit=5):
    """
    Return top CPU and RAM consuming processes.
    """

    processes = []

    # Iterate through running system processes
    for process in psutil.process_iter([
        "pid",
        "name",
        "cpu_percent",
        "memory_percent"
    ]):

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

    # ==========================================
    # TOP CPU PROCESSES
    # ==========================================

    top_cpu = sorted(

        processes,

        key=lambda process: process["cpu"],

        reverse=True

    )[:limit]

    # ==========================================
    # TOP MEMORY PROCESSES
    # ==========================================

    top_memory = sorted(

        processes,

        key=lambda process: process["memory"],

        reverse=True

    )[:limit]

    # ==========================================
    # RETURN RESULTS
    # ==========================================

    return {

        "top_cpu": top_cpu,

        "top_memory": top_memory

    }