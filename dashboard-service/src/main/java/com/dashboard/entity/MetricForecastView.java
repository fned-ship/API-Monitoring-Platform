package com.dashboard.entity;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "metric_forecast")
public class MetricForecastView {
    @Id
    private Long id;
    private String serviceName;
    private String targetMetric;
    private double currentValue;
    private double predictedValue;
    private double predictedChangePct;
    private String trendDirection;
    private String modelVersion;
    private Instant generatedAt;

    public String getServiceName() { return serviceName; }
    public String getTargetMetric() { return targetMetric; }
    public double getCurrentValue() { return currentValue; }
    public double getPredictedValue() { return predictedValue; }
    public double getPredictedChangePct() { return predictedChangePct; }
    public String getTrendDirection() { return trendDirection; }
    public String getModelVersion() { return modelVersion; }
    public Instant getGeneratedAt() { return generatedAt; }
}