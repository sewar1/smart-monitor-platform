package com.sewarl.smartmonitor.repository;

import com.sewarl.smartmonitor.entity.Metric;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.stereotype.Repository;

import java.time.OffsetDateTime;
import java.util.List;

/**
 * High-performance JPA Data Access Layer for remote node metrics.
 * Integrated with Hibernate 6 JSONB mapping capabilities and transactional boundaries.
 */
@Repository
public interface MetricRepository extends JpaRepository<Metric, Long> {

    /**
     * Extracts the single most recent telemetry payload for every registered unique node.
     * Uses PostgreSQL proprietary optimization for high-frequency time-series datasets.
     */
    @Query(value = "SELECT DISTINCT ON (node_id) * FROM metrics ORDER BY node_id, id DESC", nativeQuery = true)
    List<Metric> findLatestClusterState();

    /**
     * Fetches historical logs for a targeted node ordered chronologically to assist front-end visualization timelines.
     */
    @Query("SELECT m FROM Metric m WHERE m.nodeId = :nodeId ORDER BY m.timestamp DESC")
    List<Metric> getNodeHistory(@Param("nodeId") String nodeId);

/**
     * Custom repository lookup sequence utilized by the system health check layer.
     * Retreives the latest 3 metrics for reliable variance analysis.
     */
    List<Metric> findTop3ByNodeIdOrderByTimestampDesc(String nodeId);

    /**
     * Retention policy ledger execution tool. Purges records older than a dynamic moving target date.
     */
    @Transactional
    @Modifying
    @Query("DELETE FROM Metric m WHERE m.timestamp < :cutoff")
    int purgeMetricsOlderThan(@Param("cutoff") OffsetDateTime cutoff);
}