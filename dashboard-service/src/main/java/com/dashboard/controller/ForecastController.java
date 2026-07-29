package com.dashboard.controller;

import com.dashboard.entity.MetricForecastView;
import com.dashboard.repository.MetricForecastViewRepository;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/dashboard/forecasts")
public class ForecastController {

    private final MetricForecastViewRepository repository;

    public ForecastController(MetricForecastViewRepository repository) {
        this.repository = repository;
    }

    @GetMapping
    public List<MetricForecastView> forService(@RequestParam String serviceName, @RequestParam String metric) {
        return repository.findByServiceNameAndTargetMetricOrderByGeneratedAtDesc(serviceName, metric);
    }

    @GetMapping("/trending")
    public List<MetricForecastView> trendingUp() {
        return repository.findByTrendDirectionOrderByGeneratedAtDesc("RISING");
    }
}