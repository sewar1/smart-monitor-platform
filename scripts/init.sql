-- ====================================================================
-- SMART MONITOR PLATFORM - ENTERPRISE DATABASE INITIALIZATION LEDGER
-- ====================================================================

-- 1. Identity & Access Management (RBAC Setup - Prepared for Sprint 2)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'operator', -- Enterprise access roles: 'operator' or 'administrator'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Distributed Telemetry Metrics Storage Core (Ticket 1 & Ticket 4 Multi-Node Matrix)
-- Captures geographical cluster streams and internal OS process maps uniformly.
CREATE TABLE IF NOT EXISTS metrics (
    id BIGSERIAL PRIMARY KEY,
    node_id VARCHAR(100) NOT NULL,          -- Unique node identifier (Unified Nomenclature: e.g., 'Windows_Host')
    location VARCHAR(100) NOT NULL,         -- Geographical zone anchoring (e.g., 'Ludwigshafen')
    os_type VARCHAR(50) NOT NULL,           -- Hosting kernel identifier injected by pipeline (e.g., 'Windows', 'Linux')
    cpu_usage NUMERIC(5, 2) NOT NULL,       -- Total CPU state utilization percentage vector
    ram_usage NUMERIC(5, 2) NOT NULL,       -- Total Virtual Memory footprint allocation percentage
    disk_usage NUMERIC(5, 2) NOT NULL,      -- Primary mount point partition saturation percentage
    top_processes JSONB NOT NULL,           -- [Ticket 4]: High-frequency process footprint maps cached as binary JSON
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP -- Unified UTC anchor for chronological timeline ordering
);

-- 3. Centralized Incident Management & Telemetry Alerting Ledger (Ticket 3 Extension)
-- Tracks system anomaly thresholds and records automated mitigation flags.
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    node_id VARCHAR(100) NOT NULL,          -- Targeted anomaly source node identifier
    alert_type VARCHAR(50) NOT NULL,        -- Kernel breach vector classification (e.g., 'CPU_CRITICAL', 'ANTI_FREEZE_MITIGATION')
    message TEXT NOT NULL,                  -- Structured analytical diagnostics payload string
    resolved BOOLEAN DEFAULT FALSE,         -- Toggled during administrative system incident lifecycle
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ====================================================================
-- ENTERPRISE INDEXING OPTIMIZATION & PERFORMANCE TUNING
-- ====================================================================

-- Optimized composite index tailored for high-frequency concurrent ingestions from multiple hosts.
-- Accelerates lookups for the front-end dashboard telemetry timelines and real-time state extraction.
CREATE INDEX IF NOT EXISTS idx_metrics_node_timestamp ON metrics (node_id, timestamp DESC);

-- Partial conditional index designed to scan unresolved system alerts efficiently without linear table fatigue.
CREATE INDEX IF NOT EXISTS idx_alerts_unresolved ON alerts (node_id) WHERE resolved = FALSE;