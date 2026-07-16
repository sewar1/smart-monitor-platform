package com.sewarl.smartmonitor.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.time.OffsetDateTime;

/**
 * Decentralized Node Anomaly Incident Log.
 * Records alerts and system failures reported by edge clients.
 */
@Entity
@Table(name = "alerts")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class MetricAlert { // Renamed slightly to avoid SQL reserved keyword 'Alert' in some databases

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "node_id", nullable = false)
    private String nodeId;

    @Column(nullable = false)
    private String location;

    @Column(name = "alert_type", nullable = false)
    private String alertType = "WARNING";

    @Column(nullable = false, columnDefinition = "TEXT")
    private String message;

    @Column(nullable = false)
    private OffsetDateTime timestamp = OffsetDateTime.now();
}