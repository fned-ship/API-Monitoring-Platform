package com.dashboard.controller;

import com.dashboard.entity.ApiMetricView;
import com.dashboard.repository.ApiMetricViewRepository;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/v1/dashboard")
public class DashboardController {

    private final ApiMetricViewRepository repository;

    public DashboardController(ApiMetricViewRepository repository) {
        this.repository = repository;
    }

    @GetMapping("/overview")
    public Map<String, Object> overview() {
        List<ApiMetricView> recent = repository.findTop50ByOrderByTimestampDesc();
        Map<String, Long> requestsByService = recent.stream()
                .collect(Collectors.groupingBy(ApiMetricView::getServiceName, Collectors.counting()));
        double avgLatency = recent.stream().mapToInt(ApiMetricView::getResponseTimeMs).average().orElse(0);
        return Map.of(
                "totalRecentRequests", recent.size(),
                "requestsByService", requestsByService,
                "averageLatencyMs", avgLatency
        );
    }

    @GetMapping("/services/{serviceName}")
    public List<ApiMetricView> serviceDetail(@PathVariable String serviceName) {
        return repository.findByServiceNameOrderByTimestampDesc(serviceName);
    }

    @GetMapping("/services")
    public List<String> listServices() {
        return repository.findDistinctServiceNames();
    }
}