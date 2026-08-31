#!/bin/bash

# ==============================================================================
# Smart Monitor Platform - Self-Health Check & Diagnostics Tool
# ==============================================================================

echo "========================================================"
echo "🔍 Starting Smart Monitor Platform Health Check..."
echo "========================================================"

# 1. Check Docker Containers Status & Health
echo -e "\n[1/3] Checking Docker Containers Health..."
if command -v docker &> /dev/null; then
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    # Inspect explicit health statuses if configured
    docker inspect --format='{{.Name}}: Health Status -> {{if .State.Health}}{{.State.Health.Status}}{{else}}N/A (No healthcheck){{end}}' $(docker ps -q) 2>/dev/null
else
    echo "⚠️ Docker command not found on host."
fi

# 2. Check Backend API Reachability via Nginx Proxy
echo -e "\n[2/3] Checking API Endpoints Reachability..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/metrics/status)
if [ "$HTTP_STATUS" -eq 200 ] || [ "$HTTP_STATUS" -eq 401 ] || [ "$HTTP_STATUS" -eq 403 ]; then
    echo "✅ Backend API via Nginx is reachable (HTTP Status: $HTTP_STATUS)"
else
    echo "❌ Backend API unreachable or returned unexpected status: $HTTP_STATUS"
fi

# 3. Check Backend Container Logs for Recent Errors/Exceptions
echo -e "\n[3/3] Scanning Backend Container Logs for Errors..."
if docker ps | grep -q "smart_monitor_backend"; then
    ERROR_COUNT=$(docker logs --tail=50 smart_monitor_backend 2>&1 | grep -iE "error|exception|fatal" | wc -l)
    if [ "$ERROR_COUNT" -gt 0 ]; then
        echo "⚠️ Found $ERROR_COUNT error/exception entries in recent backend logs:"
        docker logs --tail=50 smart_monitor_backend 2>&1 | grep -iE "error|exception|fatal" | tail -n 5
    else
        echo "✅ No major errors found in recent backend logs."
    fi
else
    echo "⚠️ Backend container 'smart_monitor_backend' is not running."
fi

echo -e "\n========================================================"
echo "🎯 Health Check Completed Successfully."
echo "========================================================"