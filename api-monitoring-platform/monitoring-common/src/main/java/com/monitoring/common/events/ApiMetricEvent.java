package com.monitoring.common.events;

import java.time.Instant;
import java.util.UUID;

public record ApiMetricEvent(
        UUID eventId,
        String serviceName,
        String endpoint,
        String httpMethod,
        int statusCode,
        long responseTimeMs,
        Instant timestamp
) {
    public static ApiMetricEvent of(String serviceName, String endpoint, String method,
                                     int statusCode, long responseTimeMs) {
        return new ApiMetricEvent(UUID.randomUUID(), serviceName, endpoint, method,
                statusCode, responseTimeMs, Instant.now());
    }
}