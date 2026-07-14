package com.sewarl.smartmonitor.repository;

import com.sewarl.smartmonitor.entity.Metric;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.transaction.annotation.Transactional;
import java.time.OffsetDateTime;
import java.util.List;

/**
 * High-performance JPA Data Access Layer for remote node metrics.
 * Auto-registered by Spring Data JPA.
 */
public interface MetricRepository extends JpaRepository<Metric, Long> {

    @Query(value = "SELECT DISTINCT ON (node_id) * FROM metrics ORDER BY node_id, id DESC", nativeQuery = true)
    List<Metric> findLatestClusterState();

    List<Metric> findFirstByNodeIdOrderByTimestampDesc(String nodeId);

    @Transactional
    @Modifying
    @Query("DELETE FROM Metric m WHERE m.timestamp < :cutoffTime")
    int purgeMetricsOlderThan(@Param("cutoffTime") OffsetDateTime cutoffTime);
}