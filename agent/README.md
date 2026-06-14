# Distributed Hardware Telemetry Agent
This directory contains the lightweight background monitoring daemon (`agent.py`).
This subsystem operates as an isolated, lightweight background daemon deployed directly on client host machines. Its core responsibility is extracting granular OS sensor telemetry and securely shipping it to the central server via asynchronous streams.

## Implemented Features
- **Low-Level Hardware Hooks:** Leverages `psutil` to inspect kernel-level metrics (CPU cores usage, physical memory arrays, disk I/O, and active task manager processes).
- **Resilient Network Ingestion:** Packages data frames into clean JSON structures and transmits them via HTTP POST to the central `/api/metrics` gateway.
- **Failover & Error Catching:** Includes exception handling to prevent daemon crashes during temporary network dropouts or API service downtimes.
- **Automated Verification:** Equipped with a test script (`test_agent.py`) utilizing `pytest` to audit payload consistency and calculation functions before runtime.

## File Architecture Analysis
- **`agent.py`**: The core runtime executable containing the telemetry gathering loops.
- **`test_agent.py`**: Automated unit tests checking metrics structure and endpoint connectivity simulations.

## Deployment Instructions (Windows / Linux Bare-Metal / VMware)

1. **Install Host Requirements:**
   ```bash
   pip install psutil requests pytest
