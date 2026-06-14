# Smart Monitor Platform

A production-grade, distributed real-time infrastructure monitoring platform engineered for high-availability cloud environments. The system features cross-platform host telemetry extraction, containerized microservices orchestration, stateless API token authentication, and enterprise-tier reverse-proxy edge routing.

---

## Architectural Overview

The platform features a modern microservices architecture managed entirely via **Docker Compose**. Edge traffic is intercepted by an **Nginx Reverse Proxy**, which serves static visual assets as a Single Page Application (SPA) while securely bridging underlying asynchronous telemetry streams directly to an isolated **Flask API Engine** backed by a persistent **PostgreSQL 15** data warehouse.

---

## Tech Stack

- **Containerization & Orchestration:** Docker, Docker Compose (Isolated Bridge Topology)
- **Edge Routing & Proxy:** Nginx (Static Content Caching, Port 80 Gateway)
- **Backend Framework:** Python 3, Flask RESTful API Engine
- **Database Architecture:** PostgreSQL 15 (Persistent Named Volume Block Storage)
- **WSGI Application Server:** Gunicorn (Production-grade worker process management)
- **Telemetry Hardware Daemon:** Standalone Python Daemon backed by `psutil`
- **Target Environments:** Linux (Ubuntu/Debian Enterprise Server), WSL2 Staging Core, VMware Virtualized Clusters
---




## System Network Topology
```bash
┌──────────────────────────────┐
│       Client Browser         │
└──────────────┬───────────────┘
               │ HTTP (Port 80 Access Gate)
               ▼
┌──────────────────────────────┐
│        Nginx Container       │  ← Microservices Edge Gateway & Asset Cache
│  - Static Asset Delivery     │
│  - Port 80 Proxy Routing     │
└──────────────┬───────────────┘
               │ Internal Docker Bridge Forwarding
               ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        DOCKER COMPOSE NETWORK MATRIX                   │
│                                                                        │
│   ┌──────────────────────────┐            ┌────────────────────────┐   │
│   │ Flask Dashboard Container│            │  PostgreSQL Container  │   │
│   │       (dashboard)        ├───────────►│          (db)          │   │
│   │ - Gunicorn Worker Stack  │  Internal  │ - Port 5432            │   │
│   │ - Telemetry REST API     │  Bridge    │ - Named Database Volume│   │
│   │ - RBAC Access Controller │  Network   │ - Operational Ledger   │   │
│   └──────────────────────────┘            └────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
               ▲
               │ Secure Stream Connection (HTTP/POST Metrics Push)
               │
┌────────────────────────────────────────────────────────────────────────┐
│                     DISTRIBUTED HARDWARE AGENT LAYER                   │
│  - Standalone OS Resource Extraction Pipeline (`agent.py`)             │
│  - Distributed Multi-City Node Tracking (Ludwigshafen, Mannheim, etc.) │
└────────────────────────────────────────────────────────────────────────┘
```
---
## Project Structure
```bash
smart-monitor-platform/
│   .gitignore
│   docker-compose.yml     # Microservices cluster blueprint (Nginx + Flask Server + Postgres DB)
│   nginx.conf             # Unified reverse-proxy configurations and edge routing rules
│   README.md              # Main high-level system documentation root
│
├───agent                  # Distributed telemetry collector daemon
│   │   agent.py           # Cross-platform sensor extraction script
│   │   README.md          # Agent environment deployment manual
│   │   test_agent.py      # Automated computational validation suite
│   │
│   ├───.pytest_cache      # Test automation cache registries
│   │   │   .gitignore
│   │   │   CACHEDIR.TAG
│   │   │   README.md
│   │   │
│   │   └───v
│   │       └───cache
│   │               lastfailed
│   │               nodeids
│   │
│   └───__pycache__
│           agent.cpython-310.pyc
│           test_agent.cpython-310-pytest-9.0.3.pyc
│
├───core                   # Core logical framework & systemic utilities
│       alerts.py          # Automated threshold alerts and Telegram piping
│       analyzer.py        # Micro-process structural analysis mapping
│       database.py        # Relational storage pooling interface
│       logger.py          # System logging, diagnostics, and metrics tracing
│       mailer.py          # SMTP engine transmitting transactional alert emails
│       metrics.py         # OS hardware sensor metrics parsing layer
│       processes.py       # Detailed active task manager analytics tracking
│       security.py        # Cryptographic password hashing (bcrypt) and token validations
│       __init__.py
│
├───dashboard              # Visual management application engine
│   │   app.py             # Main Flask routing server entrypoint
│   │   Dockerfile         # Production Gunicorn worker container builder
│   │   README.md          # Visual components and API specs documentation
│   │   requirements.txt   # Pinned application Python dependencies
│   │   test_app.py        # Integration test maps evaluating authorization walls
│   │   __init__.py
│   │
│   ├───static             # Application styles, themes, and native assets
│   └───templates          # Client-side UI markup frameworks
│           index.html     # Main asynchronous performance monitoring panel
│           login.html     # Overhauled state-aware corporate check-in portal
│
└───screenshots            # Infrastructure deployment verification captures
        dashboard-home_1.png
        dashboard-home_2.png
        nginx-status.png
```
---

