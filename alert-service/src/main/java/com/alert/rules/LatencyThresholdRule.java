package com.alert.rules;

import com.monitoring.common.events.ApiMetricEvent;
import com.monitoring.common.events.AlertEvent;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.time.Instant;
import java.util.Optional;
import java.util.UUID;

@Component
public class LatencyThresholdRule {

    @Value("${alert.latency-threshold-ms:1000}")
    private double thresholdMs;

    public Optional<AlertEvent> evaluate(ApiMetricEvent event) {
        if (event.responseTimeMs() > thresholdMs) {
            return Optional.of(new AlertEvent(
                    UUID.randomUUID(), event.serviceName(), "HIGH_LATENCY", "CRITICAL",
                    "Response time exceeded threshold on " + event.endpoint(),
                    thresholdMs, event.responseTimeMs(), Instant.now()
            ));
        }
        return Optional.empty();
    }
}