package com.dashboard.controller;

import com.dashboard.entity.PredictionView;
import com.dashboard.repository.PredictionViewRepository;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/dashboard/predictions")
public class PredictionController {

    private final PredictionViewRepository repository;

    public PredictionController(PredictionViewRepository repository) {
        this.repository = repository;
    }

    @GetMapping
    public List<PredictionView> recent() {
        return repository.findTop20ByOrderByGeneratedAtDesc();
    }

    @GetMapping("/service/{serviceName}")
    public List<PredictionView> forService(@PathVariable String serviceName) {
        return repository.findByServiceNameOrderByGeneratedAtDesc(serviceName);
    }

    @GetMapping("/at-risk")
    public List<PredictionView> atRisk() {
        return repository.findBySeverityInOrderByGeneratedAtDesc(List.of("MEDIUM", "HIGH"));
    }
}