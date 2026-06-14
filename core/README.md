# Operational Core & Deep Infrastructure Subsystems
The `core` directory serves as the decoupled, underlying business logic backbone of the whole platform. It maps data transformations, handles alerts, and controls relational data operations.

## Functional Structural Subsystems
- **PostgreSQL Abstraction Mapping (`database.py`):** Establishes database pool routines, manages structural schema mappings, and coordinates transactions safely.
- **Enterprise Notification Alerters (`alerts.py`, `mailer.py`):** Evaluates incoming telemetry signals against thresholds; pushes warning messages out to dedicated administrative **Telegram Bots** and transactional **SMTP email servers**.
- **Process Profiler & Analytical Tools (`processes.py`, `analyzer.py`):** Inspects active runtime PIDs, extracts high-footprint anomalies, and pipes metrics to the ledger tracking nodes.
- **Cryptographic Security Ring (`security.py`):** Powers hashing layers via `bcrypt` to protect stored credentials, handles token creation seeds, and manages signing validations.

## Structural File Blueprint
- **`database.py`**: Connectors managing pool threads directly talking to PostgreSQL.
- **`security.py`**: Security controller wrapping salting mechanisms and stateless JWT token signing keys.
- **`alerts.py` & `mailer.py`**: Automated alerting delivery vectors processing warning states.
- **`metrics.py` & `processes.py`**: Translators turning low-level kernel sensor logs into tabular structures.
