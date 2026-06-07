# ==============================================================================
# SMART MONITOR PLATFORM - ADVANCED PROCESS INVESTIGATOR
# ==============================================================================
# Specialized engine for Linux process tree auditing and lifecycle analysis.
# Extracts micro-level telemetry for specialized administrative investigation.
# ==============================================================================

import psutil
from datetime import datetime
from typing import List, Dict


class ProcessInvestigator:
    """
    Advanced inspector encapsulated to analyze, filter, and audit 
    low-level OS process parameters inside Linux Kernel space.
    """

    def __init__(self):
        pass

    def harvest_detailed_process_table(self) -> List[Dict]:
        """
        Scans the active OS process descriptor table.
        Safely maps system-level structures while guarding against volatile state shifts.
        """
        detailed_table: List[Dict] = []

        # Target rich parameters directly from the Linux task structures
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
                # Standard lifecycle mitigation for fast-dying processes
                continue
            except Exception:
                continue

        return detailed_table

    def get_top_resource_consumers(self, limit: int = 5) -> Dict[str, List[Dict]]:
        """
        Profiles the system process state to extract isolated core metric consumers.
        """
        all_processes = self.harvest_detailed_process_table()

        top_cpu = sorted(all_processes, key=lambda x: x["cpu"], reverse=True)[:limit]
        top_memory = sorted(all_processes, key=lambda x: x["memory"], reverse=True)[:limit]

        return {
            "top_cpu": top_cpu,
            "top_memory": top_memory
        }


# ==============================================================================
# COMPATIBILITY ROUTER (Guards existing hooks inside app.py or analyzer.py)
# ==============================================================================
_investigator_instance = ProcessInvestigator()

def get_top_processes(limit: int = 5) -> Dict[str, List[Dict]]:
    """
    Main abstract function executing top resource usage diagnostics.
    """
    return _investigator_instance.get_top_resource_consumers(limit=limit)