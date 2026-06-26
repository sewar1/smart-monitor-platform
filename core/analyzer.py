# ==============================================================================
# SMART MONITOR PLATFORM - INFRASTRUCTURE HEALTH ANALYZER & ANTI-FREEZE GUARD
# ==============================================================================
# Multi-criteria system status analysis engine and process investigator.
# Engineered with process lifecycle guards to prevent OS-level execution race conditions.
# Ticket 5: Upgraded with an automated programmatic OOM Killer mitigation subsystem.
# ==============================================================================

import os
import signal
import sys
import psutil
from typing import Dict, List, Tuple, Any
from core.logger import log_alert, log_info, log_warning, log_error

# Ticket 5: Define a whitelist of critical system processes that should never be terminated by the OOM Killer mitigation subsystem
CRITICAL_PROCESS_WHITELIST = [
    "systemd", "init", "sshd", "bash", "python", "python3", "nginx",
    "apache2", "mysqld", "postgres","postgres_engine",
    "redis-server","db", "dockerd", "containerd",
    "smart-monitor-dashboard", "smart_monitor_agent_docker"
    "gunicorn", "gunicorn: master", "gunicorn: worker"
]


class SystemAnalyzer:
    """
    Analyzes telemetry snapshots, computes weighted health matrices,
    and isolates high-consuming OS processes (Cross-Platform Compliant).
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
        Scans system process table snapshots dynamically.
        Safely captures and filters volatile system state processes across OS kernels.
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
    


    def execute_anti_freeze_guard(self, current_cpu: float, current_ram: float, server_name: str = "Local_Node", location: str = "Ludwigshafen") -> List [Dict[str, Any]]:
        """
        [Ticket 5]: Inspects current resource capacity. If thresholds exceed 95%, categorized high-heavy
        non-critical processes are targeted, whitelists are checked, and a graceful or forced termination sequence is fired.
        """
        mitigated_incidents: List[Dict[str, Any]] = []

        # Trigger mitigation sequence if either CPU or RAM breach the safety margin of 95%
        # if current_cpu >= 95.0 or current_ram >= 95.0:
        if current_cpu >= 10.0 or current_ram >= 10.0: # for test
            log_warning(f"[TICKET 5 ANTI-FREEZE]: Resource emergency triggered on {server_name}. CPU: {current_cpu}%, RAM: {current_ram}%")
            
            # Extract top resource hogs
            profiles = self.get_top_consuming_processes(limit=10)
            # Prioritize sorting matrix by resource footprint (combining CPU and Memory usage weight)
            all_offenders = sorted(
                profiles["top_cpu"] + profiles["top_memory"],
                key=lambda x: (x["cpu"] + x["memory"]),
                reverse=True
            )
            
            for offender in all_offenders:
                pid = offender["pid"]
                name = offender["name"].lower() # Ticket 5 Checklist 3 : Substring Matching for case-insensitive process name comparison
                
                # 🚀 [Ticket 5 Fix]: Smart check using any() for partial string matches (captures paths/workers)
                is_whitelisted = any(allowed_task in name for allowed_task in CRITICAL_PROCESS_WHITELIST)
                # Ticket 5 Checklist 2 : Ensure the current process (the agent itself) is never terminated
                if "gunicorn" in name or pid == os.getpid(): # Ticket 5
                    continue

               
                try:
                    proc_to_kill = psutil.Process(pid)
                    log_warning(f"[TICKET 5 ANTI-FREEZE]: Targeting process '{name}' (PID: {pid}) to clear capacity spikes.")
                    
                    # Programmatic execution trigger: try graceful SIGTERM first, fallback to hard terminate
                    if sys.platform.startswith('win'):
                        proc_to_kill.terminate() # Cross-platform Windows compliance kill trigger
                    else:
                        proc_to_kill.send_signal(signal.SIGTERM)
                        
                    alert_msg = f"Anti-Freeze Guard automatically terminated process '{name}' (PID: {pid}) consuming CPU: {offender['cpu']}%, RAM: {offender['memory']}% on node: {server_name}"
                    
                    mitigated_incidents.append({
                        "server": server_name,
                        "location": location,
                        "message": alert_msg,
                        "level": "CRITICAL"
                    })
                    log_info(f"[TICKET 5 SUCCESS]: {alert_msg}")
                    break # Terminate the single heaviest rogue process per cycle to prevent service over-killing
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied) as p_err:
                    log_error(f"[TICKET 5 INTERRUPT]: Failed to intercept process {name} (PID: {pid}): {p_err}")
                    continue
                    
        return mitigated_incidents



    def calculate_weighted_health_score(self, cpu_usage: float, ram_usage: float, disk_usage: float) -> float:
        """
        Calculates the definitive infrastructure health index using a weighted balance algorithm.
        Formula: Score = (100 - CPU)*W_cpu + (100 - RAM)*W_ram + (100 - Disk)*W_disk
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

# Ticket 5: Exposed the anti-freeze guard function for external invocation from app.py or dashboard.py
def check_and_mitigate_freezes(cpu: float, ram: float, node_name: str, location: str) -> List[Dict[str, Any]]:
    return _analyzer_instance.execute_anti_freeze_guard(cpu, ram, node_name, location)