package com.monitoring.common.events;

import java.time.Instant;

public record MetricForecastEvent(
        String forecastId,
        String serviceName,
        String targetMetric,
        double currentValue,
        double predictedValue,
        double predictedChangePct,
        int horizonSeconds,
        String trendDirection,
        String modelVersion,
        Instant windowTimestamp,
        Instant generatedAt
) {}