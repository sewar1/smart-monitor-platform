package com.sewarl.smartmonitor.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.time.OffsetDateTime;

/**
 * Node Hardware Telemetry Metrics Entity.
 * Captures core performance statistics and JSONB execution maps from remote agents.
 */
@Entity
@Table(name = "metrics")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Metric {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "node_id", nullable = false)
    private String nodeId;

    @Column(nullable = false)
    private String location;

    @Column(name = "os_type", nullable = false)
    private String osType = "Linux/Docker";

    @Column(name = "cpu_usage", nullable = false)
    private Double cpuUsage;

    @Column(name = "ram_usage", nullable = false)
    private Double ramUsage;

    @Column(name = "disk_usage", nullable = false)
    private Double diskUsage;

    // Persist as a JSON / JSONB column natively in PostgreSQL
    @Column(name = "top_processes", columnDefinition = "jsonb")
    private String topProcesses = "[]";

    @Column(nullable = false)
    private OffsetDateTime timestamp = OffsetDateTime.now();
}