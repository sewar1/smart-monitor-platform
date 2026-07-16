# ==============================================================================
# SMART MONITOR PLATFORM - INCIDENT ALERTING ENGINE
# ==============================================================================
# Evaluates structural infrastructure telemetry states against strict boundaries.
# Complies with dynamic Twelve-Factor environment dynamic configuration standards.
# ==============================================================================

import os
from typing import List, Dict
from core.logger import log_alert


class AlertEngine:
    """
    Evaluates node performance matrices dynamically using decoupled operational thresholds.
    """

    def __init__(self):
        # Fallback values are strictly defined if OS values are missing in .env
        self.cpu_threshold = float(os.getenv("ALERT_CPU_THRESHOLD", 85.0))
        self.ram_threshold = float(os.getenv("ALERT_RAM_THRESHOLD", 85.0))
        self.disk_threshold = float(os.getenv("ALERT_DISK_THRESHOLD", 90.0))

    def evaluate_infrastructure_nodes(self, nodes: List[Dict]) -> List[str]:
        """
        Iterates across active node topologies to intercept anomalous system behaviors.
        """
        active_warnings: List[str] = []

        # Inversion of Control: Configuration dictionary driving dynamic validation rules
        validation_rules = [
            {"key": "cpu", "threshold": self.cpu_threshold, "label": "HIGH CPU USAGE"},
            {"key": "ram", "threshold": self.ram_threshold, "label": "HIGH RAM USAGE"},
            {"key": "disk", "threshold": self.disk_threshold, "label": "HIGH DISK USAGE"}
        ]

        for node in nodes:
            node_name = node.get("name") or node.get("server") or "unknown-server"

            for rule in validation_rules:
                metric_key = rule["key"]
                threshold_limit = rule["threshold"]
                alarm_label = rule["label"]

                # Extract metric with fail-safe zero boundary
                current_value = node.get(metric_key, 0.0)

                if current_value > threshold_limit:
                    incident_message = f"⚠️ [{node_name}] - {alarm_label}: {current_value:.1f}% (Threshold: {threshold_limit}%)"
                    
                    active_warnings.append(incident_message)
                    log_alert(incident_message)

        return active_warnings


# ==============================================================================
# SEAMLESS REFRACTORING BRIDGE (Maintains perfect backward compatibility)
# ==============================================================================
_alert_engine_instance = AlertEngine()

def check_alerts(nodes: List[Dict]) -> List[str]:
    """
    Main abstract functional router required by dashboard/app.py logic layers.
    """
    return _alert_engine_instance.evaluate_infrastructure_nodes(nodes)