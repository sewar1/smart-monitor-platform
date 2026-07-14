package com.sewarl.smartmonitor.controller;

import com.sewarl.smartmonitor.entity.Metric;
import com.sewarl.smartmonitor.service.MetricService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

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
     * POST /api/metrics
     */
    @PostMapping
    public ResponseEntity<Metric> receiveMetrics(@RequestBody Metric metric) {
        Metric saved = metricService.saveMetric(metric);
        return new ResponseEntity<>(saved, HttpStatus.CREATED);
    }

    /**
     * Endpoint for Dashboard to fetch the latest state of all active nodes.
     * GET /api/metrics/latest
     */
    @SuppressWarnings("null")
    @GetMapping("/latest")
    public ResponseEntity<List<Metric>> getLatestClusterState() {
        List<Metric> state = metricService.getLatestClusterState();
        return ResponseEntity.ok(state);
    }

    /**
     * Endpoint for Dashboard to view detailed history of a single node.
     * GET /api/metrics/node/{nodeId}
     */
    @SuppressWarnings("null")
    @GetMapping("/node/{nodeId}")
    public ResponseEntity<List<Metric>> getNodeHistory(@PathVariable String nodeId) {
        List<Metric> history = metricService.getNodeHistory(nodeId);
        return ResponseEntity.ok(history);
    }
}