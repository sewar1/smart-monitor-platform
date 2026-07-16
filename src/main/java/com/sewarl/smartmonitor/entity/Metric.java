package com.sewarl.smartmonitor.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;
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
    // Matches BIGSERIAL in database schema
    private Long id;

    @Column(name = "node_id", nullable = false, length = 100)
    private String nodeId;

    @Column(nullable = false, length = 100)
    private String location;

    @Column(name = "os_type", nullable = false, length = 50)
    private String osType = "Linux/Docker";

    // Matching NUMERIC(5, 2) decimal limits for continuous usage calculations
    @Column(name = "cpu_usage", nullable = false, precision = 5, scale = 2)
    private Double cpuUsage;

    @Column(name = "ram_usage", nullable = false, precision = 5, scale = 2)
    private Double ramUsage;

    @Column(name = "disk_usage", nullable = false, precision = 5, scale = 2)
    private Double diskUsage;

    // Calculated aggregated node health score, matching NUMERIC(5, 2) for percentage precision
    @Column(name = "health_score", nullable = false, precision = 5, scale = 2)
    private Double healthScore = 100.0;

    // Classified categorical health status (e.g., Healthy, Warning, Critical) for quick querying and UI rendering
    @Column(name = "status", nullable = false, length = 50)
    private String status = "Healthy";

    // Enables native binary JSON (JSONB) parsing and binding directly in Hibernate
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "top_processes", nullable = false, columnDefinition = "jsonb")
    private String topProcesses = "[]";

    // Matches 'TIMESTAMP WITH TIME ZONE' to handle globally distributed geographical telemetry safely
    @Column(nullable = false, columnDefinition = "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP")
    private OffsetDateTime timestamp = OffsetDateTime.now();
}