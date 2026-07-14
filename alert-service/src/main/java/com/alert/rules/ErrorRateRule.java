package com.alert.rules;

import com.monitoring.common.events.ApiMetricEvent;
import com.monitoring.common.events.AlertEvent;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;

@Component
public class ErrorRateRule {

    @Value("${alert.error-rate-window-seconds:60}")
    private int windowSeconds;

    @Value("${alert.error-rate-threshold:5}")
    private int errorCountThreshold;

    private final ConcurrentHashMap<String, List<Instant>> errorTimestamps = new ConcurrentHashMap<>();

    public Optional<AlertEvent> evaluate(ApiMetricEvent event) {
        if (event.statusCode() != 500) return Optional.empty();

        List<Instant> timestamps = errorTimestamps.computeIfAbsent(
                event.serviceName(), k -> new CopyOnWriteArrayList<>());
        Instant now = Instant.now();
        timestamps.add(now);
        timestamps.removeIf(t -> t.isBefore(now.minusSeconds(windowSeconds)));

        if (timestamps.size() >= errorCountThreshold) {
            return Optional.of(new AlertEvent(
                    UUID.randomUUID(), event.serviceName(), "HIGH_ERROR_RATE", "CRITICAL",
                    timestamps.size() + " HTTP 500 errors in the last " + windowSeconds + "s",
                    errorCountThreshold, timestamps.size(), now
            ));
        }
        return Optional.empty();
    }
}