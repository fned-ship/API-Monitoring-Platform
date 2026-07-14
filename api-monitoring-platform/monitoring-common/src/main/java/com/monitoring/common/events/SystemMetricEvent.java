package com.monitoring.common.events;

import java.time.Instant;
import java.util.UUID;

public record SystemMetricEvent(
        UUID eventId,
        String serviceName,
        double cpuUsagePercent,
        double memoryUsedMb,
        double memoryMaxMb,
        Instant timestamp
) {}