#!/bin/bash
# ==============================================================================
# Smart Monitor Platform - Incident Diagnostics & Logs Collector
# Generates an SRE-style diagnostics bundle for rapid troubleshooting.
# ==============================================================================

DIAG_DIR="./diagnostics"

echo "========================================================"
echo "📦 Collecting Smart Monitor Platform Diagnostics..."
echo "========================================================"

# 1. Create clean diagnostics directory
rm -rf "$DIAG_DIR"
mkdir -p "$DIAG_DIR"

# 2. Collect Docker Compose Logs
echo "⏳ Exporting Docker Compose container logs..."
docker compose logs --no-color > "$DIAG_DIR/docker-compose.log" 2>/dev/null || echo "⚠️ Docker compose logs export skipped."

# 3. Collect Systemd Logs for Docker daemon (if running on Linux)
echo "⏳ Checking system daemon logs..."
if command -v journalctl &> /dev/null; then
    journalctl -u docker --since "1 hour ago" > "$DIAG_DIR/docker-daemon.log" 2>/dev/null || true
else
    echo "ℹ️ journalctl not available (non-systemd environment)."
fi

# 4. Collect Local Application Logs if they exist
if [ -d "logs" ]; then
    echo "⏳ Aggregating local application logs..."
    cat logs/*.log > "$DIAG_DIR/app-logs.log" 2>/dev/null || true
fi

# 5. Extract and summarize errors/exceptions into a single summary file
echo "🔍 Filtering and summarizing critical errors..."
grep -riE "error|exception|fatal|failed" "$DIAG_DIR/"/*.log > "$DIAG_DIR/errors-summary.log" 2>/dev/null || true

echo "========================================================"
echo "✅ Diagnostics bundle generated successfully!"
echo "📁 All logs and summaries are saved in: $DIAG_DIR/"
echo "========================================================"