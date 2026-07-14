package com.monitoring.common.events;

import java.time.Instant;
import java.util.UUID;

public record AlertEvent(
        UUID alertId,
        String serviceName,
        String alertType,      // HIGH_LATENCY, HIGH_ERROR_RATE
        String severity,       // WARNING, CRITICAL
        String message,
        double thresholdValue,
        double observedValue,
        Instant triggeredAt
) {}