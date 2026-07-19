package com.sewarl.smartmonitor.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;
import java.time.OffsetDateTime;
import java.math.BigDecimal; // to handle NUMERIC(5, 2) precision for CPU, RAM, Disk usage and health score

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
    private BigDecimal cpuUsage; //transfer from float to BigDecimal for precision and to match NUMERIC(5, 2) in PostgreSQL

    @Column(name = "ram_usage", nullable = false, precision = 5, scale = 2)
    private BigDecimal ramUsage; // transfer from float to BigDecimal for precision and to match NUMERIC(5, 2) in PostgreSQL

    @Column(name = "disk_usage", nullable = false, precision = 5, scale = 2)
    private BigDecimal diskUsage; // transfer from float to BigDecimal for precision and to match NUMERIC(5, 2) in PostgreSQL

    // Calculated aggregated node health score, matching NUMERIC(5, 2) for percentage precision
    @Column(name = "health_score", nullable = false, precision = 5, scale = 2)
    private BigDecimal healthScore = new BigDecimal("100.00"); // default to 100% health until metrics are ingested and calculated

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