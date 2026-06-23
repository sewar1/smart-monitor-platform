-- ====================================================================
-- SMART MONITOR PLATFORM - ENTERPRISE DATABASE INITIALIZATION LEDGER
-- ====================================================================

-- 1. جدول إدارة المستخدمين والصلاحيات (RBAC Setup - تمهيداً لـ Sprint 2)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'operator', -- operator, administrator
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. جدول مقاييس العقد الموزعة جغرافياً (Distributed Telemetry Metrics Table)
CREATE TABLE IF NOT EXISTS metrics (
    id BIGSERIAL PRIMARY KEY,
    node_id VARCHAR(100) NOT NULL,          -- معرف فريد للعقدة: e.g., 'ludwigshafen-win'
    location VARCHAR(100) NOT NULL,         -- الموقع الجغرافي: Ludwigshafen, Mannheim, Heidelberg
    os_type VARCHAR(50) NOT NULL,           -- نظام التشغيل المضيف: Windows, Linux
    cpu_usage NUMERIC(5, 2) NOT NULL,       -- نسبة استهلاك المعالج الكلية
    ram_usage NUMERIC(5, 2) NOT NULL,       -- نسبة استهلاك الذاكرة العشوائية
    disk_usage NUMERIC(5, 2) NOT NULL,      -- نسبة استهلاك القرص الصلب الرئيسي
    top_processes JSONB NOT NULL,           -- أعلى 5 عمليات استهلاكاً للموارد مخزنة بصيغة كائن بيكسل جيسون مدمج
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. جدول التنبيهات وإدارة الكوارث المركزية (Centralized System Alerts)
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    node_id VARCHAR(100) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,        -- e.g., 'CPU_CRITICAL', 'RAM_HIGH', 'OOM_GUARD_TRIGGER'
    message TEXT NOT NULL,
    resolved BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ====================================================================
-- INDEXING OPTIMIZATION (تجهيز قاعدة البيانات لتتحمل البيانات الضخمة من 3 سيرفرات بالتوازي)
-- ====================================================================
-- فهرس مركب سريع جداً لجلب أحدث المقاييس الخاصة بسيرفر معين فوراً وعرضها في الـ Front-end
CREATE INDEX IF NOT EXISTS idx_metrics_node_timestamp ON metrics (node_id, timestamp DESC);

-- فهرس لتسريع البحث عن التنبيهات غير المحلولة الخاصة بالعقد
CREATE INDEX IF NOT EXISTS idx_alerts_unresolved ON alerts (node_id) WHERE resolved = FALSE;