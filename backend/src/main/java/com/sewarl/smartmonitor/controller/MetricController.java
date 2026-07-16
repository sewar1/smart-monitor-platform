package com.sewarl.smartmonitor.controller;

import com.sewarl.smartmonitor.entity.Metric;
import com.sewarl.smartmonitor.service.MetricService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

// Required Java Utility imports to resolve the Map errors
import java.util.List;
import java.util.Map;

/**
 * REST Controller handling inbound node telemetry and dashboard telemetry queries.
 */
@RestController
@RequestMapping("/api/metrics")
@RequiredArgsConstructor
@CrossOrigin(origins = "*") // Allows your frontend dashboard to connect without CORS blocks
public class MetricController {

    private final MetricService metricService;

    /**
     * Endpoint for Python Agent to submit real-time hardware metrics.
     * Validates required payload structural properties before downstream ingestion.
     * POST /api/metrics
     */
    @PostMapping
    public ResponseEntity<?> receiveMetrics(@RequestBody Metric metric) {
        // Validation Guard: Ensure payload structural consistency
        if (metric == null || metric.getNodeId() == null || metric.getNodeId().trim().isEmpty()) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(Map.of("error", "Invalid telemetry data: nodeId is strictly required."));
        }
        
        Metric saved = metricService.saveMetric(metric);
        return new ResponseEntity<>(saved, HttpStatus.CREATED);
    }

    /**
     * Endpoint for Dashboard to fetch the latest state of all active nodes.
     * GET /api/metrics/latest
     */
    @GetMapping("/latest")
    public ResponseEntity<List<Metric>> getLatestClusterState() {
        List<Metric> state = metricService.getLatestClusterState();
        return ResponseEntity.ok(state);
    }

    /**
     * Endpoint for Dashboard to view detailed history of a single node.
     * GET /api/metrics/node/{nodeId}
     */
    @GetMapping("/node/{nodeId}")
    public ResponseEntity<List<Metric>> getNodeHistory(@PathVariable String nodeId) {
        List<Metric> history = metricService.getNodeHistory(nodeId);
        return ResponseEntity.ok(history);
    }

    /**
     * Endpoint for Dashboard to fetch real-time connectivity status (Online/Offline) of all nodes.
     * Derived dynamically via the in-memory Heartbeat Tracker map.
     * GET /api/metrics/status
     */
    @GetMapping("/status")
    public ResponseEntity<Map<String, String>> getClusterConnectivityStatus() {
        Map<String, String> statuses = metricService.getNodesConnectivityStatuses();
        return ResponseEntity.ok(statuses);
    }
}