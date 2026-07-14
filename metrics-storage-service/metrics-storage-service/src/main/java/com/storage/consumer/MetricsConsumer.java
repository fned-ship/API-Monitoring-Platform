package com.storage.consumer;

import com.monitoring.common.events.ApiMetricEvent;
import com.storage.entity.ApiMetric;
import com.storage.repository.ApiMetricRepository;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
public class MetricsConsumer {

    private final ApiMetricRepository repository;

    public MetricsConsumer(ApiMetricRepository repository) {
        this.repository = repository;
    }

    @KafkaListener(
        topics = "api-request-metrics",
        groupId = "cg-metrics-storage",
        properties = {"spring.json.value.default.type=com.monitoring.common.events.ApiMetricEvent"}
    )
    public void consume(ApiMetricEvent event) {
        ApiMetric metric = new ApiMetric();
        metric.setServiceName(event.serviceName());
        metric.setEndpoint(event.endpoint());
        metric.setHttpMethod(event.httpMethod());
        metric.setStatusCode(event.statusCode());
        metric.setResponseTimeMs((int) event.responseTimeMs());
        metric.setTimestamp(event.timestamp());
        repository.save(metric);
    }
}