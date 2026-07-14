package com.monitoring.starter.metrics;

import com.monitoring.common.events.SystemMetricEvent;
import com.monitoring.starter.config.MonitoringProperties;
import com.monitoring.starter.kafka.KafkaEventPublisher;
import org.springframework.scheduling.annotation.Scheduled;

import java.lang.management.ManagementFactory;
// 1. Change the import to the com.sun implementation
import com.sun.management.OperatingSystemMXBean;
import java.time.Instant;
import java.util.UUID;

public class SystemMetricsScheduler {

    private final KafkaEventPublisher publisher;
    private final MonitoringProperties properties;
    
    // 2. Fetch the platform MXBean using the correct interface class
    private final OperatingSystemMXBean osBean = 
            ManagementFactory.getPlatformMXBean(OperatingSystemMXBean.class);

    public SystemMetricsScheduler(KafkaEventPublisher publisher, MonitoringProperties properties) {
        this.publisher = publisher;
        this.properties = properties;
    }

    @Scheduled(fixedDelayString = "${monitoring.system-metrics-interval-ms:15000}")
    public void sample() {
        // 3. This method will now resolve successfully
        double cpuLoad = osBean.getCpuLoad() * 100.0; 
        Runtime runtime = Runtime.getRuntime();
        double usedMb = (runtime.totalMemory() - runtime.freeMemory()) / (1024.0 * 1024.0);
        double maxMb = runtime.maxMemory() / (1024.0 * 1024.0);

        publisher.publishSystemMetric(new SystemMetricEvent(
                UUID.randomUUID(), properties.getServiceName(),
                cpuLoad, usedMb, maxMb, Instant.now()
        ));
    }
}
