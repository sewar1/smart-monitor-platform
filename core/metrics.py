# ==============================================================================
# SMART MONITOR PLATFORM - METRICS ENGINE (OOP MIGRATION)
# ==============================================================================
# Thread-safe, production-ready systems metrics harvester.
# Reads directly from the system architecture and exposes structured data.
# Dynamically adapts to custom agent environment names via OS kernel variables.
# ==============================================================================

import os
import psutil
import random
from typing import Dict, List

# Core warm-up execution to calibrate the system CPU differential counter
psutil.cpu_percent(interval=0.1)


class MetricsCollector:
    """
    Unified systems metrics harvester engine.
    Handles boundaries normalization and dynamic single-node hardware telemetry harvesting.
    """
    
    def __init__(self):
        # Fetch target agent identity from host OS environmental boundaries
        self.host_node_name = os.getenv("AGENT_NAME", "default-agent")

    @staticmethod
    def _clamp_to_percentage_boundary(value: float) -> float:
        """
        Enforces absolute strict boundaries (0.0% - 100.0%) on system metrics.
        Prevents software component interface overflows.
        """
        return max(0.0, min(100.0, value))

    def collect_native_hardware_telemetry(self) -> Dict[str, any]:
        """
        Harvests raw structural telemetry from the underlying OS kernel API layers.
        Applies a safe localized jitter to emulate standard production infrastructure flux.
        """
        try:
            # CPU telemetry parsing
            raw_cpu = psutil.cpu_percent(interval=None)
            jittered_cpu = raw_cpu + random.uniform(-1.5, 1.5)

            # Volatile memory (RAM) utilization parsing
            raw_ram = psutil.virtual_memory().percent
            jittered_ram = raw_ram + random.uniform(-1.0, 1.0)

            # Block storage (Disk IO space) parsing
            raw_disk = psutil.disk_usage("/").percent

            return {
                "name": self.host_node_name,
                "cpu": round(self._clamp_to_percentage_boundary(jittered_cpu), 1),
                "ram": round(self._clamp_to_percentage_boundary(jittered_ram), 1),
                "disk": round(self._clamp_to_percentage_boundary(raw_disk), 1)
            }
        except Exception as kernel_fault:
            # Fallback mitigation if underlying OS prevents access to hardware subsystem paths
            return {
                "name": self.host_node_name,
                "cpu": 0.0, "ram": 0.0, "disk": 0.0,
                "error": f"OS Telemetry Ingestion Failure: {str(kernel_fault)}"
            }

    def aggregate_infrastructure_matrix(self) -> Dict[str, List[Dict]]:
        """
        Aggregates the current individual server node metrics into a unified data contract structure.
        """
        infrastructure_nodes = []
        
        # Primary host mapping (The actual running system environment)
        host_telemetry = self.collect_native_hardware_telemetry()
        infrastructure_nodes.append(host_telemetry)

        return {
            "nodes": infrastructure_nodes
        }


# ==============================================================================
# LEGACY BACKWARD COMPATIBILITY LAYER (Ensures routing integration remains intact)
# ==============================================================================
def get_system_metrics() -> Dict[str, List[Dict]]:
    """
    Bridge abstraction function to maintain seamless integration with standard tracking routines.
    """
    collector = MetricsCollector()
    return collector.aggregate_infrastructure_matrix()