package com.monitoring.common.events;

import java.time.Instant;
import java.util.List;

public record PredictionEvent(
        String predictionId,
        String serviceName,
        String predictionType,
        double riskScore,
        String severity,
        double confidence,
        List<String> contributingFeatures,
        String modelVersion,
        Instant windowTimestamp,
        Instant generatedAt
) {}