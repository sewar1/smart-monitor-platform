package com.sewarl.smartmonitor.service;

import com.sewarl.smartmonitor.entity.MetricAlert;
import com.sewarl.smartmonitor.repository.AlertRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.OffsetDateTime;
import java.util.List;

/**
 * Core business logic for managing node anomaly logs and incidents.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class AlertService {

    private final AlertRepository alertRepository;

    /**
     * Records a critical event or warning dispatched by an edge node.
     */
    public MetricAlert recordAlert(MetricAlert alert) {
        if (alert.getTimestamp() == null) {
            alert.setTimestamp(OffsetDateTime.now());
        }
        log.warn("🚨 [ALERT INBOUND] Node {} generated: {}", alert.getNodeId(), alert.getMessage());
        return alertRepository.save(alert);
    }

    /**
     * Retrieves all alerts ordered by recent occurrence.
     */
    public List<MetricAlert> getAllAlerts() {
        return alertRepository.findAllByOrderByTimestampDesc();
    }

    /**
     * Retrieves incidents filtered by a single node identifier.
     */
    public List<MetricAlert> getAlertsByNode(String nodeId) {
        return alertRepository.findByNodeIdOrderByTimestampDesc(nodeId);
    }
}