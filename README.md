# Smart Monitor Platform

A production-grade, distributed real-time infrastructure monitoring platform and reactive mitigation engine engineered for high-availability cloud environments. The platform features cross-platform host telemetry extraction, containerized orchestration with host-kernel process injection, stateless cryptographic authentication, and automated anti-freeze guard resilience.

---

## Architectural Overview

The platform features a decoupled microservices-ready architecture managed entirely via **Docker Compose**. Edge traffic is intercepted by an **Nginx Reverse Proxy & Edge Gateway**, which serves static runtime visual assets while securely routing high-frequency metrics streams and WebSockets protocols directly to an enterprise-grade **Spring Boot REST API Engine**. 

Persistence is driven by an enterprise **PostgreSQL 15** data warehouse utilizing high-performance connection pooling (HikariCP), composite time-series indexing, and automated data retention workers. Distributed multi-city telemetry agents hook directly into host operating systems, bypassing container isolation parameters (`pid: "host"`, `privileged: true`) to profile and mitigate host-level runtime freeze vectors.

---

## Tech Stack

- **Containerization & Orchestration:** Docker, Docker Compose (Isolated Bridge Topology, Shared Host PID Context)
- **Edge Routing & API Gateway:** Nginx (Static Asset Caching, Cross-Protocol Reverse Proxy, Port 80 Access Gate)
- **Backend Core & Analytics Framework:** Java 21, Spring Boot 3.x, Spring MVC, Asynchronous Task Executors
- **Database Architecture:** PostgreSQL 15, Spring Data JPA / Hibernate (HikariCP Connection Pooling, Named Persistent Volumes)
- **Security & IAM Infrastructure:** Stateless JWT Tokens (HS256 Signature via `jjwt`), BCrypt Password Encoder, Immutability Guards
- **Application Server:** Embedded Production-grade Apache Tomcat Container
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
│   │  Spring Boot Dashboard   │            │  PostgreSQL 15 Cluster │   │
│   │       Container          ├───────────►│          (db)          │   │
│   │ - Embedded Tomcat Stack  │  HikariCP  │ - Min/Max Conn Pool    │   │
│   │ - Anti-Freeze Analyser   │  Thread    │ - BIGSERIAL Ledgers    │   │
│   │ - Scheduled Purge Task   │  Sockets   │ - Composite Timeline IX│   │
│   └──────────────────────────┘            └────────────────────────┘   │
└──────────────────────▲─────────────────────────────────────────────────┘
                       │
                       │ Concurrent Secure Keep-Alive Telemetry Payload Push
                       │
