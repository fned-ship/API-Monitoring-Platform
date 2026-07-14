package com.storage.controller;

import com.storage.entity.ErrorLog;
import com.storage.repository.ErrorLogRepository;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/logs")
public class LogsQueryController {

    private final ErrorLogRepository repository;

    public LogsQueryController(ErrorLogRepository repository) {
        this.repository = repository;
    }

    @GetMapping("/errors")
    public List<ErrorLog> getErrors(@RequestParam String serviceName) {
        return repository.findByServiceNameOrderByTimestampDesc(serviceName);
    }
}