
import psutil                      # System metrics (CPU, RAM, Disk)
import random                      # Used to simulate multiple machines

def get_system_metrics():
    """
    Collects and simulates monitoring metrics
    for multiple system nodes.
    """

    nodes = []
    # Simulate 3 different servers
    for i in range(1, 4):

        # CPU usage (with small randomness to simulate real fluctuations)
        cpu = psutil.cpu_percent() + random.uniform(-5, 5)

        # RAM usage (also slightly randomized)
        ram = psutil.virtual_memory().percent + random.uniform(-3, 3)

        # Disk usage (real system value)
        disk = psutil.disk_usage('/').percent

        # Store node data
        nodes.append({
            "name": f"server-{i}",
            
            # Ensure values stay within valid range (0–100%)
            "cpu": max(0, min(cpu, 100)),
            "ram": max(0, min(ram, 100)),
            "disk": disk
        })

    return {"nodes": nodes}