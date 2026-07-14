package com.monitoring.starter.kafka;

import com.monitoring.common.events.*;
import org.springframework.kafka.core.KafkaTemplate;

public class KafkaEventPublisher {

    private final KafkaTemplate<String, Object> kafkaTemplate;

    public KafkaEventPublisher(KafkaTemplate<String, Object> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    public void publishMetric(ApiMetricEvent event) {
        kafkaTemplate.send("api-request-metrics", event.serviceName(), event);
    }

    public void publishSystemMetric(SystemMetricEvent event) {
        kafkaTemplate.send("api-system-metrics", event.serviceName(), event);
    }

    public void publishErrorLog(ErrorLogEvent event) {
        kafkaTemplate.send("api-error-logs", event.serviceName(), event);
    }
}