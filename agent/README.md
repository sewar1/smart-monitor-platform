# Distributed Hardware Telemetry Agent
This directory contains the lightweight background monitoring daemon (`agent.py`).
This subsystem operates as an isolated, lightweight background daemon deployed directly on client host machines. Its core responsibility is extracting granular OS sensor telemetry and securely shipping it to the central server via asynchronous streams.

## Implemented Features
- **Low-Level Hardware Hooks:** Leverages psutil to inspect kernel-level metrics (CPU cores usage, physical memory arrays, disk I/O, and active task manager processes).

- **Resilient Network Ingestion (HTTP Keep-Alive):** Packages data frames into clean JSON structures and transmits them via persistent HTTP sessions (requests.Session()) to the central /api/metrics/receiver gateway, maximizing connection throughput and avoiding TCP handshake fatigue.

- **Unified Nomenclature Matrix [Ticket 9]:** Enforces strict key alignment (node_id, cpu_usage, ram_usage, disk_usage, location, os_type) matching the enterprise database schema directly.

- **High-Frequency JSONB Serializer [Ticket 4]:** Incorporates explicit json.dumps() serialization on the active processes list to prevent 400 Bad Request rejections during deep binary JSON ingestion at the central API layer.

- **Failover & Error Catching:** Includes non-blocking exception handling to gracefully bypass transient process ring collection errors (NoSuchProcess, AccessDenied) and prevent daemon crashes during temporary network dropouts.

- **Automated Verification:** Equipped with an upgraded test script (test_agent.py) utilizing pytest to audit unified payload consistency, strict data types, and JSON string serialization validity before runtime.

## File Architecture Analysis
- **`agent.py`**: The core runtime executable containing the environment configuration matrix (.env loading) and the infinite telemetry gathering loop
- **`test_agent.py`**: Automated unit tests checking unified metrics structures, data type sanity, and payload compatibility against code regressions
- **agent.env.example:** Reference template outlining deployment variables like CENTRAL_SERVER_URL and geographical markers.

## Deployment Instructions (Windows / Linux Bare-Metal / VMware / Docker)

1. **Bare-Metal & VMware Deployment**
1.1. Install Host Requirements:
 ```bash
   pip install psutil requests pytest python-dotenv
```

1.2. Configure Environment: Create a .env file referencing your node configuration:
```bash
CENTRAL_SERVER_URL=http://<server-ip>:5000/api/metrics/receiver
STREAM_INTERVAL_SECONDS=5
NODE_ID=Your_Custom_Node_ID
NODE_LOCATION=Ludwigshafen
```
1.3. Execute Daemon:
```bash
python agent.py
```


2. **Isolated Container Deployment [Ticket 5]**
When deployed inside a Docker container context, the agent requires direct namespace mapping to break containment boundaries and monitor the actual host machine:

- Host Process Table Access: Must be run with pid: "host" to let the telemetry loops hook the true host kernel.

- Kernel Capabilities: Requires privileged: true inside the orchestration setup to allow smooth resource metric queries and signal execution.


## Automated Testing Baseline
To execute the nomenclature and structure shielding tests locally, run:

```bash
pytest test_agent.py -v
```
