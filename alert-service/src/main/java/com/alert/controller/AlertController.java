package com.alert.controller;

import com.alert.entity.Alert;
import com.alert.repository.AlertRepository;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.util.List;

@RestController
@RequestMapping("/api/v1/alerts")
public class AlertController {

    private final AlertRepository repository;

    public AlertController(AlertRepository repository) {
        this.repository = repository;
    }

    @GetMapping
    public List<Alert> list(@RequestParam(defaultValue = "OPEN") String status) {
        return repository.findByStatus(status);
    }

    @GetMapping("/{id}")
    public Alert get(@PathVariable Long id) {
        return repository.findById(id).orElseThrow();
    }

    @PutMapping("/{id}/acknowledge")
    public Alert acknowledge(@PathVariable Long id) {
        Alert alert = repository.findById(id).orElseThrow();
        alert.setStatus("ACKNOWLEDGED");
        return repository.save(alert);
    }

    @PutMapping("/{id}/resolve")
    public Alert resolve(@PathVariable Long id) {
        Alert alert = repository.findById(id).orElseThrow();
        alert.setStatus("RESOLVED");
        alert.setResolvedAt(Instant.now());
        return repository.save(alert);
    }
}