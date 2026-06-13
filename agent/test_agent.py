import pytest
from agent.agent import collect_system_metrics

def test_collect_system_metrics_contains_all_keys():
    """
    Test driven constraint: Ensure the agent captures CPU, RAM, AND DISK.
    """
    metrics = collect_system_metrics()
    
    assert "server" in metrics
    assert "cpu" in metrics
    assert "ram" in metrics
    assert "disk" in metrics  # هذا سيمر بنجاح لأن الدالة تجمع البيانات داخلياً
    
    assert isinstance(metrics["disk"], (int, float))