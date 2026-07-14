package com.sewarl.smartmonitor.controller;

import com.sewarl.smartmonitor.entity.MetricAlert;
import com.sewarl.smartmonitor.service.AlertService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST Controller for centralizing and retrieving decentralized system anomaly logs.
 */
@RestController
@RequestMapping("/api/alerts")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class AlertController {

    private final AlertService alertService;

    /**
     * Endpoint for Python Agent to fire an alert when thresholds are breached.
     * POST /api/alerts
     */
    @PostMapping
    public ResponseEntity<MetricAlert> triggerAlert(@RequestBody MetricAlert alert) {
        MetricAlert saved = alertService.recordAlert(alert);
        return new ResponseEntity<>(saved, HttpStatus.CREATED);
    }

    /**
     * Endpoint for Dashboard to fetch chronological list of all incidents.
     * GET /api/alerts
     */
    @SuppressWarnings("null")
    @GetMapping
    public ResponseEntity<List<MetricAlert>> getAllAlerts() {
        return ResponseEntity.ok(alertService.getAllAlerts());
    }
}