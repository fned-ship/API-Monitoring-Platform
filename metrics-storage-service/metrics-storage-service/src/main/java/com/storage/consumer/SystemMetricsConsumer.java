package com.storage.consumer;

import com.monitoring.common.events.SystemMetricEvent;
import com.storage.entity.SystemMetric;
import com.storage.repository.SystemMetricRepository;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
public class SystemMetricsConsumer {

    private final SystemMetricRepository repository;

    public SystemMetricsConsumer(SystemMetricRepository repository) {
        this.repository = repository;
    }

    @KafkaListener(
        topics = "api-system-metrics",
        groupId = "cg-metrics-storage",
        properties = {"spring.json.value.default.type=com.monitoring.common.events.SystemMetricEvent"}
    )
    public void consume(SystemMetricEvent event) {
        SystemMetric metric = new SystemMetric();
        metric.setServiceName(event.serviceName());
        metric.setCpuUsagePct(event.cpuUsagePercent());
        metric.setMemoryUsedMb(event.memoryUsedMb());
        metric.setMemoryMaxMb(event.memoryMaxMb());
        metric.setTimestamp(event.timestamp());
        repository.save(metric);
    }
}