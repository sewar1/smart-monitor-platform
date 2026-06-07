
# ==============================================================================
# SMART MONITOR PLATFORM - METRICS ENGINE (OOP MIGRATION)
# ==============================================================================
# Thread-safe, production-ready systems metrics harvester.
# Reads directly from the Linux system architecture and exposes structured data.
# ==============================================================================

import psutil
import random
from typing import Dict, List

# Core warm-up execution to calibrate the Linux CPU differential counter
psutil.cpu_percent(interval=0.1)


class MetricsCollector:
    """
    Monolithic and distributed systems metrics harvester engine.
    Handles boundaries normalization and dynamic multi-node architecture emulation.
    """
    
    def __init__(self, host_node_name: str = "linux-node-01"):
        self.host_node_name = host_node_name

    @staticmethod
    def _clamp_to_percentage_boundary(value: float) -> float:
        """
        Enforces absolute strict boundaries (0.0% - 100.0%) on system metrics.
        Prevents software component interface overflows.
        """
        return max(0.0, min(100.0, value))

    def collect_native_hardware_telemetry(self, node_identifier: str) -> Dict[str, any]:
        """
        Harvests raw structural telemetry from the Linux kernel virtual filesystems (/proc).
        Applies a safe localized jitter to emulate standard production infrastructure flux.
        """
        try:
            # CPU telemetry parsing
            raw_cpu = psutil.cpu_percent(interval=None)
            jittered_cpu = raw_cpu + random.uniform(-3.5, 3.5)

            # Volatile memory (RAM) utilization parsing
            raw_ram = psutil.virtual_memory().percent
            jittered_ram = raw_ram + random.uniform(-2.5, 2.5)

            # Block storage (Disk IO space) parsing
            raw_disk = psutil.disk_usage("/").percent

            return {
                "name": node_identifier,
                "cpu": round(self._clamp_to_percentage_boundary(jittered_cpu), 1),
                "ram": round(self._clamp_to_percentage_boundary(jittered_ram), 1),
                "disk": round(self._clamp_to_percentage_boundary(raw_disk), 1)
            }
        except Exception as kernel_fault:
            # Fallback mitigation if underlying OS prevents access to /proc paths
            return {
                "name": node_identifier,
                "cpu": 0.0, "ram": 0.0, "disk": 0.0,
                "error": f"OS Telemetry Ingestion Failure: {str(kernel_fault)}"
            }

    def aggregate_infrastructure_matrix(self, total_simulated_nodes: int = 3) -> Dict[str, List[Dict]]:
        """
        Aggregates individual server nodes into a unified data contract structure.
        """
        infrastructure_nodes = []
        
        # Primary host mapping (Your real running VM)
        host_telemetry = self.collect_native_hardware_telemetry(self.host_node_name)
        infrastructure_nodes.append(host_telemetry)

        # Emulation loop for additional topology nodes
        for node_index in range(2, total_simulated_nodes + 1):
            simulated_name = f"linux-node-0{node_index}"
            simulated_telemetry = self.collect_native_hardware_telemetry(simulated_name)
            infrastructure_nodes.append(simulated_telemetry)

        return {
            "nodes": infrastructure_nodes
        }


# ==============================================================================
# LEGACY BACKWARD COMPATIBILITY LAYER (Ensures app.py integration is intact)
# ==============================================================================
def get_system_metrics(nodes_count: int = 3) -> Dict[str, List[Dict]]:
    """
    Bridge abstraction function to maintain seamless integration with app.py routing
    """
    collector = MetricsCollector(host_node_name="server-1")
    return collector.aggregate_infrastructure_matrix(total_simulated_nodes=nodes_count)