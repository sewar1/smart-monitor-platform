# ==============================================================================
# SMART MONITOR PLATFORM - INFRSTRUCTURE HEALTH ANALYZER
# ==============================================================================
# Multi-criteria system status analysis engine and process investigator.
# Engineered with process lifecycle guards to prevent OS-level execution race conditions.
# ==============================================================================

import psutil
from typing import Dict, List, Tuple


class SystemAnalyzer:
    """
    Analyzes telemetry snapshots, computes weighted health matrices,
    and isolates high-consuming Linux OS processes.
    """

    def __init__(self, cpu_weight: float = 0.4, ram_weight: float = 0.4, disk_weight: float = 0.2):
        # Validate that weights strictly total up to 1.0 (100%)
        total_weight = cpu_weight + ram_weight + disk_weight
        if not abs(total_weight - 1.0) < 1e-9:
            raise ValueError("Telemetry weights allocation matrix must precisely sum up to 1.0")
            
        self.cpu_weight = cpu_weight
        self.ram_weight = ram_weight
        self.disk_weight = disk_weight

    def get_top_consuming_processes(self, limit: int = 5) -> Dict[str, List[Dict]]:
        """
        Scans Linux kernel process table snapshots dynamically.
        Safely captures and filters volatile system state processes (Zombies, Privileged).
        """
        active_processes: List[Dict] = []

        # Stream active processes efficiently with targeted memory/cpu attributes
        for process in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                # Capture info dictionary safe-loaded by psutil abstract layers
                p_info = process.info
                active_processes.append({
                    "pid": p_info.get("pid"),
                    "name": p_info.get("name") or "unknown",
                    "cpu": p_info.get("cpu_percent") or 0.0,
                    "memory": round(p_info.get("memory_percent") or 0.0, 2)
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Guard triggered: Process lifecycle mutated during iterator loop, skip to avoid crashes
                continue
            except Exception:
                continue

        # Mathematical slice sorting for resource profiling
        top_cpu = sorted(active_processes, key=lambda x: x["cpu"], reverse=True)[:limit]
        top_memory = sorted(active_processes, key=lambda x: x["memory"], reverse=True)[:limit]

        return {
            "top_cpu": top_cpu,
            "top_memory": top_memory
        }

    def calculate_weighted_health_score(self, cpu_usage: float, ram_usage: float, disk_usage: float) -> float:
        """
        Calculates the definitive infrastructure health index using a weighted balance algorithm.
        """
        cpu_free_component = (100.0 - cpu_usage) * self.cpu_weight
        ram_free_component = (100.0 - ram_usage) * self.ram_weight
        disk_free_component = (100.0 - disk_usage) * self.disk_weight

        aggregated_score = cpu_free_component + ram_free_component + disk_free_component
        return round(aggregated_score, 1)

    @staticmethod
    def classify_health_status(health_score: float) -> str:
        """
        Categorizes system operation states based on deterministic thresholds.
        """
        if health_score >= 80.0:
            return "Healthy"
        elif health_score >= 60.0:
            return "Warning"
        return "Critical"


# ==============================================================================
# BACKWARD COMPATIBILITY BRIDGE (Seamless abstraction for app.py integration)
# ==============================================================================
_analyzer_instance = SystemAnalyzer()

def get_top_processes(limit: int = 5) -> Dict[str, List[Dict]]:
    return _analyzer_instance.get_top_consuming_processes(limit=limit)

def calculate_health_score(cpu: float, ram: float, disk: float) -> float:
    return _analyzer_instance.calculate_weighted_health_score(cpu, ram, disk)

def get_health_status(score: float) -> str:
    return _analyzer_instance.classify_health_status(score)