┌──────────────────────┴─────────────────────────────────────────────────┐
│                    DISTRIBUTED CROSS-PLATFORM AGENTS                   │
│                                                                        │
│  [Docker Target Node]    [Bare-Metal Windows Node]   [VMware Ubuntu]   │
│    (Mannheim Container)      (Ludwigshafen NSSM)      (Heidelberg Server│
│   - privileged: true         - Win32 API Wrapper       - systemd Daemon │
│   - pid: "host" mapping      - LOCATION=.env tracking  - Fail-Over Check│
└────────────────────────────────────────────────────────────────────────┘
```
---
## Project Structure
```bash
smart-monitor-platform/
│   .env                        # Global cluster database environment vectors
│   .gitignore                  # Git audit exclusion configuration
│   docker-compose.yml          # Container topology coordinator (PID shared, Ingestion-bound)
│   nginx.conf                  # Edge reverse-proxy configuration & socket upgrade matrices
│   README.md                   # Main high-level system documentation root (This File)
│
├───.vscode                     # Local editor integration context
├───agent                       # Autonomous distributed telemetry collector daemon
│   │   agent.py                # Cross-platform sensor poll & JSONB process tree compiler
│   │   Dockerfile              # Lightweight minimal layer agent cache builder
│   │   README.md               # Local agent deployment runbook
│   │   requirements.txt        # Core environment libraries (psutil, requests)
│   │   test_agent.py           # Unified nomenclature unit validation suite
│   └─── agent.env.example      # Reference guide for distributed server setups
│
└───dashboard                   # Central visual monitoring hub (Spring Boot)
    │   pom.xml                 # Maven project configuration & dependency tree
    │   Dockerfile              # Multi-stage production JRE/JDK Docker builder
    │   README.md               # Local Java visual layer deployment instructions
    │
    └───src
        ├───main
        │   ├───java/com/smartmonitor/platform
        │   │   ├───config      # Spring Security, CORS, and HikariCP database pool configurations
        │   │   ├───controller  # REST API Endpoints & Auth Gateways
        │   │   ├───model       # JPA Entities (Metrics, Nodes, Users)
        │   │   ├───repository  # Spring Data JPA Repository interfaces
        │   │   ├───security    # JWT filter chain, token provider, and BCrypt mechanisms
        │   │   ├───service     # Core business logic (Analyzer, Alerts, Mailer, Scheduler)
        │   │   └───PlatformApplication.java # Spring Boot bootstrapper
        │   │
        │   └───resources
        │       ├───static      # Asynchronous telemetry themes & dashboard frontend assets
        │       ├───templates   # Thymeleaf template engine UI panels (index, login)
        │       └───application.yml # Centralized Spring Boot profiles & configurations
        │
        └───test/java/com/smartmonitor/platform
                └───PlatformApplicationTests.java # Context loading & security integration tests
```
---

## Installation & Automated Deployment


Spin up the entire interconnected ecosystem (Reverse Proxy, Spring Boot Application, and Relational Database Pools) with a single orchestration layer build command:


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

- [x] Sprint 1: Distributed Telemetry Ingestion Core & Multi-Node Tracking (Java Migration)

  - Spring Boot Migration: Fully refactored backend core from Python/Flask to Java 21 & Spring Boot 3.x, ensuring enterprise-grade scalability and type safety.

  - Database Decentralization Matrix: Migrated persistence initialization to native container scripts (init.sql) using BIGSERIAL keys, JSONB process map spaces, and composite indexes for high-speed dashboard rendering.

  - Enterprise Connection Pooling: Integrated HikariCP natively within Spring Data JPA to prevent database socket starvation across concurrent distributed agents.

  - Cross-Platform Host Injection: Fabricated native multi-node deployment paths; distributed and stabilized agent daemons across bare-metal Windows Server hosts (via NSSM), virtualized VMware Ubuntu instances (via systemd), and sandboxed Docker container isolations.

  - Dynamic Environment Externalization: Standardized runtime configuration mapping through Spring's application.yml and global .env files.

  - Automated Anti-Freeze Subsystem (OOM Killer): Engineered a priority-sorting resource optimization service in Spring Boot. When system resource limits cross critical safety boundaries (95.0%), the guard programmatically triggers mitigation workflows, terminating the heaviest non-critical offender.

  - Scheduled Data Retention Worker: Replaced ad-hoc daemon threads with Spring's @Scheduled annotation to systematically purge historical metrics older than 24 hours every 12 hours.

  - Multi-Node State UI Switching: Overhauled JavaScript loops to track active nodes, prevent       canvas memory leaks via clean Chart.js destruction, and dynamically pass node-scoped queries       (/api/metrics?nodeId=) to Spring RestControllers.

  - Live Node Heartbeat Tracking: Established a 60-second threshold evaluation system. Missing agent   transmissions automatically trigger state shifting, rendering red warning badges on the UI.

  - Test-Driven Nomenclature Safeguard: Upgraded test suites to validate payload structures against   code regressions, shielding data ingestion API endpoints.

- [ ] Sprint 2: Granular Role-Based Access Control (RBAC) Expansion & Security Hardening

  - Implement dynamic user configuration panels inside the dashboard restricted exclusively to       the system root administration account.

  - Secure API vectors with adaptive rate-limiting middleware (using Bucket4j or Spring Cloud         Gateway) to shield security rings.

  - Enforce automated user activity logging ledgers to preserve compliance auditing records.

- [ ] Sprint 3: Distributed Microservices Architecture Decomposition

  - Decouple the monolithic receiver route out of the main dashboard Spring Boot container.

  - Establish a dedicated, high-speed Java-based ingestion service engineered exclusively for         write-heavy multi-agent operations.

  - Isolate the client user interface into a localized dashboard service processing read-heavy       analytical dashboard data streams.
- [ ] Sprint 4: CI/CD Pipeline Automation & Cloud Staging

  - Build automated workflows via GitHub Actions to enforce continuous checking, test execution, and isolated container registry uploads.

## Summary

This project demonstrates a complete DevOps lifecycle from development to containerized orchestration and bare-metal production deployment on an enterprise virtualized Linux server.
