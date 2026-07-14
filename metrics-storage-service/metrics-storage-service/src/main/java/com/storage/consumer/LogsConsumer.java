package com.storage.consumer;

import com.monitoring.common.events.ErrorLogEvent;
import com.storage.entity.ErrorLog;
import com.storage.repository.ErrorLogRepository;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
public class LogsConsumer {

    private final ErrorLogRepository repository;

    public LogsConsumer(ErrorLogRepository repository) {
        this.repository = repository;
    }

    @KafkaListener(
        topics = "api-error-logs",
        groupId = "cg-metrics-storage",
        properties = {"spring.json.value.default.type=com.monitoring.common.events.ErrorLogEvent"}
    )
    public void consume(ErrorLogEvent event) {
        ErrorLog log = new ErrorLog();
        log.setServiceName(event.serviceName());
        log.setEndpoint(event.endpoint());
        log.setStatusCode(event.statusCode());
        log.setErrorMessage(event.errorMessage());
        log.setStackTrace(event.stackTrace());
        log.setTimestamp(event.timestamp());
        repository.save(log);
    }
}