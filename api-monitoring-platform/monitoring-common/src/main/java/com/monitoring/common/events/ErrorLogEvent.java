package com.monitoring.common.events;

import java.time.Instant;
import java.util.UUID;

public record ErrorLogEvent(
        UUID eventId,
        String serviceName,
        String endpoint,
        int statusCode,
        String errorMessage,
        String stackTrace,
        Instant timestamp
) {}