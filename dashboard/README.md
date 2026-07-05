# Centralized Web Dashboard & RESTful API Gateway
This subsystem governs the user interface layer and JWT session verification rings. This module acts as the core controller for the User Interface layer, role-based visualization workflows, and access security validation gateways.
---

## Implemented Features & Sprint Highlights
- **State-Aware Corporate Login:** A fully overhauled `login.html` styling layout featuring modern clean UI palettes, interactive form feedback, loading spinners, and failure warning banners.
- **Role-Based Access Control (RBAC Middleware):** Secure token parsing loops dividing application permissions between enterprise access rings (`Admin`, `DevSecOps`, `Operator`).
- **Stateless Token Rings:** User access validation handled purely via cryptographically signed **JWT (JSON Web Tokens)** tokens stored securely on the client-side.
- **Dynamic Single Page Interactivity:** Tab mechanics fixed and bound to Bootstrap 5 JavaScript events (`shown.bs.tab`), making the navigation between the main live monitor maps and the user directory seamless.
- **Multi-Node Telemetry Switching UI [Ticket 11]:** Dynamic JavaScript implementation in index.html allowing operators to switch live charts between multiple geographical nodes (e.g., Ludwigshafen Server, Heidelberg Container) without page reloads, integrating proper Chart.js canvas destruction to completely eliminate browser memory leaks
- **Autonomous Retention Thread Worker:** Houses a background daemon worker that runs systematically every 12 hours to prune time-series metrics older than 24 hours, ensuring optimal database index sizes.
- **Node Heartbeat Analytics:** Implements a 60-second differential threshold evaluation; if a remote node fails to stream metrics within this window, the API dynamically shifts its state to flag a warning badge on the interface.

## File Architecture Analysis
- **`app.py`**: The central Flask application manager housing database orchestration interfaces, token validation, background retention threads, and REST controller mappings
- **`Dockerfile`**: Minimalist container blueprint deploying Gunicorn multi-worker WSGI layer using high-performance **PYTHONPATH** environments.
- **`templates/login.html`**: The newly styled secure entry portal UI.
- **`templates/index.html`**: Main workspace template loading multi-series Chart.js waves, dynamic node switches, and active system anomaly ledgers
- **`test_app.py`**: High-coverage integration tests evaluating API routing security, user tokens, and layout access barriers


## API Endpoint & Specifications
### 1. POST /api/metrics/receiver [Ticket 2]
The centralized gateway path where distributed agents stream sub-second hardware telemetry payloads:
- Payload Format: Strict JSON dictionary passing node_id, location, os_type, cpu_usage, ram_usage, disk_usage, and top_processes (as a JSONB string block).


### 2. GET /api/metrics
Delivers high-frequency system telemetry vectors to the active frontend graph interfaces, filtered dynamically via query strings (?node_id=).

**Sample Ingestion Matrix Response:**
```bash

{
  "health": {
    "score": 88.50,
    "status": "Healthy"
  },
  "metrics": {
    "node_id": "Docker_Production_Container",
    "location": "Ludwigshafen",
    "os_type": "Linux",
    "cpu_usage": 12.40,
    "ram_usage": 45.20,
    "disk_usage": 33.10,
    "top_processes": [
      {"pid": 1204, "name": "gunicorn", "cpu": 1.2, "memory": 2.4}
    ]
  },
  "alerts": []
}
```

### 3. Target API Specifications
- POST /api/auth/login -> Authenticates operator credentials, returning cryptographic token rings.

- POST /api/users/create -> (Enforced Admin RBAC) Instantly provisions new operators on the cloud database engine.
