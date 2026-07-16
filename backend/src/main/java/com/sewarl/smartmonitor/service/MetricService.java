package com.sewarl.smartmonitor.service;

import com.sewarl.smartmonitor.entity.Metric;
import com.sewarl.smartmonitor.repository.MetricRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.OffsetDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Core business logic for processing, purging, anomaly detection, and heartbeat tracking of system telemetry.
 * Integrates the Automated Data Retention Scheduler and SystemAnalyzerService to optimize resource utilization
 * and execute reactive self-healing.
 */
@Service
public class MetricService {

    private static final Logger log = LoggerFactory.getLogger(MetricService.class);

    private final MetricRepository metricRepository;
    private final AlertService alertService; 
    private final SystemAnalyzerService systemAnalyzerService; // Injected for advanced system analytics and mitigation

    // Thread-safe in-memory cache tracking the exact absolute time of the last received heartbeat per Node.
    private final ConcurrentHashMap<String, OffsetDateTime> heartbeatTracker = new ConcurrentHashMap<>();

    // Dynamic configuration limit for heartbeats (60 seconds threshold matching the Python Agent cycle)
    private static final long OFFLINE_THRESHOLD_SECONDS = 60;

    /**
     * Standard Constructor injecting dependencies manually.
     * Prevents annotation processing errors and compilation failures.
     */
    public MetricService(MetricRepository metricRepository, AlertService alertService, SystemAnalyzerService systemAnalyzerService) {
        this.metricRepository = metricRepository;
        this.alertService = alertService;
        this.systemAnalyzerService = systemAnalyzerService;
    }

    /**
     * Saves inbound telemetry metrics from an edge agent, updates heartbeat maps, calculates system health, 
     * executes statistical anomaly checks, and triggers reactive self-healing when critical thresholds are breached.
     */
    public Metric saveMetric(Metric metric) {
        if (metric.getTimestamp() == null) {
            metric.setTimestamp(OffsetDateTime.now());
        }

        String nodeId = metric.getNodeId();
        log.info("Processing fresh incoming telemetry metrics for node: {}", nodeId);

        // 1. Heartbeat Tracking Core Mechanism: Register or update the last seen timestamp
        heartbeatTracker.put(nodeId, metric.getTimestamp());

        // 2. Advanced System Analysis: Compute the precise aggregated health score and status
        double healthScore = systemAnalyzerService.calculateWeightedHealthScore(
                metric.getCpuUsage(),
                metric.getRamUsage(),
                metric.getDiskUsage()
        );
        metric.setHealthScore(healthScore);
        metric.setStatus(systemAnalyzerService.classifyHealthStatus(healthScore));

        log.info("[METRIC INGESTED] Node: {}, Calculated Health Score: {}% ({})", 
                nodeId, healthScore, metric.getStatus());

        // 3. Anti-Freeze Anomaly Mitigation Guard Engine execution (Statistical analysis check)
        checkAndMitigateFreezes(metric);

        // 4. Active Self-Healing Execution: Run automated anti-freeze remediation to release resources if critical
        List<Map<String, Object>> incidents = systemAnalyzerService.executeAntiFreezeGuard(
                metric.getCpuUsage(),
                metric.getRamUsage(),
                nodeId,
                "Ludwigshafen"
        );

        if (!incidents.isEmpty()) {
            log.error("[MITIGATION TRIGGERED] Anti-Freeze guard intercepted and resolved a critical resource leak on node [{}]!", nodeId);
        }
        // 5. Run Centralized Infrastructure Threshold Evaluation (Ported from alerts.py)
        alertService.evaluateInfrastructureNode(metric);

        // 6. Persist metrics state directly into the relational store
        return metricRepository.save(metric);
    }

    /**
     * Pure Java implementation mirroring 'check_and_mitigate_freezes'.
     * Evaluates variance across past metrics to detect system freeze lockups and triggers active alerting.
     */
    private void checkAndMitigateFreezes(Metric currentMetric) {
        String nodeId = currentMetric.getNodeId();
        
        // Fetch historical windows to build structural pattern analysis using existing repository query
        // We retrieve the last 3 metrics for the node to perform variance checks
        List<Metric> recentHistory = metricRepository.findTop3ByNodeIdOrderByTimestampDesc(nodeId);
        
        // We require at least 3 distinct past cycles to execute statistical variance check safely
        if (recentHistory.size() < 3) {
            return; 
        }

        Metric m1 = recentHistory.get(0);
        Metric m2 = recentHistory.get(1);

        // Anti-Freeze Mathematical Logic with safe floating-point comparison
        boolean isCpuFrozen = Math.abs(currentMetric.getCpuUsage() - m1.getCpuUsage()) < 0.001 
                && Math.abs(m1.getCpuUsage() - m2.getCpuUsage()) < 0.001;
                
        boolean isRamFrozen = Math.abs(currentMetric.getRamUsage() - m1.getRamUsage()) < 0.001 
                && Math.abs(m1.getRamUsage() - m2.getRamUsage()) < 0.001;

        if (isCpuFrozen && isRamFrozen) {
            log.warn("CRITICAL ANOMALY: Anti-Freeze Guard triggered for Node ID: {}. System metrics have frozen completely!", nodeId);
            
            String alertMessage = String.format(
                "CRITICAL WARNING: Node [%s] appears to be FROZEN. CPU usage stuck at %.2f%% and RAM usage stuck at %.2f%% across the last 3 monitoring cycles consecutively.",
                nodeId, currentMetric.getCpuUsage(), currentMetric.getRamUsage()
            );

            // Active Alert Dispatch Pipeline via Email & Telegram Bot API
            alertService.sendCriticalAlert(nodeId, "SYSTEM_FREEZE", alertMessage);
        }
    }

    /**
     * Iterates over tracked network nodes and calculates active connectivity status against the heartbeat cache map.
     */
    public Map<String, String> getNodesConnectivityStatuses() {
        Map<String, String> statuses = new HashMap<>();
        OffsetDateTime standardLimit = OffsetDateTime.now().minusSeconds(OFFLINE_THRESHOLD_SECONDS);
        
        heartbeatTracker.forEach((nodeId, lastHeartbeat) -> {
            if (lastHeartbeat.isBefore(standardLimit)) {
                statuses.put(nodeId, "Offline");
            } else {
                statuses.put(nodeId, "Online");
            }
        });

        return statuses;
    }

    /**
     * Fetches the latest distinct state for all nodes in the cluster.
     */
    public List<Metric> getLatestClusterState() {
        return metricRepository.findLatestClusterState();
    }

    /**
     * Fetches full history for a specific node to map telemetry graphs.
     * Calls the dedicated historical query from MetricRepository.
     */
    public List<Metric> getNodeHistory(String nodeId) {
        return metricRepository.getNodeHistory(nodeId);
    }

    /**
     * Ticket 6: Data Retention Policy & Automated Cleanup.
     */
    @Scheduled(cron = "0 0 */12 * * *")
    @Transactional
    public void purgeHistoricalMetrics() {
        OffsetDateTime cutoff = OffsetDateTime.now().minusDays(7); 
        log.info("📊 Automated Data Retention Scheduler activated. Analyzing records older than: {}", cutoff);
        
        try {
            int deletedRows = metricRepository.purgeMetricsOlderThan(cutoff);
            log.info("✅ Database retention cleanup completed successfully. Purged [{}] stale telemetry rows.", deletedRows);
        } catch (Exception e) {
            log.error("❌ Failed to complete the database retention cleanup cycle: {}", e.getMessage());
        }
    }
}