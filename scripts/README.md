# Smart Monitor Platform — SRE Automation Scripts

This directory contains utility and automation scripts designed for rapid deployment, health verification, and incident diagnostics of the Smart Monitor Platform in Ubuntu/Linux environments.

---

## Available Scripts

### 1. `health-check.sh`
* **Purpose:** Performs a comprehensive system health check.
* **What it does:**
  * Inspects Docker container statuses and health probes.
  * Verifies backend API reachability and HTTP response codes.
  * Scans recent backend container logs for critical exceptions, database connection errors, and fatal failures.
* **Usage:**
  ```bash
  ./scripts/health-check.sh
  ```
### 2. `collect-diagnostics.sh`
* **Purpose:** Generates an SRE-style diagnostics bundle for rapid troubleshooting.
* **What it does:**
  * Exports all Docker Compose container logs into a structured directory.
  * Captures journalctl logs for the Docker system daemon (Linux/Systemd).
  * Aggregates local application logs if available.
  * Automatically scans, filters, and summarizes critical errors, exceptions, and fatal failures into an errors-summary.log file.
* **Usage:**
  ```bash
  ./scripts/collect-diagnostics.sh
  ```
* **Output bundle location:** ./diagnostics/

## Quick Setup & Permissions
Before running any script for the first time on Ubuntu, ensure they have execution permissions:
  ```bash
  chmod +x ./scripts/*.shh
  ```
