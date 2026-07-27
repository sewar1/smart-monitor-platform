package main.java.com.sewarl.smartmonitor.service;

import com.sewarl.smartmonitor.entity.Metric;
import com.sewarl.smartmonitor.repository.MetricRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class MetricServiceTest {

    @Mock
    private MetricRepository metricRepository;

    @Mock
    private AlertService alertService;

    @Mock
    private SystemAnalyzerService systemAnalyzerService;

    @InjectMocks
    private MetricService metricService;

    private Metric sampleMetric;

    @BeforeEach
    void setUp() {
        sampleMetric = new Metric();
        sampleMetric.setNodeId("node-1");
        sampleMetric.setCpuUsage(new BigDecimal("45.50"));
        sampleMetric.setRamUsage(new BigDecimal("60.00"));
        sampleMetric.setDiskUsage(new BigDecimal("30.00"));
        sampleMetric.setTimestamp(OffsetDateTime.now());
    }

    @Test
    void testSaveMetric_Success() {
        // Mock behaviors
        when(systemAnalyzerService.calculateWeightedHealthScore(any(), any(), any()))
                .thenReturn(new BigDecimal("85.00"));
        when(systemAnalyzerService.classifyHealthStatus(any()))
                .thenReturn("HEALTHY");
        when(systemAnalyzerService.executeAntiFreezeGuard(any(), any(), any(), any()))
                .thenReturn(List.of());
        when(metricRepository.findTop3ByNodeIdOrderByTimestampDesc(any()))
                .thenReturn(List.of());
        when(metricRepository.save(any(Metric.class)))
                .thenReturn(sampleMetric);

        // Execute
        Metric savedMetric = metricService.saveMetric(sampleMetric);

        // Verify
        assertNotNull(savedMetric);
        assertEquals("node-1", savedMetric.getNodeId());
        assertEquals("HEALTHY", savedMetric.getStatus());
        verify(metricRepository, times(1)).save(sampleMetric);
        verify(alertService, times(1)).evaluateInfrastructureNode(sampleMetric);
    }

    @Test
    void testGetNodesConnectivityStatuses_Online() {
        // First save a metric to populate the internal heartbeatTracker cache
        when(systemAnalyzerService.calculateWeightedHealthScore(any(), any(), any()))
                .thenReturn(new BigDecimal("90.00"));
        when(systemAnalyzerService.classifyHealthStatus(any()))
                .thenReturn("HEALTHY");
        when(systemAnalyzerService.executeAntiFreezeGuard(any(), any(), any(), any()))
                .thenReturn(List.of());
        when(metricRepository.findTop3ByNodeIdOrderByTimestampDesc(any()))
                .thenReturn(List.of());
        when(metricRepository.save(any(Metric.class)))
                .thenReturn(sampleMetric);

        metricService.saveMetric(sampleMetric);

        // Check connectivity status
        Map<String, String> statuses = metricService.getNodesConnectivityStatuses();

        assertFalse(statuses.isEmpty());
        assertEquals("Online", statuses.get("node-1"));
    }

    @Test
    void testPurgeHistoricalMetrics() {
        when(metricRepository.purgeMetricsOlderThan(any())).thenReturn(5);

        // Run the scheduled purge method directly
        assertDoesNotThrow(() -> metricService.purgeHistoricalMetrics());

        verify(metricRepository, times(1)).purgeMetricsOlderThan(any());
    }
}
