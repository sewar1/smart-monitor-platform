# Smart Monitor Platform

A production-grade, distributed real-time infrastructure monitoring platform and reactive mitigation engine engineered for high-availability cloud environments. The platform features cross-platform host telemetry extraction, containerized orchestration with host-kernel process injection, stateless cryptographic authentication, and automated anti-freeze guard resilience.

---

## Architectural Overview

The platform features a decoupled microservices-ready architecture managed entirely via **Docker Compose**. Edge traffic is intercepted by an **Nginx Reverse Proxy & Edge Gateway**, which serves static runtime visual assets while securely routing high-frequency metrics streams and WebSockets protocols directly to a concurrent **Flask API Engine**. 

Persistence is driven by an enterprise **PostgreSQL 15** data warehouse utilizing high-performance connection pooling, composite time-series indexing, and automated data retention workers. Distributed multi-city telemetry agents hook directly into host operating systems, bypassing container isolation parameters (`pid: "host"`, `privileged: true`) to profile and mitigate host-level runtime freeze vectors.

---

## Tech Stack

- **Containerization & Orchestration:** Docker, Docker Compose (Isolated Bridge Topology, Shared Host PID Context)
- **Edge Routing & API Gateway:** Nginx (Static Asset Caching, Cross-Protocol Reverse Proxy, Port 80 Access Gate)
- **Backend Core & Analytics Framework:** Python 3, Flask RESTful API Engine, Asynchronous Threading Workers
- **Database Architecture:** PostgreSQL 15 (Thread-Safe Connection Pooling, Named Persistent Volumes)
- **Security & IAM Infrastructure:** Stateless JWT Tokens (HS256 Signature), Constant-Time `bcrypt` Password Hashing rings, Immutability Guards
- **WSGI Application Server:** Gunicorn (Production-grade worker process management)
- **Telemetry Hardware Daemon:** Standalone Python Daemon backed by cross-platform `psutil` kernel space extraction
- **Target Environments:** Bare-Metal Windows Server Hosts (NSSM Daemonized), VMware Virtualized Clusters (Systemd isolated), Docker Container Sandboxes

---

## System Network Topology

```bash
┌──────────────────────────────┐
│        Client Browser        │
└──────────────┬───────────────┘
               │ HTTP (Port 80 Access Gate)
               ▼
┌──────────────────────────────┐
│     Nginx Proxy Gateway      │  ← Microservices Edge Routing & Static File Buffer
│  - Static Asset Delivery     │
│  - X-Real-IP Headers Injection
└──────────────┬───────────────┘
               │ Internal Docker Bridge Forwarding (/api Proxy Core)
               ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        DOCKER COMPOSE NETWORK MATRIX                   │
│                                                                        │
│   ┌──────────────────────────┐            ┌────────────────────────┐   │
│   │ Flask Dashboard Container│            │  PostgreSQL 15 Cluster │   │
│   │        (dashboard)       ├───────────►│          (db)          │   │
│   │ - Gunicorn Worker Stack  │  Thread    │ - Min/Max Conn Pool    │   │
│   │ - Anti-Freeze Analyser   │  Pooled    │ - BIGSERIAL Ledgers    │   │
│   │ - Retention Thread Cron  │  Sockets   │ - Composite Timeline IX│   │
│   └──────────────────────────┘            └────────────────────────┘   │
└──────────────────────▲─────────────────────────────────────────────────┘
                       │
                       │ Concurrent Secure Keep-Alive Telemetry Payload Push
                       │
┌──────────────────────┴─────────────────────────────────────────────────┐
│                    DISTRIBUTED CROSS-PLATFORM AGENTS                   │
│                                                                        │
│  [Docker Target Node]    [Bare-Metal Windows Node]   [VMware Ubuntu]   │
│    (Mannheim Container)      (Ludwigshafen NSSM)     (Heidelberg Server│
│   - privileged: true         - Win32 API Wrapper      - systemd Daemon │
│   - pid: "host" mapping      - LOCATION=.env tracking - Fail-Over Check│
└────────────────────────────────────────────────────────────────────────┘
```
---
## Project Structure
```bash
smart-monitor-platform/
│   .env                       # Global cluster database environment vectors
│   .gitignore                 # Git audit exclusion configuration
│   docker-compose.yml         # Container topology coordinator (PID shared, Ingestion-bound)
│   nginx.conf                 # Edge reverse-proxy configuration & socket upgrade matrices
│   README.md                  # Main high-level system documentation root (This File)
│   requirements.txt           # Shared staging dependencies
│
├───.vscode                    # Local editor integration context
├───agent                      # Autonomous distributed telemetry collector daemon
│   │   agent.py               # Cross-platform sensor poll & JSONB process tree compiler
│   │   Dockerfile             # Lightweight minimal layer agent cache builder
│   │   README.md              # Local agent deployment runbook
│   │   requirements.txt       # Core environment libraries (psutil, requests)
│   │   test_agent.py          # Unified nomenclature unit validation suite
│   └─── agent.env.example     # Reference guide for distributed server setups
│
├───core                       # Enterprise logical framework & system utilities
│       alerts.py              # Anomaly notification workflows (Telegram & SMTP)
│       analyzer.py            # Resource health indexing & automated OOM Anti-Freeze Guard
│       database.py            # Singleton pool manager & structural emulation routing
│       logger.py              # Chronological auditing and tracing engine
│       mailer.py              # SMTP email transmission handler
│       metrics.py             # OS state data abstraction parser
│       processes.py           # Deep task manager tracking metrics
│       security.py            # Cryptographic RBAC middleware and JWT decoders
│       __init__.py
│
├───dashboard                  # Central visual monitoring hub
│   │   app.py                 # Core WSGI Flask server, heartbeats, IAM routes
│   │   Dockerfile             # Production Gunicorn orchestration layer
│   │   README.md              # Local visual layer deployment instructions
│   │   requirements.txt       # Pinned backend application packages
│   │   test_app.py            # Auth ring security regression maps
│   │   __init__.py
│   ├───logs                   # Persistent application transaction logs
│   ├───static                 # Asynchronous telemetry themes & styles
│   └───templates              # Dynamic HTML engine UI panels (index, login)
│
└───screenshots                # Verification captures of verified interfaces
```
---

