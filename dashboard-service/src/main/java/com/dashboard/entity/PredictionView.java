package com.dashboard.entity;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "prediction")
public class PredictionView {
    @Id
    private Long id;
    private String predictionId;
    private String serviceName;
    private String predictionType;
    private double riskScore;
    private String severity;
    private boolean isAnomaly;
    private String contributingFeatures;   // stored as JSON text
    private String modelVersion;
    private Instant windowTimestamp;
    private Instant generatedAt;

    public String getPredictionId() { return predictionId; }
    public String getServiceName() { return serviceName; }
    public String getPredictionType() { return predictionType; }
    public double getRiskScore() { return riskScore; }
    public String getSeverity() { return severity; }
    public boolean getIsAnomaly() { return isAnomaly; }
    public String getContributingFeatures() { return contributingFeatures; }
    public String getModelVersion() { return modelVersion; }
    public Instant getGeneratedAt() { return generatedAt; }
}