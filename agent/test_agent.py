import pytest
import json
from agent.agent import collect_system_metrics

def test_collect_system_metrics_contains_all_keys():
    """
    Test driven constraint: Ensure the agent captures unified telemetry keys: node_id, cpu_usage, ram_usage, and disk_usage.
    """
    metrics = collect_system_metrics()
    
    # Unified Nomenclature Check
    assert "node_id" in metrics
    assert "location" in metrics
    assert "os_type" in metrics
    assert "cpu_usage" in metrics
    assert "ram_usage" in metrics
    assert "disk_usage" in metrics
    assert "top_processes" in metrics
    
    # Data Type Sanity Checks
    assert isinstance(metrics["cpu_usage"], (int, float))
    assert isinstance(metrics["ram_usage"], (int, float))
    assert isinstance(metrics["disk_usage"], (int, float))
    
    # Ensure that the operations have been successfully converted to JSON text to avoid a 400 Bad Request error
    assert isinstance(metrics["top_processes"], str)
    try:
        parsed_processes = json.loads(metrics["top_processes"])
        assert isinstance(parsed_processes, list)
    except json.JSONDecodeError:
        pytest.fail("top_processes field is not a valid JSON serialized string!")