## Installation & Automated Deployment (Docker Way)
Spin up the entire interconnected ecosystem (Reverse Proxy, API Gateway, and Relational Database) with one single orchestration command:

1. Clone repository
``` bash
git clone git@github.com:sewar1/smart-monitor-platform.git
cd smart-monitor-platform
```
2. Launch Infrastructure with One Command
``` bash
docker-compose up --build
```
This handles automated database pool synchronization, internal bridge network creation, Python image isolation staging, and production-grade reverse-proxy reverse caching mapping

3. Access the Web Dashboard Portal:
Open your preferred modern browser and navigate to: http://localhost (Port 80 Edge Gate)


## Proof of Deployment Traffic Flow
```bash
Distributed Agent ──► HTTP POST ──► Nginx Proxy (Port 80) ──► Gunicorn WSGI ──► Flask App ──► PostgreSQL 15 Volume
```

##  Engineering Roadmap Achievements & Milestones

- [x] **Phase 1: Multi-Container Orchestration Core**
  - Segmented platform workloads into isolated microservice networks using Docker Compose.
  
- [x] **Phase 2: Visual Telemetry Web Engine**
  - Built multi-tab asynchronous dashboard UI mapping Chart.js telemetry waveforms cleanly

- [x] **Phase 3: Secure Operator Access Control Ring**
  - Overhauled login templates with professional responsive styles, flash alert banners, and stateless session verification driven by cryptographically signed JWT (JSON Web Tokens).

- [ ] **Phase 4: Automated Disaster Recovery Subsystem**
  - Build an automated backup utility engine for PostgreSQL transaction logs and configuration data layers.
  - Implement cron-driven scheduled snapshots to preserve historical metric states.

- [ ] **Phase 5: Multi-City Distributed Node Scalability**

  - Expand telemetry parsers to consume separate host streams across individual targeted nodes representing geographical deployments (Ludwigshafen, Mannheim, Heidelberg, Stuttgart).

- [ ] **Phase 6: Automated Testing Baseline**

  - Enhance test_app.py and test_agent.py suites to shield data ingest loops against code regression.


- [ ] **Phase 7: PostgreSQL Core Analytics Pipeline**
  - Build advanced analytical backend queries inside PostgreSQL to process and analyze long-term performance trends and historical server logs.

- [ ] **Phase 8: Continuous Integration / Continuous Deployment (CI/CD)**
  - Construct a robust CI/CD workflow pipeline via **GitHub Actions** to automate codebase auditing, test suite execution, and live container deployment.
---

## Summary

This project demonstrates a complete DevOps lifecycle from development to containerized orchestration and bare-metal production deployment on an enterprise virtualized Linux server.
