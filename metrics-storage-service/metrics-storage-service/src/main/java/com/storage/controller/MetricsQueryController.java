package com.storage.controller;

import com.storage.entity.ApiMetric;
import com.storage.entity.SystemMetric;
import com.storage.repository.ApiMetricRepository;
import com.storage.repository.SystemMetricRepository;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/metrics")
public class MetricsQueryController {

    private final ApiMetricRepository metricRepository;
    private final SystemMetricRepository systemRepository;

    public MetricsQueryController(ApiMetricRepository metricRepository,
                                   SystemMetricRepository systemRepository) {
        this.metricRepository = metricRepository;
        this.systemRepository = systemRepository;
    }

    @GetMapping("/requests")
    public List<ApiMetric> getRequests(@RequestParam String serviceName) {
        return metricRepository.findByServiceNameOrderByTimestampDesc(serviceName);
    }

    @GetMapping("/requests/summary")
    public Map<String, Object> getSummary(@RequestParam String serviceName) {
        List<ApiMetric> metrics = metricRepository.findByServiceNameOrderByTimestampDesc(serviceName);
        double avgLatency = metrics.stream().mapToInt(ApiMetric::getResponseTimeMs).average().orElse(0);
        long errorCount = metrics.stream().filter(m -> m.getStatusCode() >= 500).count();
        return Map.of(
                "serviceName", serviceName,
                "totalRequests", metrics.size(),
                "averageLatencyMs", avgLatency,
                "errorCount", errorCount
        );
    }

    @GetMapping("/system")
    public List<SystemMetric> getSystemMetrics(@RequestParam String serviceName) {
        return systemRepository.findByServiceNameOrderByTimestampDesc(serviceName);
    }
}