## Installation & Automated Deployment


Spin up the entire interconnected ecosystem (Reverse Proxy, API Gateway, and Relational Database Pools) with a single orchestration layer build command:


1. Clone repository
``` bash
git clone git@github.com:sewar1/smart-monitor-platform.git
cd smart-monitor-platform
```
2. Initialize Configurations
Ensure your local environment variable frameworks (.env) are active in the root folder.
Launch Local Cloud Stack
``` bash
docker-compose up --build
```
This handles automated connection pool seeding, declarative schema provisioning via container-native scripts (init.sql), internal bridge setup, and edge routing mapping.

3. Access Web Interface:
Open your browser and navigate to: http://localhost (Port 80 Gate).


##  Engineering Roadmap Achievements & Milestones

[x] Sprint 1: Distributed Telemetry Ingestion Core & Multi-Node Tracking (Delivered)

  - Database Decentralization Matrix: Separated schemas from Python logic; migrated persistence initialization to native container scripts (init.sql) using BIGSERIAL keys, JSONB process map spaces, and composite indexes (node_id, timestamp DESC) for lightning-fast dashboard rendering.

  - Thread-Safe Connection Pooling: Refactored database.py to leverage PostgreSQL connection pooling wrappers (psycopg2.pool.SimpleConnectionPool), mitigating socket resource starvation across concurrent agents.

  - Cross-Platform Host Injection: Fabricated native multi-node deployment paths; distributed and stabilized agent daemons across bare-metal Windows Server hosts (via NSSM in Ludwigshafen), virtualized VMware Ubuntu instances (via systemd units in Heidelberg), and sandboxed Docker container isolations.

  - Dynamic Environment Externalization: Cleansed agents and servers from hardcoded variables, leveraging runtime OS configurations (NODE_ID, NODE_LOCATION, CENTRAL_SERVER_URL).

  - Automated Anti-Freeze Subsystem (OOM Killer Simulation): Engineered a priority-sorting resource optimization trigger in analyzer.py. When system resource limits cross critical safety boundaries (95.0%), the guard cross-checks a case-insensitive whitelist and programmatically issues SIGTERM/termination signals to the single heaviest non-critical offender, logging incident history transparently.

  - Asynchronous Data Retention Worker: Built a background daemon thread (daemon=True) running inside the backend environment to systematically wipe historical     time-series metric snapshots older than 24 hours every 12 hours, ensuring lean index sizes.

  - Multi-Node State UI Switching: Overhauled JavaScript loops in index.html to track active_node variables, prevent canvas memory leaks via clean Chart.js     destruction, and dynamically pass node-scoped queries (/api/metrics?node_id=) to backend routers.

  - Live Node Heartbeat Tracking: Established a 60-second threshold evaluation system. Missing agent transmissions automatically trigger status shifting, rendering     red badge warning metrics on the client interface immediately if an edge node fails.

  - Test-Driven Nomenclature Safeguard: Upgraded test_agent.py to validate unified payload structures against code regressions, shielding data ingestion parameters.

- [ ] Sprint 2: Granular Role-Based Access Control (RBAC) Expansion & Security Hardening

  - Implement dynamic user configuration panels inside the dashboard restricted exclusively to the system root administration account.

  - Secure API vectors with adaptive rate-limiting middleware to shield security rings from brute-force authentication vectors.

  - Enforce automated user activity logging ledgers to preserve compliance auditing records.

- [ ] Sprint 3: Distributed Microservices Architecture Decomposition

  - Decouple the monolithic receiver route out of the dashboard portal container.

  - Establish a dedicated, high-speed ingestion-service engineered exclusively for multi-agent write-heavy operations.

  - Isolate the client user interface into a localized dashboard-service processing read-heavy analytical dashboard data streams.

- [ ] Sprint 4: CI/CD Pipeline Automation & Cloud Staging

  - Build automated workflows via GitHub Actions to enforce continuous checking, test execution, and isolated container registry uploads.

## Summary

This project demonstrates a complete DevOps lifecycle from development to containerized orchestration and bare-metal production deployment on an enterprise virtualized Linux server.
