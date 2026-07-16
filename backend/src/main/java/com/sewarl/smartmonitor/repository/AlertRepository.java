package com.sewarl.smartmonitor.repository;

import com.sewarl.smartmonitor.entity.MetricAlert;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

/**
 * JPA Data Access Layer for centralizing network alerts and incidents.
 * Auto-registered by Spring Data JPA.
 */
public interface AlertRepository extends JpaRepository<MetricAlert, Long> {

    List<MetricAlert> findAllByOrderByTimestampDesc();

    List<MetricAlert> findByNodeIdOrderByTimestampDesc(String nodeId);
}