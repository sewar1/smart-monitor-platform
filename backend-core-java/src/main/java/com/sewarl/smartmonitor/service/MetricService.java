package com.sewarl.smartmonitor.service;

import com.sewarl.smartmonitor.entity.Metric;
import com.sewarl.smartmonitor.repository.MetricRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.time.OffsetDateTime;
import java.util.List;

/**
 * Core business logic for processing and purging system telemetry metrics.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class MetricService {

    private final MetricRepository metricRepository;

    /**
     * Saves inbound telemetry metrics from an edge agent.
     */
    public Metric saveMetric(Metric metric) {
        if (metric.getTimestamp() == null) {
            metric.setTimestamp(OffsetDateTime.now());
        }
        log.info("Persisting fresh metrics for node: {}", metric.getNodeId());
        return metricRepository.save(metric);
    }

    /**
     * Fetches the latest distinct state for all nodes in the cluster.
     */
    public List<Metric> getLatestClusterState() {
        return metricRepository.findLatestClusterState();
    }

    /**
     * Fetches full history for a specific node.
     */
    public List<Metric> getNodeHistory(String nodeId) {
        return metricRepository.findFirstByNodeIdOrderByTimestampDesc(nodeId);
    }

    /**
     * Ticket 6: Retention Policy.
     * Automated job running every 24 hours to purge records older than 30 days.
     * "0 0 0 * * ?" translates to midnight every day.
     */
    @Scheduled(cron = "0 0 0 * * ?")
    public void purgeHistoricalMetrics() {
        OffsetDateTime cutoff = OffsetDateTime.now().minusDays(30);
        log.info("Triggering data retention policy cycle. Cutoff threshold: {}", cutoff);
        
        int deletedRows = metricRepository.purgeMetricsOlderThan(cutoff);
        
        log.info("Retention cycle complete. Successfully purged {} stale metric rows.", deletedRows);
    }
}