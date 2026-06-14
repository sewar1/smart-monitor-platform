# Centralized Web Dashboard & RESTful API Gateway
This subsystem governs the user interface layer and JWT session verification rings.This module acts as the core controller for the User Interface layer, role-based visualization workflows, and access security validation gateways.
---

## Implemented Features & Sprint 3 Highlights
- **State-Aware Corporate Login:** A fully overhauled `login.html` styling layout featuring modern clean UI palettes, interactive form feedback, loading spinners, and failure warning banners.
- **Role-Based Access Control (RBAC Middleware):** Secure token parsing loops dividing application permissions between enterprise access rings (`Admin`, `DevSecOps`, `Operator`).
- **Stateless Token Rings:** User access validation handled purely via cryptographically signed **JWT (JSON Web Tokens)** tokens stored securely on the client-side.
- **Dynamic Single Page Interactivity:** Tab mechanics fixed and bound to Bootstrap 5 JavaScript events (`shown.bs.tab`), making the navigation between the main live monitor maps and the user directory seamless.

## File Architecture Analysis
- **`app.py`**: The central Flask application manager housing database orchestration interfaces and REST controller mappings.
- **`Dockerfile`**: Minimalist container blueprint deploying Gunicorn multi-worker WSGI layer.
- **`templates/login.html`**: The newly styled secure entry portal UI.
- **`templates/index.html`**: Main workspace template loading multi-series Chart.js waves and structural user tables.
- **`test_app.py`**: High-coverage integration tests evaluating API routing security, user tokens, and layout access barriers.

## Target API Specifications
- `POST /api/auth/login` -> Authenticates operator credentials, returning cryptographic token rings.
- `GET /api/metrics` -> Delivers high-frequency system telemetry vectors to the active frontend graph interfaces.
- `POST /api/users/create` -> *(Enforced Admin RBAC)* Instantly provisions new operators on the cloud database engine.
