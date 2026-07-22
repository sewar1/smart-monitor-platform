# Smart Monitor Platform

Polyglot Distributed Infrastructure Telemetry & Autonomous Self-Healing Management System

Engineered for high-availability cloud environments to meet rigorous German enterprise software architecture standards (Production-Grade).

---
# Executive Overview
Smart Monitor Platform is an enterprise-grade, distributed infrastructure monitoring and automated incident-mitigation ecosystem. Built with a decoupled Polyglot Architecture, it unifies low-level telemetry collection, centralized reactive Java backend processing, advanced OS process-level self-healing, multi-channel alerting pipelines, and a high-performance React dashboard.

---

## Key Architectural Features & Subsystems
1. **Autonomous Anti-Freeze & OOM Mitigation (SystemAnalyzerService)**
   - OS-Level Process Intervention: Continuously monitors host resource capacity. If CPU or RAM breaches 95.0%, the backend dynamically queries the operating system process table (ps on Unix, tasklist on Windows).
   - Safe Termination Guards: Identifies rogue resource hogs and executes safe process termination (destroyForcibly()) while strictly respecting a Critical Process Whitelist (systemd, postgres, docker, java, nginx, etc.) to prevent host lockups or service crashes.
   - Variance Freeze Detection: Evaluates historical metric windows using floating-point precision (EPSILON) to catch deadlocks where system metrics freeze completely across consecutive cycles.
2. **Multi-Channel Alerting & Notification Pipeline (AlertService)**
   - Centralized Threshold Evaluation: Compares real-time telemetry against dynamic configuration limits (application.yaml).
   - Multi-Channel Dispatch: Automatically logs incidents locally and broadcasts critical warnings externally via SMTP HTML Emails (JavaMailSender) and Telegram Bot REST APIs (RestTemplate).
3. **Enterprise Security & Identity Management (UserService & TwoFactorAuthService)**
   - Stateless Authentication: Secure JWT-based architecture (jjwt) with Brute-Force protection filters.
   - CSPRNG 2FA Subsystem: Cryptographically secure 6-digit verification token generation using Java's SecureRandom, paired with responsive HTML email templates and local container console fallbacks.
4. **Heartbeat Tracking & Health Scoring (MetricService)**
   - Cluster Connectivity: Thread-safe in-memory caching (ConcurrentHashMap) tracking absolute heartbeat timestamps with a 60-second offline threshold margin.
   - Weighted Health Index: Calculates system health scores via a multi-criteria weighted matrix ($\text{CPU 40\%}, \text{RAM 40\%}, \text{Disk 20\%}$) with automated 12-hour database retention cleanup schedulers.

---

🎥 System Live Demonstration
A comprehensive end-to-end demonstration showcasing authentication, real-time node switching, multi-language support (English/German), and dashboard telemetry:

<p align="center">
  <a href="https://github.com/sewarl/smart-monitor-platform/blob/main/Demo/Demo.mp4" target="_blank">
    🎬 <b>Click here to watch the System Live Demonstration Video</b>
  </a>
</p>



---

## Project Architecture
The platform is structured as a Monorepo with decoupled services:

- **backend/:** Java Spring Boot API engine handling telemetry persistence, authentication, and analysis.

- **frontend/:** React/TypeScript dashboard providing real-time visualization.

---
## Tech Stack

- **Infrastructure & Security** Docker, Docker Compose, Nginx (Reverse Proxy & Edge Gateway), Stateless JWT (HS256), BCrypt, CSPRNG 2FA
- **Edge Agent** Standalone Python Daemon backed by cross-platform psutil kernel space extraction
- **Backend Core & Analytics** Java 21, Spring Boot 3.x, Spring MVC, Spring Data JPA, Hibernate, Maven
- **Database Architecture:** PostgreSQL 15, HikariCP Connection Pooling, Composite Time-Series Indexing
- **Frontend UI** React 19, TypeScript, Tailwind CSS, Bootstrap Icons, Vite


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
│    ┌──────────────────────────┐            ┌────────────────────────┐  │
│    │  Spring Boot Dashboard   │            │ PostgreSQL 15 Cluster  │  │
│    │      Container           ├───────────►│          (db)          │  │
│    │ - Embedded Tomcat Stack  │  HikariCP  │ - Min/Max Conn Pool    │  │
│    │ - Anti-Freeze Analyser   │  Thread    │ - BIGSERIAL Ledgers    │  │
│    │ - Scheduled Purge Task   │  Sockets   │ - Composite Timeline IX│  │
│    └──────────────────────────┘            └────────────────────────┘  │
└──────────────────────▲─────────────────────────────────────────────────┘
                       │
                       │ Concurrent Secure Keep-Alive Telemetry Payload Push
                       │
┌──────────────────────┴─────────────────────────────────────────────────┘
│                        DISTRIBUTED CROSS-PLATFORM AGENTS               │
│                                                                        │
│   [Docker Target Node]     [Bare-Metal Windows Node]   [VMware Ubuntu] │
│    (Mannheim Container)      (Ludwigshafen NSSM)       (Heidelberg Server)
│   - privileged: true         - Win32 API Wrapper       - systemd Daemon │
│   - pid: "host" mapping      - LOCATION=.env tracking  - Fail-Over Check│
└────────────────────────────────────────────────────────────────────────┘
```
---
## Project Structure
```bash
smart-monitor-platform/
├── agent/                 # Python Telemetry Agent (Collects CPU, RAM, Disk & heartbeats)
├── backend/               # Java Spring Boot Central Gateway & Enterprise Security Engine
│   └── src/main/java/com/sewarl/smartmonitor/
│       ├── config/        # Security, JWT filters, and Database initializers
│       ├── controller/    # REST Endpoints (Metrics, Auth, Alerts management)
│       ├── entity/        # Relational PostgreSQL Entities (User, Metric, MetricAlert)
│       ├── repository/    # Spring Data JPA Data Access Layer
│       ├── security/      # Brute-force protection & threat mitigation guards
│       └── service/       # Core Business Logic (Anti-freeze, OOM mitigation, 2FA, Alerting)
├── frontend/              # React 19 + TypeScript + Tailwind CSS Enterprise Dashboard
│   └── src/pages/         # Modular architecture for Login (with i18n) & Real-time Dashboard
├── docker-compose.yml     # Multi-container orchestration (PostgreSQL, Backend, Frontend, Agent)
├── nginx.conf             # Reverse Proxy & Load Balancer configuration
└── README.md              # Project Documentation & Live Demo
```
---

## Installation & Automated Deployment


Spin up the entire interconnected ecosystem (Reverse Proxy, Spring Boot Application, and Relational Database Pools) with a single orchestration layer build command:


1. Clone repository
``` bash
git clone git@github.com:sewar1/smart-monitor-platform.git
cd smart-monitor-platform
```
2. Backend (Java)
Navigate to the backend directory and start the service:
``` bash
cd backend
mvn spring-boot:run
```
3. Frontend (React)
Navigate to the frontend directory, install dependencies, and start the development server:
``` bash
cd frontend
npm install
npm run dev
```
4. Initialize Configurations
To run the full stack (Database, Backend, and Frontend) in production-like containers:
``` bash
docker-compose up --build
```

5. Access Web Interface:
Open your browser and navigate to: http://localhost (Port 80 Gate).
